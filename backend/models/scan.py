from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url_hash = Column(Text, nullable=False)
    verdict = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    ip_hash = Column(Text, nullable=False)
    scanned_at = Column(DateTime, server_default=func.now())
