from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.core.database import get_db
from app.services.ml.scorer import scorer

router = APIRouter()

class PredictionRequest(BaseModel):
    amount: float
    customer_ltv: float = 0.0
    successful_transactions: int = 0
    failed_transactions: int = 0
    retry_count: int = 0
    is_suspicious: bool = False
    failure_category: str = "TEMPORARY_GATEWAY"
    payment_method: str = "UPI"

@router.post("/predict")
def predict_recovery_probability(payload: PredictionRequest):
    data = payload.model_dump()
    prob, tier, score = scorer.predict_probability(data)
    return {
        "recovery_probability": prob,
        "priority_tier": tier,
        "priority_score": score,
        "features_evaluated": data
    }

@router.post("/train")
def train_model_endpoint(db: Session = Depends(get_db)):
    results = scorer.train_model(db)
    return results
