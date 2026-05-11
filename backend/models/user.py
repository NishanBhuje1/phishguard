from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    totp_secret = Column(Text, nullable=False)
    role = Column(Text, default="user")
    created_at = Column(DateTime, server_default=func.now())
