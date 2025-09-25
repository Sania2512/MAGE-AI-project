import time
import pandas as pd
import os
from fetch_open_full_data import get_full_open_data

# Initialisation
last_values = {"temperature": None, "pressure": None, "wind_speed": None}
last_update = {"temperature": 0, "pressure": 0, "wind_speed": 0}
csv_path = "donnees_iot.csv"

# Création du fichier si inexistant
if not os.path.exists(csv_path):
    pd.DataFrame(columns=["timestamp", "temperature", "pressure", "wind_speed"]).to_csv(csv_path, index=False)

# Boucle principale
while True:
    now = time.time()
    current = get_full_open_data()["current"]
    row = {"timestamp": pd.Timestamp.now()}

    # Température : toutes les 10s
    if now - last_update["temperature"] >= 10:
        last_values["temperature"] = current["temperature"]
        last_update["temperature"] = now
    row["temperature"] = last_values["temperature"]

    # Pression : toutes les 15s
    if now - last_update["pressure"] >= 15:
        last_values["pressure"] = current["pressure"]
        last_update["pressure"] = now
    row["pressure"] = last_values["pressure"]

    # Vitesse du vent : toutes les 20s
    if now - last_update["wind_speed"] >= 20:
        last_values["wind_speed"] = current["wind_speed"]
        last_update["wind_speed"] = now
    row["wind_speed"] = last_values["wind_speed"]

    # Injection dans le CSV
    pd.DataFrame([row]).to_csv(csv_path, mode='a', header=False, index=False)
    print("Ligne ajoutée :", row)

    time.sleep(5)