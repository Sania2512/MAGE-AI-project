# 🚀 Système de Maintenance Prédictive LSTM

## 📋 Description

Ce projet implémente un système de maintenance prédictive utilisant un réseau de neurones LSTM (Long Short-Term Memory) pour détecter les pannes avant qu'elles ne surviennent.

## 🏗️ Architecture

- **Modèle**: LSTM avec 64 unités + couches denses
- **Données**: Température, Pression, Vitesse de rotation
- **Séquence**: 50 points consécutifs requis pour prédiction
- **Sortie**: Probabilité de panne (0-1) + classification binaire

## 📁 Structure des Fichiers

```
MAGE-AI-project/
├── deploy_ai.py              # Script principal d'entraînement et sauvegarde
├── test_deployed_model.py     # Tests du modèle déployé
├── predict_interactive.py     # Interface interactive pour prédictions
├── requirements_ai.txt        # Dépendances Python
├── models/                    # Dossier des modèles sauvés
│   ├── lstm_maintenance_model.h5          # Modèle TensorFlow
│   ├── lstm_maintenance_model_scaler.pkl  # Normaliseur des données
│   ├── lstm_maintenance_model_metadata.pkl # Métadonnées
│   └── model_version.txt                  # Informations de version
└── README.md                 # Ce fichier
```

## 🚀 Installation et Utilisation

### 1. Configuration de l'environnement

```bash
# Activer l'environnement virtuel (déjà configuré)
source venv/bin/activate

# Les packages sont déjà installés, mais si nécessaire :
pip install -r requirements_ai.txt
```

### 2. Entraînement du modèle

```bash
# Lancer l'entraînement complet (génération données + entraînement + sauvegarde)
python deploy_ai.py
```

**Ce script va :**

- ✅ Générer 1000 points de données synthétiques avec corrélations réalistes
- ✅ Créer les séquences temporelles pour l'entraînement LSTM
- ✅ Entraîner le modèle avec validation croisée
- ✅ Évaluer les performances
- ✅ Sauvegarder le modèle, scaler et métadonnées
- ✅ Tester le modèle déployé

### 3. Test du modèle

```bash
# Tester le modèle avec différents scénarios
python test_deployed_model.py
```

### 4. Utilisation interactive

```bash
# Interface interactive pour prédictions en temps réel
python predict_interactive.py
```

**Options disponibles :**

- `manuel` : Saisie manuelle des valeurs
- `auto` : Simulation automatique avec évolution progressive
- `info` : Afficher les informations du modèle
- `quit` : Quitter

## 📊 Données d'Entrée

Le modèle attend 3 paramètres par point :

| Paramètre   | Unité | Plage normale | Plage de panne |
| ----------- | ----- | ------------- | -------------- |
| Température | °C    | 60-75         | >75            |
| Pression    | bar   | 3.5-4.5       | <3.5 ou >4.5   |
| Vitesse     | rpm   | 700-900       | <700 ou >900   |

## 🎯 Interprétation des Résultats

### Probabilités de Panne

- `0.0 - 0.3` : 🟢 Risque **Faible** - Fonctionnement normal
- `0.3 - 0.55` : 🟡 Risque **Modéré** - Surveillance recommandée
- `0.55 - 0.8` : 🟠 Risque **Élevé** - Attention requise
- `0.8 - 1.0` : 🔴 Risque **Critique** - Intervention immédiate

### États

- ✅ **Fonctionnement normal** : Aucune anomalie détectée
- 🚨 **Panne détectée** : Seuil de 0.55 dépassé
- 🔄 **Collecte en cours** : Accumulation des 50 points requis

## 🔧 Utilisation en Production

### Import de la classe

```python
from deploy_ai import MaintenancePredictor

# Initialiser le prédicteur
predictor = MaintenancePredictor()

# Faire une prédiction
data = {'temperature': 75, 'pression': 4.0, 'vitesse': 850}
result = predictor.predict_single(data)

print(f"Statut: {result['status']}")
print(f"Probabilité: {result['probability']:.3f}")
print(f"Risque: {result['risk_level']}")
```

### Intégration avec Kafka (exemple)

```python
from kafka import KafkaConsumer
import json

# Consumer Kafka + Prédicteur
consumer = KafkaConsumer('sensor_data', value_deserializer=json.loads)
predictor = MaintenancePredictor()

for message in consumer:
    data = message.value
    result = predictor.predict_single(data)

    if result['prediction'] == 1:
        send_alert(f"Panne détectée: {result['probability']:.3f}")
```

## 📈 Performances du Modèle

Le modèle actuel a été entraîné avec :

- **Architecture**: LSTM(64) → LSTM(32) → Dense(16) → Dense(1)
- **Optimiseur**: Adam
- **Loss**: Binary Crossentropy
- **Métriques**: Accuracy, Precision, Recall
- **Arrêt anticipé**: Patience de 15 epochs

## 🔄 Réentraînement

Pour réentraîner avec de nouvelles données :

1. Modifier les données dans `generate_training_data()`
2. Ajuster les paramètres dans `build_lstm_model()`
3. Relancer `python deploy_ai.py`

## 🚨 Troubleshooting

### Erreur "Modèle non trouvé"

```bash
# Réentraîner le modèle
python deploy_ai.py
```

### Erreur d'importation

```bash
# Réinstaller les dépendances
pip install -r requirements_ai.txt
```

### Performance insuffisante

- Augmenter le nombre de données d'entraînement
- Ajuster l'architecture du réseau
- Modifier les seuils de décision

## 📞 Support

Le système est maintenant **prêt pour la production** !

**Fichiers générés :**

- ✅ Modèle LSTM entraîné et sauvegardé
- ✅ Scripts de test et d'utilisation interactive
- ✅ Classe réutilisable pour intégration
- ✅ Documentation complète

**Prochaines étapes possibles :**

- Intégration avec votre pipeline Kafka → InfluxDB
- Ajout d'alertes automatiques
- Interface web pour monitoring
- Déploiement sur serveur de production
