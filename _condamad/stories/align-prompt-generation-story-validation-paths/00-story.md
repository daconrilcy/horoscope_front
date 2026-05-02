# Story align-prompt-generation-story-validation-paths: Align prompt-generation story validation paths with collected tests

Status: ready-for-review

## 1. Objective

Corriger les chemins de validation obsoletes dans les stories prompt-generation
livrees afin que chaque commande de test cible un fichier collecte.
Ajouter une garde documentaire pour bloquer les chemins non collectes dans les
blocs `Validation Plan`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-05-02-1452/03-story-candidates.md`
- Reason for change: F-002 indique que plusieurs stories pointent vers une racine
  `tests` obsolete alors que les fichiers reels sont sous `app/tests/unit`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `_condamad/stories`
- In scope:
  - Corriger les references story aux trois chemins obsoletes listes par SC-002.
  - Verifier que les commandes de validation prompt-generation collectent au moins un test.
  - Mettre a jour le registre de guardrails si la correction etablit un invariant durable.
- Out of scope:
  - Modifier le code applicatif backend ou frontend.
  - Renommer ou deplacer les tests existants.
  - Changer le statut fonctionnel des stories livrees hors correction de preuve.
- Explicit non-goals:
  - Ne pas affaiblir `RG-010`: les tests backend restent sous les racines collectees par `backend/pyproject.toml`.
  - Ne pas affaiblir `RG-020`: la garde guidance/consultation reste executable via le chemin reel collecte.
  - Ne pas transformer des preuves historiques `generated/10-final-evidence.md` en etat attendu quand elles documentent une limitation passee.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime des chemins de validation obsoletes des plans actifs et doit bloquer leur retour.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Seuls les chemins de validation et preuves documentaires peuvent changer.
  - Les commandes corrigees doivent pointer vers les fichiers collectes reels.
  - Les preuves historiques peuvent rester si elles expliquent explicitement l'ancienne limitation.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une story `ready-for-dev` doit etre requalifiee en `completed` plutot que corrigee comme contrat de validation.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source de verite est la collecte pytest effective, pas seulement les chemins markdown. |
| Baseline Snapshot | yes | Les anciens chemins actifs doivent etre inventories avant/apres correction. |
| Ownership Routing | no | Aucun proprietaire applicatif n'est deplace. |
| Allowlist Exception | yes | Les exceptions de preuves historiques doivent etre exactes et justifiees. |
| Contract Shape | no | Aucun contrat API, DTO, schema ou type frontend n'est modifie. |
| Batch Migration | no | Les corrections sont documentaires et ciblees par fichier. |
| Reintroduction Guard | yes | Les chemins obsoletes ne doivent pas redevenir des plans de validation actifs. |
| Persistent Evidence | yes | La preuve des chemins collectes doit etre conservee dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - generated manifest: `pytest --collect-only` output ou execution pytest depuis `backend/` sur les chemins corriges.
  - Existence des fichiers sous `backend/app/tests/unit`.
- Secondary evidence:
  - `rg -n "test_seed_horoscope_narrator_assembly.py|test_guidance_service.py|test_consultation_generation_service.py" _condamad/stories`
- Static scans alone are not sufficient for this story because:
  - un chemin present dans markdown peut exister textuellement sans etre collectable par pytest depuis `backend/`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md` must include a `Before active references` table.
- After artifact after implementation:
  - `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md` must include an `After active references` table.
- Comparison command or test:
  - `rg -n "test_guidance_service.py" ..\_condamad\stories`
- Comparison after implementation:
  - the command must return zero active hits; historical hits must be listed in the audit artifact.
- Expected invariant:
  - active validation paths point to collected files.
- Allowed differences:
  - correction from obsolete `tests` paths to `app/tests/unit`.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `converge-horoscope-daily-narration-assembly/generated/10-final-evidence.md` | obsolete historical path | Limitation passee | permanent if labelled historical |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Validation path audit | `validation-path-audit.md` | Lister chemins corriges et preuve de collecte. |
| Final validation evidence | `_condamad/stories/align-prompt-generation-story-validation-paths/generated/10-final-evidence.md` | Conserver les commandes executees et resultats. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states

Required forbidden examples:

- active validation plan command `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`
- active validation plan command `pytest -q tests/unit/test_guidance_service.py`
- active validation plan command `pytest -q tests/unit/test_consultation_generation_service.py`

Guard evidence:

- Evidence profile: `reintroduction_guard`; a targeted scan or pytest-backed docs guard checks active validation blocks under `_condamad/stories`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-05-02-1452/01-evidence-log.md` - E-012 documents failed story-listed paths and equivalent collected paths.
- Evidence 2: `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` -
  active validation references the obsolete seed assembly path.
- Evidence 3: `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` -
  active validation references obsolete guidance and consultation paths.
- Evidence 4: `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py` - real collected seed test path.
- Evidence 5: `backend/app/tests/unit/test_guidance_service.py` - real collected guidance test path.
- Evidence 6: `backend/app/tests/unit/test_consultation_generation_service.py` - real collected consultation test path.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- Les plans de validation actifs referencent `app/tests/unit` quand les tests
  vivent sous `backend/app/tests/unit`.
- Chaque commande corrigee est collectable ou executable depuis `backend/`.
- Les references historiques aux anciens chemins restent seulement si elles sont marquees comme limitation passee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - la story touche la coherence des racines de tests backend collectees.
  - `RG-020` - la correction concerne la validation guidance/consultation.
  - `RG-019` - la correction concerne la validation seed assembly `horoscope_daily/narration`.
- Non-applicable invariants:
  - `RG-018` - la story ne modifie pas `PROMPT_FALLBACK_CONFIGS`.
  - `RG-016` - la story ne modifie pas `LLMNarrator`.
  - `RG-017` - la story ne touche pas les appels provider directs.
- Required regression evidence:
  - Pytest cible sur les chemins corriges.
  - Scan des anciens chemins dans les plans actifs.
  - Audit persistant des corrections.
- Allowed differences:
  - Correction des chemins markdown de validation.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les chemins actifs obsoletes sont remplaces. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n tests/unit/test_guidance_service.py _condamad`. |
| AC2 | Les commandes corrigees executent au moins un test depuis `backend/`. | Evidence profile: `runtime_contract`; targeted pytest on corrected paths. |
| AC3 | Les anciens chemins historiques restent limites aux preuves passees. | Evidence profile: `allowlist_register_validated`; `rg -n "historical" validation-path-audit.md`. |
| AC4 | Une garde bloque le retour des anciens chemins. | Evidence profile: `reintroduction_guard`; `rg -n test_seed_horoscope_narrator_assembly.py _condamad`. |

## 8. Implementation Tasks

- [x] Task 1 - Auditer les chemins de validation obsoletes (AC: AC1, AC3)
  - [x] Subtask 1.1 - Scanner `_condamad/stories` pour les trois chemins obsoletes.
  - [x] Subtask 1.2 - Ecrire `validation-path-audit.md` avec ancien chemin, chemin reel, fichier touche et statut historique/actif.

- [x] Task 2 - Corriger les plans actifs (AC: AC1)
  - [x] Subtask 2.1 - Mettre a jour les `00-story.md` concernes.
  - [x] Subtask 2.2 - Mettre a jour les `generated/06-validation-plan.md` si un plan actif contient encore un ancien chemin.

- [x] Task 3 - Ajouter ou documenter la garde anti-retour (AC: AC4)
  - [x] Subtask 3.1 - Preferer un test documentaire existant si disponible; sinon ajouter un test cible sous la racine de tests collectee.
  - [x] Subtask 3.2 - Verifier que les preuves historiques restent explicitement marquees comme anciennes limitations.

- [x] Task 4 - Executer et consigner la validation (AC: AC2, AC3, AC4)
  - [x] Subtask 4.1 - Executer pytest et scans dans le venv.
  - [x] Subtask 4.2 - Ecrire `generated/10-final-evidence.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Les chemins reels deja collectes sous `backend/app/tests/unit`.
  - Les guards de topologie existants lies a `RG-010` si une garde documentaire est ajoutee.
- Do not recreate:
  - Une deuxieme convention de chemins backend.
  - Des copies de tests sous `backend/tests/unit` pour satisfaire l'ancien markdown.
  - Un script ad hoc si un test existant peut porter la garde clairement.
- Shared abstraction allowed only if:
  - Elle verifie plusieurs stories prompt-generation avec une meme logique de collecte de chemins.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- Active validation command `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`
- Active validation command `pytest -q tests/unit/test_guidance_service.py`
- Active validation command `pytest -q tests/unit/test_consultation_generation_service.py`
- Creating `backend/tests/unit` files only to make obsolete story paths pass.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: path is the collected pytest file path or a canonical story validation command.
- `external-active`: path is referenced by external documentation or generated public evidence outside `_condamad/stories`.
- `historical-facade`: obsolete path appears only as evidence of an old failed command.
- `dead`: obsolete path appears in an active story validation plan and does not exist in the repository.
- `needs-user-decision`: ambiguity remains after scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `keep`, `needs-user-decision` | May remain only if labelled historical failed evidence. |
| `dead` | `delete` | Must be deleted from active plans. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Backend unit tests collected from application test root | `backend/app/tests/unit` | Story validation paths under `tests/unit` for these files |
| LLM orchestration tests collected from orchestration root | `backend/tests/llm_orchestration` | Story references to files that do not exist in that root |
| CONDAMAD validation evidence | `00-story.md` and `generated/06-validation-plan.md` | Unlabelled historical failed attempts |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed, from active validation plans.

Forbidden:

- creating duplicate test files under obsolete paths;
- adding wrapper commands that hide missing files;
- preserving an alias to an obsolete validation path;
- keeping an obsolete path active with a comment;
- preserving an obsolete validation path through re-export;
- replacing deletion with a soft warning.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/audits/prompt-generation/2026-05-02-1452/01-evidence-log.md`
- `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md`
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/app/tests/unit/test_consultation_generation_service.py`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` - corriger chemin seed assembly.
- `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` - corriger chemins guidance et consultation.
- `_condamad/stories/regression-guardrails.md` - corriger le guard attendu `RG-020` si le chemin est obsolere.
- `_condamad/stories/align-prompt-generation-story-validation-paths/validation-path-audit.md` - audit persistant des corrections.
- `_condamad/stories/align-prompt-generation-story-validation-paths/generated/10-final-evidence.md` - preuve finale.

Likely tests:

- `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py` - preuve de collecte seed.
- `backend/app/tests/unit/test_guidance_service.py` - preuve de collecte guidance.
- `backend/app/tests/unit/test_consultation_generation_service.py` - preuve de collecte consultation.
- `backend/app/tests/unit/test_backend_pytest_collection.py` or equivalent existing topology guard - preuve que les racines restent collectees.

Files not expected to change:

- `backend/app/domain/llm/prompting/catalog.py` - hors scope de correction documentaire.
- `frontend/src` - aucune surface frontend n'est touchee.
- `backend/pyproject.toml` - aucune modification de configuration pytest n'est requise.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md
pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py
rg -n "tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py|tests/unit/test_guidance_service.py|tests/unit/test_consultation_generation_service.py" ..\_condamad\stories
ruff check .
```

## 22. Regression Risks

- Risk: une story reste `ready-for-dev` avec une commande pytest non collectable.
  - Guardrail: scan cible des plans actifs + pytest sur chemins corriges.
- Risk: une preuve historique est confondue avec un plan actif.
  - Guardrail: allowlist limitee aux `generated/10-final-evidence.md` explicitement marques comme limitation passee.
- Risk: des tests sont dupliques sous une ancienne racine pour satisfaire la documentation.
  - Guardrail: `RG-010` et guards de topologie backend.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Run every Python command after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/prompt-generation/2026-05-02-1452/01-evidence-log.md` - E-010, E-011, E-012.
- `_condamad/audits/prompt-generation/2026-05-02-1452/02-finding-register.md` - F-002.
- `_condamad/audits/prompt-generation/2026-05-02-1452/03-story-candidates.md` - SC-002.
- `_condamad/stories/regression-guardrails.md` - RG-010, RG-019, RG-020.
