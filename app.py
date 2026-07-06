import streamlit as st
import sqlite3
import paho.mqtt.client as mqtt
import json
import pandas as pd

# CONFIG PAGE

st.set_page_config(
    page_title="Plateforme IoT – Détection Fruits",
    page_icon="🍎",
    layout="wide"
)


# STYLE CSS 

st.markdown("""
<style>

/* TITRE PRINCIPAL */
.main-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 5px;
}

/* SOUS TITRES */
.section-title {
    font-size: 23px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* CARTES STATISTIQUES */
.stat-card {
    background-color: #f7f7f7;
    padding: 12px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.stat-card h3 {
    font-size: 16px;
    margin-bottom: 5px;
}

.stat-card h1 {
    font-size: 22px;
    margin: 0;
}

/* TABLEAU */
[data-testid="stDataFrame"] {
    max-width: 75%;
    margin: auto;
}

/* BOUTONS */
.stButton > button {
    padding: 8px 12px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# TITRE

st.markdown("<div class='main-title'>🍌🍎 Plateforme IoT – Détection de Fruits</div>", unsafe_allow_html=True)
st.caption("Surveillance en temps réel & commandes IoT")
st.divider()


# MQTT (COMMANDES)

broker = "a0340c51dae9493c9ca67857a462c5fa.s1.eu.hivemq.cloud"
port = 8883
username = "wiemchedly"
password = "Wiemlovemama123#"
topic_cmd = "iot/command"

mqtt_client = mqtt.Client("Streamlit_CMD")
mqtt_client.username_pw_set(username, password)
mqtt_client.tls_set()
mqtt_client.tls_insecure_set(True)
mqtt_client.connect(broker, port)

# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect("iot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
SELECT objet, confiance, received_at
FROM detections
ORDER BY received_at DESC
""")
rows = cursor.fetchall()

df = pd.DataFrame(rows, columns=["Objet", "Confiance", "Date & Heure"])

# =====================================================
# STATISTIQUES
# =====================================================
st.markdown("<div class='section-title'>📊 Statistiques</div>", unsafe_allow_html=True)

if not df.empty:
    stats = df["Objet"].value_counts()
    cols = st.columns(len(stats))

    for col, (obj, count) in zip(cols, stats.items()):
        with col:
            st.markdown(f"""
                <div class="stat-card">
                    <h3>{obj}</h3>
                    <h1>{count}</h1>
                    <p>détections</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Aucune donnée disponible")

st.divider()

# =====================================================
# DERNIÈRES DÉTECTIONS
# =====================================================
st.markdown("<div class='section-title'>📋 Dernières détections</div>", unsafe_allow_html=True)

if not df.empty:
    st.dataframe(df.head(10), use_container_width=False)
else:
    st.warning("Pas encore de détection")

st.divider()

# =====================================================
# COMMANDES IoT
# =====================================================
st.markdown("<div class='section-title'>🎛️ Commandes IoT</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("🚪 Ouvrir la porte"):
        mqtt_client.publish(
            topic_cmd,
            json.dumps({"device": "door", "action": "OPEN"})
        )
        st.success("Commande envoyée : OUVRIR la porte")

    if st.button("🔒 Fermer la porte"):
        mqtt_client.publish(
            topic_cmd,
            json.dumps({"device": "door", "action": "CLOSE"})
        )
        st.success("Commande envoyée : FERMER la porte")

with col2:
    if st.button("🚨 Activer l’alarme"):
        mqtt_client.publish(
            topic_cmd,
            json.dumps({"device": "alarm", "action": "ON"})
        )
        st.success("Commande envoyée : ALARME ACTIVÉE")

    if st.button("🔕 Désactiver l’alarme"):
        mqtt_client.publish(
            topic_cmd,
            json.dumps({"device": "alarm", "action": "OFF"})
        )
        st.success("Commande envoyée : ALARME DÉSACTIVÉE")


st.divider()
st.caption("📡 Projet IoT – YOLO • MQTT • SQLite • Streamlit")
