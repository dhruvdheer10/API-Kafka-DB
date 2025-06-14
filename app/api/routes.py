from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.models import RawMarketData
from app.db import SessionLocal
import requests
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, BackgroundTasks
from app.schemas.poll_request import PollRequest
from app.services.poller import poll_prices
from app.models.processed_price_point import ProcessedPricePoint
from fastapi import Query
import uuid


router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/prices/poll", status_code=202)
def poll_market_data(payload: PollRequest, background_tasks: BackgroundTasks):
    job_id = f"poll_{uuid.uuid4().hex[:6]}"
    background_tasks.add_task(poll_prices, payload.symbols, payload.interval, payload.provider, job_id)
    return {
        "job_id": job_id,
        "status": "accepted",
        "config": {
            "symbols": payload.symbols,
            "interval": payload.interval
        }
    }

@router.get("/prices/latest")
def get_latest_price(
    symbol: str = Query(...),
    provider: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ProcessedPricePoint).filter(ProcessedPricePoint.symbol == symbol)

    if provider:
        query = query.filter(ProcessedPricePoint.provider == provider)

    latest = query.order_by(ProcessedPricePoint.timestamp.desc()).first()

    if not latest:
        return {"error": "No data found"}

    return {
        "symbol": latest.symbol,
        "price": latest.price,
        "timestamp": latest.timestamp.isoformat(),
        "provider": latest.provider
    }
