from typing import List
from ...models import Log, DataStory
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import HTTPException, status, Response

class Mongo:

    def __init__(self, URI) -> None:

        client = AsyncIOMotorClient(URI)
        self.database = client.college
        self.logCollection = self.database.get_collection("logs")
        self.storyCollection = self.database.get_collection("stories")

    async def saveStory(self, storyObject: DataStory) -> DataStory:
        existing = await self.getStory(storyObject.key)
        if existing: 
            await self.storyCollection.update_one({"url": storyObject.key}, {"$set": storyObject})
            return await self.getStory(storyObject.key)
        else:
            story = await self.storyCollection.insert_one(storyObject)
            return await self.getStory(story.inserted_id)
        
        
    async def getStories(self):
        stories = []
        async for story in self.storyCollection.find({}):
            stories.append(story)
        return stories

    async def removeStory(self, storyObjectKey: str):
        delete_result = await self.storyCollection.delete_one({"url": storyObjectKey})
        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=404, detail=f"Story {storyObjectKey} not found")





    async def getStory(self, storyObjectKey: str)-> DataStory:
        return self.storyCollection.find_one({"url": storyObjectKey})
    

    #####################################################xxx
    
    async def saveLog(self, logObject: Log) -> Log:
        log = await self.logCollection.insert_one(logObject.model_dump())
        return await self.getLog(log.inserted_id)
    

    async def getLog(self, logObjectID: str) -> Log:
        if (student := await self.logCollection.find_one({"_id": ObjectId(logObjectID)})) is not None:
            return student
        raise HTTPException(status_code=404, detail=f"Log {id} not found")

    async def getLogs(self) -> List[Log]:
        logs = []
        async for log in self.logCollection.find({}):
            logs.append(log)
        return logs


    async def removeLog(self, logObjectID: str):
        delete_result = await  self.logCollection.delete_one({"_id": ObjectId(logObjectID)})
        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=404, detail=f"Log {str(id)} not found")    


