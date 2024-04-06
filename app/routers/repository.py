from fastapi import APIRouter, Request
from ..models import Log, DataStory
from ..components.github import GithubRepo
import os
from ..components.database.mongo import Mongo
from typing import List


router = APIRouter()
DIR = "./clone"
REPO = "https://github.com/tiangolo/fastapi"


@router.get("/clone")
async def clone():

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    GithubRepo.download_repo(REPO, DIR)

    return [{"name": "User 1"}, {"name": "User 2"}]

@router.post("/logs")
async def save_story(request: Request, log: Log):
    database: Mongo = request.app.state.database
    result = await database.saveLog(log)
    if result is None:
        return {"message": "Story already exists."}
    return result


@router.get("/logs")
async def getLogs(request: Request)-> List[Log]:
    database: Mongo = request.app.state.database
    return await database.getLogs()


@router.get("/logs/{log_id}")
async def getLogById(request: Request, log_id: str) -> Log:
    database: Mongo = request.app.state.database
    return await database.getLog(log_id)

@router.delete("/logs/{log_id}")
async def getLogById(request: Request, log_id: str) -> Log:
    database: Mongo = request.app.state.database
    return await database.removeLog(log_id)


@router.post("/stories")
async def insert_data_story(request: Request, data_story: DataStory):
    database: Mongo = request.app.state.database
    result = await database.insertDataStory(data_story)
    if result is None:
        return {"message": "Data story already exists."}
    return result

@router.get("/stories")
async def get_all_data_stories(request: Request) -> List[DataStory]:
    database: Mongo = request.app.state.database
    return await database.getAllDataStories()

@router.get("/stories/{url}")
async def get_data_story_by_url(request: Request, url: str) -> DataStory:
    database: Mongo = request.app.state.database
    return await database.getDataStoryByUrl(url)

@router.delete("/stories/{url}")
async def remove_data_story_by_url(request: Request, url: str) -> DataStory:
    database: Mongo = request.app.state.database
    return await database.removeDataStoryByUrl(url)