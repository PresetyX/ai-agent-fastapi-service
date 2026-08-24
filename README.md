# ai-agent-fastapi-service

FastAPI microservice scaffold for AI-agent-generated workflow and task APIs.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
pytest
```
