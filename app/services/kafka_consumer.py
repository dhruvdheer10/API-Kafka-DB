from confluent_kafka import Consumer
from collections import defaultdict, deque
from app.db import SessionLocal
from app.models.processed_price_point import ProcessedPricePoint
from app.models.symbol_average import SymbolAverage
import json
import uuid
from datetime import datetime

# Keep track of recent prices
price_buffer = defaultdict(lambda: deque(maxlen=5))

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'price-consumer-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['price-events'])

print("📡 Kafka consumer running...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue

        data = json.loads(msg.value().decode('utf-8'))
        symbol = data["symbol"]
        price = data["price"]
        timestamp = datetime.fromisoformat(data["timestamp"])
        provider = data["source"]
        raw_response_id = data["raw_response_id"]

        session = SessionLocal()

        # Store raw price point
        pp = ProcessedPricePoint(
            id=str(uuid.uuid4()),
            symbol=symbol,
            price=price,
            timestamp=timestamp,
            provider=provider,
            raw_response_id=raw_response_id
        )
        session.add(pp)

        # Update buffer and calculate average
        price_buffer[symbol].append(price)
        if len(price_buffer[symbol]) == 5:
            avg = sum(price_buffer[symbol]) / 5
            existing = session.get(SymbolAverage, symbol)
            if existing:
                existing.average_price = avg
            else:
                session.add(SymbolAverage(symbol=symbol, average_price=avg))

        session.commit()
        session.close()

except KeyboardInterrupt:
    print("🛑 Consumer stopped")
finally:
    consumer.close()
