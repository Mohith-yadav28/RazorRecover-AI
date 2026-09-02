from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.models.domain import AuditEvent, Transaction, RecoveryCase, Customer
from app.schemas.domain import AuditEventResponse, AgentRunResponse

from app.services.agent.orchestrator import orchestrator

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/run/{transaction_id}")
def run_agent_workflow(transaction_id: str, human_approved: bool = Query(False), db: Session = Depends(get_db)):
    res = orchestrator.run_recovery_workflow(transaction_id, db, human_approved=human_approved)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/query")
def agent_conversational_query(payload: QueryRequest, db: Session = Depends(get_db)):
    q = payload.query.lower()
    
    if "at risk" in q or "risk" in q:
        tot_risk = db.query(Transaction).filter(Transaction.status.in_(["FAILED", "ABANDONED"])).all()
        val = sum(t.amount for t in tot_risk)
        return {
            "answer": f"Currently, there is **₹{val:,.2f}** total revenue at risk across {len(tot_risk):,} unrecovered transaction records.",
            "data": {"revenue_at_risk": val, "case_count": len(tot_risk)}
        }
    elif "recover" in q or "recovered" in q:
        rec_cases = db.query(RecoveryCase).filter(RecoveryCase.status == "RECOVERED").all()
        val = sum(c.recovered_amount for c in rec_cases)
        return {
            "answer": f"RazorRecover AI has successfully recovered **₹{val:,.2f}** across {len(rec_cases):,} verified payment interventions.",
            "data": {"revenue_recovered": val, "recovered_count": len(rec_cases)}
        }
    elif "human" in q or "approval" in q or "escalat" in q:
        esc_cases = db.query(RecoveryCase).filter(RecoveryCase.policy_result == "HUMAN_APPROVAL_REQUIRED").all()
        return {
            "answer": f"There are currently **{len(esc_cases)} cases requiring human merchant approval** because they exceed the automatic threshold (₹50,000) or carry high suspicion scores.",
            "data": {"escalated_count": len(esc_cases)}
        }
    else:
        # Default response using backend database facts
        cases = db.query(RecoveryCase).limit(5).all()
        return {
            "answer": f"RazorRecover AI agent is active. Total active recovery cases in queue: {len(cases)}. High recovery probability cases are automatically processed under bounded safety policy rules.",
            "data": {"active_cases": len(cases)}
        }

@router.post("/batch-run")
def run_batch_agent_scan(limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db)):
    res = orchestrator.run_batch_recovery_scan(db, limit=limit)
    return res

@router.get("/runs", response_model=List[AgentRunResponse])
def get_agent_runs(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    from app.models.domain import AgentRun
    return db.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(limit).all()

@router.get("/audit-trail", response_model=List[AuditEventResponse])
def get_audit_trail(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    agent_step: Optional[str] = None
):
    query = db.query(AuditEvent)
    if agent_step:
        query = query.filter(AuditEvent.agent_step == agent_step)
    return query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()

