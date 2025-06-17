
# Market Data Service Documentation

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

1. Make sure **Docker Desktop** is installed and running on your machine.


   ```bash
   git clone https://github.com/dhruvdheer10/API-Kafka-DB.git
   cd API-Kafka-DB
   ```


   ```bash
   docker-compose up --build
   ```

2. Check Docker Desktop: you should see **5 running containers** (API, DB, Kafka, Zookeeper, pgAdmin)


3. Open Swagger UI in your browser:
   [http://localhost:8000/docs#/](http://localhost:8000/docs#/)

4. Use the `POST /poll/prices` endpoint with the following payload:
   ```json
   {
     "symbols": ["AAPL", "MSFT"],
     "interval": 30,
     "provider": "alpha_vantage"
   }
   ```


5. Open pgAdmin:
   [http://localhost:5050/login?next=/](http://localhost:5050/login?next=/)

6. Login credentials (from `docker-compose.yml`):
   - **Email**: `admin@example.com`
   - **Password**: `admin`

7. Register a new server:
   - **General Tab**:
     - Name: *Anything*
   - **Connection Tab**:
     - Host name/address: `db`
     - Username: `nadkar` (from `POSTGRES_USER`)
     - Password: `password` (from `POSTGRES_PASSWORD`)

8. Navigate to the `market_data_db` database → **Schemas → Tables**, and you should see:
    - `polling_jobs`
    - `raw_market_data`
    - `processed_price_points`
    - `symbol_averages`


9. In a terminal, run:
   ```bash
   docker exec -it fastapi_app python3 -m app.services.kafka_consumer
   ```

10. This consumer will:
   - Read messages from Kafka
   - Insert entries into:
     - `processed_price_points`
     - `symbol_averages`

After running the polling endpoint and consumer, all four tables will be populated. You can inspect them directly via **pgAdmin**.

---

### 3. API Documentation

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
- **Indexing**: Applied on `(symbol, timestamp)`
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
- **API call only polling once**: Confirm `interval` is respected and loops aren't broken due to API failure or rate limits.

---

## 7. Challenges Faced

- Understanding polling and background job flow
- Kafka broker issues and incorrect advertised listeners
- Tables not reflecting in pgAdmin despite being in psql
- Rate limits of AlphaVantage API
- Indexing silently avoiding inserts
- Kafka consumer crashing due to unresolved environment setup
- Delay in job visibility due to asynchronous operations

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
