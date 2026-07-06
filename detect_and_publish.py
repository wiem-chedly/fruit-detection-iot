from ultralytics import YOLO
import cv2
import paho.mqtt.client as mqtt
from datetime import datetime
import json


# MQTT

broker = "a0340c51dae9493c9ca67857a462c5fa.s1.eu.hivemq.cloud"
port = 8883
username = "wiemchedly"
password = "Wiemlovemama123#"
topic = "iot/detection"

mqtt_client = mqtt.Client(client_id="YOLO_Publisher_PC", clean_session=True)
mqtt_client.username_pw_set(username, password)
mqtt_client.tls_set()
mqtt_client.tls_insecure_set(True)  # important
mqtt_client.connect(broker, port)

# YOLO

model = YOLO("C:/Users/ASUS/Desktop/Projet_IOT_Wiem/yolov8s.pt")
FRUIT_CLASSES = [46, 47, 49]  # banana, apple, orange


# Webcam

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Webcam non détectée")
    exit()

print("🎥 Webcam active – Détection en cours...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True, verbose=False)

    for r in results:
        fruit_boxes = [box for box in r.boxes if int(box.cls[0]) in FRUIT_CLASSES and float(box.conf[0]) > 0.6]

        for box in fruit_boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls_id]

            message = {
                "objet": name,
                "confiance": round(conf, 3),
                "heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            mqtt_client.publish(topic, json.dumps(message))
            print("📤 Message MQTT envoyé :", message)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} {conf:.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("🍌 Détection Fruits uniquement 🍎", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
mqtt_client.disconnect()
print("🛑 Arrêt du programme")
