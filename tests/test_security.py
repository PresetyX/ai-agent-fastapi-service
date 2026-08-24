from fastapi.testclient import TestClient
from app.main import app
from app.security import SECRET
import jwt

client = TestClient(app)

def test_protected_endpoint_requires_token():
    assert client.get("/workflows").status_code == 401

def test_valid_token_allows_access():
    token = jwt.encode({"sub": "test-user"}, SECRET, algorithm="HS256")
    assert client.get("/workflows", headers={"Authorization": f"Bearer {token}"}).status_code == 200

def test_invalid_token_is_rejected():
    assert client.get("/workflows", headers={"Authorization": "Bearer invalid"}).status_code == 401
