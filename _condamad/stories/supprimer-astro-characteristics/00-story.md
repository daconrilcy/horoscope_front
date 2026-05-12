# Supprimer proprement `astro_characteristics`

## Goal

Supprimer proprement la table `astro_characteristics` et tous ses chemins actifs sans regression du moteur astrologique ni de l'API de donnees de reference.

## Context

La table `astro_characteristics` est actuellement peuplee avec deux traits decoratifs (`sun element fire`, `aries modality cardinal`) qui sont exposes dans le payload `characteristics` mais ne sont pas consommes par le moteur. Le code supporte aussi des traits d'aspect (`orb_luminaries`, `orb_pair_overrides`) via cette table, mais aucune donnee locale ne les utilise. Les overrides d'orbes restent supportes par les definitions d'aspects elles-memes et par le moteur natal.

## Acceptance Criteria

1. Le modele SQLAlchemy, les relations, les seeds, le clonage et les suppressions de version ne referencent plus `AstroCharacteristicModel`.
2. Le payload public de reference ne contient plus la cle `characteristics`; les aspects gardent `default_orb_deg` et le moteur continue de consommer les champs d'orbes presents directement dans les definitions d'aspects.
3. Une migration Alembic supprime `astro_characteristics` pour les bases existantes, sans casser le chemin de migration complet.
4. Les tests sont ajoutes ou adaptes pour verifier le nouveau contrat et l'absence de reintroduction active.
5. Les validations locales pertinentes passent avec le venv active: tests cibles, lint Ruff, scans No Legacy, et demarrage local ou instruction exacte si non lance.

## Explicit Non-goals

- Ne pas creer une nouvelle table `aspect_orb_overrides` dans cette story.
- Ne pas modifier le calcul natal ou le calculateur d'aspects hors retrait de la source DB obsolete.
- Ne pas ajouter de compatibilite, shim, alias, fallback ou re-export pour `astro_characteristics`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - RG-010 - les tests backend doivent rester dans les racines collectees.
  - RG-011 - les nouveaux tests backend doivent utiliser le harnais DB canonique.
- Required regression evidence:
  - Tests cibles reference data et migrations.
  - Scan zero-hit actif pour `AstroCharacteristicModel` et `astro_characteristics` hors migration historique et preuves CONDAMAD.
- Allowed differences:
  - Le payload public perd volontairement la cle decorative `characteristics`.
