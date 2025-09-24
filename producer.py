import time
import json
import random
from confluent_kafka import Producer

# Configuration du producteur
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(**conf)

topic = 'donnees-machines'

print("Le producteur est prêt...")
while True:
    # Simuler des données de machine
    data = {
        'machine_id': 'machine-01',
        'temperature': round(random.uniform(70.0, 95.0), 2),  # Température normale + pics
        'pressure': round(random.uniform(1000, 1500), 2),
        'timestamp': time.time()
    }

    # Envoyer le message au format JSON
    producer.produce(topic, key=data['machine_id'], value=json.dumps(data))
    print(f"Envoi des données : {data}")

    producer.flush()  # S'assurer que le message est bien envoyé
    time.sleep(2)  # Envoyer des données toutes les 2 secondes
