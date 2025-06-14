
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.sql import func
from app.models.models import Base

class PollingJob(Base):
    __tablename__ = "polling_jobs"

    job_id = Column(String, primary_key=True)  # e.g., "poll_7691e0"
    status = Column(String, nullable=False)    # e.g., "accepted"
    config = Column(JSON, nullable=False)      # stores symbols, interval, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
