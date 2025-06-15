from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, JSON, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String, index=True)
    provider = Column(String)
    timestamp = Column(DateTime(timezone=True), index=True)  # from the key of time series
    raw_payload = Column(JSON)
    job_id = Column(String, ForeignKey("polling_jobs.job_id"), nullable=True)
