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

# Paramètres de génération de données
N_NORMAL = 500
N_PANNE = 500

# Corrélations exactes
CORRELATION_MATRIX = np.array([
    [1.000,  0.050, -0.319],  # température
    [0.050,  1.000, -0.465],  # pression
    [-0.319, -0.465,  1.000]  # vitesse
])

# États NORMAUX
MEANS_NORMAL = np.array([65.0, 3.5, 950.0])
STDS_NORMAL = np.array([8.0, 0.8, 80.0])

# États PANNE
MEANS_PANNE = np.array([82.0, 5.2, 650.0])
STDS_PANNE = np.array([6.0, 0.6, 100.0])


def generate_training_data():
    """
    Générer 1000 données avec corrélations réalistes
    """
    print("🔄 Génération de 1000 données avec corrélations réelles...")

    # Construire matrices de covariance
    cov_normal = np.outer(STDS_NORMAL, STDS_NORMAL) * CORRELATION_MATRIX
    cov_panne = np.outer(STDS_PANNE, STDS_PANNE) * CORRELATION_MATRIX

    # Générer les données
    np.random.seed(RANDOM_SEED)

    # Données normales
    normal_data = np.random.multivariate_normal(
        MEANS_NORMAL, cov_normal, N_NORMAL)

    # Données de panne
    panne_data = np.random.multivariate_normal(MEANS_PANNE, cov_panne, N_PANNE)

    # Créer DataFrame
    data = []

    # Ajouter données normales
    for temp, press, speed in normal_data:
        data.append({
            'temperature': max(temp, 55),
            'pression': max(press, 3.42),
            'vitesse': max(speed, 600),
            'panne': 0
        })

    # Ajouter données de panne
    for temp, press, speed in panne_data:
        data.append({
            'temperature': min(temp, 84),
            'pression': min(press, 4.98),
            'vitesse': max(speed, 1385),
            'panne': 1
        })

    # Créer et mélanger
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Ajouter timestamps
    df['timestamp'] = pd.date_range('2024-01-01', periods=len(df), freq='6min')

    print(f"✅ {len(df)} données générées !")
    print(
        f"📊 Pannes : {df['panne'].sum()}/{len(df)} ({df['panne'].mean():.1%})")

    return df


def create_lstm_sequences(data, sequence_length=SEQUENCE_LENGTH, features=FEATURES):
    """
    Créer des séquences temporelles pour le LSTM
    """
    print(f"🔄 Création des séquences LSTM (longueur: {sequence_length})...")

    # Extraire les features et target
    X_raw = data[features].values
    y_raw = data['panne'].values

    # Normalisation des features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    print(f"📊 Normalisation appliquée:")
    print(f"   Moyennes: {scaler.mean_.round(2)}")
    print(f"   Écarts-types: {scaler.scale_.round(2)}")

    # Créer les séquences
    X_sequences = []
    y_sequences = []

    for i in range(sequence_length, len(X_scaled)):
        X_sequences.append(X_scaled[i-sequence_length:i])
        y_sequences.append(y_raw[i])

    X_sequences = np.array(X_sequences)
    y_sequences = np.array(y_sequences)

    print(f"✅ Séquences créées:")
    print(f"   Shape X: {X_sequences.shape} (échantillons, temps, features)")
    print(f"   Shape y: {y_sequences.shape}")
    print(
        f"   Pannes: {y_sequences.sum()}/{len(y_sequences)} ({y_sequences.mean():.1%})")

    return X_sequences, y_sequences, scaler


def build_lstm_model(input_shape):
    """
    Construire le modèle LSTM pour détection de pannes
    """
    print("🔄 Construction du modèle LSTM...")

    model = Sequential([
        LSTM(LSTM_UNITS_1, return_sequences=True, input_shape=input_shape),
        Dropout(DROPOUT_RATE_1),

        LSTM(LSTM_UNITS_2, return_sequences=False),
        Dropout(DROPOUT_RATE_2),

        Dense(DENSE_UNITS, activation='relu'),
        Dropout(DROPOUT_RATE_3),
        Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )

    print("✅ Modèle LSTM créé !")
    return model


def train_lstm_model(model, X, y, test_size=TEST_SIZE):
    """
    Entraîner le modèle LSTM avec validation
    """
    print("🔄 Entraînement du LSTM...")

    # Split train/validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_SEED, stratify=y
    )

    print(f"📊 Données d'entraînement:")
    print(
        f"   Train: {len(X_train)} échantillons ({y_train.mean():.1%} pannes)")
    print(
        f"   Validation: {len(X_val)} échantillons ({y_val.mean():.1%} pannes)")

    # Callback pour arrêt anticipé
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=EARLY_STOPPING_PATIENCE,
        restore_best_weights=True,
        verbose=1
    )

    # Entraînement
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[early_stopping],
        verbose=1
    )

    print("✅ Entraînement terminé !")
    return history, X_val, y_val


def evaluate_lstm_model(model, X_val, y_val):
    """
    Évaluer les performances du LSTM
    """
    print("🔄 Évaluation du modèle LSTM...")

    # Prédictions
    y_pred_proba = model.predict(X_val)
    y_pred = (y_pred_proba > 0.5).astype(int)

    # Métriques
    print("\n📊 RÉSULTATS LSTM:")
    print("="*50)
    print(classification_report(y_val, y_pred,
          target_names=['Normal', 'Panne']))

    # Matrice de confusion
    cm = confusion_matrix(y_val, y_pred)
    print(f"\n📈 Matrice de confusion:")
    print(f"                 Prédit")
    print(f"         Normal    Panne")
    print(f"Normal     {cm[0, 0]:3d}      {cm[0, 1]:3d}")
    print(f"Panne      {cm[1, 0]:3d}      {cm[1, 1]:3d}")

    # Calculs manuels
    accuracy = (cm[0, 0] + cm[1, 1]) / cm.sum()
    precision = cm[1, 1] / (cm[1, 1] + cm[0, 1]
                            ) if (cm[1, 1] + cm[0, 1]) > 0 else 0
    recall = cm[1, 1] / (cm[1, 1] + cm[1, 0]
                         ) if (cm[1, 1] + cm[1, 0]) > 0 else 0
    f1 = 2 * (precision * recall) / (precision +
                                     recall) if (precision + recall) > 0 else 0

    print(f"\n🎯 SCORES FINAUX:")
    print(f"   Accuracy:  {accuracy:.3f}")
    print(f"   Precision: {precision:.3f}")
    print(f"   Recall:    {recall:.3f}")
    print(f"   F1-Score:  {f1:.3f}")

    return y_pred_proba, y_pred, {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }


def save_trained_model(model, scaler, sequence_length, metrics, model_name=MODEL_NAME):
    """
    Sauvegarder le modèle entraîné, le scaler et les métadonnées
    """
    print(f"💾 Sauvegarde du modèle {model_name}...")

    # Créer le dossier models s'il n'existe pas
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"📁 Dossier '{MODELS_DIR}' créé")

    # Chemins complets
    model_path = os.path.join(MODELS_DIR, f"{model_name}.h5")
    scaler_path = os.path.join(MODELS_DIR, f"{model_name}_scaler.pkl")
    metadata_path = os.path.join(MODELS_DIR, f"{model_name}_metadata.pkl")

    # 1. Sauvegarder le modèle LSTM
    model.save(model_path)
    print(f"✅ Modèle LSTM sauvé: {model_path}")

    # 2. Sauvegarder le scaler
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler sauvé: {scaler_path}")

    # 3. Sauvegarder les métadonnées
    metadata = {
        'model_name': model_name,
        'creation_date': datetime.now().isoformat(),
        'sequence_length': sequence_length,
        'features': FEATURES,
        'input_shape': (sequence_length, len(FEATURES)),
        'threshold': THRESHOLD,
        'model_architecture': {
            'lstm_units_1': LSTM_UNITS_1,
            'lstm_units_2': LSTM_UNITS_2,
            'dropout_1': DROPOUT_RATE_1,
            'dropout_2': DROPOUT_RATE_2,
            'dropout_3': DROPOUT_RATE_3,
            'dense_units': DENSE_UNITS,
            'output_activation': 'sigmoid'
        },
        'training_params': {
            'epochs': EPOCHS,
            'batch_size': BATCH_SIZE,
            'optimizer': 'adam',
            'loss': 'binary_crossentropy'
        },
        'performance_metrics': metrics
    }

    joblib.dump(metadata, metadata_path)
    print(f"✅ Métadonnées sauvées: {metadata_path}")

    # 4. Créer un fichier de version
    version_file = os.path.join(MODELS_DIR, "model_version.txt")
    with open(version_file, 'w') as f:
        f.write(f"Model: {model_name}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Version: 1.0\n")
        f.write(f"Accuracy: {metrics['accuracy']:.3f}\n")
        f.write(f"F1-Score: {metrics['f1_score']:.3f}\n")
        f.write(f"F1-Score: {metrics['precision']:.3f}\n")

    print(f"✅ Version sauvée: {version_file}")
    print("\n🎉 Modèle prêt pour le déploiement!")

    return {
        'model_path': model_path,
        'scaler_path': scaler_path,
        'metadata_path': metadata_path
    }

def main():
    """
    Fonction principale pour entraîner et déployer le modèle
    """
    print("🚀 DÉMARRAGE DU PIPELINE ML - MAINTENANCE PRÉDICTIVE")
    print("="*60)

    try:
        # 1. Génération des données
        print("\n1️⃣ GÉNÉRATION DES DONNÉES")
        train_data = generate_training_data()

        # 2. Préparation des séquences
        print("\n2️⃣ PRÉPARATION DES SÉQUENCES LSTM")
        X_sequences, y_sequences, scaler = create_lstm_sequences(train_data)

        # 3. Construction du modèle
        print("\n3️⃣ CONSTRUCTION DU MODÈLE")
        input_shape = (SEQUENCE_LENGTH, len(FEATURES))
        lstm_model = build_lstm_model(input_shape)

        # 4. Entraînement
        print("\n4️⃣ ENTRAÎNEMENT DU MODÈLE")
        history,X_val, y_val = train_lstm_model(lstm_model, X_sequences, y_sequences)

        # 5. Évaluation
        print("\n5️⃣ ÉVALUATION DU MODÈLE")
        y_pred_proba, y_pred, metrics = evaluate_lstm_model(lstm_model, X_val, y_val)

        # 6. Sauvegarde pour déploiement
        print("\n6️⃣ SAUVEGARDE POUR DÉPLOIEMENT")
        save_trained_model(lstm_model, scaler, SEQUENCE_LENGTH, metrics)

    except Exception as e:
            print(f"\n❌ ERREUR DANS LE PIPELINE: {e}")
            raise

if __name__ == "__main__":
    main()