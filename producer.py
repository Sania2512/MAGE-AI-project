import json
import random
import threading
import time
from datetime import datetime

from confluent_kafka import Producer

# Configuration du producteur
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(**conf)

topic = 'donnees-machines'

# Stockage des dernières valeurs de chaque capteur
current_values = {
    'temperature': 0,
    'pressure': 0,
    'vitesse': 0
}

# Verrous pour la synchronisation des threads
values_lock = threading.Lock()

# Variables de contrôle
is_active_phase = False
cycle_start_time = 0

# Intervalles des capteurs (en secondes)
TEMP_SENSOR_INTERVAL = 10
PRESSURE_SENSOR_INTERVAL = 15
VITESSE_SENSOR_INTERVAL = 20

# Durées du cycle (en secondes)
ACTIVE_DURATION = 5 * 60  # 5 minutes
PAUSE_DURATION = 1 * 60  # 1 minute

# Intervalle d'envoi sur Kafka (5 secondes)
KAFKA_SEND_INTERVAL = 5


def generate_realistic_temperature():
    """Génère une température réaliste (60-98°C)"""
    base_temp = random.uniform(60.0, 98.0)
    return round(base_temp + random.uniform(-2.0, 2.0), 2)


def generate_realistic_pressure():
    """Génère une pression réaliste (3-5 bar)"""
    base_pressure = random.uniform(3.0, 5.0)
    return round(base_pressure + random.uniform(-0.5, 0.5), 2)


def generate_realistic_vitesse():
    """Génère une vitesse réaliste (600-1200 rpm)"""
    base_vitesse = random.uniform(600.0, 1200.0)
    return round(base_vitesse + random.uniform(-100.0, 100.0), 2)


def temperature_sensor():
    """Simule le capteur de température qui met à jour sa valeur toutes les 10 secondes"""
    while True:
        if is_active_phase:
            temp_value = generate_realistic_temperature()

            with values_lock:
                current_values['temperature'] = temp_value

            print(f"📊 Capteur température: {temp_value}°C (mise à jour)")

        time.sleep(TEMP_SENSOR_INTERVAL)


def pressure_sensor():
    """Simule le capteur de pression qui met à jour sa valeur toutes les 15 secondes"""
    while True:
        if is_active_phase:
            pressure_value = generate_realistic_pressure()

            with values_lock:
                current_values['pressure'] = pressure_value

            print(f"📊 Capteur pression: {pressure_value} bar (mise à jour)")

        time.sleep(PRESSURE_SENSOR_INTERVAL)


def vitesse_sensor():
    """Simule le capteur de vitesse qui met à jour sa valeur toutes les 20 secondes"""
    while True:
        if is_active_phase:
            vitesse_value = generate_realistic_vitesse()

            with values_lock:
                current_values['vitesse'] = vitesse_value

            print(f"📊 Capteur vitesse: {vitesse_value} rpm (mise à jour)")

        time.sleep(VITESSE_SENSOR_INTERVAL)


def send_data_to_kafka():
    """Envoie les valeurs actuelles sur Kafka toutes les 5 secondes"""
    while True:
        if is_active_phase:
            current_time = time.time()

            with values_lock:
                # Récupérer les valeurs actuelles (conservées si pas de mise à jour)
                temp = current_values['temperature']
                pressure = current_values['pressure']
                vitesse = current_values['vitesse']

            # Créer le message à envoyer sur Kafka
            message = {
                'machine_id': 'machine-01',
                'temperature': temp,
                'pressure': pressure,
                'vitesse': vitesse,
                'timestamp': datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S.%f')
            }

            # Envoyer sur Kafka
            producer.produce(topic, key=message['machine_id'], value=json.dumps(message))
            producer.flush()

            print(f"🚀 Envoi sur Kafka:")
            print(f"   Température: {temp}°C")
            print(f"   Pression: {pressure} bar")
            print(f"   Vitesse: {vitesse} rpm")
            print(f"   Message: {message}")
            print("-" * 80)

        time.sleep(KAFKA_SEND_INTERVAL)


def main():
    global is_active_phase, cycle_start_time

    print("🔧 Démarrage du système de simulation avec conservation des valeurs...")
    print("📊 Configuration:")
    print(f"   - Capteur température: mise à jour toutes les {TEMP_SENSOR_INTERVAL}s")
    print(f"   - Capteur pression: mise à jour toutes les {PRESSURE_SENSOR_INTERVAL}s")
    print(f"   - Capteur vitesse: mise à jour toutes les {VITESSE_SENSOR_INTERVAL}s")
    print(f"   - Envoi sur Kafka: toutes les {KAFKA_SEND_INTERVAL}s (avec conservation des valeurs)")
    print(f"   - Phase active: {ACTIVE_DURATION // 60} minutes")
    print(f"   - Phase pause: {PAUSE_DURATION // 60} minute")
    print("=" * 80)

    # Démarrer les threads des capteurs
    temp_thread = threading.Thread(target=temperature_sensor, daemon=True)
    pressure_thread = threading.Thread(target=pressure_sensor, daemon=True)
    vitesse_thread = threading.Thread(target=vitesse_sensor, daemon=True)
    kafka_thread = threading.Thread(target=send_data_to_kafka, daemon=True)

    temp_thread.start()
    pressure_thread.start()
    vitesse_thread.start()
    kafka_thread.start()

    # Boucle principale de gestion des cycles
    while True:
        # Phase active
        print(f"🟢 === DÉBUT PHASE ACTIVE ({ACTIVE_DURATION // 60} minutes) ===")
        is_active_phase = True
        cycle_start_time = time.time()

        time.sleep(ACTIVE_DURATION)

        # Phase de pause
        print(f"🟡 === DÉBUT PHASE PAUSE ({PAUSE_DURATION // 60} minute) ===")
        is_active_phase = False

        time.sleep(PAUSE_DURATION)


if __name__ == "__main__":
    main()
