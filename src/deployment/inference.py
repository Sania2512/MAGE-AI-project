#!/usr/bin/env python3
"""
Script de déploiement pour le modèle LSTM de maintenance prédictive
Extrait du notebook Jupyter et adapté pour l'entraînement et la sauvegarde automatique
"""

import pandas as pd
import numpy as np
from scipy.stats import multivariate_normal
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os
from datetime import datetime
import json

# Variables globales
SEQUENCE_LENGTH = 50
FEATURES = ['temperature', 'pression', 'vitesse']
MODEL_NAME = "lstm_maintenance_model"
MODELS_DIR = "models"
THRESHOLD = 0.30
RANDOM_SEED = 42

# Paramètres d'entraînement
EPOCHS = 100
BATCH_SIZE = 16
TEST_SIZE = 0.2
EARLY_STOPPING_PATIENCE = 15

# Paramètres LSTM
LSTM_UNITS_1 = 64
LSTM_UNITS_2 = 32
DENSE_UNITS = 16
DROPOUT_RATE_1 = 0.2
DROPOUT_RATE_2 = 0.2
DROPOUT_RATE_3 = 0.1


def collect_sensor_data_from_csv(csv_path):
    """
    Collecte les données capteurs depuis un CSV et les formate pour le prédicteur

    Args:
        csv_path (str): Chemin vers le fichier CSV des données capteurs

    Returns:
        list: Liste de dictionnaires formatés pour MaintenancePredictor
    """
    try:
        df = pd.read_csv(csv_path)

        # Vérifier les colonnes requises
        required_cols = ['temperature', 'pression', 'vitesse']
        if not all(col in df.columns for col in required_cols):
            print(f"❌ Colonnes manquantes. Requis: {required_cols}")
            print(f"   Disponibles: {list(df.columns)}")
            return None

        # Récupérer seulement les 50 dernières lignes
        df_last_50 = df.tail(50)

        # Convertir en format attendu
        sensor_data = []
        for _, row in df_last_50.iterrows():
            data_point = {
                'temperature': float(row['temperature']),
                'pression': float(row['pression']),
                'vitesse': float(row['vitesse'])
            }
            sensor_data.append(data_point)

        print(
            f"✅ {len(sensor_data)} points de données collectés (50 dernières lignes)")
        return sensor_data

    except Exception as e:
        print(f"❌ Erreur lors de la collecte: {e}")
    return None


class MaintenancePredictor:
    """
    Classe pour charger et utiliser le modèle LSTM sauvé en production
    """

    def __init__(self, models_dir=MODELS_DIR, model_name=MODEL_NAME):
        print("🔄 Chargement du modèle de maintenance prédictive...")

        # Chemins des fichiers
        self.model_path = os.path.join(models_dir, f"{model_name}.h5")
        self.scaler_path = os.path.join(models_dir, f"{model_name}_scaler.pkl")
        self.metadata_path = os.path.join(
            models_dir, f"{model_name}_metadata.pkl")

        # Vérifier que les fichiers existent
        if not all(os.path.exists(path) for path in [self.model_path, self.scaler_path, self.metadata_path]):
            raise FileNotFoundError(
                "Fichiers du modèle introuvables. Exécutez d'abord l'entraînement.")

        # Charger le modèle
        self.model = tf.keras.models.load_model(self.model_path)
        print("✅ Modèle LSTM chargé")

        # Charger le scaler
        self.scaler = joblib.load(self.scaler_path)
        print("✅ Scaler chargé")

        # Charger les métadonnées
        self.metadata = joblib.load(self.metadata_path)
        self.sequence_length = self.metadata['sequence_length']
        self.features = self.metadata['features']
        self.threshold = THRESHOLD


        print(f"✅ Configuration chargée:")
        print(f"   - Modèle: {self.metadata['model_name']}")
        print(f"   - Créé le: {self.metadata['creation_date'][:19]}")
        print(f"   - Séquence: {self.sequence_length} points")
        print(f"   - Features: {self.features}")
        print(f"   - Seuil: {self.threshold}")

        # Buffer pour stocker les données historiques
        self.data_buffer = []

    def predict_sequency(self, new_data):
        """
        Prédiction sur un seul point de données
        new_data: dict avec keys ['temperature', 'pression', 'vitesse']
        """
        try:
            # Ajouter au buffer
            data_point = [new_data[feature] for feature in self.features]
            self.data_buffer.append(data_point)

            # Garder seulement les derniers points nécessaires
            if len(self.data_buffer) > self.sequence_length:
                self.data_buffer = self.data_buffer[-self.sequence_length:]

            # Vérifier si on a assez de données
            if len(self.data_buffer) < self.sequence_length:
                return {
                    'prediction': 0,
                    'probability': 0.0,
                    'status': "Not enough measures in sequency",
                    'ready': False
                }

            # Normaliser les données
            sequence = np.array(self.data_buffer)
            sequence_scaled = self.scaler.transform(sequence)

            # Reshape pour le LSTM: (1, sequence_length, features)
            X = sequence_scaled.reshape(
                1, self.sequence_length, len(self.features))

            # Prédiction
            probability = self.model.predict(X, verbose=0)[0][0]
            prediction = 1 if probability > self.threshold else 0

            return {
                'prediction': int(prediction),
                'probability': float(probability),
                'status': '🚨 Panne détectée' if prediction == 1 else '✅ Fonctionnement normal',
                'ready': True,
                'risk_level': self._get_risk_level(probability)
            }

        except Exception as e:
            return {
                'prediction': 0,
                'probability': 0.0,
                'status': f'Erreur: {str(e)}',
                'ready': False
            }

    def _get_risk_level(self, probability):
        """Déterminer le niveau de risque"""
        if probability < 0.3:
            return "🟢 Faible"
        elif probability < THRESHOLD:
            return "🟡 Modéré"
        elif probability < 0.8:
            return "🟠 Élevé"
        else:
            return "🔴 Critique"


def main():
    # Test avec quelques exemples
    # Créer 51 cas de test variés

    data = collect_sensor_data_from_csv(os.path.join("dataset_machine.csv"))
    try:
        # 7. Test du modèle déployé
        print("\n7️INFERENCE DU MODELE DEPLOYE")
        predictor = MaintenancePredictor()

        print("🧪 Test avec données d'exemple:")
        for i, data in enumerate(data, 1):
            result = predictor.predict_sequency(data)
            
        print(f"\n{result['status']} (Prob: {result['probability']:.3f})")

        # Sauvegarder les données d'entrée si une panne est détectée

        if result['prediction'] == 1: #resultat panne
            # Créer le DataFrame avec les données du buffer
            input_data = pd.DataFrame(predictor.data_buffer, columns=predictor.features)

            # Ajouter les timestamps depuis le CSV original
            df_original = pd.read_csv(os.path.join("dataset_machine.csv"))
            
            # Récupérer les 50 derniers timestamps
            timestamps = df_original['_time'].tail(50).tolist()
            
            # Ajouter la colonne timestamp au DataFrame
            input_data['timestamp'] = timestamps
            
            # Réorganiser les colonnes pour avoir timestamp en premier
            input_data = input_data[['timestamp'] + predictor.features]
            
            # Nom du fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"input_inference_{timestamp}.csv"
            
            # Sauvegarder le CSV
            input_data.to_csv(filename, index=False)
            print(f"💾 Données d'entrée sauvegardées: {filename}")

            print("\n✅ PIPELINE TERMINÉ AVEC SUCCÈS!")

    except Exception as e:
        print(f"\n❌ ERREUR DANS LE PIPELINE: {e}")
        raise


if __name__ == "__main__":
    main()
