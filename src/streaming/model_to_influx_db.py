import pandas as pd
from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class ModelToInfluxDB:
    def __init__(self, url="http://localhost:8086", token="my-super-secret-auth-token", 
                 org="machines-org", bucket="machines-data"):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = None
        self.write_api = None
    
    def connect(self):
        """Établit la connexion à InfluxDB"""
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
    
    def process_csv_to_influxdb(self, csv_file_path="input_inference.csv"):
        """Traite le fichier CSV et l'injecte dans InfluxDB"""
        # Chargement du fichier CSV
        df = pd.read_csv(csv_file_path)
        
        # Connexion à InfluxDB
        self.connect()
        
        points = []
        
        for _, row in df.iterrows():
            try:
                # Conversion du timestamp
                timestamp_str = row["timestamp"]
                dt = datetime.fromisoformat(timestamp_str.replace("+00:00", ""))
                timestamp_ns = int(dt.timestamp() * 1_000_000_000)
                
                # Création du point
                point = Point("Prediction") \
                    .tag("machine_id", "machine-01") \
                    .field("temperature", float(row["temperature"])) \
                    .field("pression", float(row["pression"])) \
                    .field("vitesse", float(row["vitesse"])) \
                    .time(timestamp_ns)
                
                points.append(point)
                
                print(f"📥 Point ajouté : T={row['temperature']}°C, P={row['pression']}, V={row['vitesse']}")
                
            except Exception as e:
                print(f"❌ Erreur sur la ligne : {row}")
                print(f"   Détail : {e}")
                continue
        
        # Écriture dans InfluxDB
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            print(f"✅ {len(points)} points injectés dans InfluxDB")
        except Exception as e:
            print(f"❌ Erreur lors de l'injection : {e}")
        
        # Fermeture de la connexion
        if self.client:
            self.client.close()


def execute_model_to_influx():
    """Fonction pour exécuter le traitement"""
    processor = ModelToInfluxDB()
    processor.process_csv_to_influxdb()


# Exécution si le script est appelé directement
if __name__ == "__main__":
    execute_model_to_influx()
