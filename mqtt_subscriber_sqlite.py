import paho.mqtt.client as mqtt
from datetime import datetime
import json
import sqlite3

# ======================
# MQTT CONFIG
# ======================
broker = "a0340c51dae9493c9ca67857a462c5fa.s1.eu.hivemq.cloud"
port = 8883
username = "wiemchedly"
password = "Wiemlovemama123#"
topic = "iot/detection"

# ======================
# SQLITE DATABASE
# ======================
conn = sqlite3.connect("iot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    objet TEXT,
    confiance REAL,
    received_at TEXT
)
""")
conn.commit()
print("✅ Base SQLite prête")

# ======================
# MQTT CALLBACKS
# ======================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe(topic)
    else:
        print("❌ Erreur connexion MQTT :", rc)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("🔔 Message reçu dans subscriber :", payload)
        data = json.loads(payload)
        timestamp = datetime.utcnow().isoformat()

        cursor.execute(
            "INSERT INTO detections (topic, objet, confiance, received_at) VALUES (?, ?, ?, ?)",
            (
                msg.topic,
                data.get("objet"),
                data.get("confiance"),
                timestamp
            )
        )
        conn.commit()
        print("📦 Donnée enregistrée dans SQLite")
    except Exception as e:
        print("❌ Erreur on_message :", e)

# ======================
# MQTT CLIENT
# ======================
client = mqtt.Client("Subscriber_SQLite")
client.username_pw_set(username, password)
client.tls_set()
client.tls_insecure_set(True)  # important pour HiveMQ Cloud
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port)
client.loop_forever()
