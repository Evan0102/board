from sqlalchemy import Column, Integer, String
from src.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    message = Column(String)