import json
from confluent_kafka import Consumer, Producer
from datetime import datetime
import uuid

# Configuration du consommateur
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'processeur-anomalies',  # Identifiant de ton groupe de consommateurs
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(**consumer_conf)
consumer.subscribe(['donnees-machines'])

# Configuration du producteur (pour envoyer les alertes)
producer_conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(**producer_conf)

alert_topic = 'alertes-pannes'
print("Le processeur de streaming est prêt...")

try:
    while True:
        msg = consumer.poll(1.0)  # Attendre 1 seconde pour un message

        if msg is None:
            continue
        if msg.error():
            print(f"Erreur de consommation : {msg.error()}")
            continue

        # Décoder le message
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Donnée reçue : {data}")

        # --- LOGIQUE DE TRAITEMENT ---
        temperature = data.get('temperature', 0)
        pression = data.get('pressure', 0)

        if temperature > 90.0:
            # Générer un ID unique pour le message d'alerte
            alert_id = f"alert_{data.get('machine_id', 'unknown')}_{str(uuid.uuid4())[:8]}"

            alerte = {
                'alert_id': alert_id,
                'type': 'CRITIQUE',
                'message': f"Température critique détectée : {temperature}°C",
                'alert_sent_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': data
            }

            # Produire l'alerte avec une clé (ID du message) dans un nouveau topic
            producer.produce(
                alert_topic,
                key=alert_id,  # Utiliser l'ID comme clé du message
                value=json.dumps(alerte)
            )
            print(f"ALERTE ENVOYÉE avec ID {alert_id} : {alerte}")
            producer.flush()

finally:
    consumer.close()
