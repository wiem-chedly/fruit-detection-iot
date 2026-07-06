from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime

# ======================
# MQTT CONFIG
# ======================
BROKER = "a0340c51dae9493c9ca67857a462c5fa.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "wiemchedly"
PASSWORD = "Wiemlovemama123#"

TOPIC_DETECTION = "iot/detection"
TOPIC_COMMAND = "iot/command"

# ======================
# DATABASE (SQLite)
# ======================
conn = sqlite3.connect("iot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objet TEXT,
    confiance REAL,
    received_at TEXT
)
""")
conn.commit()

print("✅ Backend IoT prêt")

# ======================
# MQTT CALLBACKS
# ======================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        # S'abonner aux deux topics
        client.subscribe([(TOPIC_DETECTION, 0), (TOPIC_COMMAND, 0)])
    else:
        print("❌ Erreur connexion MQTT :", rc)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    
    if msg.topic == TOPIC_COMMAND:
        # Afficher la commande dans la console
        device = data.get("device")
        action = data.get("action")

        if device == "door":
            print("🚪 Porte :", action)
        elif device == "alarm":
            print("🚨 Alarme :", action)
        
        # Republier la commande avec retain=True pour qu'elle apparaisse dans HiveMQ
        client.publish(TOPIC_COMMAND, json.dumps(data), retain=True)

# ======================
# MQTT CLIENT
# ======================
mqtt_client = mqtt.Client("IoT_Backend")
mqtt_client.username_pw_set(USERNAME, PASSWORD)
mqtt_client.tls_set()
mqtt_client.tls_insecure_set(True)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT)
mqtt_client.loop_start()

# ======================
# YOLO MODEL
# ======================
model = YOLO("C:/Users/ASUS/Desktop/Projet_IOT_Wiem/yolov8s.pt")

# Classes fruits COCO : 46=banana, 47=apple, 49=orange
FRUIT_CLASSES = [46, 47, 49]

# ======================
# WEBCAM
# ======================
cap = cv2.VideoCapture(0)
print("🎥 Webcam active (appuyez sur Q pour quitter)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if cls_id in FRUIT_CLASSES and conf > 0.6:
                name = model.names[cls_id]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # ======================
                # DRAW BOUNDING BOX
                # ======================
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2)

                # ======================
                # MQTT PUBLISH (détection)
                # ======================
                message = {
                    "objet": name,
                    "confiance": round(conf, 3),
                    "heure": timestamp
                }
                mqtt_client.publish(TOPIC_DETECTION, json.dumps(message), retain=True)

                # ======================
                # DATABASE INSERT
                # ======================
                cursor.execute(
                    "INSERT INTO detections (objet, confiance, received_at) VALUES (?, ?, ?)",
                    (name, round(conf, 3), timestamp)
                )
                conn.commit()

                print("📤 Détection envoyée & enregistrée :", message)

    cv2.imshow("Detection IoT", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ======================
# CLEAN EXIT
# ======================
cap.release()
cv2.destroyAllWindows()
mqtt_client.loop_stop()
mqtt_client.disconnect()
conn.close()

print("🛑 Backend IoT arrêté")
