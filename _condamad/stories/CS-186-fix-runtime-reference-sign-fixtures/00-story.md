# Story CS-186 fix-runtime-reference-sign-fixtures: Corriger les fixtures de signes runtime

## Goal

Corriger les tests backend qui échouent parce que des fixtures de références runtime astrologiques fournissent encore des signes partiels sans `element`, `modality` et `polarity`.

## Context

Après CS-185, `runtime_reference_from_mapping()` refuse volontairement les fixtures de signes partielles pour éviter de masquer le contrat DB-backed des profils de signes. Plusieurs tests historiques de calcul natal et de métadonnées créent encore des payloads `{code, name}` ou `{code}`.

## Acceptance Criteria

- AC1: Les tests listés par l'utilisateur ne doivent plus échouer sur `ValueError: sign fixture aries requires profile fields`.
- AC2: `runtime_reference_from_mapping()` continue de refuser les signes partiels; aucune complétion silencieuse n'est réintroduite dans cette factory.
- AC3: Les fixtures appelantes utilisent un helper de test explicite et centralisé pour construire des signes complets avec `element`, `modality` et `polarity`.
- AC4: Les guardrails applicables `RG-107`, `RG-108`, `RG-112` et `RG-114` restent respectés.
- AC5: Les validations ciblées, lint et tests backend pertinents passent avec le venv activé.

## Explicit Non-Goals

- Ne pas modifier le runtime applicatif, les repositories DB ou les données de seed.
- Ne pas réintroduire `SIGN_PROFILE_DATA` ni un fallback depuis le seed dans les tests runtime.
- Ne pas modifier les changements utilisateur préexistants sur les modèles DB, migrations ou JSON de seed.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - le runtime reference doit rester typé et sans payload métier libre.
  - `RG-108` - pas de nouveau vocabulaire métier applicatif DB-backed dans `backend/app`.
  - `RG-112` - pas de constantes astrologiques hardcodées applicatives.
  - `RG-114` - les profils structurels de signes ne doivent pas être masqués par des fixtures partielles ou fallbacks silencieux.
- Required regression evidence:
  - Tests ciblés des fichiers en échec.
  - Garde `app/tests/unit/test_astrology_runtime_reference_guard.py`.
  - Scan ciblé des constantes/fallbacks interdits dans `app/domain/astrology` et `app/services/natal`.
