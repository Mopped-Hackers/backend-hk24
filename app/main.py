from fastapi import FastAPI, status, Request, Response, Body,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from queue import Queue
from fastapi.routing import APIRouter

from .routers import repository
from .components.database.mongo import Mongo
from .models import Log
from typing import List
from .models import File
from .endpoints import items
from .endpoints import repository

import asyncio
from typing import Dict

app = FastAPI()
router = APIRouter()

app.state.database = Mongo("mongodb+srv://mongo-user:lK30SyUhSrIxND9Q@legacy-refactorer.bqdjbgf.mongodb.net/data?retryWrites=true&w=majority&appName=legacy-refactorer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(repository.router)
app.include_router(router)




queue = Queue()
status_dict: Dict[str, str] = {}

@app.post("/process")
async def process_url(url: str, background_tasks: BackgroundTasks):
    queue.put(url)
    status_dict[url] = "pending"
    background_tasks.add_task(process_queue)
    return {"message": "URL added to the queue"}

async def process_queue():
    while not queue.empty():
        url = queue.get()
        # Process the URL here
        await asyncio.sleep(10)  # Simulate time-consuming process

        
        status_dict[url] = "done"

@app.get("/status/{url}")
async def get_status(url: str):
    return {"url": url, "status": status_dict.get(url, "not found")}