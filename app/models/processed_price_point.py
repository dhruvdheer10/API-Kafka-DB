from sqlalchemy import Column, String, Float, DateTime
from app.db import Base

class ProcessedPricePoint(Base):
    __tablename__ = "processed_price_points"

    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    provider = Column(String, nullable=False)
    raw_response_id = Column(String, nullable=False)