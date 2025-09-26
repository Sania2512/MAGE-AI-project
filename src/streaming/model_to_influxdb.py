import pandas as pd
from datetime import datetime
from influxdb_client import InfluxDBClient, Point

# 🔧 Configuration InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "my-super-secret-auth-token"
INFLUX_ORG = "machines-org"
INFLUX_BUCKET = "machines-data"

# 📥 Chargement du fichier avec prédiction de panne
df = pd.read_csv("input_inference.csv")  # doit contenir colonne 'panne'

# 📡 Connexion InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

# 🧠 Injection des prédictions
for _, row in df.iterrows():

    timestamp = datetime.fromisoformat(row["timestamp"].replace("+00:00", ""))

    point = Point("Prediction") \
        .tag("machine_id", "machine-01") \
        .field("temperature", float(row["temperature"])) \
        .field("pression", float(row["pression"])) \
        .field("vitesse", float(row["vitesse"])) \
        .time(timestamp)

    write_api.write(bucket=INFLUX_BUCKET, record=point)
