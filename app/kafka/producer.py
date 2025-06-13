from confluent_kafka import Producer
import json

producer = Producer({'bootstrap.servers': 'localhost:9092'})

def send_to_kafka(message: dict):
    producer.produce(
        "price-events",
        key=message["symbol"],
        value=json.dumps(message),
    )
    producer.flush()
