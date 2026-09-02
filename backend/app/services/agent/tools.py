from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.domain import Transaction, Customer, RecoveryCase, RecoveryAction, AuditEvent, generate_uuid, utc_now
from app.services.ml.scorer import scorer
from app.services.policy.engine import policy_engine

class ControlledAgentTools:
    """
    Explicit tool definitions. The LLM agent can only execute actions via these backend methods.
    Direct SQL execution or raw command execution is strictly prohibited.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        txn = self.db.query(Transaction).filter(Transaction.id == txn_id).first()
        if not txn:
            return None
        return {
            "id": txn.id,
            "customer_id": txn.customer_id,
            "amount": txn.amount,
            "currency": txn.currency,
            "status": txn.status,
            "failure_reason": txn.failure_reason,
            "failure_category": txn.failure_category,
            "payment_method": txn.payment_method,
            "retry_count": txn.retry_count,
            "is_suspicious": txn.is_suspicious,
            "created_at": txn.created_at.isoformat()
        }

    def get_customer_history(self, customer_id: str) -> Optional[Dict[str, Any]]:
        cust = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if not cust:
            return None
        return {
            "id": cust.id,
            "name": cust.name,
            "email": cust.email,
            "lifetime_value": cust.lifetime_value,
            "total_transactions": cust.total_transactions,
            "successful_transactions": cust.successful_transactions,
            "failed_transactions": cust.failed_transactions,
            "is_vip": cust.is_vip,
            "fraud_score": cust.fraud_score
        }

    def calculate_recovery_probability(self, txn_id: str) -> Dict[str, Any]:
        txn = self.get_transaction(txn_id)
        if not txn:
            return {"error": f"Transaction {txn_id} not found"}
        
        cust = self.get_customer_history(txn["customer_id"]) or {}
        
        feature_dict = {
            "amount": txn["amount"],
            "customer_ltv": cust.get("lifetime_value", 0.0),
            "successful_transactions": cust.get("successful_transactions", 0),
            "failed_transactions": cust.get("failed_transactions", 0),
            "retry_count": txn["retry_count"],
            "is_suspicious": txn["is_suspicious"],
            "failure_category": txn.get("failure_category", "TEMPORARY_GATEWAY"),
            "payment_method": txn.get("payment_method", "UPI")
        }
        
        prob, tier, score = scorer.predict_probability(feature_dict)
        return {
            "transaction_id": txn_id,
            "recovery_probability": prob,
            "priority_tier": tier,
            "priority_score": score
        }

    def check_policy(self, recommended_action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        result = policy_engine.evaluate(recommended_action, context)
        return result.to_dict()

    def record_audit_event(
        self,
        agent_step: str,
        event_type: str,
        txn_id: str = None,
        case_id: str = None,
        decision: str = None,
        reason: str = None,
        policy_name: str = None,
        result: str = None,
        recovered_amount: float = 0.0,
        details: Dict[str, Any] = None
    ) -> str:
        audit = AuditEvent(
            id=generate_uuid(),
            transaction_id=txn_id,
            case_id=case_id,
            agent_step=agent_step,
            event_type=event_type,
            decision=decision,
            reason=reason,
            policy_name=policy_name,
            result=result,
            recovered_amount=recovered_amount,
            details_json=details,
            timestamp=utc_now()
        )
        self.db.add(audit)
        self.db.commit()
        return audit.id
