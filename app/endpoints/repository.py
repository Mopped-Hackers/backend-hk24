from fastapi import APIRouter
from ..components.github import GithubRepo
import os

router = APIRouter()
DIR = "./clone"
REPO = "https://github.com/tiangolo/fastapi"


@router.get("/clone")
async def clone():

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    GithubRepo.download_repo(REPO, DIR)

    return [{"name": "User 1"}, {"name": "User 2"}]
