from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_demo_scenarios():
    response = client.get("/api/v1/razorpay/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert isinstance(scenarios, list)
    assert len(scenarios) == 5
    assert scenarios[0]["id"] == "scenario_1"

def test_load_demo_scenario():
    response = client.post("/api/v1/razorpay/load-scenario/scenario_1")
    assert response.status_code == 200
    data = response.json()
    assert "scenario" in data
    assert data["scenario"]["id"] == "scenario_1"
    assert data["transaction_id"] == "TXN_DEMO_SCENARIO_1"

def test_create_payment_link():
    # Fetch a transaction
    txns = client.get("/api/v1/transactions?limit=1").json()
    assert len(txns) > 0
    txn_id = txns[0]["id"]

    response = client.post(f"/api/v1/razorpay/create-link/{txn_id}")
    assert response.status_code == 200
    data = response.json()
    assert "payment_link_id" in data
    assert "payment_link_url" in data
