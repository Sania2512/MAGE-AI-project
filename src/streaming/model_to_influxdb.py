import pandas as pd
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# 🔧 Configuration InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "machines-org"
INFLUXDB_BUCKET = "machines-data"

# 📥 Chargement du fichier CSV avec prédictions
df = pd.read_csv("input_inference.csv")  # doit contenir 'timestamp', 'temperature', 'pression', 'vitesse', 'panne'

# 📡 Connexion InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

points = []

for _, row in df.iterrows():
    try:
        # 🔄 Conversion du timestamp
        timestamp_str = row["timestamp"]
        dt = datetime.fromisoformat(timestamp_str.replace("+00:00", ""))
        timestamp_ns = int(dt.timestamp() * 1_000_000_000)

        # 🔧 Création du point
        point = Point("machine_readings") \
            .tag("machine_id", "machine-01") \
            .field("temperature", float(row["temperature"])) \
            .field("pression", float(row["pression"])) \
            .field("vitesse", float(row["vitesse"])) \
            .time(timestamp_ns)

        points.append(point)
        print(f"📥 Point ajouté : T={row['temperature']}°C, P={row['pression']}, V={row['vitesse']}, panne={row['panne']}")

    except Exception as e:
        print(f"❌ Erreur sur la ligne : {row}")
        print(f"   Détail : {e}")
        continue

# 📤 Écriture dans InfluxDB
try:
    write_api.write(bucket=INFLUXDB_BUCKET, record=points)
    print(f"✅ {len(points)} points injectés dans InfluxDB")
except Exception as e:
    print(f"❌ Erreur lors de l'injection : {e}")