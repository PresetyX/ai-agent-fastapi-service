from datetime import datetime, timezone
from uuid import UUID, uuid4
from .models import Task, TaskCreate, TaskUpdate, Workflow, WorkflowCreate, WorkflowUpdate

class MemoryStore:
    def __init__(self) -> None:
        self.workflows: dict[UUID, Workflow] = {}
        self.tasks: dict[UUID, dict[UUID, Task]] = {}

    def create_workflow(self, data: WorkflowCreate) -> Workflow:
        now = datetime.now(timezone.utc)
        item = Workflow(id=uuid4(), created_at=now, updated_at=now, **data.model_dump())
        self.workflows[item.id] = item
        self.tasks[item.id] = {}
        return item

    def update_workflow(self, item: Workflow, data: WorkflowUpdate) -> Workflow:
        values = data.model_dump(exclude_unset=True)
        updated = item.model_copy(update={**values, "updated_at": datetime.now(timezone.utc)})
        self.workflows[item.id] = updated
        return updated

    def create_task(self, workflow_id: UUID, data: TaskCreate) -> Task:
        task = Task(id=uuid4(), **data.model_dump())
        self.tasks[workflow_id][task.id] = task
        return task

    def update_task(self, workflow_id: UUID, task: Task, data: TaskUpdate) -> Task:
        updated = task.model_copy(update=data.model_dump(exclude_unset=True))
        self.tasks[workflow_id][task.id] = updated
        return updated

store = MemoryStore()
