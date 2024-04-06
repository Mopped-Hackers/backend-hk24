from pydantic import BaseModel, Field
from typing import List, Union


# BASE MODELS
###################################################
class AI_input_1(BaseModel):
    """
    Base AI Model
    """

    model: str = Field(default="julie", title="Default_1", max_length=20)
    limit: int = Field(default=5, gt=0, description="Default_2")
    similar: bool = Field(default=1, description="Default_3")
