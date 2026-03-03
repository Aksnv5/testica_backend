from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    testsCompleted = Column(Integer)
    totalTimeSpent = Column(Integer)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    is_admin = Column(Boolean, default=False)

    sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, nullable=False)  # store token jti or whole token
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
