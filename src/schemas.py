from pydantic import BaseModel
from typing import Optional


class CreateMessageSchema(BaseModel):
    username: str
    message: str


class MessageSchema(BaseModel):
    id:int
    username: str
    message: str 


class UpdateMessageSchema(BaseModel):
    username: Optional[str] = None
    message: Optional[str] = None  