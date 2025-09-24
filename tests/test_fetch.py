# test_fetch.py
import sys, os, json
from datetime import datetime

# Ajouter le dossier scripts au chemin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from fetch_open_full_data import get_full_open_data

# Récupérer les données
data = get_full_open_data()

# Créer un nom de fichier horodaté
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"../logs/fetch_result_{timestamp}.json"

# Enregistrer dans un fichier
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print(f"Données enregistrées dans : {filename}")