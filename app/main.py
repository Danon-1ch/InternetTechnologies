import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.log_config import setup_logging, status_level
from app.routers import comments, labels, projects, tasks, users

setup_logging()
logger = logging.getLogger("app")
request_logger = logging.getLogger("app.request")

app = FastAPI(title="TaskFlow API", version="1.0.0")


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_logger.debug("%s %s started", request.method, request.url.path)
    response = await call_next(request)
    request_logger.log(
        status_level(response.status_code),
        "%s %s -> %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.critical("database health check failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    logger.info("database health check ok")
    return {"status": "ok", "database": "up", "message": "Hello community, я не хочу быть вашей частью."}


app.include_router(users.router, prefix="/v1/users", tags=["users"])
app.include_router(projects.router, prefix="/v1/projects", tags=["projects"])
app.include_router(labels.router, prefix="/v1/labels", tags=["labels"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["tasks"])
app.include_router(comments.router, prefix="/v1/comments", tags=["comments"])
