import os
import sys
import json
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend")
)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import SessionLocal
from app.models.domain import Transaction, RecoveryCase


def run_repeatable_evaluation():
    print("[INFO] Running RazorRecover AI Experimental Benchmark Evaluation...")

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Load transactions
        # ---------------------------------------------------------
        txns = db.query(Transaction).all()

        if not txns:
            print(
                "[ERROR] Database contains no transaction records. "
                "Please run generate_synthetic_data.py first."
            )
            return

        total_txns = len(txns)
        total_value = sum(float(t.amount) for t in txns)

        # ---------------------------------------------------------
        # 2. Load RazorRecover recovery cases
        # ---------------------------------------------------------
        cases = db.query(RecoveryCase).all()

        agent_recovered_val = sum(
            float(c.recovered_amount or 0.0)
            for c in cases
            if c.status == "RECOVERED"
        )

        agent_recovered_cnt = sum(
            1
            for c in cases
            if c.status == "RECOVERED"
        )

        agent_escalated_cnt = sum(
            1
            for c in cases
            if c.policy_result == "HUMAN_APPROVAL_REQUIRED"
            or c.final_action == "ESCALATE_TO_HUMAN"
        )

        agent_stopped_cnt = sum(
            1
            for c in cases
            if c.status == "STOPPED"
            or c.final_action == "STOP_RECOVERY"
        )

        agent_recovery_rate = (
            agent_recovered_val / total_value * 100.0
            if total_value > 0
            else 0.0
        )

        # ---------------------------------------------------------
        # 3. Naive baseline
        #
        # Baseline blindly attempts two retries for every
        # transaction without using ML or safety policies.
        # ---------------------------------------------------------
        baseline_recovered_cnt = 0
        baseline_recovered_val = 0.0
        baseline_unnecessary_retries = 0

        for txn in txns:

            # Simple baseline assumption:
            # temporary gateway failures on smaller,
            # non-suspicious transactions are recoverable.
            if (
                txn.failure_category == "TEMPORARY_GATEWAY"
                and not txn.is_suspicious
                and float(txn.amount) <= 10000
            ):
                baseline_recovered_cnt += 1
                baseline_recovered_val += float(txn.amount)

            else:
                # Two unnecessary retry attempts
                # on transactions that should not be blindly retried.
                baseline_unnecessary_retries += 2

        baseline_recovery_rate = (
            baseline_recovered_val / total_value * 100.0
            if total_value > 0
            else 0.0
        )

        # ---------------------------------------------------------
        # 4. Calculate retry reduction
        # ---------------------------------------------------------
        agent_retry_attempts = max(
            0,
            total_txns - agent_recovered_cnt
        )

        if baseline_unnecessary_retries > 0:
            retry_reduction_pct = (
                (
                    baseline_unnecessary_retries
                    - agent_retry_attempts
                )
                / baseline_unnecessary_retries
                * 100.0
            )
        else:
            retry_reduction_pct = 0.0

        retry_reduction_pct = max(
            0.0,
            min(100.0, retry_reduction_pct)
        )

        # ---------------------------------------------------------
        # 5. Calculate improvement
        # ---------------------------------------------------------
        additional_revenue_recovered = (
            agent_recovered_val
            - baseline_recovered_val
        )

        recovery_yield_uplift = (
            agent_recovery_rate
            - baseline_recovery_rate
        )

        # ---------------------------------------------------------
        # 6. Build evaluation report
        # ---------------------------------------------------------
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),

            "evaluation_type": "experimental_synthetic_benchmark",

            "transactions_evaluated": total_txns,

            "total_revenue_at_risk_inr": round(
                total_value,
                2
            ),

            "razorrecover_ai": {
                "recovered_revenue_inr": round(
                    agent_recovered_val,
                    2
                ),

                "recovered_count": agent_recovered_cnt,

                "recovery_rate_pct": round(
                    agent_recovery_rate,
                    2
                ),

                "human_escalation_count": agent_escalated_cnt,

                "stopped_cases_count": agent_stopped_cnt,

                "safety_guardrails_active": True
            },

            "naive_baseline_retry": {
                "recovered_revenue_inr": round(
                    baseline_recovered_val,
                    2
                ),

                "recovered_count": baseline_recovered_cnt,

                "recovery_rate_pct": round(
                    baseline_recovery_rate,
                    2
                ),

                "wasted_unnecessary_retries": (
                    baseline_unnecessary_retries
                ),

                "safety_guardrails_active": False
            },

            "improvements": {
                "additional_revenue_recovered_inr": round(
                    additional_revenue_recovered,
                    2
                ),

                "recovery_yield_uplift_pct": round(
                    recovery_yield_uplift,
                    2
                ),

                "unnecessary_retry_reduction_pct": round(
                    retry_reduction_pct,
                    1
                )
            }
        }

        # ---------------------------------------------------------
        # 7. Save JSON evaluation artifact
        # ---------------------------------------------------------
        project_root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                ".."
            )
        )

        data_dir = os.path.join(
            project_root,
            "data"
        )

        os.makedirs(
            data_dir,
            exist_ok=True
        )

        report_path = os.path.join(
            data_dir,
            "evaluation_report.json"
        )

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                report,
                f,
                indent=2
            )

        # ---------------------------------------------------------
        # 8. Print benchmark summary
        # ---------------------------------------------------------
        print()
        print("=" * 60)
        print("EXPERIMENTAL EVALUATION BENCHMARK SUMMARY")
        print("=" * 60)

        print(
            f"Transactions Evaluated:      "
            f"{total_txns:,}"
        )

        print(
            f"Total Revenue at Risk:       "
            f"INR {total_value:,.2f}"
        )

        print(
            f"RazorRecover AI Recovered:   "
            f"INR {agent_recovered_val:,.2f} "
            f"({agent_recovery_rate:.2f}%)"
        )

        print(
            f"Naive Baseline Recovered:    "
            f"INR {baseline_recovered_val:,.2f} "
            f"({baseline_recovery_rate:.2f}%)"
        )

        print(
            f"Additional Revenue:          "
            f"INR {additional_revenue_recovered:,.2f}"
        )

        print(
            f"Recovery Yield Uplift:       "
            f"+{recovery_yield_uplift:.2f}%"
        )

        print(
            f"Human Escalations Triggered: "
            f"{agent_escalated_cnt}"
        )

        print(
            f"Recovery Stops Triggered:    "
            f"{agent_stopped_cnt}"
        )

        print(
            f"Unnecessary Retry Reduction: "
            f"{retry_reduction_pct:.1f}%"
        )

        print(
            f"Report saved to:             "
            f"{report_path}"
        )

        print("=" * 60)
        print()

    finally:
        db.close()


if __name__ == "__main__":
    run_repeatable_evaluation()