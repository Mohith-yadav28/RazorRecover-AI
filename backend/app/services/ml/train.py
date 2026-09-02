import os
import sys

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import SessionLocal
from app.services.ml.scorer import scorer

def run_training():
    print("[INFO] Initiating ML Recovery Model Comparison & Evaluation Pipeline...")
    db = SessionLocal()
    try:
        results = scorer.train_model(db)
        print("\n==========================================================")
        print("MACHINE LEARNING MODEL EVALUATION RESULTS (80/20 SPLIT)")
        print("==========================================================")
        print(f"Total Dataset Samples:   {results.get('samples_total'):,}")
        print(f"Train Split (80%):       {results.get('train_samples'):,}")
        print(f"Test Split (20%):        {results.get('test_samples'):,}")
        print(f"Selected Production Model: {results.get('selected_model')}\n")

        rf_m = results.get("random_forest_metrics", {})
        print("--- Random Forest Classifier Metrics (Test Set) ---")
        print(f"  Accuracy:    {rf_m.get('accuracy') * 100:.2f}%")
        print(f"  Precision:   {rf_m.get('precision'):.4f}")
        print(f"  Recall:      {rf_m.get('recall'):.4f}")
        print(f"  F1 Score:    {rf_m.get('f1_score'):.4f}")
        print(f"  ROC-AUC:     {rf_m.get('roc_auc'):.4f}")
        print(f"  Brier Score: {rf_m.get('brier_score'):.4f} (Calibration Quality)\n")

        lr_m = results.get("logistic_regression_metrics", {})
        print("--- Logistic Regression Metrics (Test Set) ---")
        print(f"  Accuracy:    {lr_m.get('accuracy') * 100:.2f}%")
        print(f"  Precision:   {lr_m.get('precision'):.4f}")
        print(f"  Recall:      {lr_m.get('recall'):.4f}")
        print(f"  F1 Score:    {lr_m.get('f1_score'):.4f}")
        print(f"  ROC-AUC:     {lr_m.get('roc_auc'):.4f}")
        print(f"  Brier Score: {lr_m.get('brier_score'):.4f}\n")

        print("Feature Importance (Random Forest):")
        for feat, imp in results.get("feature_importance", {}).items():
            print(f"  - {feat:<24}: {imp:.4f}")
        print("==========================================================\n")
    finally:
        db.close()

if __name__ == "__main__":
    run_training()
