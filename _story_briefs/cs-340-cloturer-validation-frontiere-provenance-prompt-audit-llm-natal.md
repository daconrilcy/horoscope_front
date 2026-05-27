# CS-340 - Cloturer La Validation Frontiere Provenance Prompt Audit LLM Natal

<!-- Commentaire global: ce brief cadre la preuve finale apres correction de la fuite audit-only vers le prompt LLM natal. -->

## Resume

Produire une validation de cloture apres CS-339 pour prouver que la frontiere `prompt_visible` / `audit_only` de `llm_astrology_input_v1` est coherente dans le code, les tests, les scans et la documentation operationnelle.

Cette story ne doit pas reimplementer la correction. Elle doit verifier que la correction est complete, que les guards sont pertinents, et que les preuves de livraison CS-330 a CS-338 ne masquent plus l'incoherence initiale autour de `provenance`.

## Contexte

CS-339 doit retirer les donnees audit-only du payload prompt-visible. Une validation separee est utile car le finding initial etait invisible aux tests existants: les tests verrouillaient eux-memes l'exposition de `provenance.llm_input_hash` dans le prompt.

La cloture doit donc verifier les tests, mais aussi leur intention.

## Prerequis

La story suivante doit etre terminee:

- CS-339 - Aligner provenance audit-only hors prompt LLM natal.

## Source obligatoire

Lire avant validation:

- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md`

## Objectif

Prouver que la frontiere finale est claire:

- prompt LLM natal: uniquement les blocs prompt-visibles utiles a la generation;
- audit narratif: hashes, version de contrat, preuves et provenance complete;
- runtime legacy: aucun retour de `chart_json` / `natal_data` dans le prompt natal moderne.

## Perimetre inclus

1. Scanner le gateway et les tests pour verifier qu'aucun test n'exige plus `provenance.llm_input_hash` dans le prompt.
2. Verifier que les tests de payload final inspectent le message juste avant handoff provider.
3. Verifier que les tests d'audit prouvent toujours la presence de `projection_hash` et `llm_input_hash` dans l'audit persistant.
4. Verifier que les tests de hash prouvent toujours:
   - invalidation sur changement prompt-visible;
   - stabilite sur donnee runtime-only ou audit-only non prompt-visible.
5. Scanner les prompts, schemas et registries natals pour confirmer qu'aucun placeholder `provenance`, `projection_hash` ou `llm_input_hash` n'est requis par un use case natal moderne.
6. Produire un rapport de validation dans `_condamad/reports`.
7. Classer les occurrences restantes de `projection_hash`, `llm_input_hash` et `provenance`:
   - audit/persistence ownerise;
   - contrat interne non prompt;
   - test de garde;
   - dette a corriger.

## Hors perimetre

- Modifier la correction CS-339 sauf bug bloquant detecte pendant validation.
- Reprendre l'extinction legacy `chart_json` / `natal_data` deja couverte par CS-338.
- Modifier les prompts editoriaux sans lien direct avec la frontiere prompt/audit.
- Produire un appel provider reel.
- Modifier le frontend.

## Livrable attendu

Creer un rapport:

```text
_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/<YYYY-MM-DD-HHMM>/validation-frontiere-provenance.md
```

Le rapport doit contenir:

1. Resume de la correction verifiee.
2. Definition finale des blocs prompt-visibles.
3. Definition finale des champs audit-only.
4. Liste des fichiers runtime/test verifies.
5. Resultats de scans.
6. Commandes de validation executees.
7. Risques residuels.

## Criteres d'acceptation

1. Le rapport de validation existe au chemin attendu.
2. Les tests ne verrouillent plus l'exposition de `provenance.llm_input_hash` dans le prompt.
3. Le payload final envoye au provider ne contient aucun champ audit-only.
4. L'audit persistant continue de contenir `projection_hash`, `llm_input_hash`, `llm_input_version`, `grounding_status` et `evidence_refs`.
5. Les use cases natals modernes ne declarent aucun placeholder de hash ou de provenance.
6. Les validations backend passent.
7. Les occurrences restantes sont classees et non ambiguës.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short
pytest -q tests --tb=short
rg -n "provenance|projection_hash|llm_input_hash|audit_only|prompt_visible" app tests ..\_condamad ..\_story_briefs
rg -n "{{provenance}}|{{projection_hash}}|{{llm_input_hash}}" app tests
```

La validation ne doit pas exiger une absence totale de `projection_hash`, `llm_input_hash` ou `provenance`: ces termes sont attendus dans l'audit, les contrats internes, les tests de hash et les rapports. Elle doit prouver qu'ils ne sont plus dans le prompt natal moderne.

## Risques

Le risque principal est de confondre la presence legitime des hashes dans l'audit avec une fuite prompt. Le rapport doit donc distinguer l'objet complet `llm_astrology_input_v1`, sa projection prompt-visible, et les champs persistants d'audit.

