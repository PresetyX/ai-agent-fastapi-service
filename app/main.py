from uuid import UUID
from fastapi import FastAPI, HTTPException
from .models import *
from .store import store
from .security import JWTMiddleware, RateLimitMiddleware, unhandled_exception_handler

app = FastAPI(title="AI Agent FastAPI Service", version="1.0.0")
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTMiddleware)
app.add_exception_handler(Exception, unhandled_exception_handler)

def workflow_or_404(workflow_id: UUID) -> Workflow:
    item = store.workflows.get(workflow_id)
    if not item: raise HTTPException(status_code=404, detail="Workflow not found")
    item.tasks = list(store.tasks[workflow_id].values())
    return item

def task_or_404(workflow_id: UUID, task_id: UUID) -> Task:
    workflow_or_404(workflow_id)
    item = store.tasks[workflow_id].get(task_id)
    if not item: raise HTTPException(status_code=404, detail="Task not found")
    return item

@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok"}
@app.post("/workflows", response_model=Workflow, status_code=201)
def create_workflow(data: WorkflowCreate): return store.create_workflow(data)
@app.get("/workflows", response_model=list[Workflow])
def list_workflows(): return [workflow_or_404(i) for i in store.workflows]
@app.get("/workflows/{workflow_id}", response_model=Workflow)
def get_workflow(workflow_id: UUID): return workflow_or_404(workflow_id)
@app.patch("/workflows/{workflow_id}", response_model=Workflow)
def update_workflow(workflow_id: UUID, data: WorkflowUpdate):
    item = workflow_or_404(workflow_id)
    return workflow_or_404(store.update_workflow(item, data).id)
@app.delete("/workflows/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: UUID):
    workflow_or_404(workflow_id)
    del store.workflows[workflow_id], store.tasks[workflow_id]
@app.post("/workflows/{workflow_id}/tasks", response_model=Task, status_code=201)
def create_task(workflow_id: UUID, data: TaskCreate):
    workflow_or_404(workflow_id); return store.create_task(workflow_id, data)
@app.get("/workflows/{workflow_id}/tasks", response_model=list[Task])
def list_tasks(workflow_id: UUID):
    workflow_or_404(workflow_id); return list(store.tasks[workflow_id].values())
@app.get("/workflows/{workflow_id}/tasks/{task_id}", response_model=Task)
def get_task(workflow_id: UUID, task_id: UUID): return task_or_404(workflow_id, task_id)
@app.patch("/workflows/{workflow_id}/tasks/{task_id}", response_model=Task)
def update_task(workflow_id: UUID, task_id: UUID, data: TaskUpdate):
    return store.update_task(workflow_id, task_or_404(workflow_id, task_id), data)
@app.delete("/workflows/{workflow_id}/tasks/{task_id}", status_code=204)
def delete_task(workflow_id: UUID, task_id: UUID):
    task_or_404(workflow_id, task_id); del store.tasks[workflow_id][task_id]
