# Déversionner les référentiels structurels astrologiques

## Objectif

Refactoriser le modèle des données de référence astrologiques pour que `reference_version_id` n'impacte plus les tables structurelles invariantes du thème astrologique.

## Contexte

Les tables structurelles `planets`, `signs`, `houses`, `aspects` et `astro_points` représentent le vocabulaire astrologique stable. Les dupliquer par `reference_version_id` mélange ce vocabulaire avec les paramètres d'un moteur/version de calcul et produit des doublons.

Les tables paramétrables/versionnées doivent rester rattachées à `reference_version_id` ou à un `ruleset` quand leur contenu métier peut varier.

## Acceptance Criteria

1. Les tables structurelles `planets`, `signs`, `houses`, `aspects` et `astro_points` ne portent plus `reference_version_id` dans les modèles SQLAlchemy et le schéma migré.
2. Les contraintes d'unicité des tables structurelles sont stables par code/numéro, sans dimension de version.
3. Les tables paramétrables/versionnées conservent un rattachement versionné pertinent: `planet_profiles`, `house_profiles`, `aspect_profiles`, `sign_rulerships`, `prediction_categories`, `planet_category_weights`, `house_category_weights`, `point_category_weights`, `prediction_rulesets`, `ruleset_event_types`, `ruleset_parameters`.
4. Le seed de référence ne clone plus les tables structurelles par version et reste idempotent.
5. Les repositories lisent les référentiels structurels sans filtrage par version, mais continuent de filtrer les profils, poids, catégories et rulesets par version.
6. Des tests ou gardes empêchent la réintroduction de `reference_version_id` sur les tables structurelles et vérifient l'absence de doublons structurels.

## Non-goals

- Ne pas changer le moteur de calcul astrologique.
- Ne pas modifier l'API publique hors conséquence directe du schéma.
- Ne pas ajouter de nouvelle dépendance.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - les données de référence astrologiques ne doivent pas recréer de surfaces génériques ou duplicatives.
- Required regression evidence:
  - Tests des repositories/migrations de données de référence.
  - Scan ciblé de `reference_version_id` sur les tables structurelles.
