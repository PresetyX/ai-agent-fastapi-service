import time

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.security import SECRET, RateLimitMiddleware


def test_protected_endpoint_requires_token(anon_client):
    response = anon_client.get("/workflows")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing bearer token"}


def test_valid_token_allows_access(client):
    assert client.get("/workflows").status_code == 200


def test_invalid_token_is_rejected(anon_client):
    response = anon_client.get("/workflows", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid bearer token"}


def test_token_signed_with_other_secret_is_rejected(anon_client):
    forged = jwt.encode({"sub": "attacker"}, "another-secret-with-32-bytes-or-more", algorithm="HS256")
    assert anon_client.get("/workflows", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_expired_token_is_rejected(anon_client):
    expired = jwt.encode({"sub": "u", "exp": int(time.time()) - 10}, SECRET, algorithm="HS256")
    assert anon_client.get("/workflows", headers={"Authorization": f"Bearer {expired}"}).status_code == 401


def test_docs_are_public(anon_client):
    assert anon_client.get("/openapi.json").status_code == 200


def test_rate_limit_returns_429_after_limit():
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limit=3, window=60)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    codes = [client.get("/ping").status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]
    assert client.get("/ping").json() == {"detail": "Rate limit exceeded"}
