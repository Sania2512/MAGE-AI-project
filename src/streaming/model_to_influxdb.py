import pandas as pd
from datetime import datetime
from influxdb_client import InfluxDBClient, Point

# 🔧 Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "my-super-secret-auth-token"
INFLUX_ORG = "machines-org"
INFLUX_BUCKET = "machines-data"

# 📥 Chargement du fichier avec prédiction de panne 
df = pd.read_csv("dataset_machine.csv")  # doit contenir colonne 'panne'

# 📡 Connexion InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

# 🧠 Injection des prédictions
for _, row in df.iterrows():
    point = Point("Prediction") \
        .tag("machine_id", data["machine_id"]) \
        .field("timestamp", timestamp) \
                    .field("temperature", float(data["temperature"])) \
                    .field("pression", float(data["pressure"])) \
                    .field("vitesse", float(data["vitesse"])) \
                    .time(timestamp_ns)
print("✅ Prédictions injectées dans InfluxDB")