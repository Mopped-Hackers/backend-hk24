import uuid
from typing import Optional
from typing import Optional, List
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class File(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    path: str = Field(...)
    content: str = Field(default="")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "example.py",
                "path": "app/example.py",
                "content": "import numpy as np\nprint(np.version)\n",
            }
        },
    )
