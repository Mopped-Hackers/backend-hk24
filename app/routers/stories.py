from fastapi import APIRouter, Request
from ..models import Log, DataStory
from ..components.github import GithubRepo
from ..components.database.mongo import Mongo
from typing import List
from ..models import getDummyStory
from urllib.parse import unquote


router = APIRouter()




@router.post("/dummy-story")
async def asf(request: Request) -> DataStory:
    database: Mongo = request.app.state.database

    dataStory: DataStory = getDummyStory()
    
    return await database.saveStory(dataStory)


@router.get("/stories")
async def getStories(request: Request, url: str = "") -> List[DataStory]|DataStory:
    database: Mongo = request.app.state.database

    if url == "":
        return await database.getStories()
    else:
        return await database.getStory(unquote(str(url)))


@router.post("/stories")
async def insert_data_story(request: Request, data_story: DataStory) -> DataStory|dict|None:
    database: Mongo = request.app.state.database
    result = await database.saveStory(data_story)
    if result is None:
        return {"message": "Data story already exists."}
    return result


@router.delete("/stories")
async def insert_data_story(request: Request, url: str):
    database: Mongo = request.app.state.database
    return await database.removeStory(unquote(str(url)))

    