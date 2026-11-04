MISSING = "00000000-0000-0000-0000-000000000000"


def test_health_is_public(anon_client):
    assert anon_client.get("/health").json() == {"status": "ok"}


def test_workflow_and_task_crud(client):
    workflow = client.post("/workflows", json={"name": "Onboarding"})
    assert workflow.status_code == 201
    body = workflow.json()
    wid = body["id"]
    assert body["status"] == "draft"

    task = client.post(f"/workflows/{wid}/tasks", json={"title": "Invite user"})
    assert task.status_code == 201
    tid = task.json()["id"]

    assert client.patch(f"/workflows/{wid}/tasks/{tid}", json={"completed": True}).json()["completed"]
    assert client.get(f"/workflows/{wid}").json()["tasks"][0]["completed"] is True
    assert client.delete(f"/workflows/{wid}/tasks/{tid}").status_code == 204
    assert client.get(f"/workflows/{wid}/tasks").json() == []
    assert client.delete(f"/workflows/{wid}").status_code == 204
    assert client.get(f"/workflows/{wid}").status_code == 404


def test_list_workflows_includes_tasks(client):
    wid = client.post("/workflows", json={"name": "Relatório semanal"}).json()["id"]
    client.post(f"/workflows/{wid}/tasks", json={"title": "Coletar métricas"})
    client.post(f"/workflows/{wid}/tasks", json={"title": "Enviar resumo"})
    workflows = client.get("/workflows").json()
    assert len(workflows) == 1
    assert [t["title"] for t in workflows[0]["tasks"]] == ["Coletar métricas", "Enviar resumo"]


def test_patch_updates_only_sent_fields_and_timestamp(client):
    created = client.post("/workflows", json={"name": "Faturas", "description": "mensal"}).json()
    updated = client.patch(f"/workflows/{created['id']}", json={"status": "active"}).json()
    assert updated["status"] == "active"
    assert updated["description"] == "mensal"
    assert updated["updated_at"] > created["updated_at"]


def test_validation_errors(client):
    assert client.post("/workflows", json={"name": ""}).status_code == 422
    assert client.post("/workflows", json={"name": "x", "status": "unknown"}).status_code == 422
    assert client.post("/workflows", json={"name": "x" * 121}).status_code == 422
    assert client.get("/workflows/not-a-uuid").status_code == 422


def test_missing_resources_return_404(client):
    assert client.get(f"/workflows/{MISSING}").status_code == 404
    assert client.post(f"/workflows/{MISSING}/tasks", json={"title": "x"}).status_code == 404
    wid = client.post("/workflows", json={"name": "W"}).json()["id"]
    response = client.get(f"/workflows/{wid}/tasks/{MISSING}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
