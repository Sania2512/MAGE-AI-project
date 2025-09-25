import time
import json
import random
from confluent_kafka import Producer
from datetime import datetime

# Configuration du producteur
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(**conf)

topic = 'donnees-machines'

# Variables pour stocker les dernières valeurs des capteurs
current_data = {
    'machine_id': 'machine-01',
    'temperature': 0,
    'pressure': 0,
    'vitesse': 0,
    'timestamp': time.time()
}

# Variables pour gérer les intervalles de mise à jour
last_temp_update = 0
last_pressure_update = 0
last_vitesse_update = 0

# Intervalles de mise à jour (en secondes)
TEMP_INTERVAL = 10
PRESSURE_INTERVAL = 15
VITESSE_INTERVAL = 20
SEND_INTERVAL = 5

# Durées du cycle (en secondes)
ACTIVE_DURATION = 5 * 60  # 5 minutes
PAUSE_DURATION = 1 * 60  # 1 minute


def update_temperature():
    """Met à jour la température avec des valeurs réalistes (60-80°C)"""
    # Génère des valeurs entre 60 et 80°C avec plus de précision
    base_temp = random.uniform(60.0, 98.0)
    # Ajoute des variations plus fines comme dans vos données
    return round(base_temp + random.uniform(-2.0, 2.0), 14)


def update_pressure():
    """Met à jour la pression avec des valeurs réalistes (3-5 bar)"""
    # Génère des valeurs entre 3 et 5 bar avec haute précision
    base_pressure = random.uniform(3.0, 5.0)
    return round(base_pressure + random.uniform(-0.5, 0.5), 14)


def update_vitesse():
    """Met à jour la vitesse avec des valeurs réalistes (600-1200 rpm)"""
    # Génère des valeurs entre 600 et 1200 rpm avec haute précision
    base_vitesse = random.uniform(600.0, 1200.0)
    return round(base_vitesse + random.uniform(-100.0, 100.0), 14)


print("Le producteur est prêt...")

while True:
    cycle_start = time.time()

    # Phase active : 5 minutes d'envoi de données
    print(f"=== Début de la phase active (5 minutes) ===")

    while time.time() - cycle_start < ACTIVE_DURATION:
        current_time = time.time()

        # Mise à jour de la température toutes les 10 secondes
        if current_time - last_temp_update >= TEMP_INTERVAL:
            current_data['temperature'] = update_temperature()
            last_temp_update = current_time
            print(f"Nouvelle température: {current_data['temperature']}°C")

        # Mise à jour de la pression toutes les 15 secondes
        if current_time - last_pressure_update >= PRESSURE_INTERVAL:
            current_data['pressure'] = update_pressure()
            last_pressure_update = current_time
            print(f"Nouvelle pression: {current_data['pressure']} bar")

        # Mise à jour de la vitesse toutes les 20 secondes
        if current_time - last_vitesse_update >= VITESSE_INTERVAL:
            current_data['vitesse'] = update_vitesse()
            last_vitesse_update = current_time
            print(f"Nouvelle vitesse: {current_data['vitesse']} rpm")

        # Mise à jour du timestamp et envoi du message
        current_data['timestamp'] = datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S.%f')

        # Envoyer le message avec les dernières valeurs disponibles
        producer.produce(topic, key=current_data['machine_id'], value=json.dumps(current_data))
        print(f"Envoi des données : {current_data}")

        producer.flush()
        time.sleep(SEND_INTERVAL)  # Attendre 5 secondes avant le prochain envoi

    # Phase de pause : 1 minute
    print(f"=== Début de la phase de pause (1 minute) ===")
    time.sleep(PAUSE_DURATION)
