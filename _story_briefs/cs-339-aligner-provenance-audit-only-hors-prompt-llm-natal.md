# CS-339 - Aligner Provenance Audit-Only Hors Prompt LLM Natal

<!-- Commentaire global: ce brief cadre la correction de frontiere entre donnees prompt-visibles et donnees d'audit du contrat LLM astrologique natal. -->

## Resume

Corriger l'incoherence detectee apres CS-330 a CS-338: `llm_astrology_input_v1` declare `projection_hash` et `llm_input_hash` comme audit-only, mais le gateway projette actuellement le bloc `provenance` dans le payload prompt-visible, ce qui expose ces hashes au generateur LLM.

La correction doit aligner la projection runtime sur le contrat canonique: le prompt natal ne doit recevoir que les blocs explicitement `prompt_visible`, tandis que `provenance`, `projection_hash` et `llm_input_hash` restent disponibles pour l'audit et la persistance.

## Contexte

La revue qualite de la livraison CS-330 a CS-338 a confirme que le legacy `chart_json` / `natal_data` n'est plus le chemin actif du prompt natal moderne. Le finding restant porte sur la frontiere interne du nouveau contrat:

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` declare `prompt_visible = facts/signals/limits/evidence/shaping`;
- le meme contrat classe `projection_hash` et `llm_input_hash` en `audit_only`;
- `backend/app/domain/llm/runtime/gateway.py` inclut actuellement `provenance` dans `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS`;
- les tests actuels acceptent explicitement `prompt_payload["provenance"]["llm_input_hash"]`.

Cette situation cree une fausse separation prompt/audit: les donnees d'audit ne sont plus seulement audit-only.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md`
- `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md`
- `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`

## Objectif

Garantir qu'aucune donnee classee audit-only dans `llm_astrology_input_v1` n'est injectee dans le prompt natal moderne.

## Perimetre inclus

1. Corriger la projection du gateway afin que le payload prompt-visible soit derive de la liste canonique `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
2. Retirer `provenance` des blocs envoyes au prompt, sauf decision explicitement justifiee de creer une projection de provenance redigee et sans hash audit-only.
3. Garantir que `projection_hash` et `llm_input_hash` restent disponibles pour:
   - l'audit narratif;
   - la persistance;
   - les rapports et preuves techniques;
   - les tests de hash.
4. Mettre a jour les tests qui verifient la composition finale du prompt natal.
5. Ajouter un guard qui echoue si le gateway diverge de `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
6. Ajouter un guard negatif qui echoue si `projection_hash`, `llm_input_hash`, `provider_response` ou `persisted_answer` apparaissent dans le payload prompt-visible.
7. Verifier que la suppression de `provenance` du prompt ne degrade pas les donnees astrologiques utiles: `facts`, `signals`, `limits`, `evidence` et `shaping` doivent rester presents.

## Hors perimetre

- Reintroduire `chart_json` ou `natal_data` comme fallback prompt.
- Modifier les prompts redactionnels autrement que pour retirer une dependance a une variable non prompt-visible.
- Modifier les endpoints publics ou le frontend.
- Modifier la politique de stockage des audits.
- Appeler un provider LLM reel.
- Recalculer la semantique de `llm_input_hash`.

## Criteres d'acceptation

1. Le prompt natal moderne contient `facts`, `signals`, `limits`, `evidence` et `shaping`.
2. Le prompt natal moderne ne contient pas `provenance`, `projection_hash`, `llm_input_hash`, `provider_response` ni `persisted_answer`.
3. Le gateway utilise la definition canonique des blocs prompt-visibles du contrat, ou un test prouve que sa liste reste strictement identique.
4. Les fonctions d'audit continuent de lire `projection_hash`, `llm_input_hash`, `contract_version`, `grounding_status` et `evidence_refs` depuis `llm_astrology_input_v1`.
5. Les tests existants de hash et d'audit continuent de passer.
6. Les guards legacy CS-336/CS-338 continuent de passer.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short
pytest -q tests --tb=short
rg -n "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS|prompt_visible|audit_only|projection_hash|llm_input_hash|provenance" app tests
```

## Risques

Le risque principal est de corriger le prompt en cassant l'audit. La correction doit donc separer le rendu prompt de la structure persistante: le payload complet peut rester l'objet source auditable, mais la projection envoyee au LLM doit exclure les champs audit-only.

