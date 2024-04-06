import uuid
from typing import Optional
from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from datetime import date, datetime, time, timedelta
from bson import ObjectId

from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Log(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    timestamp: datetime = Field(...)
    model: str = Field(...)
    raw_content: str = Field(...)
    class Config:
        allow_population_by_field_name = True


class Functions:
    def __init__(self, path, name, code, code_commented, summary) -> None:
        self.path = path
        self.name = name
        self.code = code
        self.code_commented = code_commented
        self.summary = summary

class Readme:
    def __init__(self,text, summary) -> None:
        self.text = text
        self.summary = summary
        

class DataStory(BaseModel):
    key: str = Field(...) # Repository URL
    functions_to_test: dict = Field(...)
    functions_to_code: dict = Field(...)
    files: list = Field(...)
    functions: Functions = Field(...)
    readme: Readme = Field(...)

    class Config:
        arbitrary_types_allowed=True
