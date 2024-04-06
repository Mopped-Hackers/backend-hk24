from fastapi import FastAPI

from typing import List

app = FastAPI()


@app.get("/items/", response_model=List[Item])
async def read_items():
    items = []
    async for item in collection.find():
        items.append(Item(**item))
    return items
