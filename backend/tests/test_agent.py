from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_run_agent_workflow():
    # Fetch a transaction ID from database
    txns = client.get("/api/v1/transactions?limit=1").json()
    assert len(txns) > 0
    txn_id = txns[0]["id"]

    response = client.post(f"/api/v1/agent/run/{txn_id}")
    assert response.status_code == 200
    data = response.json()
    assert "recovery_probability" in data
    assert "policy_result" in data
    assert "final_action" in data
    assert "ai_explanation" in data

def test_agent_query_endpoint():
    response = client.post("/api/v1/agent/query", json={"query": "How much revenue is at risk?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "at risk" in data["answer"].lower()

def test_audit_trail_endpoint():
    response = client.get("/api/v1/agent/audit-trail?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "agent_step" in data[0]
