# CS-346 - Audit Inputs Astrologiques Natals Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit des donnees astrologiques qui alimentent le prompt natal moderne. -->

## Resume

Auditer la construction de `llm_astrology_input_v1` et les projections astrologiques qui alimentent le prompt natal moderne.

## Contexte

Le gateway ne doit pas inventer de contexte astrologique. Les donnees prompt-visibles viennent de builders et projections internes: `structured_facts_v1`, `AINarrativeInputContract`, `client_interpretation_projection_v1`, puis `LLMAstrologyInputV1Builder`.

## Objectif

Cartographier la source et le role de chaque bloc:

- `facts`;
- `signals`;
- `limits`;
- `shaping`;
- `evidence`;
- `provenance`;
- `exclusions`;
- `data_roles`.

## Perimetre inclus

1. Auditer `LLMAstrologyInputV1Builder`.
2. Auditer `StructuredFactsV1Builder`, `AINarrativeInputBuilder`, `ClientInterpretationProjectionV1Builder`.
3. Auditer les helpers de hash et de conversion JSON.
4. Auditer les regles prompt-visible, runtime-only, validation-only, audit-only.
5. Auditer le branchement depuis `NatalInterpretationService` et `AIEngineAdapter`.
6. Auditer les tests de hash, evidence, frontieres payload et legacy.
7. Produire une cartographie bloc par bloc.

## Hors perimetre

- Modifier les calculs astrologiques.
- Ajouter des champs au contrat.
- Changer la politique de hash.
- Modifier les prompts ou le gateway.

## Sources a lire

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`

## Fichiers a inspecter en priorite

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/projections/projection_hash.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/04-natal-astrology-input-audit.md
```

Le document doit contenir:

1. Source map des builders.
2. Description de chaque bloc du contrat.
3. Classification prompt-visible vs backend-only.
4. Politique de hash actuelle.
5. Politique evidence actuelle.
6. Chemins legacy bloques.
7. Tests existants et gaps.

## Criteres d'acceptation

1. Chaque bloc `llm_astrology_input_v1` a un owner et une source.
2. Les champs prompt-visibles sont distingues des champs d'audit.
3. `chart_json` et `natal_data` sont classes comme carriers legacy interdits pour le prompt natal moderne.
4. La politique de hash est expliquee avec les blocs inclus.
5. Les implications CS-341/CS-342 sont integrees.

## Validation attendue

```powershell
rg -n "LLMAstrologyInputV1Builder|build_llm_input_hash_material|PROMPT_INFLUENCING_BLOCKS|LLM_ASTROLOGY_INPUT_DATA_ROLES|structured_facts_v1|AINarrativeInput|client_interpretation_projection_v1" backend/app backend/tests
rg -n "natal-astrology-input-audit" _condamad
```

## Risques

Le risque principal est de traiter `evidence` comme prompt-visible si CS-341 n'est pas encore terminee. Le livrable doit indiquer l'etat observe et la dependance exacte.

