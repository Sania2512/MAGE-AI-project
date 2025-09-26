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

# Variables globales
SEQUENCE_LENGTH = 50
FEATURES = ['temperature', 'pression', 'vitesse']
MODEL_NAME = "lstm_maintenance_model"
MODELS_DIR = "models"
THRESHOLD = 0.50
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
        self.threshold = self.metadata['threshold']

        print(f"✅ Configuration chargée:")
        print(f"   - Modèle: {self.metadata['model_name']}")
        print(f"   - Créé le: {self.metadata['creation_date'][:19]}")
        print(f"   - Séquence: {self.sequence_length} points")
        print(f"   - Features: {self.features}")
        print(f"   - Seuil: {self.threshold}")

        # Buffer pour stocker les données historiques
        self.data_buffer = []

    def predict_single(self, new_data):
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
                    'status': f'Collecte en cours ({len(self.data_buffer)}/{self.sequence_length})',
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
        test_cases = [
            # Cas normaux clairs
            {'temperature': 70, 'pression': 4.2, 'vitesse': 800},  # Normal
            {'temperature': 65, 'pression': 3.8, 'vitesse': 920},  # Normal
            {'temperature': 62, 'pression': 3.5, 'vitesse': 950},  # Normal
            {'temperature': 67, 'pression': 3.6, 'vitesse': 900},  # Normal
            {'temperature': 64, 'pression': 3.7, 'vitesse': 980},  # Normal
            
            # Cas de pannes clairs
            {'temperature': 85, 'pression': 3.2, 'vitesse': 1100},  # Panne
            {'temperature': 83, 'pression': 4.9, 'vitesse': 630},  # Panne
            {'temperature': 80, 'pression': 5.0, 'vitesse': 650},  # Panne
            {'temperature': 82, 'pression': 4.8, 'vitesse': 700},  # Panne
            {'temperature': 81, 'pression': 4.7, 'vitesse': 680},  # Panne
            
            # Cas limites (température)
            {'temperature': 55, 'pression': 3.6, 'vitesse': 920},  # Min normal
            {'temperature': 73, 'pression': 3.9, 'vitesse': 900},  # Max normal
            {'temperature': 76, 'pression': 4.6, 'vitesse': 700},  # Min panne
            {'temperature': 84, 'pression': 4.8, 'vitesse': 650},  # Max panne
            
            # Cas limites (pression)
            {'temperature': 65, 'pression': 3.42, 'vitesse': 950},  # Min normal
            {'temperature': 67, 'pression': 4.3, 'vitesse': 900},   # Max normal
            {'temperature': 80, 'pression': 4.6, 'vitesse': 670},   # Min panne
            {'temperature': 81, 'pression': 4.98, 'vitesse': 650},  # Max panne
            
            # Cas limites (vitesse)
            {'temperature': 64, 'pression': 3.5, 'vitesse': 600},   # Min normal
            {'temperature': 66, 'pression': 3.7, 'vitesse': 1030},  # Max normal
            {'temperature': 80, 'pression': 4.7, 'vitesse': 600},   # Min panne
            {'temperature': 82, 'pression': 4.8, 'vitesse': 750},   # Typique panne
            
            # Cas ambigus
            {'temperature': 74, 'pression': 4.4, 'vitesse': 800},   # Entre normal et panne
            {'temperature': 76, 'pression': 4.0, 'vitesse': 880},   # Entre normal et panne
            {'temperature': 70, 'pression': 4.5, 'vitesse': 750},   # Entre normal et panne
            
            # Plus de variations normales
            {'temperature': 60, 'pression': 3.5, 'vitesse': 970},
            {'temperature': 63, 'pression': 3.6, 'vitesse': 940},
            {'temperature': 65, 'pression': 3.7, 'vitesse': 910},
            {'temperature': 68, 'pression': 3.8, 'vitesse': 880},
            {'temperature': 69, 'pression': 3.9, 'vitesse': 850},
            
            # Plus de variations pannes
            {'temperature': 78, 'pression': 4.7, 'vitesse': 680},
            {'temperature': 79, 'pression': 4.8, 'vitesse': 670},
            {'temperature': 80, 'pression': 4.9, 'vitesse': 660},
            {'temperature': 81, 'pression': 5.0, 'vitesse': 650},
            {'temperature': 82, 'pression': 5.1, 'vitesse': 640},
            
            # Combinaisons extrêmes
            {'temperature': 55, 'pression': 3.42, 'vitesse': 600},  # Tout minimum normal
            {'temperature': 73, 'pression': 4.3, 'vitesse': 1030},  # Tout maximum normal
            {'temperature': 76, 'pression': 4.6, 'vitesse': 600},   # Minimum panne
            {'temperature': 84, 'pression': 4.98, 'vitesse': 750},  # Maximum panne
            
            # Cas vraiment ambigus (près de la frontière de décision)
            {'temperature': 73, 'pression': 4.5, 'vitesse': 800},
            {'temperature': 75, 'pression': 4.2, 'vitesse': 850},
            {'temperature': 74, 'pression': 4.3, 'vitesse': 820},
            {'temperature': 72, 'pression': 4.4, 'vitesse': 780},
            {'temperature': 76, 'pression': 4.1, 'vitesse': 840},
            
            # Quelques cas supplémentaires normaux
            {'temperature': 61, 'pression': 3.6, 'vitesse': 930},
            {'temperature': 66, 'pression': 3.8, 'vitesse': 890},
            {'temperature': 63, 'pression': 3.7, 'vitesse': 920},
            
            # Quelques cas supplémentaires de panne
            {'temperature': 80, 'pression': 4.7, 'vitesse': 690},
            {'temperature': 83, 'pression': 4.8, 'vitesse': 650},
            {'temperature': 81, 'pression': 4.9, 'vitesse': 670}
        ]

        try:
            # 7. Test du modèle déployé
            print("\n7️⃣ TEST DU MODÈLE DÉPLOYÉ")
            predictor = MaintenancePredictor()

            print("🧪 Test avec données d'exemple:")
            for i, data in enumerate(test_cases, 1):
                result = predictor.predict_single(data)
                print(
                    f"   Test {i}: {data} → {result['status']} (Prob: {result['probability']:.3f})")

            print("\n✅ PIPELINE TERMINÉ AVEC SUCCÈS!")

        except Exception as e:
            print(f"\n❌ ERREUR DANS LE PIPELINE: {e}")
            raise

if __name__ == "__main__":
    main()