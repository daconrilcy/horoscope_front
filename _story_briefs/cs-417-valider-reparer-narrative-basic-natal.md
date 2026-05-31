# CS-417 - Valider Et Reparer La Narrative Basic Natale

<!-- Commentaire global: ce brief cadre le validateur post-generation de la lecture natale Basic. -->

## Resume

Ajouter la validation post-generation du `NarrativeDraft` Basic contre le `ReadingPlan`. Une
sortie LLM qui invente des faits, expose des scores, oublie des sections, melange les
personnes grammaticales ou contient des conseils prescriptifs doit etre reparee ou rejetee.

## Contexte

Le plan source impose un `NarrativeValidator` avec controles obligatoires et strategie
d'echec: reparation contrainte, puis fallback deterministe court, puis journalisation avec
`request_id`, `engine_version` et `validation_errors`.

## Objectif

Garantir que la sortie acceptee:

- respecte toutes les sections demandees;
- n'ajoute pas de section interdite;
- ne mentionne que des faits presents dans le plan;
- n'expose aucun score ou champ technique;
- reste en `vous`;
- respecte la longueur maximale;
- contient limitations et disclaimers;
- evite conseils medicaux, juridiques, financiers ou psychologiques prescriptifs.

## Perimetre Inclus

1. Etendre ou creer le validateur Basic contre `BasicNatalReadingPlan`.
2. Ajouter des erreurs de validation structurees et auditables.
3. Ajouter une tentative de reparation par prompt contraint.
4. Ajouter un fallback deterministe court uniquement si la reparation echoue, sans padding
   semantique ni sources vides.
5. Journaliser `request_id`, `engine_version`, `schema_version` et `validation_errors`.
6. Rejeter les sorties qui introduisent des faits non supportes ou des marqueurs techniques.
7. Ajouter des tests de rejet pour scores internes, jargon non explique, Ascendant sans
   heure, section vocation non prouvee et melange de personnes.
8. Verifier que les rejets restent hors routes publiques.

## Hors Perimetre

- Refaire le builder de plan.
- Modifier la page `/natal`.
- Modifier les quotas, sauf verification de non-consommation avant acceptation.
- Ajouter des appels provider reels en test.
- Accepter des schemas V1/V2 pour Basic complete.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - les rejets restent sous audit et hors routes publiques.
  - `RG-152` - la lecture complete acceptee n'expose pas les details techniques.
  - `RG-154` - la denylist DOM publique reste couverte.
  - `RG-155` - pas de padding semantique, chapitres dupliques ou sources vides.
  - `RG-157` - le quota n'est consomme qu'apres acceptation valide.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_basic_natal_narrative_validator.py`
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
  - `rg -n "fallback = response\\.sections\\[0\\]|ranking_score|condition_axis|audit_input" backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant la validation Basic contre le plan de lecture.
- Allowed differences:
  - De nouveaux motifs de rejet audites apparaissent pour les sorties Basic invalides.

## Criteres D'acceptation

1. Une sortie qui oublie une section obligatoire est rejetee ou reparee.
2. Une sortie qui invente un fait absent du plan est rejetee.
3. Une sortie qui expose un score ou un identifiant technique est rejetee.
4. Une sortie date-only qui mentionne Ascendant, MC ou maisons est rejetee.
5. Une sortie valide conserve les disclaimers, limitations et sources publiques.
6. Deux echecs de validation aboutissent a rejet audite ou fallback court valide, pas a une
   acceptation silencieuse.
7. Le quota reste non consomme tant que la lecture n'est pas acceptee.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_basic_natal_narrative_validator.py --tb=short
python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
```

## Dependances

- CS-410.
- CS-411.
- CS-402.
- CS-398.

## Risques

Le risque principal est un fallback deterministe qui recree du padding generique. Le fallback
doit rester court, fonde sur les preuves publiques et refuser les sections sans source.
