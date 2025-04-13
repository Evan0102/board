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

try:
    CreateMessageSchema(
        username= "阿勳老師",
        message= "我想學python"
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)

try:
    CreateMessageSchema(
        username= 123,
        message= "我想學python"
    )
    print("通過 CreateMessageSchema 測試")
except Exception as error_message:
    print("CreateMessageSchema 錯誤", error_message)