# CS-391 - Definir Le Contrat narrative_natal_reading_v1

<!-- Commentaire global: ce brief cadre le contrat public de lecture narrative natale avant implementation. -->

## Resume

Definir un contrat versionne `narrative_natal_reading_v1` pour porter une lecture natale
grand public structuree en cinq chapitres narratifs et une justification astrologique
vulgarisee, sans exposer de codes moteur, scores, traces LLM ou payloads internes.

## Contexte

Le backend possede deja:

- `AstroResponseV3` pour une interpretation LLM longue;
- `structured_facts_v1`, `beginner_summary_v1` et
  `client_interpretation_projection_v1` pour les projections B2C;
- `llm_astrology_input_v1` pour alimenter le prompt natal moderne;
- `NarrativeAnswerAuditRepository` pour tracer et rejeter les sorties non fondees.

La page ne possede toutefois pas de contrat produit qui dise explicitement: « afficher les
conclusions, conserver les sources en justification repliee, ne jamais afficher le payload
interne ». Il faut definir ce contrat avant de modifier la generation ou React.

## Objectif

Documenter et typer `narrative_natal_reading_v1` avec:

1. `personality`
2. `emotional_world`
3. `relationships`
4. `vocation`
5. `evolution_path`
6. `used_astrological_elements`

La politique editoriale cible est:

```text
80 % interpretation
20 % justification astrologique vulgarisee
```

## Perimetre inclus

1. Definir le schema de lecture narrative et sa version.
2. Definir pour chaque chapitre: titre, contenu narratif, points cles optionnels et
   references de grounding backend-only.
3. Definir `used_astrological_elements` comme liste courte vulgarisee:
   libelle astrologique lisible + consequence synthetique, sans score ni trace de calcul.
4. Definir une denylist de surfaces publiques interdites: codes moteur, scores,
   `explanation_facts` bruts, `interpretive_signal_ids`, `audit_input`, prompts, metadata
   provider et payloads runtime.
5. Definir la compatibilite de persistance et de relecture avec les interpretations
   acceptees existantes.
6. Produire un ADR ou document de contrat avec exemples JSON free/basic/premium.

## Hors perimetre

- Implementer le builder ou modifier le prompt.
- Modifier `/natal`.
- Modifier `structured_facts_v1` ou supprimer les projections existantes.
- Reexposer `evidence_refs` dans le JSON public.

## Sources obligatoires

- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `_condamad/reports/cs-390-audit-architecture-lecture-natale.md`

## Livrables attendus

Creer:

```text
backend/docs/narrative-natal-reading-v1-contract.md
backend/docs/examples/narrative-natal-reading-v1-free.json
backend/docs/examples/narrative-natal-reading-v1-basic.json
backend/docs/examples/narrative-natal-reading-v1-premium.json
```

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - `chart_json` et `natal_data` ne redeviennent pas prompt-visible.
  - `RG-150` - les payloads rejetes restent exclus de la relecture publique.
- Needs-investigation invariants:
  - Registry gap: aucun invariant ne protege encore le contrat public narratif
    `narrative_natal_reading_v1`.
- Required regression evidence:
  - `pytest -q backend/tests/architecture/test_ai_narrative_input_boundary.py backend/tests/architecture/test_rejected_narrative_answer_boundary.py`
  - `rg -n "chart_json|natal_data|evidence_refs|audit_input|interpretive_signal_ids|technical_scores|prompt_payloads" backend/docs/narrative-natal-reading-v1-contract.md backend/docs/examples`
- Allowed differences:
  - Nouveau contrat documentaire uniquement.

## Criteres d'acceptation

1. Les cinq chapitres narratifs sont definis et ordonnes.
2. `used_astrological_elements` est defini comme justification vulgarisee de fin de lecture.
3. La denylist publique interdit explicitement les surfaces techniques et d'observabilite.
4. Les exemples free/basic/premium montrent une profondeur differenciee sans changer
   l'architecture de lecture.
5. Le document explique la relation avec `AstroResponseV3`, les interpretations persistees
   et `narrative_answer_audit_v1`.
6. Aucun ancien carrier prompt n'est reintroduit.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests/architecture/test_ai_narrative_input_boundary.py tests/architecture/test_rejected_narrative_answer_boundary.py
```

## Dependances

- CS-390.

## Risques

Le risque principal est de creer un nouveau payload concurrent sans relation claire avec
`AstroResponseV3`. Le document doit choisir un owner canonique et decrire la migration.
