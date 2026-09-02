# RazorRecover AI — Revenue at Risk Methodology

## 1. Executive Definition
**Revenue at Risk** is defined as unrecovered monetary value from failed payment attempts, abandoned checkout carts, failed subscription renewals, and overdue receivables where the customer remains active and the transaction is deemed potentially recoverable.

> **Key Distinction:** A transaction is NOT classified as Revenue at Risk merely because it exists. It requires active unrecovered status combined with valid customer activity signals.

---

## 2. Business Eligibility Signals

| Failure Category | Primary Cause | Eligibility Criteria | Risk Weight |
| :--- | :--- | :--- | :---: |
| **Temporary Gateway** | `BANK_TIMEOUT`, `GATEWAY_DOWN`, `AUTH_FAILURE` | Gateway glitch; customer history clean; retry count < 2 | **High (80 - 95%)** |
| **Checkout Abandonment** | `CART_ABANDONED`, `EXIT_INTENT` | Cart abandoned at payment step; session < 72 hours | **High (70 - 85%)** |
| **Subscription Renewal** | `SUB_EXPIRED`, `MANDATE_FAILED` | Active subscriber mandate failed due to gateway/card update | **Medium (60 - 75%)** |
| **Permanent Customer** | `INSUFFICIENT_FUNDS`, `CARD_EXPIRED` | Customer account active; payment link/update required | **Medium (40 - 60%)** |
| **Overdue Receivable** | `INVOICE_OVERDUE` | Outstanding B2B invoice past due date | **Medium (40 - 55%)** |

---

## 3. Exclusions & Excluded Categories

Transactions are explicitly **EXCLUDED** from Revenue at Risk or Recoverable Revenue if:
1. **Confirmed Fraud / Suspicious**: Fraud score $> 0.70$ or flagged as suspicious by risk engines.
2. **Exceeded Retry Limit**: Retry count $\ge 2$ without successful payment response.
3. **Hard Account Termination**: Closed customer account or chargeback dispute.
4. **Already Recovered**: Payment status is `RECOVERED` or receipt verified.

---

## 4. Mathematical Formulation

### 4.1 Total Revenue at Risk ($R_{\text{risk}}$)
$$R_{\text{risk}} = \sum_{i \in \text{Unrecovered}} \text{Amount}_i \quad \forall i \text{ where } \text{Status}_i \in \{\text{FAILED}, \text{ABANDONED}\}$$

### 4.2 Eligible Recoverable Revenue ($R_{\text{eligible}}$)
$$R_{\text{eligible}} = \sum_{i \in \text{Unrecovered}} \text{Amount}_i \quad \forall i \text{ where } P(\text{Recovery}_i) \ge 0.75 \text{ and } \text{Policy}_i = \text{ALLOWED}$$

### 4.3 Verified Recovered Revenue ($R_{\text{recovered}}$)
$$R_{\text{recovered}} = \sum_{i \in \text{Verified}} \text{RecoveredAmount}_i \quad \forall i \text{ where } \text{Status}_i = \text{RECOVERED}$$

### 4.4 Recovery Yield Rate ($Y_{\text{recovery}}$)
$$Y_{\text{recovery}} = \left( \frac{R_{\text{recovered}}}{R_{\text{risk}}} \right) \times 100\%$$

---

## 5. Dashboard Calculation Derivation
All metrics displayed on the RazorRecover AI executive dashboard are dynamically derived from backend database aggregates via the `/api/v1/analytics/summary` endpoint. Zero numbers are hardcoded.
