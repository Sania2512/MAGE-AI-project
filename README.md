# MAGE-AI Project
 
## Présentation
Ce projet vise à développer une solution de maintenance prédictive basée sur l'apprentissage automatique, l'intégration de flux de données (Kafka, InfluxDB) et la visualisation via Streamlit et Grafana.
 
## Structure du projet
```
dataset_machine.csv
input_inference_*.csv
train_dataset.csv
models/
    lstm_maintenance_model.h5
    lstm_maintenance_model_metadata.pkl
    lstm_maintenance_model_scaler.pkl
    model_version.txt
src/
    deployment/
        inference.py
        train.py
        test.py
    streaming/
        extract_data_influxdb.py
        kafka_to_influxdb.py
        model_to_influx_db.py
        producer.py
        streaming_processor.py
    visualisation/
        setup_grafana.py
streamlit_dashboard.py
Dockerfile.streamlit
requirements.txt
docker-compose.yml
README.md
```
 
## 📦 Docker Compose
 
Le fichier `docker-compose.yml` lance les services suivants :
 
- `zookeeper` et `broker` Kafka
- `influxdb` avec bucket `machines-data`
- `grafana` avec datasource préconfigurée
- `control-center` pour monitoring Kafka
 
```bash
docker compose up -d
 
## Installation
1. Cloner le dépôt :
   ```powershell
git clone <url-du-repo>
```
2. Installer les dépendances Python :
   ```powershell
pip install -r requirements.txt
```
3. (Optionnel) Démarrer les services via Docker :
   ```powershell
docker-compose up
```
 
## Utilisation
- **Entraînement du modèle** : `src/deployment/train.py`
- **Inférence** : `src/deployment/inference.py` et fichiers `input_inference_*.csv`
- **Dashboard Streamlit** : `streamlit_dashboard.py`
- **Streaming et intégration** : scripts dans `src/streaming/`
- **Visualisation Grafana** : `src/visualisation/setup_grafana.py`
 
## Modèles et données
- Modèle LSTM sauvegardé dans `models/`
- Jeux de données : `train_dataset.csv`, `dataset_machine.csv`, `input_inference_*.csv`
 