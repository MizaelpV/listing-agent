from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
import datetime



class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meli_id = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    tokens = relationship("UserToken", back_populates="user")


class UserToken(Base):
    __tablename__ = "user_tokens"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id")) 
    provider = Column(String, default="")
    access_token = Column(String, default="")
    refresh_token = Column(String, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="tokens")
