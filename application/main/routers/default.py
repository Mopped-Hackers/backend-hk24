from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi import FastAPI, Response, status, Depends, Request, HTTPException

from application.initializer import logger_instance
from pydantic import BaseModel


router = APIRouter()
logger = logger_instance.get_logger(__name__)


@router.get("/")
async def keepAliveAzure(response: Response):
    return Response(status_code=200)
