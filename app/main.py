import motor.motor_asyncio
from fastapi import FastAPI, status, Request, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from .models import File
from .routers import items
from .routers import repository


app = FastAPI()
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(items.router)
app.include_router(repository.router)
app.include_router(router)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://mongo-user:lK30SyUhSrIxND9Q@legacy-refactorer.bqdjbgf.mongodb.net/files?retryWrites=true&w=majority&appName=legacy-refactorer")
db = client.college

file_collection = db.get_collection("files")


@app.post(
    "/init",
    response_description="Add new student",
    response_model=File,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_student():
    file = await file_collection.insert_one(
        {
            "name": "example.py",
            "path": "app/example.py",
            "content": "import numpy as np\nprint(np.version)\n",
        }
    )
    return await file_collection.find_one(
        {"_id": file.inserted_id}
    )
