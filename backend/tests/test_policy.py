from fastapi.testclient import TestClient
from app.main import app
from app.services.policy.engine import policy_engine

client = TestClient(app)

def test_rule_auto_retry_allowed():
    res = policy_engine.evaluate("RETRY_PAYMENT", {
        "amount": 3500.0,
        "recovery_probability": 0.85,
        "retry_count": 0,
        "is_suspicious": False
    })
    assert res.policy_result == "ALLOWED"
    assert res.final_action == "RETRY_PAYMENT"

def test_rule_high_value_escalation():
    res = policy_engine.evaluate("RETRY_PAYMENT", {
        "amount": 85000.0,
        "recovery_probability": 0.90,
        "retry_count": 0,
        "is_suspicious": False
    })
    assert res.policy_result == "HUMAN_APPROVAL_REQUIRED"
    assert res.final_action == "HUMAN_APPROVAL_REQUIRED"
    assert "exceeds automatic recovery threshold" in res.reason

def test_rule_low_probability_halt():
    res = policy_engine.evaluate("RETRY_PAYMENT", {
        "amount": 2500.0,
        "recovery_probability": 0.42,
        "retry_count": 0,
        "is_suspicious": False
    })
    assert res.policy_result == "BLOCKED"
    assert res.final_action == "STOP_RECOVERY"

def test_rule_retry_limit_reached():
    res = policy_engine.evaluate("RETRY_PAYMENT", {
        "amount": 2500.0,
        "recovery_probability": 0.85,
        "retry_count": 2,
        "is_suspicious": False
    })
    assert res.policy_result == "BLOCKED"
    assert res.final_action == "STOP_RECOVERY"

def test_rule_fraud_escalation():
    res = policy_engine.evaluate("RETRY_PAYMENT", {
        "amount": 1000.0,
        "recovery_probability": 0.95,
        "retry_count": 0,
        "is_suspicious": True
    })
    assert res.policy_result == "BLOCKED"
    assert res.final_action == "ESCALATE_TO_HUMAN"

def test_policy_endpoint():
    payload = {
        "recommended_action": "RETRY_PAYMENT",
        "amount": 85000.0,
        "recovery_probability": 0.90,
        "retry_count": 0,
        "is_suspicious": False
    }
    response = client.post("/api/v1/policies/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["policy_result"] == "HUMAN_APPROVAL_REQUIRED"
