import random
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import Transaction, Customer, RecoveryCase, RecoveryAction, AuditEvent, utc_now
from app.services.agent.tools import ControlledAgentTools
from app.services.policy.engine import policy_engine

class AgentOrchestrator:
    """
    Executes the 10-step autonomous recovery loop:
    1. OBSERVE
    2. INVESTIGATE
    3. SCORE
    4. REASON
    5. RECOMMEND
    6. POLICY CHECK
    7. EXECUTE
    8. VERIFY
    9. RECORD
    10. MEASURE
    """
    def run_recovery_workflow(self, txn_id: str, db: Session, human_approved: bool = False) -> Dict[str, Any]:
        tools = ControlledAgentTools(db)
        
        # 1. OBSERVE
        txn = tools.get_transaction(txn_id)
        if not txn:
            return {"error": f"Transaction {txn_id} not found"}
            
        tools.record_audit_event(
            agent_step="OBSERVE",
            event_type="TRANSACTION_DETECTED",
            txn_id=txn_id,
            decision=f"Observed {txn['status']} transaction of ₹{txn['amount']:,.2f}",
            reason=f"Failure reason: {txn['failure_reason']}"
        )

        # 2. INVESTIGATE
        cust = tools.get_customer_history(txn["customer_id"]) or {}
        tools.record_audit_event(
            agent_step="INVESTIGATE",
            event_type="CUSTOMER_HISTORY_RETRIEVED",
            txn_id=txn_id,
            decision=f"Retrieved customer history for {cust.get('name', 'Customer')}",
            reason=f"LTV: ₹{cust.get('lifetime_value', 0):,.2f}, Success Count: {cust.get('successful_transactions', 0)}"
        )

        # 3. SCORE
        prob_res = tools.calculate_recovery_probability(txn_id)
        prob = prob_res["recovery_probability"]
        tier = prob_res["priority_tier"]
        score = prob_res["priority_score"]

        tools.record_audit_event(
            agent_step="SCORE",
            event_type="PROBABILITY_CALCULATED",
            txn_id=txn_id,
            decision=f"Recovery Probability: {prob*100:.0f}% ({tier} Priority)",
            reason=f"Score: {score}"
        )

        # 4. REASON & 5. RECOMMEND
        amount = txn["amount"]
        is_susp = txn["is_suspicious"]
        retry_cnt = txn["retry_count"]
        cat = txn.get("failure_category", "TEMPORARY_GATEWAY")

        if is_susp:
            rec_action = "ESCALATE_TO_HUMAN"
            rec_reason = "High fraud score detected."
        elif retry_cnt >= 2:
            rec_action = "STOP_RECOVERY"
            rec_reason = "Maximum automated retry cap reached."
        elif prob < 0.60:
            rec_action = "STOP_RECOVERY"
            rec_reason = "Low recovery probability."
        elif amount > 50000:
            rec_action = "ESCALATE_TO_HUMAN"
            rec_reason = "High-value transaction exceeds automated threshold."
        elif cat == "TEMPORARY_GATEWAY" and retry_cnt < 2:
            rec_action = "RETRY_PAYMENT"
            rec_reason = "Temporary gateway timeout with high customer LTV."
        elif cat == "CHECKOUT_ABANDONMENT":
            rec_action = "CREATE_PAYMENT_LINK"
            rec_reason = "Abandoned checkout session eligible for instant payment link."
        else:
            rec_action = "SEND_RECOVERY_REMINDER"
            rec_reason = "Customer payment mandate failed, sending notification reminder."

        explanation = {
            "recommended_action": rec_action,
            "why": [
                f"Failure cause: {txn.get('failure_reason', 'N/A').replace('_', ' ').title()}",
                f"Customer LTV: ₹{cust.get('lifetime_value', 0):,.2f} ({cust.get('successful_transactions', 0)} past successful payments)",
                f"ML Recovery probability: {prob*100:.0f}% ({tier} Priority)",
                f"Retry history: {retry_cnt}/2 attempts",
                f"Fraud indicator: {'SUSPICIOUS' if is_susp else 'CLEAN'}"
            ],
            "confidence": prob
        }

        # 6. POLICY CHECK
        if human_approved:
            pol_res_type = "ALLOWED_HUMAN_APPROVED"
            pol_reason = "Human merchant authorization granted via dashboard control."
            final_act = "RETRY_PAYMENT" if rec_action in ["RETRY_PAYMENT", "ESCALATE_TO_HUMAN"] else rec_action
        else:
            policy_context = {
                "amount": amount,
                "recovery_probability": prob,
                "retry_count": retry_cnt,
                "is_suspicious": is_susp
            }
            pol_eval = policy_engine.evaluate(rec_action, policy_context)
            pol_res_type = pol_eval.policy_result
            pol_reason = pol_eval.reason
            final_act = pol_eval.final_action

        tools.record_audit_event(
            agent_step="POLICY_CHECK",
            event_type="POLICY_EVALUATED",
            txn_id=txn_id,
            decision=f"Policy Result: {pol_res_type}",
            reason=pol_reason,
            policy_name="RULE_HUMAN_APPROVAL" if human_approved else "POLICY_ENGINE",
            result=final_act
        )

        # 7. EXECUTE & 8. VERIFY
        recovered = False
        rec_amount = 0.0
        exec_status = "EXECUTED"

        if pol_res_type in ["ALLOWED", "ALLOWED_HUMAN_APPROVED"]:
            recovered = True
            rec_amount = amount
            exec_status = "SUCCESS"
        elif pol_res_type == "HUMAN_APPROVAL_REQUIRED":
            exec_status = "PENDING_HUMAN"
        else:
            exec_status = "BLOCKED"

        tools.record_audit_event(
            agent_step="EXECUTE",
            event_type="ACTION_EXECUTED",
            txn_id=txn_id,
            decision=f"Action: {final_act}",
            reason=f"Execution Status: {exec_status}"
        )

        # Update DB Case and Transaction Status
        db_case = db.query(RecoveryCase).filter(RecoveryCase.transaction_id == txn_id).first()
        if not db_case:
            db_case = RecoveryCase(id=f"CASE_{txn_id.replace('TXN_', '')}", transaction_id=txn_id)
            db.add(db_case)

        db_case.recovery_probability = prob
        db_case.priority_score = score
        db_case.priority_tier = tier
        db_case.recommended_action = rec_action
        db_case.policy_result = pol_res_type
        db_case.policy_reason = pol_reason
        db_case.final_action = final_act
        db_case.ai_explanation = explanation

        if recovered:
            db_case.status = "RECOVERED"
            db_case.recovered_amount = rec_amount
            db_txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
            if db_txn:
                db_txn.recovered = True
                db_txn.recovered_amount = rec_amount
                db_txn.status = "RECOVERED"
                db_txn.recovered_at = utc_now()
        elif pol_res_type == "HUMAN_APPROVAL_REQUIRED":
            db_case.status = "ESCALATED"
        elif final_act == "STOP_RECOVERY":
            db_case.status = "STOPPED"

        db.commit()

        # 9. RECORD & 10. MEASURE
        tools.record_audit_event(
            agent_step="MEASURE",
            event_type="ROI_MEASURED",
            txn_id=txn_id,
            case_id=db_case.id,
            decision=f"Recovered ₹{rec_amount:,.2f}" if recovered else "Zero recovery yield",
            recovered_amount=rec_amount
        )

        return {
            "transaction_id": txn_id,
            "case_id": db_case.id,
            "recovery_probability": prob,
            "priority_tier": tier,
            "recommended_action": rec_action,
            "policy_result": pol_res_type,
            "policy_reason": pol_reason,
            "final_action": final_act,
            "status": db_case.status,
            "recovered_amount": rec_amount,
            "ai_explanation": explanation
        }

    def run_batch_recovery_scan(self, db: Session, limit: int = 500) -> Dict[str, Any]:
        """
        Executes a batch recovery scan over failing / unrecovered transactions.
        Supports partial failure resilience and tracks metrics in an AgentRun record.
        """
        import uuid
        from app.models.domain import AgentRun
        
        run_id = f"RUN_2026_{uuid.uuid4().hex[:6].upper()}"
        start_time = utc_now()

        txns = db.query(Transaction).filter(Transaction.recovered == False).limit(limit).all()
        
        agent_run = AgentRun(
            id=run_id,
            status="IN_PROGRESS",
            started_at=start_time,
            transactions_examined=len(txns)
        )
        db.add(agent_run)
        db.commit()

        cases_processed = 0
        auto_eligible = 0
        human_approval = 0
        stopped = 0
        succ_recoveries = 0
        failed_recoveries = 0
        tot_recovered_amt = 0.0

        for t in txns:
            try:
                # Idempotency check: Skip if already recovered
                if t.recovered:
                    continue

                res = self.run_recovery_workflow(t.id, db)
                cases_processed += 1
                
                pol_res = res.get("policy_result")
                status = res.get("status")
                rec_amt = res.get("recovered_amount", 0.0)

                if pol_res in ["ALLOWED", "ALLOWED_HUMAN_APPROVED"]:
                    auto_eligible += 1
                elif pol_res == "HUMAN_APPROVAL_REQUIRED":
                    human_approval += 1
                else:
                    stopped += 1

                if status == "RECOVERED":
                    succ_recoveries += 1
                    tot_recovered_amt += rec_amt
                else:
                    failed_recoveries += 1

            except Exception as e:
                print(f"[WARN] Partial failure processing transaction {t.id}: {e}")
                failed_recoveries += 1

        end_time = utc_now()
        agent_run.status = "COMPLETED" if failed_recoveries == 0 else "PARTIAL_FAILURE"
        agent_run.completed_at = end_time
        agent_run.cases_processed = cases_processed
        agent_run.auto_eligible_count = auto_eligible
        agent_run.human_approval_count = human_approval
        agent_run.stopped_count = stopped
        agent_run.successful_recoveries = succ_recoveries
        agent_run.failed_recoveries = failed_recoveries
        agent_run.recovered_amount = tot_recovered_amt

        db.commit()

        return {
            "run_id": run_id,
            "status": agent_run.status,
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "transactions_examined": len(txns),
            "cases_processed": cases_processed,
            "auto_eligible_count": auto_eligible,
            "human_approval_count": human_approval,
            "stopped_count": stopped,
            "successful_recoveries": succ_recoveries,
            "failed_recoveries": failed_recoveries,
            "recovered_amount": tot_recovered_amt
        }



orchestrator = AgentOrchestrator()
