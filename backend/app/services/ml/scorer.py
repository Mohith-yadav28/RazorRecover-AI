import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss
)
from sqlalchemy.orm import Session
from app.models.domain import Transaction, Customer

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

CATEGORY_MAP = {
    "TEMPORARY_GATEWAY": 0,
    "PERMANENT_CUSTOMER": 1,
    "CHECKOUT_ABANDONMENT": 2,
    "SUBSCRIPTION": 3,
    "OVERDUE_RECEIVABLE": 4
}

METHOD_MAP = {
    "UPI": 0,
    "CARD": 1,
    "NETBANKING": 2,
    "WALLET": 3
}

class MLRecoveryScorer:
    """
    Machine Learning Recovery Probability Engine.
    NOTE: The ML model strictly predicts the `recovery_probability`.
    The Agent Decision Engine (not the ML model) determines the intervention strategy.
    """
    def __init__(self):
        self.model = None
        self.feature_names = [
            "amount",
            "customer_ltv",
            "successful_transactions",
            "failed_transactions",
            "retry_count",
            "is_suspicious",
            "category_code",
            "method_code"
        ]
        self._load_or_create_default_model()

    def _load_or_create_default_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                return
            except Exception as e:
                print(f"[WARN] Failed to load model file: {e}")

        # Default Random Forest Model
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        dummy_X = np.array([
            [4999.0, 50000.0, 10, 1, 0, 0, 0, 0],
            [85000.0, 1000.0, 0, 3, 2, 1, 1, 1],
            [1499.0, 12000.0, 3, 0, 0, 0, 2, 0]
        ])
        dummy_y = np.array([1, 0, 1])
        self.model.fit(dummy_X, dummy_y)

    def extract_features_from_dict(self, data: Dict[str, Any]) -> np.ndarray:
        amount = float(data.get("amount", 0.0))
        ltv = float(data.get("customer_ltv", 0.0))
        succ_txns = int(data.get("successful_transactions", 0))
        failed_txns = int(data.get("failed_transactions", 0))
        retry_cnt = int(data.get("retry_count", 0))
        is_susp = 1 if data.get("is_suspicious", False) else 0
        
        cat_str = str(data.get("failure_category", "TEMPORARY_GATEWAY")).upper()
        method_str = str(data.get("payment_method", "UPI")).upper()

        cat_code = CATEGORY_MAP.get(cat_str, 0)
        method_code = METHOD_MAP.get(method_str, 0)

        return np.array([[amount, ltv, succ_txns, failed_txns, retry_cnt, is_susp, cat_code, method_code]])

    def predict_probability(self, data: Dict[str, Any]) -> Tuple[float, str, float]:
        """
        Returns (recovery_probability, priority_tier, priority_score)
        """
        features = self.extract_features_from_dict(data)
        prob_array = self.model.predict_proba(features)
        ml_prob = float(prob_array[0][1]) if len(prob_array[0]) > 1 else float(prob_array[0][0])
        
        amount = float(data.get("amount", 0.0))
        is_susp = data.get("is_suspicious", False)
        
        final_prob = ml_prob
        if is_susp:
            final_prob *= 0.3
        
        final_prob = max(0.05, min(0.98, round(final_prob, 2)))
        
        if (final_prob >= 0.75 and amount >= 3000) or amount > 50000:
            tier = "HIGH"
        elif final_prob >= 0.50:
            tier = "MEDIUM"
        else:
            tier = "LOW"
            
        priority_score = round(final_prob * (amount / 1000.0), 2)
        return final_prob, tier, priority_score

    def train_model(self, db: Session) -> Dict[str, Any]:
        """
        Trains & compares Logistic Regression vs Random Forest using 80/20 train/test split.
        Reports Accuracy, Precision, Recall, F1, ROC-AUC, and Brier Score.
        """
        records = db.query(Transaction, Customer).join(Customer, Transaction.customer_id == Customer.id).all()
        
        if not records or len(records) < 50:
            return {"status": "skipped", "reason": "Insufficient dataset records for training"}
        
        X_list = []
        y_list = []

        for txn, cust in records:
            cat_code = CATEGORY_MAP.get(str(txn.failure_category).upper(), 0)
            method_code = METHOD_MAP.get(str(txn.payment_method).upper(), 0)
            
            row = [
                float(txn.amount),
                float(cust.lifetime_value),
                int(cust.successful_transactions),
                int(cust.failed_transactions),
                int(txn.retry_count),
                1 if txn.is_suspicious else 0,
                cat_code,
                method_code
            ]
            y_list.append(1 if txn.recovered else 0)
            X_list.append(row)

        X = np.array(X_list)
        y = np.array(y_list)

        # 80/20 Train / Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

        # Model 1: Logistic Regression
        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        y_pred_lr = lr.predict(X_test)
        y_prob_lr = lr.predict_proba(X_test)[:, 1] if len(lr.classes_) > 1 else y_pred_lr

        lr_metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred_lr)), 4),
            "precision": round(float(precision_score(y_test, y_pred_lr, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred_lr, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred_lr, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_prob_lr)), 4) if len(np.unique(y_test)) > 1 else 0.5,
            "brier_score": round(float(brier_score_loss(y_test, y_prob_lr)), 4)
        }

        # Model 2: Random Forest Classifier
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)
        y_prob_rf = rf.predict_proba(X_test)[:, 1] if len(rf.classes_) > 1 else y_pred_rf

        rf_metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred_rf)), 4),
            "precision": round(float(precision_score(y_test, y_pred_rf, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred_rf, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred_rf, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_prob_rf)), 4) if len(np.unique(y_test)) > 1 else 0.5,
            "brier_score": round(float(brier_score_loss(y_test, y_prob_rf)), 4)
        }

        # Select winner (Random Forest) and save model
        joblib.dump(rf, MODEL_PATH)
        self.model = rf

        feature_importance = dict(zip(self.feature_names, [round(float(f), 4) for f in rf.feature_importances_]))

        return {
            "status": "trained",
            "samples_total": len(records),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "selected_model": "RandomForestClassifier",
            "random_forest_metrics": rf_metrics,
            "logistic_regression_metrics": lr_metrics,
            "feature_importance": feature_importance
        }

scorer = MLRecoveryScorer()
