from fastapi import APIRouter, Request
from ..models import Log, DataStory
from ..components.github import GithubRepo
from ..components.database.mongo import Mongo
from typing import List

router = APIRouter()

@router.post("/logs")
async def save_story(request: Request, log: Log) -> Log:
    database: Mongo = request.app.state.database
    return await database.saveLog(log)


@router.get("/logs")
async def getLogs(request: Request)-> List[Log]:
    database: Mongo = request.app.state.database
    return await database.getLogs()


@router.get("/logs/{log_id}")
async def getLogById(request: Request, log_id: str) -> Log:
    database: Mongo = request.app.state.database
    return await database.getLog(log_id)

@router.delete("/logs/{log_id}")
async def deleteLogById(request: Request, log_id: str) -> Log:
    database: Mongo = request.app.state.database
    return await database.removeLog(log_id)