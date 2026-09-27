from time import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.routers import auth, salas, professores, escalas, equipes, professor as professor_router

app = FastAPI(
    title="Pequeno Rebanho",
    version="1.0.0",
    description="Sistema de gestão de salas, professores, equipes e escalas.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-Id"],
)

request_timestamps = {}


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = int(time())
    bucket = request_timestamps.setdefault(client_ip, [])
    bucket[:] = [ts for ts in bucket if now - ts < 60]

    if len(bucket) >= settings.rate_limit_per_minute:
        from fastapi.responses import JSONResponse

        return JSONResponse({"detail": "Muitas requisições. Tente novamente em alguns instantes."}, status_code=429)

    bucket.append(now)

    response = await call_next(request)
    response.headers["X-Request-Id"] = f"{client_ip}-{int(time())}"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(salas.router)
app.include_router(professores.router)
app.include_router(equipes.router)
app.include_router(escalas.router)
app.include_router(professor_router.router)


@app.get("/")
def root() -> FileResponse:
    return FileResponse("static/login.html")


@app.get("/login")
def login_page() -> FileResponse:
    return FileResponse("static/login.html")


@app.get("/app")
def app_page() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/healthcheck")
def healthcheck() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
