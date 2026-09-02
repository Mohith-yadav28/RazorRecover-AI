import os
import sys
import random
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend")
)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import SessionLocal, engine, Base
from app.models.domain import (
    Customer,
    Transaction,
    RecoveryCase,
    PolicyRule,
    AuditEvent,
    generate_uuid,
)


# ---------------------------------------------------------
# Failure Categories and Correlated Reasons
# ---------------------------------------------------------

FAILURE_TYPES = [
    ("BANK_TIMEOUT", "TEMPORARY_GATEWAY", "CARD", 0.88),
    ("GATEWAY_DOWN", "TEMPORARY_GATEWAY", "UPI", 0.92),
    ("AUTH_FAILURE", "TEMPORARY_GATEWAY", "UPI", 0.82),
    ("INSUFFICIENT_FUNDS", "PERMANENT_CUSTOMER", "UPI", 0.45),
    ("CARD_EXPIRED", "PERMANENT_CUSTOMER", "CARD", 0.60),
    ("CART_ABANDONED", "CHECKOUT_ABANDONMENT", "UPI", 0.75),
    ("EXIT_INTENT", "CHECKOUT_ABANDONMENT", "CARD", 0.70),
    ("SUB_EXPIRED", "SUBSCRIPTION", "CARD", 0.65),
    ("MANDATE_FAILED", "SUBSCRIPTION", "NETBANKING", 0.58),
    ("INVOICE_OVERDUE", "OVERDUE_RECEIVABLE", "NETBANKING", 0.50),
]


FIRST_NAMES = [
    "Aarav",
    "Ananya",
    "Rohan",
    "Priya",
    "Vikram",
    "Neha",
    "Rahul",
    "Sneha",
    "Aditya",
    "Pooja",
    "Kabir",
    "Meera",
    "Siddharth",
    "Kavya",
    "Arjun",
    "Riya",
    "Dev",
    "Isha",
    "Karan",
    "Tanvi",
]


LAST_NAMES = [
    "Sharma",
    "Verma",
    "Patel",
    "Mehta",
    "Gupta",
    "Rao",
    "Nair",
    "Joshi",
    "Singhania",
    "Reddy",
    "Deshmukh",
    "Chopra",
    "Malhotra",
    "Kulkarni",
    "Bhatia",
]


def generate_synthetic_dataset(
    num_customers=1000,
    num_transactions=5000
):
    # Fixed seed makes the synthetic benchmark repeatable.
    random.seed(42)

    print(
        f"[INFO] Generating synthetic merchant dataset: "
        f"{num_customers} customers, "
        f"{num_transactions} transactions..."
    )

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Clear existing tables
        # ---------------------------------------------------------

        db.query(AuditEvent).delete()
        db.query(RecoveryCase).delete()
        db.query(Transaction).delete()
        db.query(Customer).delete()
        db.query(PolicyRule).delete()

        db.commit()

        # ---------------------------------------------------------
        # 1. Generate Customers
        # ---------------------------------------------------------

        customers = []

        now = datetime.now(timezone.utc)

        for i in range(num_customers):

            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)

            email = (
                f"{first.lower()}."
                f"{last.lower()}"
                f"{random.randint(10, 999)}"
                "@example.com"
            )

            # VIP customer distribution (~15%)
            is_vip = random.random() < 0.15

            if is_vip:
                ltv = round(
                    random.uniform(50000, 250000),
                    2
                )

                total_txns = random.randint(10, 50)

                succ_txns = int(
                    total_txns
                    * random.uniform(0.85, 0.98)
                )

            else:
                ltv = round(
                    random.uniform(1000, 40000),
                    2
                )

                total_txns = random.randint(1, 15)

                succ_txns = int(
                    total_txns
                    * random.uniform(0.50, 0.85)
                )

            failed_txns = total_txns - succ_txns

            fraud_score = (
                round(random.uniform(0.8, 0.95), 2)
                if random.random() < 0.03
                else round(random.uniform(0.01, 0.25), 2)
            )

            cust = Customer(
                id=f"CUST_{i + 10001}",
                name=f"{first} {last}",
                email=email,
                lifetime_value=ltv,
                total_transactions=total_txns,
                successful_transactions=succ_txns,
                failed_transactions=failed_txns,
                last_transaction_date=(
                    now
                    - timedelta(
                        days=random.randint(0, 30)
                    )
                ),
                is_vip=is_vip,
                fraud_score=fraud_score,
                created_at=(
                    now
                    - timedelta(
                        days=random.randint(30, 365)
                    )
                ),
            )

            customers.append(cust)
            db.add(cust)

        db.commit()

        print(
            f"[SUCCESS] Created "
            f"{len(customers)} synthetic customer profiles."
        )

        # ---------------------------------------------------------
        # 2. Generate Transactions & Recovery Cases
        # ---------------------------------------------------------

        transactions = []
        cases = []

        for i in range(num_transactions):

            cust = random.choice(customers)

            reason, category, method, base_prob = random.choice(
                FAILURE_TYPES
            )

            # -----------------------------------------------------
            # Amount distribution
            # Some transactions are high-value (> ₹50,000)
            # for human approval demonstration.
            # -----------------------------------------------------

            is_high_value = random.random() < 0.04

            if is_high_value:
                amount = round(
                    random.uniform(51000, 150000),
                    2
                )
            else:
                amount = round(
                    random.choice(
                        [
                            499,
                            999,
                            1499,
                            2499,
                            4999,
                            8999,
                            12999,
                            24999,
                        ]
                    ),
                    2
                )

            retry_cnt = random.choice(
                [0, 0, 0, 1, 1, 2, 3]
            )

            is_suspicious = (
                cust.fraud_score > 0.70
                or random.random() < 0.02
            )

            # -----------------------------------------------------
            # Context-aware recovery probability
            # -----------------------------------------------------

            prob = base_prob

            if cust.is_vip:
                prob += 0.08

            if retry_cnt >= 2:
                prob -= 0.25

            if is_suspicious:
                prob -= 0.40

            if amount > 50000:
                prob -= 0.10

            prob = max(
                0.05,
                min(
                    0.98,
                    round(prob, 2)
                )
            )

            # -----------------------------------------------------
            # Priority Score
            # -----------------------------------------------------

            priority_score = round(
                prob * (amount / 1000.0),
                2
            )

            if (
                (prob >= 0.75 and amount >= 4000)
                or amount > 50000
            ):
                priority_tier = "HIGH"

            elif prob >= 0.50:
                priority_tier = "MEDIUM"

            else:
                priority_tier = "LOW"

            # -----------------------------------------------------
            # Determine Recommended Action
            # -----------------------------------------------------

            if is_suspicious:

                rec_action = "ESCALATE_TO_HUMAN"

            elif retry_cnt >= 2 or prob < 0.60:

                rec_action = "STOP_RECOVERY"

            elif amount > 50000:

                rec_action = "ESCALATE_TO_HUMAN"

            elif (
                category == "TEMPORARY_GATEWAY"
                and retry_cnt < 2
            ):

                rec_action = "RETRY_PAYMENT"

            elif category == "CHECKOUT_ABANDONMENT":

                rec_action = "CREATE_PAYMENT_LINK"

            else:

                rec_action = "SEND_RECOVERY_REMINDER"

            # -----------------------------------------------------
            # Determine Policy Authorization
            # -----------------------------------------------------

            if amount > 50000:

                policy_res = "HUMAN_APPROVAL_REQUIRED"

                policy_reason = (
                    "Transaction amount exceeds "
                    "automatic threshold (₹50,000)."
                )

                final_action = "HUMAN_APPROVAL_REQUIRED"

            elif is_suspicious:

                policy_res = "BLOCKED"

                policy_reason = (
                    f"High fraud risk score detected "
                    f"({cust.fraud_score}). "
                    "Automated action blocked."
                )

                final_action = "ESCALATE_TO_HUMAN"

            elif prob < 0.60:

                policy_res = "BLOCKED"

                policy_reason = (
                    f"Recovery probability "
                    f"({prob * 100:.0f}%) is below "
                    "policy minimum (60%)."
                )

                final_action = "STOP_RECOVERY"

            elif retry_cnt >= 2:

                policy_res = "BLOCKED"

                policy_reason = (
                    f"Maximum automated retry limit "
                    f"reached ({retry_cnt})."
                )

                final_action = "STOP_RECOVERY"

            else:

                policy_res = "ALLOWED"

                policy_reason = (
                    "All bounded safety rules satisfied."
                )

                final_action = rec_action

            # -----------------------------------------------------
            # Simulated Recovery Outcome
            #
            # This is a synthetic benchmark.
            # It does NOT represent real payment recovery.
            # -----------------------------------------------------

            recovered = False
            rec_amt = 0.0
            case_status = "OPEN"

            if policy_res == "ALLOWED":

                if random.random() < prob:

                    recovered = True
                    rec_amt = amount
                    case_status = "RECOVERED"

                else:

                    case_status = "FAILED"

            elif policy_res == "HUMAN_APPROVAL_REQUIRED":

                case_status = "ESCALATED"

            elif final_action == "STOP_RECOVERY":

                case_status = "STOPPED"

            elif final_action == "ESCALATE_TO_HUMAN":

                case_status = "ESCALATED"

            # -----------------------------------------------------
            # Transaction timestamp
            # -----------------------------------------------------

            txn_time = (
                now
                - timedelta(
                    hours=random.randint(1, 720)
                )
            )

            # -----------------------------------------------------
            # Create Transaction
            # -----------------------------------------------------

            txn = Transaction(
                id=f"TXN_{i + 10001}",
                customer_id=cust.id,
                amount=amount,
                currency="INR",
                status=(
                    "RECOVERED"
                    if recovered
                    else (
                        "ABANDONED"
                        if category == "CHECKOUT_ABANDONMENT"
                        else "FAILED"
                    )
                ),
                failure_reason=reason,
                failure_category=category,
                payment_method=method,
                gateway="Razorpay",
                retry_count=retry_cnt,
                is_suspicious=is_suspicious,
                recovered=recovered,
                recovered_amount=rec_amt,
                created_at=txn_time,
                recovered_at=(
                    txn_time
                    + timedelta(
                        minutes=random.randint(2, 45)
                    )
                    if recovered
                    else None
                ),
            )

            transactions.append(txn)
            db.add(txn)

            # -----------------------------------------------------
            # Case Explanation
            # -----------------------------------------------------

            ai_exp = {
                "summary": (
                    f"{reason.replace('_', ' ').title()} "
                    f"failure detected for {cust.name}."
                ),

                "why": [
                    (
                        f"Failure reason: "
                        f"{reason.replace('_', ' ')}"
                    ),
                    (
                        f"Customer LTV: "
                        f"₹{cust.lifetime_value:,.2f} "
                        f"({cust.successful_transactions} "
                        "previous successful payments)"
                    ),
                    (
                        f"Calculated recovery probability: "
                        f"{prob * 100:.0f}%"
                    ),
                    (
                        f"Retry count: "
                        f"{retry_cnt}/2 allowed attempts"
                    ),
                    (
                        "Suspicion score: "
                        f"{'Suspicious' if is_suspicious else 'Clean'}"
                    ),
                ],

                "evidence": {
                    "ltv": cust.lifetime_value,
                    "previous_successes": (
                        cust.successful_transactions
                    ),
                    "retry_count": retry_cnt,
                    "fraud_score": cust.fraud_score,
                },
            }

            # -----------------------------------------------------
            # Create Recovery Case
            # -----------------------------------------------------

            case = RecoveryCase(
                id=f"CASE_{i + 10001}",
                transaction_id=txn.id,
                recovery_probability=prob,
                priority_score=priority_score,
                priority_tier=priority_tier,
                recommended_action=rec_action,
                policy_result=policy_res,
                policy_reason=policy_reason,
                final_action=final_action,
                status=case_status,
                recovered_amount=rec_amt,
                ai_explanation=ai_exp,
                created_at=txn_time,
                updated_at=txn_time + timedelta(minutes=5),
            )

            cases.append(case)
            db.add(case)

        # ---------------------------------------------------------
        # 3. Add Core Default Policy Rules
        # ---------------------------------------------------------

        default_rules = [
            PolicyRule(
                id=generate_uuid(),
                rule_code="RULE_AUTO_RETRY",
                rule_name="Automated Retry Limit",
                description=(
                    "Auto-retry allowed if probability >= 75%, "
                    "retries < 2, amount <= ₹5,000, "
                    "and not suspicious."
                ),
                is_active=True,
                parameters_json={
                    "max_amount": 5000,
                    "min_prob": 0.75,
                    "max_retries": 2,
                },
            ),

            PolicyRule(
                id=generate_uuid(),
                rule_code="RULE_HUMAN_APPROVAL",
                rule_name="High-Value Escalation",
                description=(
                    "Transactions exceeding ₹50,000 "
                    "require explicit merchant human approval."
                ),
                is_active=True,
                parameters_json={
                    "threshold_amount": 50000
                },
            ),

            PolicyRule(
                id=generate_uuid(),
                rule_code="RULE_MIN_PROBABILITY",
                rule_name="Minimum Probability Threshold",
                description=(
                    "Automated recovery halted if "
                    "recovery probability is below 60%."
                ),
                is_active=True,
                parameters_json={
                    "min_prob": 0.60
                },
            ),

            PolicyRule(
                id=generate_uuid(),
                rule_code="RULE_MAX_RETRIES",
                rule_name="Maximum Automated Retries",
                description=(
                    "Halt automated payment retries "
                    "after 2 failed attempts."
                ),
                is_active=True,
                parameters_json={
                    "max_retries": 2
                },
            ),

            PolicyRule(
                id=generate_uuid(),
                rule_code="RULE_FRAUD_ESCALATION",
                rule_name="Suspicious Transaction Guard",
                description=(
                    "Always escalate suspicious or "
                    "high fraud score transactions "
                    "to human review."
                ),
                is_active=True,
                parameters_json={
                    "always_escalate": True
                },
            ),
        ]

        for rule in default_rules:
            db.add(rule)

        db.commit()

        # ---------------------------------------------------------
        # 4. Output Summary
        # ---------------------------------------------------------

        total_value = sum(
            float(t.amount)
            for t in transactions
        )

        recovered_value = sum(
            float(t.recovered_amount or 0.0)
            for t in transactions
        )

        recovered_count = sum(
            1
            for t in transactions
            if t.recovered
        )

        print()
        print("=" * 58)
        print("SYNTHETIC DATASET SEED SUCCESSFUL")
        print("=" * 58)

        print(
            f"Total Customers:          "
            f"{len(customers):,}"
        )

        print(
            f"Total Transactions:       "
            f"{len(transactions):,}"
        )

        print(
            f"Total Revenue at Risk:    "
            f"INR {total_value:,.2f}"
        )

        print(
            f"Recovered Revenue:        "
            f"INR {recovered_value:,.2f}"
        )

        print(
            f"Recovered Count:          "
            f"{recovered_count:,} / "
            f"{len(transactions):,} "
            f"({recovered_count / len(transactions) * 100:.1f}%)"
        )

        print(
            f"Policy Default Rules:     "
            f"{len(default_rules)}"
        )

        print("=" * 58)
        print()

    except Exception as e:

        db.rollback()

        print(
            f"[ERROR] Error seeding database: {e}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":
    generate_synthetic_dataset(
        num_customers=1000,
        num_transactions=5000
    )