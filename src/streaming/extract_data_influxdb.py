import time
import pandas as pd
from influxdb_client import InfluxDBClient

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

query_template = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["_measurement"] == "machine_readings")
  |> filter(fn: (r) => r["machine_id"] == "machine-01")
  |> filter(fn: (r) => r["_field"] == "pression" or r["_field"] == "temperature" or r["_field"] == "vitesse")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

print("⏳ Démarrage de l'export automatique toutes les 1 minute...")

while True:
    try:
        # 📥 Exécution de la requête
        df = client.query_api().query_data_frame(query_template)

        # 🧼 Nettoyage des colonnes inutiles
        df = df[["_time", "temperature", "pression", "vitesse"]]
        df = df.dropna(subset=["temperature", "pression", "vitesse"])

        # 💾 Export en CSV
        df.to_csv("dataset_machine.csv", index=False)
        print("✅ Données exportées dans dataset_machine.csv")

    except Exception as e:
        print(f"❌ Erreur lors de l'export : {e}")

    # ⏱️ Attendre 1 minute avant la prochaine exportation
    time.sleep(10)
