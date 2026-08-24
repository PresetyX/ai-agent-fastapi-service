from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_workflow_and_task_crud():
    workflow = client.post("/workflows", json={"name": "Onboarding"})
    assert workflow.status_code == 201
    wid = workflow.json()["id"]
    task = client.post(f"/workflows/{wid}/tasks", json={"title": "Invite user"})
    assert task.status_code == 201
    tid = task.json()["id"]
    assert client.patch(f"/workflows/{wid}/tasks/{tid}", json={"completed": True}).json()["completed"]
    assert client.delete(f"/workflows/{wid}/tasks/{tid}").status_code == 204
    assert client.delete(f"/workflows/{wid}").status_code == 204

def test_validation_and_missing_resource():
    assert client.post("/workflows", json={"name": ""}).status_code == 422
    assert client.get("/workflows/00000000-0000-0000-0000-000000000000").status_code == 404
