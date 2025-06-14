from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Interval
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

from app.models.base import Base


# 1. Raw Market Data Responses
class RawMarketData(Base):
    __tablename__ = "raw_market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String, index=True)
    provider = Column(String)
    timestamp = Column(DateTime, index=True)  # from the key of time series
    raw_payload = Column(JSON)


# 2. Processed Price Points
# class PricePoint(Base):
#     __tablename__ = "price_points"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String, index=True)
#     provider = Column(String)
#     price = Column(Float)
#     timestamp = Column(DateTime, index=True)
#     raw_response_id = Column(UUID(as_uuid=True))

# # 3. Moving Averages
# class MovingAverage(Base):
#     __tablename__ = "moving_averages"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String, index=True)
#     provider = Column(String)
#     interval = Column(Integer)  # e.g., 5-point average
#     avg_price = Column(Float)
#     timestamp = Column(DateTime, index=True)

# # 4. Polling Job Configs
# class PollingJob(Base):
#     __tablename__ = "polling_jobs"

#     job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     symbols = Column(JSON)  # list of symbols
#     interval = Column(Integer)  # seconds
#     provider = Column(String)
#     started_at = Column(DateTime, default=func.now())
#     duration = Column(Integer)  # optional: how long to poll (seconds)
