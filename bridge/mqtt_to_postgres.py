import os
import json
import time
import psycopg2
import paho.mqtt.client as mqtt

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_USER = os.environ["MQTT_USER"]
MQTT_PASS = os.environ["MQTT_PASSWORD"]
MQTT_TOPIC = "esp32/dht11/home"

# Connect to TimescaleDB
conn = None
while conn is None:
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
        print("Connected to TimescaleDB.")
    except Exception as e:
        print("Waiting for TimescaleDB to be ready...", e)
        time.sleep(5)

cur = conn.cursor()

def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT connected with result code:", rc)
    if rc == 0:
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic '{MQTT_TOPIC}'")
    else:
        print("Failed to connect, return code:", rc)

def on_message(client, userdata, msg):
    print("MQTT message received:", msg.topic, msg.payload.decode())
    try:
        data = json.loads(msg.payload.decode())
        temp = data.get("temperature")
        hum = data.get("humidity")
        cur.execute(
            "INSERT INTO dht11_readings (time, temperature, humidity) VALUES (NOW(), %s, %s)",
            (temp, hum),
        )
        conn.commit()
        print(f"Inserted → Temp={temp}, Hum={hum}")
    except Exception as e:
        print("Insert error:", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
print("Starting MQTT loop...")
client.loop_forever()