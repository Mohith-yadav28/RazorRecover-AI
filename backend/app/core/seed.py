from sqlalchemy.orm import Session
from app.models.domain import Customer, Transaction, RecoveryCase, PolicyRule, utc_now
from datetime import timedelta
import random

def seed_database_if_empty(db: Session):
    tx_count = db.query(Transaction).count()
    if tx_count > 0:
        return

    now = utc_now()

    # 1. Seed Policy Rules
    default_rules = [
        {
            "id": "RULE_AUTO_RETRY",
            "rule_code": "MAX_RETRY_LIMIT",
            "rule_name": "Automated Retry Cap",
            "description": "Auto-retry allowed if probability >= 75%, retries < 2, amount <= ₹5,000, and not suspicious.",
            "parameters_json": {"max_amount": 5000, "min_prob": 0.75, "max_retries": 2}
        },
        {
            "id": "RULE_HUMAN_APPROVAL",
            "rule_code": "HIGH_VALUE_THRESHOLD",
            "rule_name": "High-Value Escalation",
            "description": "Transactions exceeding ₹50,000 require explicit merchant human approval.",
            "parameters_json": {"threshold_amount": 50000}
        },
        {
            "id": "RULE_MIN_PROBABILITY",
            "rule_code": "MIN_RECOVERY_PROBABILITY",
            "rule_name": "Minimum Probability Threshold",
            "description": "Automated recovery halted if recovery probability is below 60%.",
            "parameters_json": {"min_prob": 0.60}
        },
        {
            "id": "RULE_MAX_RETRIES",
            "rule_code": "MAX_ATTEMPTS",
            "rule_name": "Maximum Automated Retries",
            "description": "Halt automated payment retries after 2 failed attempts.",
            "parameters_json": {"max_retries": 2}
        }
    ]

    for r in default_rules:
        if not db.query(PolicyRule).filter(PolicyRule.id == r["id"]).first():
            rule = PolicyRule(
                id=r["id"],
                rule_code=r["rule_code"],
                rule_name=r["rule_name"],
                description=r["description"],
                is_active=True,
                parameters_json=r["parameters_json"],
                created_at=now
            )
            db.add(rule)

    # 2. Seed Base Customers and Transactions
    failure_types = [
        ("BANK_TIMEOUT", "TEMPORARY_GATEWAY", "CARD", 0.88),
        ("GATEWAY_DOWN", "TEMPORARY_GATEWAY", "UPI", 0.92),
        ("AUTH_FAILURE", "TEMPORARY_GATEWAY", "UPI", 0.82),
        ("INSUFFICIENT_FUNDS", "PERMANENT_CUSTOMER", "UPI", 0.45),
        ("CART_ABANDONED", "CHECKOUT_ABANDONMENT", "UPI", 0.75),
        ("SUB_EXPIRED", "SUBSCRIPTION", "CARD", 0.65)
    ]

    names = ["Aarav Sharma", "Ananya Patel", "Rohan Gupta", "Priya Verma", "Vikram Singh", "Neha Kapoor"]

    for i in range(1, 51):
        c_name = names[i % len(names)]
        c_email = f"user_{i}@example.com"
        cust = Customer(
            id=f"CUST_SEED_{i:04d}",
            name=c_name,
            email=c_email,
            lifetime_value=float(random.randint(15000, 120000)),
            total_transactions=random.randint(5, 30),
            successful_transactions=random.randint(3, 25),
            failed_transactions=random.randint(1, 5),
            is_vip=(i % 5 == 0),
            fraud_score=round(random.uniform(0.01, 0.15), 2),
            created_at=now
        )
        db.add(cust)
        db.flush()

        reason, cat, method, base_prob = failure_types[i % len(failure_types)]
        amt = float(random.choice([2999, 4999, 8999, 12500, 24999, 48000, 85000]))
        is_recovered = (i % 3 == 0)
        rec_amt = amt if is_recovered else 0.0
        status = "RECOVERED" if is_recovered else ("ABANDONED" if cat == "CHECKOUT_ABANDONMENT" else "FAILED")

        txn = Transaction(
            id=f"TXN_SEED_{i:04d}",
            customer_id=cust.id,
            amount=amt,
            currency="INR",
            status=status,
            failure_reason=reason,
            failure_category=cat,
            payment_method=method,
            retry_count=0 if not is_recovered else 1,
            is_suspicious=False,
            recovered=is_recovered,
            recovered_amount=rec_amt,
            created_at=now - timedelta(hours=i)
        )
        db.add(txn)
        db.flush()

        pol_res = "ALLOWED" if amt <= 50000 else "HUMAN_APPROVAL_REQUIRED"
        c_status = "RECOVERED" if is_recovered else ("ESCALATED" if pol_res == "HUMAN_APPROVAL_REQUIRED" else "OPEN")

        case = RecoveryCase(
            id=f"CASE_SEED_{i:04d}",
            transaction_id=txn.id,
            recovery_probability=base_prob,
            priority_score=round(base_prob * (amt / 1000.0), 2),
            priority_tier="HIGH" if amt > 10000 else "MEDIUM",
            recommended_action="CREATE_PAYMENT_LINK" if cat == "CHECKOUT_ABANDONMENT" else "RETRY_PAYMENT",
            policy_result=pol_res,
            policy_reason="Bounded policy check passed.",
            final_action="RETRY_PAYMENT" if pol_res == "ALLOWED" else "HUMAN_APPROVAL_REQUIRED",
            status=c_status,
            recovered_amount=rec_amt,
            created_at=now - timedelta(hours=i)
        )
        db.add(case)

    db.commit()
