# CS-413 - Integrer Basic Natal V2 Avec Persistance Cache Et QA

<!-- Commentaire global: ce brief cadre l'integration finale du moteur Basic natal versionne, de la persistance et de la QA. -->

## Resume

Brancher le pipeline Basic V2 de bout en bout: construction du plan, payload LLM contraint,
validation narrative, persistance versionnee, invalidation des anciennes lectures Basic et QA
runtime. Cette story ferme la sequence sans maintenir deux logiques Basic concurrentes.

## Contexte

Le plan source prevoit une strategie de remplacement hors production: incrementer
`schema_version` et `engine_version`, rendre les anciennes interpretations Basic incompatibles
avec le nouveau mode, regenerer a la demande et ne pas melanger l'ancien format `short` avec
le nouveau `basic`.

## Objectif

Garantir:

```text
Basic + complete + natal/interpretation
=> basic-natal-reading-v1
=> basic_natal_interpretation_v2
=> narrative_natal_reading_v1 public valide
```

Les anciennes lectures Basic incompatibles doivent etre ignorees ou regenerees selon la
politique existante, sans consommer le quota avant acceptation.

## Perimetre Inclus

1. Brancher le builder de `BasicNatalReadingPlan` dans le service d'interpretation Basic
   complete.
2. Brancher le payload LLM contraint et le validateur post-generation.
3. Persister `engine_version`, `schema_version`, version de taxonomie, version de salience,
   version de prompt et version de validateur.
4. Invalider les interpretations Basic precedentes quand les versions different.
5. Eviter toute coexistence active de deux logiques Basic concurrentes.
6. Ajouter un test d'integration avec gateway fake sur lecture complete valide.
7. Ajouter un test d'integration sur ancienne lecture Basic incompatible et regeneration.
8. Produire un rapport QA backend/frontend avec preuves runtime et scans de non-fuite.

## Hors Perimetre

- Migrer progressivement toutes les donnees existantes.
- Refaire l'UI complete `/natal`.
- Modifier les droits commerciaux.
- Declencher des appels provider reels non controles.
- Ajouter une nouvelle offre Premium.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-404-definir-contrats-versionnes-lecture-natale-basic-v2.md`
- `_story_briefs/cs-410-construire-reading-plan-basic-natal-inspectable.md`
- `_story_briefs/cs-411-contraindre-payload-llm-basic-par-reading-plan.md`
- `_story_briefs/cs-412-valider-et-reparer-narrative-basic-natal.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - le processus natal moderne reste gouverne et documente.
  - `RG-150` - les rejets restent exclus du public.
  - `RG-152` - les lectures acceptees exposent le narratif public sans fuites techniques.
  - `RG-153` - la page `/natal` reste centree sur la lecture narrative.
  - `RG-154` - la denylist DOM publique reste active.
  - `RG-155` - pas de padding semantique ni sources vides.
  - `RG-156` - la matiere Basic reste diversifiee.
  - `RG-157` - quota consomme seulement apres acceptation.
  - `RG-158` - les accordeons narratifs modernes restent le rendu attendu.
- Required regression evidence:
  - `pytest -q backend/tests/integration/test_basic_natal_v2_pipeline.py`
  - `pytest -q backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "natal_interpretation_short|basic_natal_interpretation_v2|basic-natal-reading-v1" backend/app backend/tests frontend/src`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant l'usage runtime de `basic-natal-reading-v1` pour Basic
    complete.
- Allowed differences:
  - Les anciennes lectures Basic incompatibles sont regenerees a la demande.
  - Les nouvelles metas affichent `basic_natal_interpretation_v2` et
    `basic-natal-reading-v1`.

## Criteres D'acceptation

1. Une nouvelle lecture Basic complete passe par le pipeline V2 complet.
2. Le cache ne ressert pas une ancienne lecture Basic incompatible.
3. Une sortie invalide est rejetee et non publique.
4. Le quota est consomme exactement apres acceptation valide.
5. Les metas persistees permettent d'auditer les versions du moteur.
6. Le frontend affiche la lecture narrative sans fallback legacy ni fuite technique.
7. La QA distingue fixture, cache, provider fake et eventuel provider reel controle.
8. Aucune logique `short` legacy ne reste active pour Basic complete.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short
python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
```

Frontend:

```powershell
cd frontend
pnpm test -- NatalChartPage natalNarrativeReading natalPublicDomGuard
pnpm lint
pnpm build
```

## Dependances

- CS-404.
- CS-405.
- CS-406.
- CS-407.
- CS-408.
- CS-409.
- CS-410.
- CS-411.
- CS-412.
- CS-398.
- CS-399.
- CS-401.
- CS-402.
- CS-403.

## Risques

Le risque principal est une integration qui valide seulement des fixtures unitaires. La story
doit inclure une preuve de bout en bout avec gateway fake et une QA runtime qui distingue
explicitement cache, regeneration et acceptation.
