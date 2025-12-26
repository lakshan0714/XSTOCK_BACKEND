from datetime import datetime, timedelta,timezone
from sqlalchemy import Enum as SqlEnum
from src.config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.schemas.user_schema import UserRole


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SqlEnum(UserRole, name="userrole", create_type=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sessions =relationship("Session", back_populates="user", cascade="all, delete-orphan")
    



class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_mail = Column(String(100),ForeignKey('users.email', ondelete='CASCADE'), nullable=False)
    session_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    user = relationship("User", back_populates="sessions")
