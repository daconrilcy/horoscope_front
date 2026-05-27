# Validation frontiere provenance prompt audit LLM natal

<!-- Commentaire global: ce rapport cloture la preuve que la provenance audit-only reste hors du prompt LLM natal moderne. -->

## Resume de la correction verifiee

La validation CS-340 confirme que la correction CS-339 est effective apres review: le prompt natal moderne derive le payload provider depuis les blocs `prompt_visible` canoniques et ne transmet plus le bloc `provenance` complet au LLM. Le statut CS-339 est `done` dans `_condamad/stories/story-status.md`.

Le gateway conserve l'objet complet `llm_astrology_input_v1` comme source auditable, mais compose le message provider avec une projection prompt-visible nettoyee. Les champs de provenance, hash, grounding et preuves restent disponibles pour l'audit narratif et la persistance, sans etre transmis au provider.

La review d'implementation a trouve une fuite residuelle de `grounding_status`, `validation_owner` et `evidence_refs` dans le bloc `evidence` envoye au provider. La correction retire recursivement les cles audit/validation avant serialization et les tests de handoff les interdisent explicitement.

## Definition finale des blocs prompt-visible

Source canonique: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`.

Blocs autorises dans le prompt provider:

- `facts`
- `signals`
- `limits`
- `evidence`
- `shaping`

Le gateway lit `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` via `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS`, applique `_prompt_visible_llm_astrology_input(...)`, puis retire les cles audit/validation via `_without_prompt_excluded_keys(...)` avant la composition du message utilisateur.

## Definition finale des champs audit-only

Champs exclus du prompt moderne et conserves pour audit, contrat interne ou persistance:

- `provenance`
- `projection_hash`
- `llm_input_hash`
- `llm_input_version`
- `grounding_status`
- `evidence_refs`
- `provider_response`
- `persisted_answer`

`projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status` et `evidence_refs` sont prouves par `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`.

## Fichiers runtime et tests verifies

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`: roles canoniques `prompt_visible` / `audit_only` et bloc `provenance` audit.
- `backend/app/domain/llm/runtime/gateway.py`: projection provider `_prompt_visible_llm_astrology_input` et exclusion recursive des champs audit/validation.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`: registry des use cases modernes sans placeholders hash/provenance.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: lecture audit de la provenance et persistance des hashes.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`: payload final provider et message utilisateur inspectes avec double local; les champs audit/validation imbriques sont interdits.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`: guard AST contre divergence des roles et champs audit-only, y compris `grounding_status`, `validation_owner` et `evidence_refs`.
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`: audit persistant et stabilite hash runtime-only.

## Resultats de scans

Artifacts:

- Baseline: `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-before.txt`
- Apres validation: `_condamad/stories/CS-340-frontiere-provenance-prompt-audit/evidence/boundary-scan-after.txt`

Classification des occurrences restantes:

- audit/persistence owned: `interpretation_service.py`, `test_natal_llm_astrology_input_audit.py`, champs `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, `evidence_refs`.
- internal non-prompt contract: `llm_astrology_input_v1.py`, roles `prompt_visible` / `audit_only`, bloc complet `provenance`.
- guard test: `test_llm_astrology_input_boundaries.py` et `test_llm_astrology_input_payload_boundaries.py`, assertions negatives sur `provenance`, `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status`, `validation_owner`, `evidence_refs`, `provider_response`, `persisted_answer`, `chart_json`, `natal_data`.
- historical evidence: `_condamad/**` et `_story_briefs/**`, references de stories et rapports deja livres.
- debt to fix: aucune occurrence executable non classee detectee dans le perimetre de cette story.

Scan negatif des placeholders modernes:

- `rg -n "\{\{provenance\}\}|\{\{projection_hash\}\}|\{\{llm_input_hash\}\}" app tests`
- Resultat: `PASS: no matches`

## Commandes de validation executees

Toutes les commandes Python/Ruff/Pytest ont ete executees apres activation de `.\.venv\Scripts\Activate.ps1`.

- `python -B -c "...CS-339..."`: PASS, row CS-339 `done`.
- `ruff format app/domain/llm/runtime/gateway.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py`: PASS, 1 fichier reformate.
- `ruff format --check app tests`: PASS, 1465 fichiers deja formates.
- `ruff check .`: PASS.
- `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`: PASS, 24 passed, 9 deselected.
- `python -B -m pytest -q tests --tb=short`: PASS, 1211 passed, 221 deselected.
- `rg -n "provenance|projection_hash|llm_input_hash|audit_only|prompt_visible|evidence_refs|grounding_status" app tests ..\_condamad ..\_story_briefs`: PASS, resultats sauvegardes.
- `rg -n "\{\{provenance\}\}|\{\{projection_hash\}\}|\{\{llm_input_hash\}\}" app tests`: PASS, aucune occurrence.

## Risques residuels

- Aucun risque restant identifie dans le perimetre CS-340.
- Aucun appel provider reel n'a ete effectue; la preuve de handoff repose sur le double local inspectant le message juste avant la frontiere provider, conformement au non-goal.
