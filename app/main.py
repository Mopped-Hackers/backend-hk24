from fastapi import FastAPI, status, Request, Response, Body,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from queue import Queue
from fastapi.routing import APIRouter

from .routers import repository
from .components.database.mongo import Mongo
from .models import Log
from typing import List
from .routers import items
from .routers import repository
from .routers import logs
from .routers import stories
import asyncio
from typing import Dict
from .models import getDummyStory
from .components.pdf.pdf import PdfGenerator
from .models import DataStory, Functions, Readme
import json

from .components.github import GithubRepo

from starlette.requests import Request
import os

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL: str = os.getenv("MONGODB_URL")


app = FastAPI()
router = APIRouter()


app.state.database = Mongo(MONGODB_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repository.router)
app.include_router(items.router)
app.include_router(logs.router)
app.include_router(stories.router)


queue = Queue()
status_dict: Dict[str, str] = {}

@app.post("/process")
async def process_url(url: str, background_tasks: BackgroundTasks):
    queue.put(url)
    status_dict[url] = "pending"
    background_tasks.add_task(process_queue)
    return {"message": "URL added to the queue"}

async def process_queue():
    database: Mongo = app.state.database
    while not queue.empty():
        url = queue.get()

        story = await database.getStory(url)
        if story is not None:
            
            PdfGenerator(app,story).generate_pdf()

            status_dict[url] = "done"
            return

        repo_dir = GithubRepo.download_repo(url)
        print(repo_dir)

        # TODO: GENERATE BUSINESS ANALYSIS
        status_dict[url] = "done"
        

@app.get("/status")
async def get_status(request: Request,url: str):
    database: Mongo = request.app.state.database

    # DEMO OVERRIDE
    #url = "my-example-refactor"

    status: str = status_dict.get(url, "not found")
    if status == "done":
        story = await database.getStory(url)
        if story is None:
            return {"url":url, "status":status, "output": None}
        filename = f"./structured_output_{story.url}_{story.id}.pdf"
        output = f"{request.url.scheme}://{request.headers['host']}/static/{filename}"
        GithubRepo.remove_repo(url)
        return {"url": url, "status": status, "output": output}
    else: 
        return {"url":url, "status":status, "output": None}


# DEMO GENERATION
@app.get("/test-pdf")
async def asf(request: Request):
    database: Mongo = request.app.state.database

    exampleStory = await database.getStory("my-example-refactor")

    PdfGenerator(request.app,exampleStory).generate_pdf()
    
    return exampleStory