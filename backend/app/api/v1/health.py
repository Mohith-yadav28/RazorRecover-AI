from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    db_status = "unhealthy"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/status")
def get_status():
    return {
        "agent_status": "ACTIVE",
        "mode": "TEST_MODE" if settings.RAZORPAY_MODE == "test" else "LIVE",
        "razorpay_integration": "ACTIVE" if settings.RAZORPAY_KEY_ID and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_demo") else "DEMO_FALLBACK",
        "bounded_policy_engine": "ACTIVE",
        "audit_logging": "ENABLED"
    }

@router.post("/reset-demo")
def reset_demo_state(db: Session = Depends(get_db)):
    """
    Resets all demo transactions, cases, and audit events back to their initial state.
    Restores KPI calculations to baseline seed state.
    """
    from app.models.domain import Transaction, RecoveryCase, AuditEvent
    
    # 1. Reset demo transactions
    demo_txns = db.query(Transaction).filter(Transaction.id.like("TXN_DEMO_%")).all()
    for dt in demo_txns:
        dt.status = "FAILED"
        dt.recovered = False
        dt.recovered_amount = 0.0
        dt.recovered_at = None

    # 2. Reset cases created for demo transactions
    demo_cases = db.query(RecoveryCase).filter(RecoveryCase.transaction_id.like("TXN_DEMO_%")).all()
    for dc in demo_cases:
        if "SCENARIO_3" in dc.id or "SCENARIO_5" in dc.id:
            dc.status = "ESCALATED"
        elif "SCENARIO_4" in dc.id:
            dc.status = "STOPPED"
        else:
            dc.status = "OPEN"
        dc.recovered_amount = 0.0

    # 3. Delete demo audit events created during interactive testing
    db.query(AuditEvent).filter(AuditEvent.transaction_id.like("TXN_DEMO_%")).delete(synchronize_session=False)
    
    db.commit()

    return {
        "status": "success",
        "message": "Demo state reset successfully. Initial transaction states restored."
    }

