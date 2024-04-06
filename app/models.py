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

class Functions(BaseModel):
    path: str
    name: str
    code: str
    code_commented: str
    summary: str

class Readme(BaseModel):
    text: str
    summary: str
  
class DataStory(BaseModel):
    key: str  # Repository URL
    functions_to_test: dict
    functions_to_code: dict
    files: List[str]
    functions: List[Functions]
    readme: Readme

    class Config:
        arbitrary_types_allowed = True

def convert_to_data_story(result_dict, url) -> DataStory:
    # Extract the necessary data from the dictionary
    data = result_dict[url]
    
    # Create Functions instances
    functions_instances = []
    for func_data in data["functions"]:
        func_instance = Functions(
            path=func_data["path"],
            name=func_data["name"],
            code=func_data["code"],
            code_commented=func_data.get("code_with_comments", ""),
            summary=func_data["summary"]
        )
        functions_instances.append(func_instance)
    
    # Create a Readme instance
    readme_data = data["readme"]
    readme_instance = Readme(
        text=readme_data["text"],
        summary=readme_data["summary"]
    )
    
    # Create the DataStory instance
    data_story_instance = DataStory(
        key=url,
        functions_to_test=data["function_to_test"],
        functions_to_code=data["function_to_code"],
        files=data["files"],
        functions=functions_instances,
        readme=readme_instance
    )
    
    return data_story_instance