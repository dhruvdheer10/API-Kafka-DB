
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class PollingJob(Base):
    __tablename__ = "polling_jobs"

    job_id = Column(String, primary_key=True)  
    status = Column(String, nullable=False)    
    config = Column(JSON, nullable=False)      
    created_at = Column(DateTime(timezone=False), server_default=func.now())
