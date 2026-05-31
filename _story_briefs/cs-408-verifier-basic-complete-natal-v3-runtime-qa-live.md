# CS-408 - Verifier Basic Complete Natal V3 En Runtime Et QA Live

<!-- Commentaire global: ce brief cadre la preuve de bout en bout que Basic complete utilise bien le pipeline natal V3. -->

## Resume

Produire une preuve runtime et QA authentifiee que le compte Basic n'utilise plus le pipeline
free/V1 pour la lecture natale complete. La validation doit couvrir la resolution d'assembly,
les metadonnees gateway, la persistance, le rejet des sorties non conformes, la non
consommation de quota en cas de rejet et l'affichage public sans fuite technique.

## Contexte

Les indices actuels d'une mauvaise route sont:

```text
schema_version: "v2"
repair_attempted: false
prompt_version_id: id d'assembly free/short
validation_status: "rejected" apres projection CS-396
```

Apres CS-401 et CS-402, une lecture Basic complete nominale doit montrer:

```text
use_case: natal_interpretation
assembly target: natal/interpretation/basic/fr-FR
output schema: AstroResponse_v3
schema_version: v3
narrative_natal_reading_v1: present
used_astrological_elements: non vide
quota consomme uniquement apres acceptation
```

## Perimetre Inclus

1. Ajouter un test d'integration sans appel provider reel avec gateway fake prouvant le
   contrat Basic complete V3.
2. Ajouter une preuve de seed/catalogue que `natal/interpretation/basic` existe et reste
   publie.
3. Ajouter ou mettre a jour une fixture de sortie V3 Basic valide.
4. Tester une sortie V1/V2 courte injectee dans le chemin Basic complete et verifier le rejet.
5. Tester les champs meta publics: `use_case`, `schema_version`, `validation_status`,
   `repair_attempted`, `fallback_triggered`.
6. Executer une QA navigateur authentifiee avec l'utilisateur test si l'environnement local
   permet un appel controle.
7. Mettre a jour le rapport de cloture QA natal pour documenter l'avant/apres.
8. Verifier que le frontend ne reintroduit aucun fallback legacy pour masquer l'absence de
   lecture narrative.

## Hors Perimetre

- Declencher des appels provider reels non controles.
- Modifier les styles frontend.
- Modifier les quotas commerciaux.
- Refaire la page `/natal`.
- Modifier les calculs astrologiques.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-406-router-basic-complete-assembly-natale-v3.md`
- `_story_briefs/cs-407-refuser-downgrade-schema-v3-lecture-natale-complete.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - le flux natal moderne doit rester gouverne par assembly et documente.
  - `RG-150` - les rejets restent hors routes publiques.
  - `RG-152` - la lecture complete acceptee expose `narrative_natal_reading_v1`.
  - `RG-153` - la page `/natal` reste composee autour de la lecture narrative.
  - `RG-154` - la denylist DOM publique reste active.
  - `RG-155` - pas de padding semantique ni sources vides.
  - `RG-156` - Basic conserve une matiere editoriale diversifiee.
  - `RG-157` - quota consomme seulement apres acceptation.
  - `RG-158` - les accordeons narratifs modernes restent le rendu attendu.
- Required regression evidence:
  - `pytest -q backend/tests/integration/test_natal_basic_complete_v3_runtime.py` (nouveau test attendu)
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` (nouveau test attendu)
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - Rapport QA avec captures si serveur local disponible.
- Allowed differences:
  - Les anciennes lectures Basic invalides peuvent etre exclues du cache et forcees en
    regeneration corrective.
  - Les metas publiques passent de `schema_version=v2` a `schema_version=v3` sur les
    nouvelles lectures Basic complete valides.

## Criteres D'acceptation

1. Une generation Basic complete nouvelle utilise `natal_interpretation`, pas
   `natal_interpretation_short`.
2. La cible d'assembly observee est `natal/interpretation/basic/fr-FR`.
3. Le schema gateway et le schema service sont V3.
4. `repair_attempted=false` sur une sortie valide ne masque plus une validation V1.
5. Une sortie V1/V2 courte injectee est rejetee, auditee et non publique.
6. Le quota n'est pas consomme pour le rejet et l'est exactement une fois pour l'acceptation.
7. Le DOM public Basic contient la lecture narrative moderne et aucune fuite technique.
8. Le rapport QA mentionne explicitement la cause racine corrigee et les fichiers touches.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_natal_basic_complete_v3_runtime.py --tb=short
python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short
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

## QA Manuelle Indicative

Utilisateur test autorise:

```text
email: daconrilcy@hotmail.com
password: admin123
```

Verifier sur `/natal`:

1. Demander une lecture complete Basic apres correction.
2. Confirmer dans les logs/metas que `schema_version` vaut `v3`.
3. Confirmer que les cinq chapitres narratifs ont des sources non vides.
4. Confirmer que le DOM ne contient pas les champs techniques interdits par `RG-154`.

## Dependances

- CS-401.
- CS-402.
- CS-398 pour la preuve quota.
- CS-399 pour la preuve UI moderne.

## Risques

Le risque principal est une QA qui valide seulement une relecture cachee. La story doit
forcer une nouvelle generation ou une regeneration corrective controlee et distinguer cache,
fixture, provider fake et provider reel.
