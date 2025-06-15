import os
from confluent_kafka import Producer
import json

kafka_port = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
print("Kafka bootstrap:", os.getenv("KAFKA_BOOTSTRAP_SERVERS"))

producer = Producer({'bootstrap.servers': kafka_port})

def send_to_kafka(message: dict):
    print(f"Inside kafka producer with message: {message}")
    producer.produce(
        "price-events",
        key=message["symbol"],
        value=json.dumps(message),
    )
    producer.flush()
