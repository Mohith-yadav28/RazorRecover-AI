from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain import Transaction, Customer, RecoveryCase, AuditEvent, generate_uuid, utc_now
from app.services.razorpay.service import razorpay_service

DEMO_SCENARIOS = [
    {
        "id": "scenario_1",
        "title": "Scenario 1: Bank Timeout Recovery (Auto-Retry Success)",
        "description": "Temporary bank timeout on ₹4,999 transaction. High recovery probability (91%). Policy allows automatic retry. Recovered successfully.",
        "amount": 4999.0,
        "customer": {"name": "Aarav Sharma", "email": "aarav.sharma@example.com", "ltv": 85000.0, "vip": True},
        "failure_reason": "BANK_TIMEOUT",
        "failure_category": "TEMPORARY_GATEWAY",
        "payment_method": "CARD",
        "retry_count": 0,
        "is_suspicious": False,
        "probability": 0.91,
        "priority_tier": "HIGH",
        "recommended_action": "RETRY_PAYMENT",
        "policy_result": "ALLOWED",
        "policy_reason": "All bounded safety rules satisfied.",
        "final_action": "RETRY_PAYMENT",
        "status": "OPEN",
        "recovered_amount": 0.0
    },

    {
        "id": "scenario_2",
        "title": "Scenario 2: Abandoned Checkout (Razorpay Payment Link)",
        "description": "Abandoned checkout cart of ₹8,999. High recovery probability (84%). Policy authorizes instant Razorpay Payment Link generation.",
        "amount": 8999.0,
        "customer": {"name": "Priya Patel", "email": "priya.patel@example.com", "ltv": 32000.0, "vip": False},
        "failure_reason": "CART_ABANDONED",
        "failure_category": "CHECKOUT_ABANDONMENT",
        "payment_method": "UPI",
        "retry_count": 0,
        "is_suspicious": False,
        "probability": 0.84,
        "priority_tier": "HIGH",
        "recommended_action": "CREATE_PAYMENT_LINK",
        "policy_result": "ALLOWED",
        "policy_reason": "All bounded safety rules satisfied.",
        "final_action": "CREATE_PAYMENT_LINK",
        "status": "OPEN",
        "recovered_amount": 0.0
    },

    {
        "id": "scenario_3",
        "title": "Scenario 3: High-Value Transaction (Human Approval Required)",
        "description": "High-value enterprise order of ₹85,000. Moderate recovery probability (68%). Exceeds automatic recovery threshold (₹50,000). Requires human merchant authorization.",
        "amount": 85000.0,
        "customer": {"name": "Siddharth Malhotra", "email": "siddharth.m@example.com", "ltv": 150000.0, "vip": True},
        "failure_reason": "GATEWAY_DOWN",
        "failure_category": "TEMPORARY_GATEWAY",
        "payment_method": "NETBANKING",
        "retry_count": 0,
        "is_suspicious": False,
        "probability": 0.68,
        "priority_tier": "HIGH",
        "recommended_action": "RETRY_PAYMENT",
        "policy_result": "HUMAN_APPROVAL_REQUIRED",
        "policy_reason": "Transaction amount (₹85,000.00) exceeds automatic recovery threshold (₹50,000.00). Human authorization required.",
        "final_action": "HUMAN_APPROVAL_REQUIRED",
        "status": "ESCALATED",
        "recovered_amount": 0.0
    },
    {
        "id": "scenario_4",
        "title": "Scenario 4: Repeated Failed Retries (Stop Recovery Rule)",
        "description": "Repeated failed payments on ₹3,499. Low recovery probability (42%). Maximum automated retries (2/2) reached. Automated recovery halted.",
        "amount": 3499.0,
        "customer": {"name": "Karan Gupta", "email": "karan.gupta@example.com", "ltv": 12000.0, "vip": False},
        "failure_reason": "INSUFFICIENT_FUNDS",
        "failure_category": "PERMANENT_CUSTOMER",
        "payment_method": "CARD",
        "retry_count": 2,
        "is_suspicious": False,
        "probability": 0.42,
        "priority_tier": "LOW",
        "recommended_action": "STOP_RECOVERY",
        "policy_result": "BLOCKED",
        "policy_reason": "Maximum automated payment retry limit reached (2/2).",
        "final_action": "STOP_RECOVERY",
        "status": "STOPPED",
        "recovered_amount": 0.0
    },
    {
        "id": "scenario_5",
        "title": "Scenario 5: Suspicious Fraud Transaction (Immediate Escalation)",
        "description": "Suspicious transaction of ₹20,000 with elevated fraud score (0.85). Automated recovery blocked immediately to protect merchant security.",
        "amount": 20000.0,
        "customer": {"name": "Dev Verma", "email": "dev.verma@example.com", "ltv": 5000.0, "vip": False},
        "failure_reason": "AUTH_FAILURE",
        "failure_category": "TEMPORARY_GATEWAY",
        "payment_method": "CARD",
        "retry_count": 0,
        "is_suspicious": True,
        "probability": 0.35,
        "priority_tier": "HIGH",
        "recommended_action": "ESCALATE_TO_HUMAN",
        "policy_result": "BLOCKED",
        "policy_reason": "Suspicious activity detected. Automated action blocked.",
        "final_action": "ESCALATE_TO_HUMAN",
        "status": "ESCALATED",
        "recovered_amount": 0.0
    }
]

def load_demo_scenario(scenario_id: str, db: Session) -> Dict[str, Any]:
    sc = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not sc:
        return {"error": f"Scenario {scenario_id} not found"}

    now = utc_now()
    
    # 1. Create or fetch demo customer
    cust_email = sc["customer"]["email"]
    cust = db.query(Customer).filter(Customer.email == cust_email).first()
    if not cust:
        cust = Customer(
            id=f"CUST_DEMO_{scenario_id.upper()}",
            name=sc["customer"]["name"],
            email=cust_email,
            lifetime_value=sc["customer"]["ltv"],
            is_vip=sc["customer"]["vip"],
            created_at=now
        )
        db.add(cust)
        db.commit()

    # 2. Create demo transaction
    txn_id = f"TXN_DEMO_{scenario_id.upper()}"
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if txn:
        db.query(RecoveryCase).filter(RecoveryCase.transaction_id == txn_id).delete()
        db.query(AuditEvent).filter(AuditEvent.transaction_id == txn_id).delete()
        db.query(Transaction).filter(Transaction.id == txn_id).delete()
        db.commit()

    txn = Transaction(
        id=txn_id,
        customer_id=cust.id,
        amount=sc["amount"],
        currency="INR",
        status="RECOVERED" if sc["status"] == "RECOVERED" else "FAILED",
        failure_reason=sc["failure_reason"],
        failure_category=sc["failure_category"],
        payment_method=sc["payment_method"],
        retry_count=sc["retry_count"],
        is_suspicious=sc["is_suspicious"],
        recovered=(sc["status"] == "RECOVERED"),
        recovered_amount=sc["recovered_amount"],
        created_at=now
    )
    db.add(txn)

    # 3. Generate Payment Link if applicable
    payment_link_info = None
    if sc["final_action"] == "CREATE_PAYMENT_LINK":
        payment_link_info = razorpay_service.create_payment_link(
            amount=sc["amount"],
            customer_name=cust.name,
            customer_email=cust.email,
            description=f"RazorRecover AI Payment Link for {txn_id}",
            reference_id=txn_id
        )

    # 4. Create Recovery Case
    case = RecoveryCase(
        id=f"CASE_DEMO_{scenario_id.upper()}",
        transaction_id=txn_id,
        recovery_probability=sc["probability"],
        priority_score=round(sc["probability"] * (sc["amount"]/1000.0), 2),
        priority_tier=sc["priority_tier"],
        recommended_action=sc["recommended_action"],
        policy_result=sc["policy_result"],
        policy_reason=sc["policy_reason"],
        final_action=sc["final_action"],
        status=sc["status"],
        recovered_amount=sc["recovered_amount"],
        ai_explanation={
            "summary": f"{sc['title']} executed in Demo Simulator.",
            "why": [
                f"Failure reason: {sc['failure_reason']}",
                f"Customer LTV: ₹{cust.lifetime_value:,.2f}",
                f"Recovery probability: {sc['probability']*100:.0f}%",
                f"Policy evaluation result: {sc['policy_result']}"
            ],
            "evidence": {"payment_link": payment_link_info}
        },
        created_at=now
    )
    db.add(case)

    # 5. Populate Audit Log Timeline Steps
    steps = [
        ("OBSERVE", "TRANSACTION_DETECTED", f"Observed failed transaction {txn_id} (₹{sc['amount']:,.2f})"),
        ("INVESTIGATE", "CUSTOMER_RETRIEVED", f"Retrieved profile for {cust.name} (LTV ₹{cust.lifetime_value:,.2f})"),
        ("SCORE", "PROBABILITY_CALCULATED", f"Calculated Recovery Probability: {sc['probability']*100:.0f}%"),
        ("RECOMMEND", "STRATEGY_FORMULATED", f"Recommended Action: {sc['recommended_action']}"),
        ("POLICY_CHECK", "POLICY_EVALUATED", f"Policy Result: {sc['policy_result']} ({sc['policy_reason']})"),
        ("EXECUTE", "ACTION_EXECUTED", f"Final Action Executed: {sc['final_action']}"),
        ("VERIFY", "VERIFICATION_COMPLETE", f"Recovery Status: {sc['status']}"),
        ("MEASURE", "ROI_RECORDED", f"Revenue Recovered: ₹{sc['recovered_amount']:,.2f}")
    ]

    for step, evt, desc in steps:
        audit = AuditEvent(
            id=generate_uuid(),
            transaction_id=txn_id,
            case_id=case.id,
            agent_step=step,
            event_type=evt,
            decision=desc,
            reason=sc["policy_reason"],
            policy_name="POLICY_ENGINE_GUARDRAILS",
            result=sc["final_action"],
            recovered_amount=sc["recovered_amount"],
            timestamp=now
        )
        db.add(audit)

    db.commit()

    return {
        "scenario": sc,
        "transaction_id": txn_id,
        "case_id": case.id,
        "payment_link": payment_link_info
    }
