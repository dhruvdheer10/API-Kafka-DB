from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class SymbolAverage(Base):
    __tablename__ = "symbol_averages"

    symbol = Column(String, primary_key=True)
    average_price = Column(Float, nullable=False)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
