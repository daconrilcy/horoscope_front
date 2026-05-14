<!-- Guardrails No Legacy et DRY specifiques a CS-162. -->

# No Legacy / DRY Guardrails

## Canonical paths

- `AstralSystemModel.inherits_from_system_id` porte l'heritage entre systemes.
- `AstralAspectOrbRuleModel` porte seulement les regles physiques locales et les overrides explicites.
- `backend/app/domain/astrology/calculators/aspects.py` resout local puis parent sans acceder a SQL.
- `ReferenceRepository.get_reference_data` expose les metadonnees d'heritage utiles au runtime.

## Forbidden legacy patterns

- `copy_rules_from` dans `docs/recherches astro/astral_aspect_orb_rules.json`.
- Copie physique complete des regles `traditional` dans `hellenistic` ou `medieval`.
- Fallback silencieux vers `modern`.
- Nouvelle table d'heritage parallele.
- `reference_version_id` sur `astral_systems`.
- Import `app.domain.prediction` ou `app.services.prediction` depuis `backend/app/domain/astrology`.
- Usage de `astro_characteristics` comme source d'orbes.

## Required negative evidence

- Scan zero-hit de `copy_rules_from` dans le JSON actif.
- Tests DB prouvant `modern = 39`, `traditional = 40`, `hellenistic = 0`, `medieval = 0` par version sans override enfant.
- Test cycle d'heritage avec erreur explicite.
- Scan zero-hit prediction depuis `app/domain/astrology`.
- Classification des hits `astro_characteristics|AstroCharacteristicModel` limitee aux guards historiques attendus.

## Applicable regression guardrails

- `RG-091`, `RG-092`, `RG-093`, `RG-094`, `RG-095`, `RG-096`, `RG-097`.

## Review checklist

- Un seul mecanisme d'heritage: la self-FK `astral_systems`.
- Aucun depliage seed ne recree les copies physiques enfant.
- Les overrides locaux enfant restent possibles et prioritaires.
- Le tri respecte local avant parent, puis priorite et specificite.
- Les docs ne presentent plus la recopie comme mecanisme supporte.
