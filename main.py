import secrets

from jwt import encode, decode, PyJWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.security import APIKeyHeader  
from sqlalchemy.orm import Session
from src.schemas import CreateMessageSchema, UpdateMessageSchema, MessageSchema, CreateLoginSchema, JwtTokenSchema, UserSchema
from src.database import Base, engine, SessionLocal
from src.models import User, Message
from typing import List, Optional

app = FastAPI()


# 創建已經定義的資料表
Base.metadata.create_all(bind=engine)


# 密碼加密（Hashing）
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT Token 的加密與解密
SECRET_KEY = secrets.token_urlsafe(32)  # 32 位元的隨機字串（動態產生）
ALGORITHM = "HS256"  # JWT 的加密演算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access Token 的有效時間（分鐘）
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Refresh Token 的有效時間（分鐘）（7 天）
# OAuth2 的 Bearer Token
oauth2_scheme = APIKeyHeader(name="Authorization")  

# 取得資料庫的 Session 會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# 產生 JWT Token
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
   
# 驗證 JWT Token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="無效的 Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 修正：自動去除 Bearer 前綴
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

   
# 註冊 API
@app.post("/register", response_model=UserSchema)
def register(body: CreateLoginSchema, db: Session = Depends(get_db)):
    # 檢查使用者是否已存在
    user = db.query(User).filter(User.username == body.username).first()
    if user:
        raise HTTPException(status_code=400, detail="使用者已存在")
    # 建立新使用者
    hashed_pw = hash_password(body.password)
    new_user = User(username=body.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 登入 API
@app.post("/login", response_model=JwtTokenSchema)
def login(body: CreateLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access": access_token, "refresh": refresh_token}

# refresh token API
@app.post("/refresh", response_model=JwtTokenSchema)
def refresh_token(refresh: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="無效的 Refresh Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(refresh, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access": access_token, "refresh": refresh_token}


@app.post(
    "/message",
    response_model=MessageSchema
)
async def create_message(
    body: CreateMessageSchema, 
    
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_message = Message(    
        username = body.current_user.username,
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
# 取得單一的留言（需登入）
    "/message/{message_id}",
    response_model=MessageSchema
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
    if body.message:
        messages.message = body.message
    db.commit()
    db.refresh(messages)
    return messages