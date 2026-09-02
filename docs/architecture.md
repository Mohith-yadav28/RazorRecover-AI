# RazorRecover AI — Technical Architecture Document

## Executive Overview
**RazorRecover AI** is an autonomous, explainable, and bounded AI revenue recovery system built for merchants using Razorpay. It shifts payment failure management from passive tracking to active, safe recovery interventions.

Tagline: *"Detect. Decide. Recover. Measure."*

---

## High-Level System Architecture

```
                                 [ Merchant Dashboard ]
                                (React 18 + Vite UI)
                                         |
                                         v  REST API / SSE
                              [ FastAPI Async Gateway ]
                                         |
                                         v
                         [ Agentic Workflow Orchestrator ]
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
[ Recovery Engine ]             [ Policy Safety Engine ]         [ Audit Trail Engine ]
 - Failure Diagnosis             - Hard Guardrail Checks          - Immutable Event Logging
 - ML Prob Scoring (Scikit)      - Human Escalation Rules         - Step Execution History
 - Context Retrieval             - Override Prevention            - ROI Measurement
         |                               |                               |
         +-------------------------------+-------------------------------+
                                         |
                                         v
                                [ Action Executor ]
                                         |
                        +----------------+----------------+
                        |                                 |
                        v                                 v
               [ Razorpay Service ]             [ Demo Simulator ]
               (Test Mode Links API)            (Deterministic Scenarios)
                        |                                 |
                        +----------------+----------------+
                                         |
                                         v
                              [ Relational Storage ]
                             (SQLAlchemy + SQLite/Postgres)
```

---

## Core System Modules

### 1. Agentic Loop Orchestrator
The workflow follows a 10-step deterministic cycle:
1. **OBSERVE**: Ingest failed payment or abandoned checkout record.
2. **INVESTIGATE**: Retrieve customer history, LTV, retry attempts, fraud indicators.
3. **SCORE**: Execute Scikit-Learn ML model to calculate `recovery_probability` (0.0 to 1.0).
4. **REASON**: Generate business-facing explanation ("Why?") from structured data.
5. **RECOMMEND**: Formulate optimal intervention strategy (`RETRY_PAYMENT`, `CREATE_PAYMENT_LINK`, `SEND_RECOVERY_REMINDER`, `ESCALATE_TO_HUMAN`, `STOP_RECOVERY`).
6. **POLICY CHECK**: Route recommendation through the Policy Engine for deterministic authorization.
7. **EXECUTE**: Invoke backend Action Executor (Razorpay Test Mode / Simulator).
8. **VERIFY**: Verify status change and payment receipt.
9. **RECORD**: Store event entry in immutable Audit Log.
10. **MEASURE**: Re-calculate revenue metrics (Recovered Revenue, ROI, Recovery Rate).

### 2. Deterministic Policy Engine (Bounded Autonomy Guardrails)
The LLM is strictly decoupled from action authorization. The Policy Engine executes hard python rules:
- **Rule 1 (Auto-Retry)**: `recovery_probability >= 75%` AND `retry_count < 2` AND `amount <= ₹5,000` AND NOT `is_suspicious` -> `ALLOWED`.
- **Rule 2 (High Value Escalation)**: `amount > ₹50,000` -> `HUMAN_APPROVAL_REQUIRED`.
- **Rule 3 (Low Probability Stop)**: `recovery_probability < 60%` -> `STOP_RECOVERY`.
- **Rule 4 (Retry Cap)**: `retry_count >= 2` -> `STOP_AUTOMATED_RETRIES`.
- **Rule 5 (Fraud & Suspicious)**: `is_suspicious == True` -> `ESCALATE_TO_HUMAN`.
- **Rule 6 (Contact Limit)**: `customer_contact_count >= 3` -> `STOP`.
- **Rule 7 (Prompt Injection Shield)**: External text or user prompt cannot alter rule definitions or override execution decisions.

### 3. ML Recovery Probability Engine
- Model: Scikit-learn Random Forest Classifier.
- Features: Transaction amount, customer lifetime value, historical success rate, failure reason category, retry count, time elapsed since failure, suspicion score.
- Output: Probability array `[p_failure, p_recovery]`, confidence score, risk category.

### 4. Controlled AI Tool Registry
The AI agent interacts exclusively through backend tools:
- `get_transaction(id)`
- `get_customer_history(customer_id)`
- `get_failure_details(txn_id)`
- `calculate_recovery_probability(txn_id)`
- `check_policy(recommendation, txn_context)`
- `retry_payment(txn_id)`
- `create_payment_link(txn_id)`
- `send_recovery_reminder(txn_id)`
- `escalate_to_human(txn_id, reason)`
- `stop_recovery(txn_id, reason)`
- `record_audit_event(event_dict)`

---

## Security & Reliability Design
1. **Zero Prompt Execution Vulnerability**: No direct database execution or unvalidated API triggers allowed from raw LLM output.
2. **API Credential Protection**: Environment variable configuration via `.env`, credentials never exposed to client side or git.
3. **Demo Mode Isolation**: Deterministic scenarios run completely offline with fallback abstractions if live APIs or keys are unavailable.
