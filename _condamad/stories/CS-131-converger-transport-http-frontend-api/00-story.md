# Story CS-131 converger-transport-http-frontend-api: Converger le transport HTTP frontend API

Status: ready-to-dev

## 1. Objective

Faire de `frontend/src/api/client.ts` le point de passage unique des appels backend effectues par `frontend/src/api`.
La migration doit conserver les chemins, methodes, en-tetes, corps de requete, gestion `token_expired` et le timeout geocoding de 15 secondes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-001`
- Reason for change: l'audit `frontend-api` signale `F-001`, des appels `fetch` directs qui contournent le helper canonique et dupliquent la gestion transport.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Migrer les appels backend directs listes par `SC-001`.
  - Le lot inclut B2B, billing, enterprise credentials, help, ops monitoring, support et geocoding.
  - Etendre `client.ts` uniquement pour les besoins transport partages constates par l'audit.
  - Ajouter ou ajuster les tests API qui prouvent les chemins, en-tetes, erreurs et timeout.
- Out of scope:
  - Changer les contrats backend ou les DTO fonctionnels.
  - Reorganiser les modules par domaine, couvert par `CS-133`.
  - Centraliser toutes les enveloppes d'erreur, couvert par `CS-132`.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064` et `RG-069`.
  - Ne pas ajouter un second client HTTP actif.
  - Ne pas cacher les appels directs par un wrapper local propre a un module.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: api-adapter-boundary-convergence
- Archetype reason: la frontiere transport API frontend doit converger vers un adaptateur unique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les seules differences autorisees sont la normalisation interne du transport et les erreurs preservees par `ApiError`.
  - Les paths, methodes, en-tetes et corps emis doivent rester identiques.
  - Le timeout geocoding de 15 secondes doit etre conserve ou reimplemente explicitement dans le client canonique.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un appel direct cible une URL hors backend applicatif ou depend d'un comportement navigateur non portable par `client.ts`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `client.ts` et les tests API deviennent la source de verite du transport frontend. |
| Baseline Snapshot | yes | l'inventaire des appels `fetch` avant/apres doit prouver la convergence. |
| Ownership Routing | yes | chaque appel backend doit etre route vers le client canonique. |
| Allowlist Exception | yes | toute exception transport restante doit etre exacte et temporaire par condition de sortie. |
| Contract Shape | no | les DTO et formes de reponse ne changent pas dans cette story. |
| Batch Migration | no | le lot est borne par les fichiers `SC-001`, sans plan multi-lots durable. |
| Reintroduction Guard | yes | un guard doit bloquer la reintroduction de `fetch` direct sous `frontend/src/api`. |
| Persistent Evidence | yes | les inventaires before/after et la classification des exceptions doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `frontend/src/api/client.ts`
  - tests Vitest des modules API migres.
- Secondary evidence:
  - scan cible `rg -n "\bfetch\(" src/api -g "*.ts"` depuis `frontend`.
- Static scans alone are not sufficient:
  - le test `api-architecture` doit agir comme AST guard ou guard de fichiers chargeant l'inventaire versionne.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-after.md`
- Expected invariant:
  - le scan `fetch` ne retourne que `src/api/client.ts` et des exceptions exactes classees.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Transport HTTP backend | `frontend/src/api/client.ts` | helper `fetch` local dans un module API |
| Timeout geocoding | option transport explicite de `client.ts` ou wrapper documente autour de lui | `AbortController` duplique sans test |
| Conversion token expire | mecanisme existant de `apiFetch` | parser local par module |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/api/client.ts` | `fetch(` | proprietaire canonique du transport | permanent canonical owner |
| `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-after.md` | retained exception rows | cas non convergent prouve | until explicit user decision |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: les schemas, champs et status codes publics ne sont pas modifies.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: la story migre un lot audite unique et ferme par inventaire before/after.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| before inventory | `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-before.md` | capturer les appels directs initiaux. |
| after inventory | `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-after.md` | prouver la fermeture ou les exceptions exactes. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if direct backend transport returns under `frontend/src/api`.

Required guard evidence:

```powershell
cd frontend
npm run test -- api-architecture
rg -n "\bfetch\(" src/api -g "*.ts"
```

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md` - `F-001` classe les appels `fetch` directs comme finding high.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-001` liste les fichiers a migrer et le timeout geocoding a conserver.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `frontend/src/api/client.ts` est le seul owner du transport HTTP backend.
- Les modules listes par `SC-001` consomment le helper canonique sans dupliquer `fetch`, timeout ou parsing `token_expired`.
- Le timeout geocoding de 15 secondes est teste.
- Un guard executable echoue si un nouvel appel `fetch` direct apparait sous `frontend/src/api`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-053` - la migration ne doit pas recreer de compatibilite runtime historique.
  - `RG-057` - aucun vocabulaire ou fallback de compatibilite ne doit etre ajoute.
  - `RG-064` - les pages ne doivent pas redevenir consommatrices API directes.
  - `RG-069` - les composants partages ne doivent pas recevoir d'orchestration API.
- Required regression evidence:
  - `npm run test -- api-architecture`
  - `npm run test -- page-architecture component-architecture`
  - scans cibles `fetch` et vocabulaire No Legacy.
- Allowed differences:
  - differences internes de transport uniquement, sans changement observable de contrat.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline liste tous les appels directs sous `frontend/src/api`. | Evidence profile: `baseline_before_after_diff`; AST guard via `npm run test -- api-architecture`. |
| AC2 | Les fichiers `SC-001` utilisent le client canonique. | Evidence profile: `ast_architecture_guard`; `npm run test -- api-architecture` et tests API cibles. |
| AC3 | Le timeout geocoding de 15 secondes reste couvert. | Evidence profile: `runtime_contract_preservation`; `npm run test -- geocodingApi apiClient`. |
| AC4 | Aucun helper transport local concurrent n'est ajoute. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "\bfetch\(|AbortController|token_expired" src/api`. |
| AC5 | Les invariants frontend applicables restent verts. | Evidence profile: `reintroduction_guard`; `npm run test -- page-architecture component-architecture design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire transport initial (AC: AC1)
  - [ ] Ecrire `api-fetch-before.md`.
  - [ ] Classer chaque hit par fichier et endpoint.
- [ ] Task 2 - Etendre le client canonique pour le timeout ou signal requis (AC: AC2, AC3)
  - [ ] Ajouter les options minimales pour timeout ou signal.
  - [ ] Tester `token_expired`, erreurs et timeout.
- [ ] Task 3 - Migrer les modules listes par `SC-001` (AC: AC2, AC4)
  - [ ] Remplacer les appels directs sans changer les payloads.
  - [ ] Supprimer les helpers locaux devenus inutiles.
- [ ] Task 4 - Ajouter la garde de reintroduction et l'inventaire final (AC: AC1, AC4, AC5)
  - [ ] Ecrire `api-fetch-after.md`.
  - [ ] Ajouter ou mettre a jour le test `api-architecture`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/api/client.ts`
  - `ApiError` et le comportement existant de `apiFetch`
  - conventions de tests API sous `frontend/src/tests` ou tests adjacents existants.
- Do not recreate:
  - helper `fetchJson` local par fichier.
  - parsing `token_expired` local.
  - second client HTTP avec base URL.
- Shared abstraction allowed only if:
  - elle vit dans `client.ts` ou un sous-module core explicitement importe par `client.ts`.
  - elle remplace au moins deux duplications auditees.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- legacy imports
- fallback transport behavior
- duplicate active HTTP clients
- silent fallback behavior

Specific forbidden symbols / paths:

- `fetch(` hors `frontend/src/api/client.ts`
- `window.fetch(` hors `frontend/src/api/client.ts`
- `token_expired` parse local hors client canonique
- wrapper local `requestJson` ou `fetchJson` dans les fichiers listes par `SC-001`

## 11. Removal Classification Rules

- Removal classification: not applicable
- Reason: la story remplace des implementations internes mais ne supprime pas de surface publique.

## 12. Removal Audit Format

- Removal audit: not applicable
- Reason: aucun endpoint, fichier public ou champ contractuel n'est retire par cette story.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Transport backend frontend | `frontend/src/api/client.ts` | appels `fetch` locaux dans modules API |
| Timeout transport | option du client canonique | timeout ad hoc non teste |

## 14. Delete-Only Rule

- Delete-only rule: not applicable
- Reason: les suppressions sont internes aux helpers locaux et ne demandent pas de classification removal.

## 15. External Usage Blocker

- External usage blocker: not applicable
- Reason: les appels `fetch` directs audites sont internes au frontend.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucun contrat genere, OpenAPI ou client genere n'est modifie.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/client.ts`
- `frontend/src/api/geocoding.ts`
- `frontend/src/api/billing.ts`
- `frontend/src/api/support.ts`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/client.ts` - options transport partagees.
- `frontend/src/api/b2bAstrology.ts` - migration transport.
- `frontend/src/api/b2bBilling.ts` - migration transport.
- `frontend/src/api/b2bEditorial.ts` - migration transport.
- `frontend/src/api/b2bUsage.ts` - migration transport.
- `frontend/src/api/billing.ts` - migration transport.
- `frontend/src/api/enterpriseCredentials.ts` - migration transport.
- `frontend/src/api/help.ts` - migration transport.
- `frontend/src/api/opsMonitoring.ts` - migration transport.
- `frontend/src/api/support.ts` - migration transport.
- `frontend/src/api/geocoding.ts` - migration transport avec timeout.
- `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-before.md` - baseline.
- `_condamad/stories/CS-131-converger-transport-http-frontend-api/api-fetch-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/api-architecture-guards.test.ts` - guard transport.
- tests existants ciblant `apiClient`, `b2b`, `billing`, `help`, `support`, `geocodingApi`.

Files not expected to change:

- `backend/app/**` - aucun contrat backend.
- `frontend/src/pages/**` - aucune orchestration page.
- `frontend/src/components/**` - aucun composant partage.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- apiClient b2b billing help support geocodingApi
npm run test -- api-architecture page-architecture component-architecture
npm run lint
npm run typecheck
rg -n "\bfetch\(" src/api -g "*.ts"
rg -n "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility" src
```

## 21. Regression Risks

- Risk: perte du timeout geocoding.
  - Guardrail: test cible `geocodingApi` avec timeout attendu.
- Risk: erreur `token_expired` geree differemment.
  - Guardrail: tests `apiClient` sur conversion d'erreur.
- Risk: migration partielle cachant un `fetch` restant.
  - Guardrail: guard `api-architecture` et inventaire after.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Respect existing imports and tests before adding new files.
- Do not change backend contracts.
- Keep all Python commands, including story validation, behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-001`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-001`
- `_condamad/stories/regression-guardrails.md`
