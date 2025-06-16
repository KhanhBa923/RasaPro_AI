# watch_events.py
import pika
import json
import sys

def callback(ch, method, properties, body):
    event = json.loads(body)
    print(f"📨 Event: {event.get('event', 'unknown')}")
    if event.get('event') == 'user':
        print(f"   👤 User said: {event.get('text', '')}")
    elif event.get('event') == 'bot':
        print(f"   🤖 Bot replied: {event.get('text', '')}")
    print(f"   📝 Full event: {json.dumps(event, indent=2)}")
    print("-" * 50)

# Kết nối RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Tạo queue nếu chưa có
channel.queue_declare(queue='rasa_core_events', durable=True)

print("🔄 Đang chờ events từ Rasa...")
print("Để thoát, nhấn CTRL+C")

channel.basic_consume(
    queue='rasa_core_events',
    on_message_callback=callback,
    auto_ack=True
)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n👋 Đang thoát...")
    channel.stop_consuming()
    connection.close()
    sys.exit(0)