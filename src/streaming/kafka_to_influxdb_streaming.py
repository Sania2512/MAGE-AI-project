#!/usr/bin/env python3
"""
Consumer Kafka vers InfluxDB - Version Streaming Temps Réel
Traite chaque message immédiatement pour affichage en temps réel dans le dashboard
"""

import time
import json
from datetime import datetime
from confluent_kafka import Consumer, KafkaError
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configuration InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "machines-org"
INFLUXDB_BUCKET = "machines-data"

# Configuration Kafka Consumer pour streaming temps réel
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'influxdb-streaming-consumer',
    'auto.offset.reset': 'earliest',  # Lire depuis le début pour récupérer toutes les données
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000
}


class KafkaToInfluxDBStreaming:
    def __init__(self):
        print("🚀 Initialisation du consumer Kafka→InfluxDB streaming...")

        # Initialiser le client InfluxDB
        self.influx_client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)

        # Initialiser le consumer Kafka
        self.consumer = Consumer(KAFKA_CONFIG)
        self.consumer.subscribe(['donnees-machines'])

        print("✅ Consumer streaming initialisé")
        print("📊 Mode: Traitement en temps réel (chaque message)")
        print("🎯 Dashboard mis à jour instantanément")

    def process_message_immediately(self, message_data):
        """Traite un message Kafka immédiatement et l'écrit dans InfluxDB"""
        try:
            # Créer un point InfluxDB avec les bons noms de champs
            point = Point("machine_data") \
                .tag("machine_id", message_data['machine_id']) \
                .field("temperature", float(message_data['temperature'])) \
                .field("pressure", float(message_data['pressure'])) \
                .field("vitesse", float(message_data['vitesse']))

            # Gérer le timestamp du message
            if 'timestamp' in message_data:
                try:
                    if isinstance(message_data['timestamp'], str):
                        timestamp = datetime.strptime(message_data['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                        point = point.time(timestamp)
                except ValueError:
                    # Si le parsing échoue, utiliser le timestamp actuel
                    pass

            # Écrire immédiatement dans InfluxDB
            self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)

            # Log de confirmation
            print(f"✅ Données écrites dans InfluxDB (temps réel):")
            print(f"   🏭 Machine: {message_data['machine_id']}")
            print(f"   🌡️  Température: {message_data['temperature']}°C")
            print(f"   ⚡ Pression: {message_data['pressure']} bar")  # Nom correct pour le dashboard
            print(f"   ⚙️  Vitesse: {message_data['vitesse']} rpm")
            print(f"   🕐 Timestamp: {message_data.get('timestamp', 'N/A')}")
            print("-" * 70)

            return True

        except Exception as e:
            print(f"❌ Erreur lors de l'écriture dans InfluxDB: {e}")
            print(f"   Message problématique: {message_data}")
            return False

    def run_streaming(self):
        """Lance le mode streaming - traite chaque message en temps réel"""
        print("🔄 Démarrage du mode streaming temps réel...")
        print("📡 En attente des messages Kafka...")
        print("=" * 70)

        message_count = 0

        try:
            while True:
                # Lire un message avec timeout court
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"❌ Erreur Kafka: {msg.error()}")
                        continue

                # Décoder le message JSON
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    message_count += 1

                    print(f"📨 Message #{message_count} reçu de Kafka:")
                    print(f"   {message_data}")

                    # Traiter le message immédiatement
                    success = self.process_message_immediately(message_data)

                    if success:
                        print(f"🎯 Dashboard mis à jour! (Message #{message_count})")
                    else:
                        print(f"⚠️ Échec traitement message #{message_count}")

                except json.JSONDecodeError as e:
                    print(f"❌ Erreur décodage JSON: {e}")
                    continue
                except Exception as e:
                    print(f"❌ Erreur traitement message: {e}")
                    continue

        except KeyboardInterrupt:
            print(f"\n🛑 Arrêt demandé par l'utilisateur")
            print(f"📊 Messages traités: {message_count}")
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Nettoie les ressources"""
        print("🧹 Nettoyage des ressources...")
        try:
            if hasattr(self, 'consumer'):
                self.consumer.close()
            if hasattr(self, 'influx_client'):
                self.influx_client.close()
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
        print("✅ Consumer streaming fermé proprement")


def main():
    print("🏭 === KAFKA TO INFLUXDB STREAMING ===")
    print("🎯 Mode temps réel pour dashboard Streamlit")
    print("📊 Résout le problème de pression = 0")
    print()

    consumer = KafkaToInfluxDBStreaming()
    consumer.run_streaming()


if __name__ == "__main__":
    main()
