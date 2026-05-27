# CS-341 - Sortir Evidence Du Prompt Et Valider La Redaction LLM Natale

<!-- Commentaire global: ce brief cadre l'alignement final entre evidence interne, prompt LLM natal et validation post-generation. -->

## Resume

Finaliser la frontiere `evidence` du contrat `llm_astrology_input_v1`: les evidences ne doivent pas etre transmises au prompt engine, mais elles doivent rester disponibles cote backend pour valider la redaction obtenue du LLM.

La correction attendue retire `evidence` des blocs prompt-visibles, supprime le payload prompt `evidence: {}` vide, et renforce le process de validation post-generation afin que la reponse LLM soit controlee contre les faits, signaux, limites et preuves internes.

## Contexte

CS-339 et CS-340 ont corrige la fuite `provenance` / hashes audit-only vers le prompt natal moderne. La revue de cloture a toutefois identifie une ambiguite restante:

- `llm_astrology_input_v1` declare encore `evidence` dans `prompt_visible`;
- le gateway retire recursivement `evidence_refs`, `grounding_status` et `validation_owner`;
- le bloc `evidence` transmis au prompt devient donc `{}`;
- le test de handoff verrouille actuellement ce bloc vide.

La decision produit est maintenant claire: les evidences ne doivent pas etre envoyees au prompt engine. Elles doivent servir au controle backend de la redaction apres generation.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-340-cloturer-validation-frontiere-provenance-prompt-audit-llm-natal.md`
- `_condamad/reports/cs-339-cs-340-delivery-report.md`
- `_condamad/reports/frontiere-provenance-prompt-audit-llm-natal/2026-05-27-1407/validation-frontiere-provenance.md`

## Objectif

Etablir un process definitif:

- prompt engine: recoit uniquement la matiere utile a la redaction (`facts`, `signals`, `limits`, `shaping`);
- backend validation/audit: conserve `evidence`, `evidence_refs`, `grounding_status`, `validation_owner`, `projection_hash`, `llm_input_hash`;
- reponse LLM: contient une structure suffisante pour etre validee apres generation contre les donnees internes.

## Perimetre inclus

1. Retirer `evidence` de `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
2. Ajouter ou clarifier un role de donnees pour `evidence`, par exemple `validation_only` ou `audit_validation`, sans l'exposer au prompt.
3. Mettre a jour le gateway pour que le payload prompt-visible ne contienne plus de cle `evidence`, meme vide.
4. Mettre a jour les tests de prompt/provider handoff qui attendent actuellement `evidence: {}`.
5. Renforcer la validation post-generation afin que la redaction LLM soit controlee contre les donnees internes disponibles, notamment:
   - facts et signaux injectes;
   - limites et donnees manquantes injectees;
   - evidences et evidence refs conservees cote backend;
   - statut de grounding attendu.
6. Definir le contrat minimal attendu en sortie LLM pour permettre cette validation, sans imposer un appel provider reel:
   - sections ou items identifiables;
   - claims ou assertions interpretatives;
   - prise en compte des limites;
   - absence d'affirmations contredisant les donnees internes;
   - marqueur ou statut de validation exploitable cote backend si le schema existant le permet.
7. Ajouter des tests negatifs prouvant qu'une redaction invente une donnee absente ou ignore une limite critique est rejetee ou marquee non conforme.
8. Verifier que l'audit persistant continue de conserver les evidences et hashes necessaires.

## Hors perimetre

- Envoyer les evidences au prompt engine.
- Ajouter un appel provider LLM reel.
- Reecrire editorialement tous les prompts.
- Modifier le frontend ou les endpoints publics.
- Changer la semantique de calcul des hashes.
- Supprimer les evidences de l'audit ou de la persistance.
- Reintroduire `chart_json` ou `natal_data` dans le prompt natal moderne.

## Criteres d'acceptation

1. `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` ne contient plus `evidence`.
2. Le payload provider natal moderne contient `facts`, `signals`, `limits` et `shaping`, mais ne contient pas `evidence`.
3. Aucun test ne verrouille plus `prompt_payload["evidence"] == {}`.
4. Les evidences restent presentes dans l'objet complet `llm_astrology_input_v1` et dans l'audit backend.
5. La validation post-generation utilise les evidences internes sans les avoir envoyees au prompt.
6. Un test positif prouve qu'une redaction coherente avec facts/signals/limits/evidences passe la validation.
7. Un test negatif prouve qu'une redaction inventant une information non supportee par les donnees internes echoue ou est marquee non conforme.
8. Les guards CS-339/CS-340 sur provenance, hashes et champs audit-only restent actifs.
9. Les guards CS-336/CS-338 sur `chart_json` / `natal_data` restent actifs.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short
pytest -q tests --tb=short
rg -n "prompt_visible|validation_only|audit_only|evidence|evidence_refs|grounding_status|llm_input_hash|projection_hash" app tests
rg -n "\"evidence\": \{\}|prompt_payload\\[\"evidence\"\\]|{{evidence}}|{{evidence_refs}}|{{grounding_status}}" app tests
```

Le dernier scan doit prouver qu'aucun prompt, fixture de handoff ou test de payload provider ne depend d'un bloc `evidence` vide.

## Risques

Le risque principal est de retirer `evidence` du prompt sans mettre en place une validation post-generation suffisamment forte. Cette story doit donc fermer les deux cotes du process: absence d'evidence dans le prompt et controle effectif de la redaction par le backend.

