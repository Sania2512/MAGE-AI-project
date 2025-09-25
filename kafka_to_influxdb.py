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

# Configuration Kafka Consumer
KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'influxdb-consumer-group',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000
}

# Intervalle de traitement (12 minutes en secondes)
PROCESSING_INTERVAL = 1 * 60  # 12 minutes

class KafkaToInfluxDB:
    def __init__(self):
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

        # Buffer pour stocker les messages collectés
        self.message_buffer = []

        print("✅ Kafka to InfluxDB consumer initialisé")
        print(f"📊 Traitement des données toutes les {PROCESSING_INTERVAL/60} minutes")

    def collect_messages(self, duration_seconds):
        """Collecte les messages Kafka pendant une durée donnée"""
        start_time = time.time()
        messages_collected = 0

        print(f"🔄 Début de la collecte des messages pour {duration_seconds/60:.1f} minutes...")

        while time.time() - start_time < duration_seconds:
            try:
                # Poll pour récupérer des messages (timeout de 1 seconde)
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"❌ Erreur Consumer: {msg.error()}")
                        continue

                # Décoder le message JSON
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    self.message_buffer.append(data)
                    messages_collected += 1
                    print(f"📥 Message collecté #{messages_collected}: {data['machine_id']} - T:{data['temperature']}°C")

                except json.JSONDecodeError as e:
                    print(f"❌ Erreur de décodage JSON: {e}")
                    continue

            except Exception as e:
                print(f"❌ Erreur lors de la collecte: {e}")
                continue

        print(f"✅ Collecte terminée: {messages_collected} messages collectés")
        return messages_collected

    def write_to_influxdb(self):
        """Écrit tous les messages du buffer vers InfluxDB"""
        if not self.message_buffer:
            print("⚠️ Aucun message à écrire dans InfluxDB")
            return 0

        points = []

        for data in self.message_buffer:
            try:
                # Conversion du timestamp - gérer le format exact du producer
                timestamp = data["timestamp"]

                if isinstance(timestamp, str):
                    # Le producer génère: "2025-09-25 04:34:18.459475"
                    try:
                        # Parser le format exact du producer
                        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                        # Convertir en nanoseconds pour InfluxDB
                        timestamp_ns = int(dt.timestamp() * 1000000000)
                    except ValueError:
                        # Essayer d'autres formats si nécessaire
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp_ns = int(dt.timestamp() * 1000000000)
                        except:
                            print(f"❌ Format de timestamp non reconnu: {timestamp}")
                            continue
                elif isinstance(timestamp, (float, int)):
                    # Si c'est déjà un timestamp Unix
                    timestamp_ns = int(timestamp * 1000000000)
                else:
                    print(f"❌ Type de timestamp non supporté: {type(timestamp)}")
                    continue

                # Créer un point InfluxDB pour chaque message
                point = Point("machine_data") \
                    .tag("machine_id", data["machine_id"]) \
                    .field("temperature", float(data["temperature"])) \
                    .field("pressure", float(data["pressure"])) \
                    .field("vitesse", float(data["vitesse"])) \
                    .time(timestamp_ns)

                points.append(point)
                print(f"🔧 Point créé: {data['machine_id']} - T:{data['temperature']}°C - Time:{timestamp}")

            except Exception as e:
                print(f"❌ Erreur lors de la création du point: {e}")
                print(f"   Data problématique: {data}")
                continue

        try:
            # Écrire tous les points en une seule fois
            self.write_api.write(bucket=INFLUXDB_BUCKET, record=points)
            print(f"✅ {len(points)} points écrits dans InfluxDB")

            # Vider le buffer après écriture réussie
            self.message_buffer.clear()
            return len(points)

        except Exception as e:
            print(f"❌ Erreur lors de l'écriture dans InfluxDB: {e}")
            print(f"   Points à écrire: {len(points)}")
            return 0

    def run(self):
        """Lance le processus principal de collecte et écriture"""
        print("🚀 Démarrage du processus Kafka → InfluxDB")

        try:
            while True:
                cycle_start = time.time()
                print(f"\n=== 🔄 Nouveau cycle à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

                # Collecter les messages pendant 12 minutes
                messages_collected = self.collect_messages(PROCESSING_INTERVAL)

                # Écrire dans InfluxDB
                if messages_collected > 0:
                    points_written = self.write_to_influxdb()
                    print(f"📊 Résumé: {messages_collected} messages → {points_written} points dans InfluxDB")
                else:
                    print("⚠️ Aucun message collecté pendant cette période")

                cycle_duration = time.time() - cycle_start
                print(f"⏱️ Cycle terminé en {cycle_duration/60:.2f} minutes")

        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Nettoie les ressources"""
        print("🧹 Nettoyage des ressources...")
        if hasattr(self, 'consumer'):
            self.consumer.close()
        if hasattr(self, 'influx_client'):
            self.influx_client.close()
        print("✅ Nettoyage terminé")

if __name__ == "__main__":
    kafka_to_influx = KafkaToInfluxDB()
    kafka_to_influx.run()
