# CS-289 — Implement evidence_refs Validation

## Résumé

Implémenter la validation des `evidence_refs` section par section.

## Contexte

CS-260 définit le contrat des preuves. Les références doivent pointer vers des sources validées et hashées, pas vers des chaînes décoratives.

## Objectif

Ajouter la validation technique des preuves utilisées par les réponses narratives.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les validateurs de provenance existants.
2. Valider que chaque `evidence_ref` pointe vers une source autorisée.
3. Vérifier le lien avec projection hashée ou entrée LLM hashée.
4. Ajouter les statuts de validation section par section.
5. Ajouter les tests de preuve absente, invalide et valide.

## Hors périmètre

- Implémenter un moteur sémantique complet.
- Exposer les preuves techniques au client.
- Créer une UI admin.
- Modifier les calculs astrologiques.

## Critères d'acceptation

1. Une `evidence_ref` décorative est rejetée.
2. Les sources validées et hashées sont acceptées.
3. Les sections sans preuve requise sont distinguées des sections invalides.
4. Les tests couvrent les statuts grounded, partial et ungrounded.
5. La validation s'intègre à `narrative_answer_audit_v1`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-260 pour le contrat.
- CS-288 pour la persistance d'audit.
- CS-264 pour `projection_hash`, si requis par l'implémentation retenue.

## Risques

Le risque principal est de valider uniquement la présence d'une chaîne. La validation doit prouver que la référence cible une source autorisée.



