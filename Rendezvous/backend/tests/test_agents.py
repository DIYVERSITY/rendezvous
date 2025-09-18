from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_agent():
    response = client.post("/agent/search/invoke", json={"query": "hello world"})
    assert response.status_code == 200
    assert "summary" in response.json()
