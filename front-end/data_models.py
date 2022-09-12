from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4


class UserData(BaseModel):
    user_id: Optional[str] = Field(default_factory=lambda: uuid4().__str__())
    name: str
    age: float
    sex: str


class ResponseData(UserData):
    response: str
