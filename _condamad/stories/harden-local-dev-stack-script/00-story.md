# Story harden-local-dev-stack-script: Durcir le script de demarrage dev local

Status: ready-for-dev

## 1. Objective

Rendre `scripts/start-dev-stack.ps1` utilisable pour demarrer backend et frontend
sans Stripe par defaut, avec une option explicite pour le listener Stripe.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/scripts-ops/2026-05-02-1847/03-story-candidates.md` (`SC-004`)
- Source finding: `_condamad/audits/scripts-ops/2026-05-02-1847/02-finding-register.md` (`F-004`)
- Reason for change: l'audit indique que le script est utile mais non teste, non documente et rend Stripe obligatoire pour le demarrage local.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `scripts/start-dev-stack.ps1`
- In scope:
  - Ajouter un parametre PowerShell explicite pour activer Stripe.
  - Ne pas lancer l'onglet Stripe lorsque le parametre n'est pas demande.
  - Ajouter une erreur claire si Stripe est demande mais absent.
  - Documenter l'usage local du script.
- Out of scope:
  - Modifier `scripts/stripe-listen-webhook.ps1` ou `scripts/stripe-listen-webhook.sh`.
  - Changer les ports backend/frontend.
  - Modifier la configuration Stripe applicative.
- Explicit non-goals:
  - Ne pas decider du support bash `stripe-listen-webhook.sh`.
  - Ne pas ajouter de fallback silencieux si Stripe est demande.
  - Ne pas changer `RG-015` autrement que par evidence de validation scripts.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: test-guard-hardening
- Archetype reason: la story durcit un script ops/dev avec parametre explicite, erreur controlee et garde de non-regression.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le demarrage backend/frontend devient possible sans Stripe.
  - Le mode Stripe reste disponible uniquement via parametre explicite.
  - L'absence de Stripe doit echouer seulement lorsque Stripe est demande.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le script doit lancer Stripe par defaut pour un workflow non documente.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source de verite est l'execution PowerShell parsee/testee du script et ses parametres effectifs. |
| Baseline Snapshot | no | Aucun refactor large ni migration de chemins n'est prevu. |
| Ownership Routing | no | Aucun deplacement de responsabilite n'est prevu. |
| Allowlist Exception | yes | Le lancement Stripe devient une exception explicite a l'usage backend/frontend minimal. |
| Contract Shape | no | Aucun contrat API, DTO ou type frontend n'est touche. |
| Batch Migration | no | Aucun lot de migration n'est requis. |
| Reintroduction Guard | yes | Le script ne doit pas redevenir dependant de Stripe par defaut. |
| Persistent Evidence | yes | La decision d'exception Stripe doit etre portee par la story et la documentation. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - AST guard or loaded config-style PowerShell parser/execution guard for `scripts/start-dev-stack.ps1` parameters and Stripe branch.
- Secondary evidence:
  - `rg -n "SkipStripe|WithStripe|stripe" scripts/start-dev-stack.ps1 docs README.md backend/app/tests`.
- Static scans alone are not sufficient for this story because:
  - Le comportement attendu depend du chemin d'execution PowerShell lorsque Stripe est demande ou omis.

## 4c. Baseline / Before-After Rule

- Baseline rule: not applicable
- Reason: no behavior-preserving refactor, migration, route restructuring, or API contract change is involved.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `scripts/start-dev-stack.ps1` | Stripe listener branch | Webhooks locaux uniquement. | Permanent tant que backend/frontend demarrent sans Stripe. |

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

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Dev stack usage note | `_condamad/stories/harden-local-dev-stack-script/dev-stack-usage-evidence.md` | Documenter commandes et resultat du test. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states

Required forbidden examples:

- unconditional `Get-Command stripe`
- unconditional start of `stripe-listen-webhook.ps1`
- default branch requiring Stripe CLI

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_start_dev_stack_script.py` checks the PowerShell text and mocked branches.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/scripts-ops/2026-05-02-1847/01-evidence-log.md` - `E-008` signale que Stripe CLI est requis et que l'onglet Stripe est toujours cree.
- Evidence 2: `_condamad/audits/scripts-ops/2026-05-02-1847/02-finding-register.md` - `F-004` recommande une garde/test minimal et un parametre rendant Stripe optionnel.
- Evidence 3: `scripts/start-dev-stack.ps1` - script cible du durcissement.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-015`.

## 6. Target State

After implementation:

- `scripts/start-dev-stack.ps1` demarre backend/frontend sans dependance Stripe par defaut.
- Un parametre explicite, par exemple `-WithStripe`, active le listener Stripe.
- Une erreur lisible explique comment installer ou desactiver Stripe si `-WithStripe` est demande sans CLI.
- Une documentation courte donne les commandes PowerShell supportees.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-015` - la story modifie un script dev local et doit fournir une commande/test d'ownership ops.
- Non-applicable invariants:
  - `RG-001` - aucune route historique n'est touchee.
  - `RG-011` - aucun harnais DB de test n'est touche.
- Required regression evidence:
  - Test PowerShell mocke ou garde statique ciblee, scan de l'absence de dependance Stripe inconditionnelle.
- Allowed differences:
  - Stripe devient opt-in pour `start-dev-stack.ps1`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La branche par defaut ignore Stripe. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_start_dev_stack_script.py`. |
| AC2 | Stripe explicite exige la CLI. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_start_dev_stack_script.py`. |
| AC3 | La doc nomme `WithStripe`. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "start-dev-stack.ps1|WithStripe" README.md docs`. |
| AC4 | Aucun fallback silencieux ou alias n'est ajoute. | Evidence profile: `repo_wide_negative_scan`; `rg -n "fallback|compat|alias|SkipStripe" scripts/start-dev-stack.ps1`. |
| AC5 | La story valide. | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py this-file`. |

## 8. Implementation Tasks

- [ ] Task 1 - Rendre Stripe opt-in dans le script (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Ajouter un parametre PowerShell explicite.
  - [ ] Subtask 1.2 - Isoler la verification `Get-Command stripe` dans la branche Stripe.

- [ ] Task 2 - Ajouter garde et documentation (AC: AC3, AC4)
  - [ ] Subtask 2.1 - Ajouter un test ou garde PowerShell cible.
  - [ ] Subtask 2.2 - Documenter les commandes supportees.

- [ ] Task 3 - Valider la story (AC: AC5)
  - [ ] Subtask 3.1 - Executer tests cibles.
  - [ ] Subtask 3.2 - Executer validateurs CONDAMAD.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `scripts/stripe-listen-webhook.ps1` pour la logique Stripe existante.
  - Les helpers de test scripts existants si disponibles.
- Do not recreate:
  - Une deuxieme implementation du listener Stripe.
  - Une logique PowerShell inline qui duplique `stripe-listen-webhook.ps1`.
- Shared abstraction allowed only if:
  - Elle evite une duplication immediate dans les tests PowerShell existants.

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

- unconditional `Get-Command stripe`
- unconditional `stripe-listen-webhook.ps1`
- undocumented `SkipStripe` compatibility switch

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `scripts/start-dev-stack.ps1`
- `scripts/stripe-listen-webhook.ps1`
- `README.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `scripts/start-dev-stack.ps1` - Stripe opt-in and clear error branch.
- `README.md` - local dev command documentation, or assumption risk: unknown until repo inspection if a dedicated dev guide exists.

Likely tests:

- `backend/app/tests/unit/test_start_dev_stack_script.py` - script behavior guard, or assumption risk: unknown until repo inspection if script tests are grouped elsewhere.

Files not expected to change:

- `scripts/stripe-listen-webhook.sh` - support decision is out of scope.
- `backend/app/main.py` - runtime app behavior is out of scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q app/tests/unit/test_start_dev_stack_script.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-dev-stack.ps1 -Help
rg -n "Get-Command stripe|stripe-listen-webhook.ps1|WithStripe|SkipStripe" scripts/start-dev-stack.ps1 README.md docs
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/harden-local-dev-stack-script/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/harden-local-dev-stack-script/00-story.md
```

## 22. Regression Risks

- Risk: masquer une absence de Stripe lorsque le developpeur veut tester les webhooks.
  - Guardrail: erreur explicite en mode `-WithStripe`.
- Risk: casser le demarrage backend/frontend simple.
  - Guardrail: test de branche par defaut sans Stripe.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Ne pas modifier le statut du script bash Stripe.

## 24. References

- `_condamad/audits/scripts-ops/2026-05-02-1847/03-story-candidates.md` - source candidate `SC-004`.
- `_condamad/audits/scripts-ops/2026-05-02-1847/02-finding-register.md` - details du finding `F-004`.
- `_condamad/audits/scripts-ops/2026-05-02-1847/01-evidence-log.md` - preuve `E-008`.
- `_condamad/stories/regression-guardrails.md` - invariant `RG-015`.
