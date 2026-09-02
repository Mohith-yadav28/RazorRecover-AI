# RazorRecover AI — Product Limitations & Honest Technical Trade-offs

This document transparently outlines the limitations, assumptions, and future production roadmap for **RazorRecover AI**.

---

## 1. Data & Environment Scope

### Synthetic Dataset vs Real Merchant Data
- **Current State**: Evaluated on 5,001 realistic synthetic transaction records generated via `scripts/generate_synthetic_data.py`.
- **Limitation**: Synthetic distributions, while correlated with real fintech behavior (e.g. VIP customer purchase histories, gateway timeouts), cannot capture unexpected real-world black swan gateway outages or regional payment failure spikes.
- **Production Transition**: Replace synthetic generator with live Razorpay Webhook Ingestion (`payment.failed`, `order.paid`, `checkout.abandoned`).

### Test Mode Scope
- **Current State**: Integrated with Razorpay API Test Mode keys and Payment Links API.
- **Limitation**: Real money is not moved in Test Mode. Simulated payment recoveries rely on status polling or demo scenario execution.

---

## 2. Machine Learning Scope

### Feature Scope
- **Current State**: Model utilizes 8 primary features (amount, LTV, past success count, failed count, retry count, fraud flag, failure category, payment method).
- **Limitation**: Does not yet incorporate real-time device fingerprinting, IP geolocation, or bank-side bin routing metadata.

---

## 3. Future Roadmap for Production Readiness

1. **Live Webhook Listener**: Ingest real-time Razorpay webhooks for instant recovery trigger.
2. **Multi-Merchant Organization Isolation**: Multi-tenant database partitioning for multi-merchant SaaS deployment.
3. **Advanced Personalization**: Custom merchant recovery email & WhatsApp template engines.
