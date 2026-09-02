from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_transactions_endpoint():
    response = client.get("/api/v1/transactions?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10
    assert "amount" in data[0]
    assert "status" in data[0]
    assert "customer" in data[0]

def test_cases_endpoint():
    response = client.get("/api/v1/cases?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10
    assert "recovery_probability" in data[0]
    assert "policy_result" in data[0]

def test_analytics_summary_endpoint():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] >= 5000
    assert data["revenue_at_risk"] > 0
    assert "recovery_rate" in data


def test_policy_rules_endpoint():
    response = client.get("/api/v1/policies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    assert data[0]["rule_code"].startswith("RULE_")
