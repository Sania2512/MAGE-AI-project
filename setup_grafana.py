import requests

# Configuration Grafana
GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"

# Configuration InfluxDB
INFLUX_URL = "http://influxdb:8086"
INFLUX_ORG = "machines-org"
INFLUX_BUCKET = "machines-data"
INFLUX_TOKEN = "my-super-secret-auth-token"

# Requête pour créer la datasource
datasource_payload = {
    "name": "InfluxDB",
    "type": "influxdb",
    "access": "proxy",
    "url": INFLUX_URL,
    "jsonData": {
        "version": "Flux",
        "organization": INFLUX_ORG,
        "defaultBucket": INFLUX_BUCKET,
        "tlsSkipVerify": True
    },
    "secureJsonData": {
        "token": INFLUX_TOKEN
    }
}

# Envoi à Grafana
response = requests.post(
    f"{GRAFANA_URL}/api/datasources",
    auth=(GRAFANA_USER, GRAFANA_PASSWORD),
    json=datasource_payload
)

# Vérification du résultat
if response.status_code == 200:
    print("✅ Datasource InfluxDB créée avec succès dans Grafana")
elif response.status_code == 409:
    print("⚠️ Datasource existe déjà")
else:
    print(f"❌ Erreur ({response.status_code}): {response.text}")
