from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.domain import Transaction, Customer
from app.schemas.domain import TransactionResponse

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    failure_reason: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(Transaction)

    if status:
        query = query.filter(Transaction.status == status)
    if failure_reason:
        query = query.filter(Transaction.failure_reason == failure_reason)
    if search:
        query = query.join(Customer).filter(
            (Transaction.id.ilike(f"%{search}%")) |
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )

    return query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_detail(transaction_id: str, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
    return txn
