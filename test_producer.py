# from confluent_kafka import Producer
# import json

# p = Producer({'bootstrap.servers': 'localhost:9092'})

# def delivery_report(err, msg):
#     if err:
#         print(f'❌ Delivery failed: {err}')
#     else:
#         print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}]')

# sample_message = {
#     "symbol": "AAPL",
#     "price": 150.25,
#     "timestamp": "2025-06-12T10:30:00Z",
#     "source": "alpha_vantage",
#     "raw_response_id": "test-uuid-123"
# }

# p.produce(
#     topic="price-events",
#     key=sample_message["symbol"],
#     value=json.dumps(sample_message),
#     callback=delivery_report
# )

# p.flush()
