from sqlalchemy import Column, Integer, String
from src.database import Base


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, idnex=True)
    message = Column(String)