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
import uuid


router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/fetch-price")
def fetch_and_store_raw(symbol: str = "AAPL", db: Session = Depends(get_db)):
    API_KEY = "B2MYYTYG9G64B7AJ"
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    time_series = data.get("Time Series (5min)", {})
    if not time_series:
        return {"error": "No time series data found"}

    entry = RawMarketData(
        symbol=symbol,
        provider="alpha_vantage",
        timestamp=datetime.now(),
        raw_payload=(data)
    )
    db.add(entry)

    db.commit()
    print(entry)

    return JSONResponse(content=jsonable_encoder(entry))



# router = APIRouter()

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
