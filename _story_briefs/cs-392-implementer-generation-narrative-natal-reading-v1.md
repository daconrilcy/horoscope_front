# CS-392 - Implementer La Generation narrative_natal_reading_v1

<!-- Commentaire global: ce brief cadre l'implementation backend de la lecture narrative natale. -->

## Resume

Implementer le contrat `narrative_natal_reading_v1` defini par CS-391 dans le runtime natal
moderne. La sortie acceptee doit raconter le theme en cinq chapitres et fournir une courte
justification astrologique vulgarisee, avec validation stricte et rejet des sorties qui
exposent des donnees techniques interdites.

## Contexte

`llm_astrology_input_v1` contient deja la richesse astrologique necessaire et
`NatalInterpretationService` persiste les interpretations acceptees ou route les rejets vers
`NarrativeAnswerAuditRepository`. Cette story doit exploiter cette architecture, pas ajouter
un second pipeline LLM.

## Objectif

Faire de la generation natale moderne la source canonique d'une lecture narrative structuree:

- personnalite;
- monde emotionnel;
- relations;
- vocation;
- chemin d'evolution;
- ce que nous avons utilise.

## Perimetre inclus

1. Ajouter le schema Pydantic versionne de sortie narrative.
2. Aligner l'assembly/prompt natal nominal pour demander les cinq chapitres dans l'ordre.
3. Ajouter une validation de sortie qui refuse codes moteur, scores, traces calculatoires,
   payloads internes et observabilite LLM dans les champs utilisateur.
4. Produire `used_astrological_elements` depuis des libelles vulgarises, jamais depuis une
   serialisation brute de `explanation_facts`.
5. Persister et relire le schema sans contourner les gardes accepted/rejected.
6. Ajouter des fixtures et tests free/basic/premium, dont un rejet sur fuite technique.
7. Conserver `llm_astrology_input_v1` et `evidence_refs` comme surfaces backend-only.

## Hors perimetre

- Modifier React ou CSS.
- Modifier les calculs astrologiques.
- Appeler un provider reel pendant les tests.
- Ajouter un fallback legacy ou un second use-case provider-capable.

## Sources obligatoires

- `backend/docs/narrative-natal-reading-v1-contract.md`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/**`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - conserver la taxonomie prompt-generation et l'absence de carriers legacy.
  - `RG-150` - ne jamais deserialiser ni exposer les rejets comme interpretations valides.
- Needs-investigation invariants:
  - Registry gap: ajouter apres livraison un invariant durable sur la denylist publique
    narrative si la story cree ce nouveau contrat runtime.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_natal_interpretation_stored_payload.py backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py backend/tests/integration/test_rejected_narrative_answer_audit.py`
  - `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`
  - `rg -n "chart_json|natal_data|technical_scores|prompt_payloads|audit_input|interpretive_signal_ids" backend/app/services/llm_generation/natal backend/app/domain/llm`
- Allowed differences:
  - Nouveau schema de sortie narrative versionne et adaptation du prompt natal nominal.

## Criteres d'acceptation

1. Les sorties acceptees contiennent exactement les cinq chapitres attendus.
2. Les chapitres privilegient l'interpretation et ne contiennent pas de codes moteur.
3. `used_astrological_elements` contient des libelles lisibles et une consequence courte.
4. Une fixture contenant `visibility_expression`, `condition_axis:constraint`,
   `centrality score`, `audit_input` ou `interpretive_signal_ids` est rejetee.
5. Les rejets sont persistes sous `narrative_answer_audit_v1` et restent absents des routes
   publiques POST/GET/LIST.
6. Les tests provider-payload prouvent que `llm_astrology_input_v1` reste la source canonique.
7. Aucun fallback legacy n'est introduit.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py tests/integration/test_rejected_narrative_answer_audit.py
python -B -m pytest -q tests/llm_orchestration --tb=short -k "natal or theme_astral"
```

## Dependances

- CS-391.

## Risques

Le risque principal est d'ajouter un schema sans fermer le chemin de relecture persistee ou
de laisser passer des fuites techniques dans du texte libre. La validation doit etre
exercee avant persistance et lors de la deserialisation.
