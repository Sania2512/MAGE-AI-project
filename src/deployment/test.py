from deployment.inference import MaintenancePredictor


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
        # Entre normal et panne
        {'temperature': 74, 'pression': 4.4, 'vitesse': 800},
        # Entre normal et panne
        {'temperature': 76, 'pression': 4.0, 'vitesse': 880},
        # Entre normal et panne
        {'temperature': 70, 'pression': 4.5, 'vitesse': 750},

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
        {'temperature': 55, 'pression': 3.42,
            'vitesse': 600},  # Tout minimum normal
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
            result = predictor.predict_sequency(data)
            print(
                f"   Test {i}: {data} → {result['status']} (Prob: {result['probability']:.3f})")

        print("\n✅ PIPELINE TERMINÉ AVEC SUCCÈS!")

    except Exception as e:
        print(f"\n❌ ERREUR DANS LE PIPELINE: {e}")
        raise


if __name__ == "__main__":
    main()
