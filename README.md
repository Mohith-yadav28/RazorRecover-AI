# RazorRecover AI — Autonomous Revenue Recovery Platform

> **Detect lost revenue. Understand why payments fail. Recover safely. Prove the outcome.**

RazorRecover AI is an **internship-oriented agentic AI prototype developed for the Razorpay AI Builder Internship 2026 / AI Buildathon — Track 3: AI Revenue Recovery**.

The project explores how **Artificial Intelligence, Machine Learning, deterministic policy enforcement, and payment APIs** can be combined to build an automated revenue-recovery workflow.

The system identifies failed or at-risk transactions, analyzes transaction and customer signals, predicts recovery probability, recommends an appropriate recovery action, validates that action against predefined safety policies, executes permitted recovery workflows using **Razorpay Test Mode**, and records the resulting decision and outcome.

> **Project Context:** This repository represents an internship/buildathon-oriented technical prototype rather than a college academic project. The current evaluation uses synthetic transaction data and Test Mode payment workflows.

---

## 🎯 The Problem

Payment failures do not always mean lost customers.

Merchants can lose potential revenue because of:

* Temporary bank or gateway failures
* Network timeouts
* Abandoned checkout sessions
* Failed recurring subscription payments
* Overdue invoices
* Customers who require another payment attempt
* Uncoordinated or excessive payment retries
* Transactions that require human intervention

Traditional systems often stop at:

> **Payment Failed**

RazorRecover AI attempts to close that gap by answering:

> **Why did the payment fail?**
> **Is recovery likely?**
> **What should we do next?**
> **Is the action safe?**
> **Did the recovery actually work?**

---

# 🔁 Agentic Revenue Recovery Loop

```text
DETECT
   ↓
DIAGNOSE
   ↓
PRIORITIZE
   ↓
PREDICT
   ↓
RECOMMEND
   ↓
POLICY CHECK
   ↓
ACT
   ↓
VERIFY
   ↓
AUDIT
   ↓
MEASURE
```

### 1. Detect

The system scans failed and at-risk transactions and identifies cases that may be recoverable.

### 2. Diagnose

Relevant transaction and customer signals are analyzed, including:

* Transaction amount
* Previous successful payments
* Customer lifetime value
* Retry count
* Payment/gateway information
* Suspicion indicators

### 3. Predict

A trained **Random Forest classifier** estimates the probability that a transaction can be successfully recovered.

Transactions are categorized into recovery/risk tiers:

```text
HIGH
MEDIUM
LOW
```

### 4. Explain

The system produces a business-facing explanation based on the available transaction evidence.

Example:

```text
The customer has a strong previous payment history,
high lifetime value, and the failure appears temporary.
The predicted recovery probability is high.
```

### 5. Recommend

The recovery engine selects an appropriate action:

```text
RETRY_PAYMENT
CREATE_PAYMENT_LINK
SEND_RECOVERY_REMINDER
ESCALATE_TO_HUMAN
STOP_RECOVERY
```

### 6. Policy Check

Before a recovery action is executed, deterministic Python guardrails evaluate whether the action is permitted.

**The AI/LLM recommendation does not directly authorize financial actions.**

### 7. Act

For permitted scenarios, the prototype executes the corresponding recovery workflow, including generating a **Razorpay Test Mode Payment Link** where applicable.

### 8. Verify

The system checks the resulting payment/recovery status.

### 9. Audit

The decision, policy evaluation, selected action, and outcome are recorded for traceability.

### 10. Measure

The evaluation layer calculates recovery yield, recovered revenue, retry efficiency, and safety escalations.

---

# 🤖 Machine Learning

The prototype compares two classification approaches:

| ML Metric       | Random Forest | Logistic Regression |
| :-------------- | ------------: | ------------------: |
| **Accuracy**    |    **90.51%** |              77.82% |
| **ROC-AUC**     |    **0.9634** |              0.8285 |
| **Precision**   |    **0.9023** |              0.7229 |
| **Recall**      |    **0.8267** |              0.6080 |
| **F1 Score**    |    **0.8629** |              0.6605 |
| **Brier Score** |    **0.0717** |              0.1584 |

The Random Forest model was selected for the prototype because it performed better than the Logistic Regression baseline on the held-out evaluation set.

### ⚠️ Evaluation Disclaimer

These results are based on the project's **synthetic dataset and controlled evaluation setup**.

They should not be interpreted as production performance on real Razorpay merchant traffic.

---

# 🛡️ Bounded Autonomy & Safety

A core design principle of RazorRecover AI is the separation of:

```text
AI RECOMMENDATION
        ↓
DETERMINISTIC POLICY
        ↓
AUTHORIZED ACTION
```

The AI can recommend an action, but the deterministic policy engine decides whether that action is allowed.

This prevents an AI-generated recommendation from directly bypassing predefined financial safety rules.

---

## Policy Rules

### Rule 1 — Automatic Retry

Automatic retry is allowed only when:

```text
recovery_probability >= 75%
transaction_amount <= ₹5,000
retry_count < 2
transaction is not suspicious
```

### Rule 2 — High-Value Transaction

```text
transaction_amount > ₹50,000
        ↓
HUMAN APPROVAL REQUIRED
```

### Rule 3 — Low Recovery Probability

```text
recovery_probability < 60%
        ↓
STOP AUTOMATED RECOVERY
```

### Rule 4 — Retry Limit

```text
retry_count >= 2
        ↓
STOP AUTOMATED RETRIES
```

### Rule 5 — Suspicious Transaction

```text
suspicious == true
        ↓
ESCALATE TO HUMAN
```

---

# AI vs Policy Engine

The system intentionally separates intelligence from authorization.

For example, the ML model may produce:

```text
Recovery Probability: 91%
Recommendation: RETRY_PAYMENT
```

However, if the transaction is worth ₹85,000:

```text
Transaction Amount > ₹50,000
            ↓
Policy Engine
            ↓
HUMAN APPROVAL REQUIRED
```

Therefore:

> **High model confidence does not automatically mean that an action is authorized.**

This bounded-autonomy architecture is designed to make automated revenue recovery safer and more controllable.

---

# High-Level Architecture

```text
                         ┌─────────────────────┐
                         │   Failed Payments   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Transaction Scanner │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Customer / Payment  │
                         │      Signals        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   ML Risk Engine    │
                         │ Recovery Probability│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  AI Recommendation │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Policy Guardrails  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                         ▼                     ▼
                  ┌──────────────┐      ┌───────────────┐
                  │  Auto Action │      │ Human Review  │
                  └──────┬───────┘      └───────┬───────┘
                         │                      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Payment / Recovery  │
                         │       Outcome       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Audit + Measurement │
                         └─────────────────────┘
```

---

# 📊 Prototype Evaluation

The evaluation script tests the proposed recovery strategy against a naive retry baseline using **5,001 synthetic merchant transactions**.

| Metric                   |     Naive Retry |  RazorRecover AI |
| :----------------------- | --------------: | ---------------: |
| Transactions Evaluated   |           5,001 |            5,001 |
| Revenue at Risk          | ₹5,48,25,304.92 |  ₹5,48,25,304.92 |
| Recovered Revenue        |      ₹32,68,511 | **₹1,27,27,725** |
| Recovery Yield           |           5.96% |       **23.22%** |
| Human Safety Escalations |               0 |          **441** |

According to the controlled synthetic benchmark, the proposed strategy achieves a higher recovery yield than the naive retry baseline while explicitly escalating transactions that violate defined safety policies.

### Benchmark Interpretation

The benchmark demonstrates the behavior of the proposed system under the project's synthetic conditions.

The reported:

* ₹1.27 crore recovered revenue
* 23.22% recovery yield
* 441 human escalations

are **simulation/evaluation results**, not real merchant revenue or live Razorpay production results.

---

# 🧪 Example Recovery Scenario

Consider the following failed transaction:

```text
Transaction Amount:           ₹4,500
Customer LTV:                 ₹85,000
Previous Successful Payments: 12
Retry Count:                  0
Suspicious:                   No
Recovery Probability:         91%
```

The policy engine evaluates:

```text
Recovery Probability ≥ 75%     ✓
Amount ≤ ₹5,000                ✓
Retry Count < 2                ✓
Not Suspicious                  ✓
```

Result:

```text
POLICY STATUS: ALLOWED
```

The system can then proceed with the permitted recovery workflow.

---

# 🚨 Example Human Approval Scenario

Consider a high-value transaction:

```text
Transaction Amount:   ₹85,000
Recovery Probability: 91%
```

The ML model may consider the transaction highly recoverable.

However:

```text
Amount > ₹50,000
        ↓
HUMAN APPROVAL REQUIRED
```

The policy engine overrides automatic execution.

Only after an authorized human approval can the recovery workflow continue.

This demonstrates the project's **bounded autonomy** principle.

---

# 📈 Key Prototype Results

Based on the current synthetic benchmark and ML evaluation:

* **90.51%** Random Forest accuracy
* **0.9634** ROC-AUC
* **0.9023** precision
* **0.8267** recall
* **0.8629** F1 score
* **23.22%** simulated recovery yield
* **₹1.27 crore** simulated recovered revenue
* **441** safety escalations
* **5,001** synthetic transactions evaluated

---

# 🧰 Technology Stack

## Backend

* Python
* FastAPI
* Scikit-learn
* Pandas
* Uvicorn

## Frontend

* React
* Vite
* Tailwind CSS

## AI / Decision Layer

* Machine Learning recovery prediction
* AI/LLM-based explanation and recommendation
* Deterministic Python policy engine

## Payment Integration

* Razorpay Test Mode
* Razorpay Payment Link workflow

## Testing

* Pytest

---

# 📁 Project Structure

```text
RazorRecover-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
│
├── scripts/
│   ├── generate_synthetic_data.py
│   └── run_evaluation.py
│
├── docs/
│   ├── revenue-risk-methodology.md
│   ├── evaluation.md
│   ├── technical-decisions.md
│   ├── limitations.md
│   └── interview-questions.md
│
└── README.md
```

> **Note:** The exact directory structure may evolve as the prototype is developed.

---

# 🚀 Running Locally

## 1. Backend Setup

Open PowerShell/Terminal from the project root:

```bash
cd backend
```

Set the Python path in PowerShell:

```powershell
$env:PYTHONPATH="backend"
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Generate the synthetic dataset:

```bash
python ../scripts/generate_synthetic_data.py
```

Train the ML model:

```bash
python app/services/ml/train.py
```

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 2. Run Tests

From the project root:

```bash
pytest backend/tests
```

---

## 3. Start the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend communicates with the FastAPI backend through the configured API endpoints.

---

# 🎥 Recommended Demo Flow

The recommended internship/buildathon demonstration is:

```text
1. Open Dashboard
        ↓
2. Run Recovery Scan
        ↓
3. Select High-Priority Transaction
        ↓
4. View AI Diagnosis
        ↓
5. View Recovery Probability
        ↓
6. View Recommended Action
        ↓
7. Run Policy Safety Check
        ↓
8. Generate Razorpay Test Payment Link
        ↓
9. Demonstrate High-Value Human Approval
        ↓
10. Show Audit Trail
        ↓
11. Show Evaluation Metrics
```

### Demo Story

Start with the revenue-at-risk dashboard.

Then select a high-probability recovery case and show:

```text
Customer History
       +
Transaction Signals
       +
ML Prediction
       ↓
Recovery Recommendation
       ↓
Policy Validation
       ↓
Recovery Action
```

Finally, demonstrate a high-value transaction where the policy engine prevents automatic execution and requires human approval.

---

# 📚 Technical Documentation

Additional documentation is available in the `docs/` directory:

| Document                      | Purpose                                           |
| :---------------------------- | :------------------------------------------------ |
| `revenue-risk-methodology.md` | Revenue-risk calculations and eligibility rules   |
| `evaluation.md`               | Benchmark methodology and evaluation results      |
| `technical-decisions.md`      | Architecture and engineering decisions            |
| `limitations.md`              | Current limitations and production considerations |
| `interview-questions.md`      | Technical interview preparation                   |

---

# ⚠️ Limitations

RazorRecover AI is currently a prototype and has several limitations.

### Synthetic Data

The ML training and benchmark results use synthetic transaction data and may not represent real merchant behavior.

### Test Mode

Payment workflows are demonstrated using Razorpay Test Mode rather than live financial transactions.

### ML Generalization

The reported model metrics are based on the project's evaluation dataset. Real-world performance would require representative historical payment outcomes and extensive validation.

### Fraud Detection

The current suspicion/fraud mechanism should not be considered a production fraud-detection system.

### LLM Reliability

AI-generated explanations and recommendations may be incorrect or incomplete.

For this reason, sensitive actions are protected by deterministic policy rules.

### Production Readiness

A production implementation would require additional engineering and operational controls, including:

* Authentication and authorization
* Secure secret management
* Encryption
* Rate limiting
* Idempotency
* Distributed job processing
* Stronger fraud and risk models
* Human approval infrastructure
* Monitoring and alerting
* Production payment-provider integration
* Extensive offline and online evaluation
* Comprehensive observability

---

# 🔮 Future Improvements

Potential future improvements include:

1. Train recovery models using anonymized historical payment outcomes.
2. Add time-based features for recurring payment failures.
3. Introduce merchant-specific recovery policies.
4. Improve customer communication personalization.
5. Add stronger fraud and risk detection.
6. Implement idempotent recovery execution.
7. Introduce asynchronous job queues for large transaction volumes.
8. Add real-time monitoring and alerting.
9. Continuously evaluate recovery strategies through controlled experiments.
10. Explore contextual bandits or reinforcement-learning approaches for recovery-strategy optimization.

---

# 🔐 Safety Philosophy

The project follows three important principles:

```text
AI SHOULD RECOMMEND.
POLICY SHOULD AUTHORIZE.
SYSTEMS SHOULD EXECUTE.
```

This separation is particularly important when building AI systems that interact with financial workflows.

The goal is not unrestricted automation.

The goal is:

> **Bounded, explainable, measurable automation.**

---

# 🏆 Project Objective

RazorRecover AI demonstrates how **machine learning, agentic AI, deterministic safety policies, payment APIs, and auditability** can work together to create an automated revenue-recovery workflow.

The core idea is simple:

```text
DON'T JUST DETECT FAILED PAYMENTS.

UNDERSTAND THEM.
        ↓
PREDICT RECOVERY.
        ↓
RECOMMEND AN ACTION.
        ↓
CHECK WHETHER IT IS SAFE.
        ↓
TAKE THE ACTION.
        ↓
VERIFY THE RESULT.
        ↓
MEASURE THE RECOVERY.
```

---

## 📜 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.
