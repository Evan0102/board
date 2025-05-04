from fastapi import FastAPI,Depends,HTTPException, Response
import pandas as pd
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema,MessageSchema,UpdateMessageSchema
from src.database import Base, engine, SessionLocal
from src.models import Message
from typing import List
app = FastAPI()


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/message",
    response_model=MessageSchema
)
async def create_message(body: CreateMessageSchema, db: Session = Depends(get_db)):
    new_message = Message(    
        username = body.username,
        message = body.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.get(
    "/message/{message_id}",
    response_model=MessageSchema
)
def get_message(message_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.id == message_id).first()
    if not messages:
        raise HTTPException(status_code=404, detail="找不到訊息")
    return messages


@app.get(
    "/messages",
    response_model=list[MessageSchema]
)
def get_all_messages(db:Session = Depends(get_db)):
    # 1. 讀取現有的留言(get or not)
    messages = db.query(Message).all()
    # 2. 回傳留言
    return messages


@app.delete(
    "/message/{message_id}",
)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.id == message_id).first()
    if not messages:
            raise HTTPException(status_code=204, detail="刪除成功")
    db.delete(messages)
    db.commit()
    return Response(status_code=204)


@app.patch(
    "/message/{message_id}",
    response_model=MessageSchema
)
def update_message(message_id: int, body: UpdateMessageSchema, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.id == message_id).first()
    if not messages:
        raise HTTPException(status_code=404, detail="找不到訊息")
    if body.username:
        messages.username = body.username
    if body.message:
        messages.message = body.message
    db.commit()
    db.refresh(messages)
    return messages