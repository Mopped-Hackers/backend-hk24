from fastapi.routing import APIRouter
from fastapi import Response, Request, HTTPException, Header

from pydantic import BaseModel, Field
from typing import List, Union
import json

from application.initializer import logger_instance
from application.main.components.Ai import controller as AI_controller
from application.main.routers.models import AI_input_1
from application.main.routers import validation
from application.main.infrastructure.sql.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()
logger = logger_instance.get_logger(__name__)


@router.post("/one")
async def ai_path_1(
    body: AI_input_1,
    request: Request,
    response: Response,
):
    logger.info(f"INCOMING REQUEST: {body.dict()}")
    response = AI_controller.stuff()
    return response


@router.get("/two")
async def ai_path_2(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@router.get("/three/{user_id}/items/{item_id}")
async def ai_path_3(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@router.get("/four")
async def ai_path_2(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return {"skip": skip, "limit": limit}
