from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.domain import RecoveryCase, Transaction, Customer
from app.schemas.domain import RecoveryCaseResponse

router = APIRouter()

@router.get("/", response_model=List[RecoveryCaseResponse])
def get_recovery_cases(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    priority_tier: Optional[str] = None,
    status: Optional[str] = None,
    policy_result: Optional[str] = None,
    min_probability: Optional[float] = None,
    search: Optional[str] = None
):
    query = db.query(RecoveryCase).join(Transaction)

    if priority_tier:
        query = query.filter(RecoveryCase.priority_tier == priority_tier)
    if status:
        query = query.filter(RecoveryCase.status == status)
    if policy_result:
        query = query.filter(RecoveryCase.policy_result == policy_result)
    if min_probability is not None:
        query = query.filter(RecoveryCase.recovery_probability >= min_probability)
    if search:
        query = query.join(Customer).filter(
            (RecoveryCase.id.ilike(f"%{search}%")) |
            (Transaction.id.ilike(f"%{search}%")) |
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )

    return query.order_by(RecoveryCase.priority_score.desc(), RecoveryCase.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{case_id}", response_model=RecoveryCaseResponse)
def get_recovery_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Recovery case {case_id} not found")
    return case
