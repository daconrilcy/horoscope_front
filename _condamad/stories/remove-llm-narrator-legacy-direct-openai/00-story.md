# Story remove-llm-narrator-legacy-direct-openai: Remove direct OpenAI LLMNarrator runtime

Status: ready-for-dev

## 1. Objective

Supprimer le chemin executable `LLMNarrator` hors gateway pour `horoscope_daily`.
La narration quotidienne doit passer uniquement par `AIEngineAdapter.generate_horoscope_narration`
puis par le service canonique `services/llm_generation/horoscope_daily`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-04-30-1810`
- Reason for change: F-001 identifie un narrateur deprecie qui instancie `openai.AsyncOpenAI`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/llm_generation/horoscope_daily`
- In scope:
  - Supprimer la consommation nominale de `LLMNarrator`.
  - Deplacer ou conserver les dataclasses narratives dans un module contrat non legacy.
  - Prouver que les tests utilisent le chemin `AIEngineAdapter.generate_horoscope_narration`.
  - Ajouter une garde qui bloque le retour du fournisseur direct hors provider canonique.
- Out of scope:
  - Modifier la generation des predictions publiques.
  - Recrire le gateway LLM.
  - Changer les schemas de sortie narratifs.
- Explicit non-goals:
  - Ne pas recreer `app.services.ai_engine_adapter`.
  - Ne pas remettre la logique narrative dans `AIEngineAdapter`.
  - Ne pas changer les invariants `RG-004`, `RG-005`, `RG-006`, `RG-016`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: `LLMNarrator` est une surface historique executable avec appel provider direct.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le contrat narratif retourne les memes champs utiles.
  - Le chemin runtime direct OpenAI disparait.
  - Les echecs restent controles par le service canonique.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une surface externe prouve une dependance nominale a `LLMNarrator`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La preuve doit interroger une garde AST ou import runtime. |
| Baseline Snapshot | yes | L'inventaire avant/apres des symboles legacy doit etre conserve. |
| Ownership Routing | yes | Le contrat narratif doit appartenir au domaine canonique. |
| Allowlist Exception | no | Aucun appel direct provider hors provider canonique n'est autorise. |
| Contract Shape | no | Aucun DTO HTTP ou OpenAPI n'est modifie. |
| Batch Migration | no | La migration vise une seule facade legacy. |
| Reintroduction Guard | yes | Le retour de `LLMNarrator` doit faire echouer une garde. |
| Persistent Evidence | yes | Les scans avant/apres doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard backend detectant `LLMNarrator` dans les tests collectes.
  - AST guard backend detectant `openai.AsyncOpenAI` hors provider canonique.
- Secondary evidence:
  - `rg -n "LLMNarrator\(|chat\.completions\.create|openai\.AsyncOpenAI" backend/app backend/tests`
- Static scans alone are not sufficient for this story because:
  - le symbole peut revenir par import indirect ou instanciation non triviale.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-before.md`
- Comparison after implementation:
  - `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-after.md`
- Expected invariant:
  - `LLMNarrator` n'est plus une surface runtime ou test nominale.
- Allowed differences:
  - Suppression du module legacy ou extraction des dataclasses vers un contrat canonique.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Horoscope narration use case | `backend/app/services/llm_generation/horoscope_daily` | `backend/app/prediction/llm_narrator.py` |
| Provider call | `backend/app/infra/providers/llm` | `backend/app/prediction` |
| Application facade | `backend/app/domain/llm/runtime/adapter.py` | narrative business logic |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Legacy scan before | `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-before.md` | Capturer les references initiales. |
| Legacy scan after | `_condamad/stories/remove-llm-narrator-legacy-direct-openai/legacy-narrator-scan-after.md` | Prouver l'absence nominale finale. |
| Removal audit | `_condamad/stories/remove-llm-narrator-legacy-direct-openai/removal-audit.md` | Classer la facade avant suppression. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- `LLMNarrator(` revient dans `backend/app` ou les tests collectes;
- `from app.prediction.llm_narrator import LLMNarrator` revient;
- `chat.completions.create` apparait hors `backend/app/infra/providers/llm`;
- `openai.AsyncOpenAI` apparait hors provider canonique.

Required architecture guard against reintroduction:
- Deterministic source: forbidden symbols.
- Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` checks `LLMNarrator`.
- The guard must fail when `LLMNarrator` is reintroduced.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-008 identifie `LLMNarrator`.
- Evidence 2: `backend/app/prediction/llm_narrator.py` - le module instancie `openai.AsyncOpenAI`.
- Evidence 3: `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - le service importe les dataclasses historiques.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le runtime horoscope daily ne depend plus de `backend/app/prediction/llm_narrator.py`.
- Les types narratifs utiles vivent dans un module canonique ou sont remplaces par contrat equivalent.
- Les tests de migration passent par `AIEngineAdapter.generate_horoscope_narration`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-016` - les tests backend ne doivent pas consommer nominalement `LLMNarrator`.
  - `RG-006` - les couches non API ne doivent pas importer `app.api`.
- Non-applicable invariants:
  - `RG-001` - aucune route facade historique n'est touchee.
  - `RG-007` - les endpoints admin observability ne sont pas touches.
- Required regression evidence:
  - Test de garde narrator.
  - Scan provider direct.
  - Tests de migration narration.
- Allowed differences:
  - Disparition du module legacy ou de son import nominal.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Facade inventory completed. | Evidence profile: `baseline_before_after_diff`; `rg -n "LLMNarrator\|llm_narrator" backend/app backend/tests docs`. |
| AC2 | Canonical narration owner used. | Evidence profile: `ast_architecture_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py`. |
| AC3 | Direct provider path absent. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "chat\.completions\.create\|openai\.AsyncOpenAI" backend/app backend/tests`. |
| AC4 | Migration tests preserved. | Evidence profile: `reintroduction_guard`; `pytest -q tests/llm_orchestration/test_narrator_migration.py`. |
| AC5 | Regression guard registry honored. | Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'inventaire legacy avant suppression (AC: AC1)
- [x] Task 2 - Classer `LLMNarrator` puis extraire le contrat narratif canonique (AC: AC1, AC2)
- [x] Task 3 - Migrer les imports internes vers le contrat canonique (AC: AC2)
- [x] Task 4 - Supprimer ou rendre non importable la facade legacy (AC: AC1, AC3)
- [x] Task 5 - Durcir les tests anti-retour provider direct (AC: AC3, AC5)
- [x] Task 6 - Executer les tests cibles dans le venv (AC: AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AIEngineAdapter.generate_horoscope_narration` pour le chemin applicatif.
  - `backend/app/services/llm_generation/horoscope_daily/narration_service.py` pour le use case.
  - `backend/app/infra/providers/llm/openai_responses_client.py` pour le provider.
- Do not recreate:
  - Un client OpenAI direct.
  - Une facade `app.services.ai_engine_adapter`.
  - Un narrateur parallele sous `backend/app/prediction`.
- Shared abstraction allowed only if:
  - Elle porte uniquement des types de contrat narratif reutilises par plusieurs modules canonique.

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

- `backend/app/prediction/llm_narrator.py`
- `LLMNarrator`
- `LLMNarrator(`
- `from app.prediction.llm_narrator import LLMNarrator`
- `client.chat.completions.create`
- `openai.AsyncOpenAI`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: type ou service canonique encore utilise par le runtime.
- `external-active`: documentation publique ou client externe depend du symbole.
- `historical-facade`: surface de compatibilite vers le chemin canonique.
- `dead`: zero reference utile apres migration des types.
- `needs-user-decision`: ambiguite externe apres scans requis.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `LLMNarrator` | symbol | `historical-facade` | to audit | `AIEngineAdapter.generate_horoscope_narration` | `delete` | scan before | direct provider return |

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/remove-llm-narrator-legacy-direct-openai/removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Daily horoscope narration | `backend/app/services/llm_generation/horoscope_daily` | `backend/app/prediction/llm_narrator.py` |
| OpenAI provider execution | `backend/app/infra/providers/llm` | direct OpenAI call in prediction |
| Application LLM entry | `backend/app/domain/llm/runtime/adapter.py` | root service shim |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with external evidence.

## 17. Generated Contract Check

- OpenAPI absence:
  - No OpenAPI path is removed by this story.
- Generated artifact absence:
  - No generated client or schema references `LLMNarrator`.
- Required check:
  - `rg -n "LLMNarrator|llm_narrator" frontend/src backend/app/api docs`

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/prediction/llm_narrator.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - remplacer les imports legacy.
- `backend/app/prediction/llm_narrator.py` - supprimer la facade ou retirer son export executable.
- `backend/app/domain/llm/prompting/narrator_contract.py` - destination probable du contrat narratif.

Likely tests:

- `backend/tests/llm_orchestration/test_narrator_migration.py` - conserver la preuve gateway.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` - durcir la garde.

Files not expected to change:

- `frontend/src/main.tsx` - aucun comportement frontend n'est dans le scope.
- `backend/app/api/v1/routers` - aucune route API n'est dans le scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\remove-llm-narrator-legacy-direct-openai\00-story.md
pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py
pytest -q tests/llm_orchestration/test_narrator_migration.py
rg -n "LLMNarrator\(|from app\.prediction\.llm_narrator import LLMNarrator|chat\.completions\.create|openai\.AsyncOpenAI" app tests
ruff check .
```

## 22. Regression Risks

- Risk: perte du mapping narratif.
  - Guardrail: tests `test_narrator_migration.py`.
- Risk: retour d'un appel provider direct.
  - Guardrail: garde `RG-016` plus scan cible.

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

- `_condamad/audits/prompt-generation/2026-04-30-1810/03-story-candidates.md` - SC-001.
- `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-008, E-015.
- `_bmad-output/implementation-artifacts/70-20.md` - adapter minimal.
- `_bmad-output/implementation-artifacts/70-21-analyser-factoriser-et-deplacer-les-services-llm-residuels-sous-services.md` - namespace cible.
