import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="rasa_events", durable=True)

message = json.dumps({"event": "test", "text": "Hello from test!"})
channel.basic_publish(exchange='', routing_key='rasa_events', body=message)
print("✅ Test message sent.")

connection.close()