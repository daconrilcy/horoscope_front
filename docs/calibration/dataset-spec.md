# Spécification du Dataset de Calibration

## En-tête
- **dataset_version**: 1.0.0
- **Date de création**: 2026-03-08
- **Auteur**: Cyril (BMAD Dev Agent)

## Panel de profils natals
Ce dataset s'appuie sur 5 profils natals représentatifs pour couvrir une diversité de contextes astronomiques et géographiques.

| Label | Signe Solaire | Ascendant | Timezone | Lat/Lon |
| :--- | :--- | :--- | :--- | :--- |
| profile_paris_aries | Bélier | Lion | Europe/Paris | 48.85 / 2.35 |
| profile_london_scorpio | Scorpion | Taureau | Europe/London | 51.51 / -0.13 |
| profile_new_york_cancer | Cancer | Capricorne | America/New_York | 40.71 / -74.01 |
| profile_tokyo_capricorn | Capricorne | Cancer | Asia/Tokyo | 35.68 / 139.69 |
| profile_stockholm_aquarius | Verseau | Vierge | Europe/Stockholm | 59.33 / 18.07 |

## Plage temporelle
- **Date de début**: 2024-01-01
- **Date de fin**: 2024-12-31
- **Durée**: 366 jours (année bissextile)
- **Politique des jours invalides**: En cas d'éphémérides manquantes ou d'interruption du job, le jour est marqué comme `invalid` dans les résultats et exclu des agrégations de calibration.

## Versions moteur fixées
*Note: Ces versions sont lues dynamiquement depuis la configuration active au moment du run.*

- **reference_version**: 1.0.0
- **ruleset_version**: 1.0.0

## Liste des catégories actives couvertes
Le dataset couvre l'ensemble des catégories définies dans le moteur de prédiction :
- Amour / Relations
- Travail / Carrière
- Vitalité / Énergie
- Finances / Matériel

## Politique des jours invalides
Toute anomalie de calcul (SwissEph inaccessible, erreur de parsing) entraîne l'invalidation du jour pour le profil concerné. Le dataset de calibration exige une continuité > 95% pour être considéré comme valide pour une campagne.

## Changelog du dataset
- **2026-03-08 (v1.0.0)**: Création initiale de la spécification avec 5 profils de base.
