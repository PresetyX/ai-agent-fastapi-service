import os

# Configuração antes de importar o app: o middleware lê as variáveis na inicialização.
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000")
os.environ.setdefault("JWT_SECRET", "test-secret-with-at-least-32-bytes!!")

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.security import SECRET  # noqa: E402
from app.store import store  # noqa: E402


@pytest.fixture(autouse=True)
def clean_store():
    store.workflows.clear()
    store.tasks.clear()
    yield


@pytest.fixture
def token():
    return jwt.encode({"sub": "test-user"}, SECRET, algorithm="HS256")


@pytest.fixture
def anon_client():
    return TestClient(app)


@pytest.fixture
def client(token):
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})
