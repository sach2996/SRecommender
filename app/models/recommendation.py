from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from datetime import datetime

class Recommendation(Base):
    __tablename__ = "recommendations" 

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    strategy = Column(String, index=True)
    buy = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)
    date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
