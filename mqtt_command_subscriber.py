import paho.mqtt.client as mqtt
import json

# MQTT CONFIG
broker = "a0340c51dae9493c9ca67857a462c5fa.s1.eu.hivemq.cloud"
port = 8883
username = "wiemchedly"
password = "Wiemlovemama123#"
topic_cmd = "iot/command"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Objet IoT connecté au broker")
        client.subscribe(topic_cmd)
        print("📡 En attente de commandes IoT...")
    else:
        print("❌ Erreur connexion MQTT")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    device = data.get("device")
    action = data.get("action")

    if device == "door":
        if action == "OPEN":
            print("🚪 Porte OUVERTE")
        elif action == "CLOSE":
            print("🔒 Porte FERMÉE")

    if device == "alarm":
        if action == "ON":
            print("🚨 Alarme ACTIVÉE")
        elif action == "OFF":
            print("🔕 Alarme DÉSACTIVÉE")

client = mqtt.Client("IoT_Device")
client.username_pw_set(username, password)
client.tls_set()
client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port)
client.loop_forever()
