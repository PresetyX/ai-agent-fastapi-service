import os
from collections import defaultdict
from time import monotonic

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Defina JWT_SECRET (32+ bytes) fora do ambiente de desenvolvimento.
SECRET = os.getenv("JWT_SECRET", "development-only-secret-change-me-in-prod")
PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int | None = None, window: int = 60):
        super().__init__(app)
        self.limit = limit if limit is not None else int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        now = monotonic()
        key = request.client.host if request.client else "unknown"
        values = [t for t in self.requests[key] if now - t < self.window]
        if len(values) >= self.limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        values.append(now)
        self.requests[key] = values
        return await call_next(request)

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"detail": "Missing bearer token"}, status_code=401)
        try:
            jwt.decode(auth.removeprefix("Bearer ").strip(), SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return JSONResponse({"detail": "Invalid bearer token"}, status_code=401)
        return await call_next(request)

def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse({"detail": "Internal server error"}, status_code=500)
