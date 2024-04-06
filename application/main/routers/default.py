from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel

from application.initializer import logger_instance
from application.main.components.github import github

router = APIRouter()
logger = logger_instance.get_logger(__name__)


@router.get("/")
async def keep_alive_azure(response: Response) -> Response:
    return Response(status_code=200)


# localhost:8000/repo?url=dement
@router.get("/repo")
async def get_repo(url: str = "d..") -> object:
    download_status = github.download_repo(url)
    return {"url": url, "status": download_status}
