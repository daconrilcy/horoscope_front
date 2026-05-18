# CS-183 - Corriger les échecs longs des prédictions daily liés aux aspects

## Source

Demande utilisateur du 2026-05-18: corriger les nombreux échecs de `pytest -q --long` observés sur les prédictions daily, le moteur de prédiction et les contrats d'aspects.

## Objectif

Réduire le lot d'échecs longs en corrigeant les causes racines visibles:

- la résolution d'orbes natales doit utiliser les règles ciblées par type/corps astrologique;
- la projection publique doit charger les profils d'aspects depuis l'identifiant de référence persistant du snapshot;
- les tests doivent respecter le contrat runtime canonique des profils et orbes d'aspects.

## Acceptance Criteria

1. Les calculs natals ne demandent plus une règle générique `natal any/any` quand les règles canoniques sont ciblées par type de corps.
2. Les routes daily publiques et QA internes ne cassent pas les snapshots persistés ou doubles de test à cause d'une résolution de référence par chaîne non alignée.
3. Les tests unitaires de sensibilité natale construisent des aspects complets selon le contrat runtime.
4. Les validations ciblées passent dans le venv PowerShell du projet.

## Non-goals

- Ne pas changer la stack.
- Ne pas ajouter de dépendance.
- Ne pas refondre le moteur de prédiction hors des surfaces nécessaires.
