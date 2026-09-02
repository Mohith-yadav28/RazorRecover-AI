from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.domain import PolicyRule
from app.schemas.domain import PolicyRuleResponse
from app.services.policy.engine import policy_engine

router = APIRouter()

class PolicyEvaluationRequest(BaseModel):
    recommended_action: str
    amount: float
    recovery_probability: float
    retry_count: int = 0
    is_suspicious: bool = False
    contact_count: int = 0

@router.get("/", response_model=List[PolicyRuleResponse])
def get_policy_rules(db: Session = Depends(get_db)):
    return db.query(PolicyRule).all()

@router.post("/evaluate")
def evaluate_policy(payload: PolicyEvaluationRequest):
    context = payload.model_dump()
    res = policy_engine.evaluate(payload.recommended_action, context)
    return res.to_dict()

