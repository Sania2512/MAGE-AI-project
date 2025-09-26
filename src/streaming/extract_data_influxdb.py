from influxdb_client import InfluxDBClient
import pandas as pd

# 🔐 Configuration InfluxDB
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "my-super-secret-auth-token"
INFLUXDB_ORG = "machines-org"
INFLUXDB_BUCKET = "machines-data"

# 📡 Connexion au client
client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

# 🔍 Requête Flux adaptée
query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["_measurement"] == "machine_readings")
  |> filter(fn: (r) => r["machine_id"] == "machine-01")
  |> filter(fn: (r) => r["_field"] == "pression" or r["_field"] == "temperature" or r["_field"] == "vitesse")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

# 📥 Exécution de la requête
df = client.query_api().query_data_frame(query)

# 🧼 Nettoyage des colonnes inutiles
df = df[["_time", "temperature", "pression", "vitesse"]]
df = df.dropna(subset=["temperature", "pression", "vitesse"])

# 💾 Export en CSV
df.to_csv("dataset_machine.csv", index=False)
print("✅ Données exportées dans dataset_machine.csv")