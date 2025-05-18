from pydantic import BaseModel
from typing import Optional


class CreateMessageSchema(BaseModel):
    message: str


class MessageSchema(BaseModel):
    id:int
    username: str
    message: str 

    class Config:
        orm_mode = True


class UpdateMessageSchema(BaseModel):
    message: Optional[str] = None  


class CreateLoginschema(BaseModel):
    username:str
    password:str


class JwtTokenSchema(BaseModel):
    username:str
    message:str