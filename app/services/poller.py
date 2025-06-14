# app/services/poller.py
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
    
    try:
        for _ in range(1):  # simulate 10 polling rounds (10 mins for interval=60)
            for symbol in symbols:
                print(f"Polling: {symbol}")
                if provider == "yahoo_finance":
                    ticker = yf.Ticker("AAPL")
                    df = ticker.history(period="5d", interval="5m")

                    json_data = {
                        ts.isoformat(): values
                        for ts, values in df.to_dict(orient="index").items()
                    }

                    raw_entry = RawMarketData(
                        symbol=symbol,
                        provider=provider,
                        timestamp=datetime.utcnow(),
                        raw_payload=json_data
                    )
                    db.add(raw_entry)
                    db.commit()
                    db.refresh(raw_entry)
                    for ts, values in json_data.items():
                        price = float(values["Close"])
                        send_to_kafka({
                            "symbol": symbol,
                            "price": price,
                            "timestamp": ts,
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
                        timestamp=datetime.utcnow(),
                        raw_payload=data
                    )

                    # Send individual price points to Kafka
                    time_series = data.get("Time Series (5min)", {})
                    for ts, values in time_series.items():
                        price = float(values["4. close"])
                        send_to_kafka({
                            "symbol": symbol,
                            "price": price,
                            "timestamp": ts,
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
    except Exception as e:
        print("Polling failed:", e)
    finally:
        db.close()
