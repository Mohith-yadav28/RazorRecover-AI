from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ml_prediction():
    payload = {
        "amount": 4999.0,
        "customer_ltv": 65000.0,
        "successful_transactions": 8,
        "failed_transactions": 1,
        "retry_count": 0,
        "is_suspicious": False,
        "failure_category": "TEMPORARY_GATEWAY",
        "payment_method": "UPI"
    }
    response = client.post("/api/v1/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recovery_probability" in data
    assert 0.0 <= data["recovery_probability"] <= 1.0
    assert data["priority_tier"] in ["HIGH", "MEDIUM", "LOW"]
    assert "priority_score" in data
