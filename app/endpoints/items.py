from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/items")
async def read_items():
    return {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}