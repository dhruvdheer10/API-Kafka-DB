# app/services/poller.py
from zoneinfo import ZoneInfo
import requests
import time
import uuid
import threading
from app.models.models import RawMarketData
from app.models.polling_job import PollingJob
from app.kafka.producer import send_to_kafka
from app.db import SessionLocal
from datetime import datetime
import yfinance as yf

API_KEY = "B2MYYTYG9G64B7AJ"

def poll_prices(symbols, interval, provider, job_id):
    db = SessionLocal()
    raw_entry_ids = []
    try:
        for _ in range(1):  # simulate 10 polling rounds (10 mins for interval=60)
            for symbol in symbols:
                print(f"Polling: {symbol}")
                if provider == "yahoo_finance":
                    ticker = yf.Ticker("AAPL")
                    df = ticker.history(period="1d", interval="5m")

                    json_data = {
                        ts.isoformat(): values
                        for ts, values in df.to_dict(orient="index").items()
                    }

                    raw_entry = RawMarketData(
                        symbol=symbol,
                        provider=provider,
                        timestamp=datetime.now(),
                        # job_id=job_id,
                        raw_payload=json_data
                    )
                    db.add(raw_entry)
                    db.commit()
                    db.refresh(raw_entry)
                    raw_entry_ids.append(raw_entry.id)
                    for ts, values in json_data.items():
                        price = float(values["Close"])
                        utc_time = datetime.fromisoformat(ts)
                        la_time = utc_time.astimezone(ZoneInfo("America/Los_Angeles"))
                        send_to_kafka({
                            "symbol": symbol,
                            "price": price,
                            "timestamp": la_time.isoformat(),
                            "source": provider,
                            "raw_response_id": str(raw_entry.id)
    })
                    
                if provider == "alpha_vantage":

                #ALPHA VANTAGE API
                # Uncomment the following lines to use Alpha Vantage API

                    url = "https://www.alphavantage.co/query"
                    params = {
                        "function": "TIME_SERIES_INTRADAY",
                        "symbol": symbol,
                        "interval": "5min",
                        "apikey": API_KEY
                    }
                    response = requests.get(url, params=params)
                    data = response.json()
                    raw_entry = RawMarketData(
                        symbol=symbol,
                        provider=provider,
                        timestamp=datetime.now(),
                        # job_id=job_id,
                        raw_payload=data
                    )
                    db.add(raw_entry)
                    db.commit()
                    db.refresh(raw_entry)
                    # Send individual price points to Kafka
                    raw_entry_ids.append(raw_entry.id)
                    time_series = data.get("Time Series (5min)", {})
                    for ts, values in time_series.items():
                        price = float(values["4. close"])
                        utc_time = datetime.fromisoformat(ts)
                        la_time = utc_time.astimezone(ZoneInfo("America/Los_Angeles"))
                        send_to_kafka({
                            "symbol": symbol,
                            "price": price,
                            "timestamp": la_time.isoformat(),
                            "source": provider,
                            "raw_response_id": str(raw_entry.id)
                        })
            time.sleep(interval)
        config = {
            "symbols": symbols,
            "interval": interval
        }
        polling_job = PollingJob(
            job_id=job_id,
            status="accepted",
            config=config
        )
        db.add(polling_job)
        db.commit()

        db.query(RawMarketData).filter(RawMarketData.id.in_(raw_entry_ids)).update(
            {RawMarketData.job_id: job_id}, synchronize_session=False
        )
        db.commit()
    except Exception as e:
        print("Polling failed:", e)
    finally:
        db.close()
