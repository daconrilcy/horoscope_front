# Code Review

## Sous-agent

Revue independante: Mendel (`019e2879-f45e-77d0-aee8-382792293c31`).

## Findings traites

- Catalogues hardcodes restants dans `ReferenceRepository`: corriges via `structural_reference_catalog.json` et `astral_systems.json`.
- Audit persistant manquant: ajoute et enrichi dans `astrology-duplication-audit.md`.
- Garde anti-retour trop faible: durcie avec les noms locaux `planet_rows`, `sign_rows`, `dignity_type_rows`, `house_rows` et les scans associes.
- Changement de shape public `sign_rulerships`: retire du payload `ReferenceDataService`; injection gardee localement dans `NatalCalculationService`.
- Migration 0107 hardcodant les aspects: corrigee pour lire `aspects.json` et `astral_aspect_families.json`.
- Littéral succedent dans `natal_sensitivity`: remplace par `SUCCEDENT_HOUSE_NUMBERS`.
- Commit implicite dans `NatalCalculationService.calculate`: corrige par une resynchronisation stable locale sans `commit`.
- Seed stable superficiellement complet: corrige par une synchronisation systematique des catalogues JSON canoniques et par une regression testant les valeurs obsoletes.
- Migration 0107 dependante de `OR IGNORE` SQLite: corrigee par un test d'existence portable avant insertion.
- QA/regression prediction: fixtures et snapshots recalibres apres activation des references completes.
- Cycle 2: aucun finding fonctionnel nouveau; ajout d'une assertion explicite bloquant l'exposition publique de `sign_rulerships` et alignement du libelle de test sur la synchronisation JSON.

## Findings residuels

Pas de finding de revue CS-171 reste ouvert.
