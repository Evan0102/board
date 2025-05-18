import secrets
from jwt import encode, decode, PyJWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import FastAPI,Depends,HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema,MessageSchema,UpdateMessageSchema
from src.database import Base, engine, SessionLocal
from src.models import Message, User
from typing import List, Optional
app = FastAPI()


Base.metadata.create_all(bind=engine)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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

def hash_password(password: str) -> str:
    return password_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="無效的 Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 檢查 Token 是否有效
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    # 檢查使用者是否存在
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


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