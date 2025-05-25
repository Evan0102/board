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


class UserSchema(BaseModel):
    id:int
    username:str
    password:str

    class Config:
        orm_mode = True


class CreateLoginSchema(BaseModel):
    username:str
    password:str


class JwtTokenSchema(BaseModel):
    access:str
    refresh:str