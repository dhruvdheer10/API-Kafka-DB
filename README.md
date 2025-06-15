
# BlockHouse Documentation

## 1. Overview

This microservice fetches real-time stock price data from external APIs (Yahoo Finance, AlphaVantage), processes the data using Kafka, and stores it in PostgreSQL. The service exposes APIs via FastAPI, with support for background polling jobs and retrieval of the latest prices.

NOTE: I have added pgadmin in the Dockerfile as well, for users to see the data that they are inserting in the tables with every poll.

**Tech Stack:**
- FastAPI
- Kafka + Zookeeper
- PostgreSQL
- Docker + Docker Compose
- SQLAlchemy ORM

---

## 2. Setup Instructions

### Environment File (`.env`)
```env
DATABASE_URL=postgresql://nadkar:password@postgres_db:5432/market_data_db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
API_KEY=your_alpha_vantage_api_key
KAFKA_GROUP_ID=price-consumer-group
KAFKA_TOPIC_NAME=price-events
YAHOO_FINANCE=yahoo_finance
ALPHA_VANTAGE=alpha_vantage
ALPHA_VANTAGE_URL=https://www.alphavantage.co/query
```

### To Start the System
```bash
docker-compose up --build
```

---

## 3. API Documentation

### POST `/prices/poll`
Starts polling job in the background.

**Request Body**
```json
{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "alpha_vantage"
}
```

**Response (202 Accepted)**
```json
{
  "job_id": "poll_123",
  "status": "accepted",
  "config": {
    "symbols": ["AAPL", "MSFT"],
    "interval": 60
  }
}
```

---

### GET `/prices/latest?symbol=AAPL&provider=alpha_vantage`

**Response**
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": "2024-03-20T10:30:00Z",
  "provider": "alpha_vantage"
}
```

---

## 4. Architecture Decisions

- **Kafka**: Used as the message broker between polling jobs and consumer services.
- **Database**: PostgreSQL schema includes:
  - `raw_market_data`: Raw JSON response from APIs
  - `processed_price_points`: Flattened price values
  - `symbol_averages`: Moving 5-point average
  - `polling_jobs`: Job tracking
- **Indexing**: Applied on `(symbol, timestamp)` to avoid duplicate inserts.
- **Foreign Key Constraints**: Tables `raw_market_data`, `processed_price_points`, and `polling_jobs` are linked using foreign key relationships to maintain referential integrity and better traceability across the data pipeline.


---

## 5. Local Development

- Add `load_dotenv()` to the beginning of `main.py` and other scripts to load env vars.
- Use `.env` to avoid hardcoded values.
- Restart containers after DB schema changes:  
```bash
docker-compose down && docker-compose up --build
```

### To Run the Kafka Consumer
```bash
python3 -m app.services.kafka_consumer
```

---

## 6. Troubleshooting Tips

- **Cannot connect to Kafka**: Ensure you're using `kafka:9092` inside Docker or `localhost:9092` from the host.
- **Tables not visible**: Ensure `Base.metadata.create_all()` is being called and the DB URL is correct.
- **API call only polling once**: Confirm `interval` is respected and loops aren't broken due to API failure or rate limits

---

## 7. Challenges Faced

- Understanding polling and background job flow
- Kafka broker issues and incorrect advertised listeners
- Tables not reflecting in pgAdmin despite being in psql
- Rate limits of AlphaVantage API
- Indexing silently avoiding inserts
- Kafka consumer crashing due to unresolved environment setup
- Delay in job visibility due to asynchronous operations
- Getting rate limited (25 requests/day for AlphaVantage)

---

## 8. Useful Commands

```bash
docker-compose up --build                 # Start all services
docker-compose down                       # Stop all services
docker exec -it postgres_db bash          # Enter DB container
psql -U nadkar -d market_data_db          # Open psql CLI
python3 -m app.services.kafka_consumer    # Run Kafka consumer
git fetch --all                           # Fetch latest branches
git branch                                # Check current branch
```

### Kafka Topic Management
```bash
docker exec -it market-data-service-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
docker exec -it market-data-service-kafka-1 kafka-topics --bootstrap-server localhost:9092 --delete --topic price-events
docker exec -it market-data-service-kafka-1 kafka-topics --bootstrap-server localhost:9092 --create --topic price-events --partitions 1 --replication-factor 1
```
