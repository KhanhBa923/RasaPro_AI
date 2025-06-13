from kafka import KafkaConsumer
import json
import oracledb  
import requests

# Kết nối DB
conn = oracledb.connect(
    user="C##TEST",
    password="test",
    dsn="localhost:1521/ORCLCDB"
)
cursor = conn.cursor()

# Kết nối Kafka consumer
consumer = KafkaConsumer(
    'chat_topic',                      # tên topic Kafka
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
)

print("Listening for messages...")

for message in consumer:
    try:
        user_message = message.value.get("message")
        print(f"\n📩 Received message: {user_message}")

        # Gửi message tới Rasa để phân tích intent
        response = requests.post(
            "http://localhost:5005/model/parse",
            json={"text": user_message}
        )
        intent_name = "intent_test"
        print(f"✅ Detected intent: {intent_name}")

        # Lưu vào Oracle DB
        cursor.execute("""
            INSERT INTO chat_logs (message_text, intent_name)
            VALUES (:msg, :intent)
        """, msg=user_message, intent=intent_name)
        conn.commit()
        print("💾 Saved to Oracle DB.")

    except Exception as e:
        print(f"❌ Error: {e}")
