<!-- Candidats stories issus du re-audit App.css apres CS-121 a CS-124. -->

# Story Candidates - frontend-app-css-standardization

## Exhaustive Files To Modify

### F-001

- Application files:
  - `frontend/src/App.css`
  - all TSX consumers returned by `rg -n "app-(page|section|stack|grid|card|panel|state|badge|avatar|modal|actions|list)|precision-badge|evidence-pill|evidence-tags" frontend/src -g "*.tsx"`
  - exact CSS owner files only if a classified prefix is extracted from `App.css` to an existing page/feature stylesheet; no new base folder under `backend/`
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md` if typographic roles are changed
- Selection rule:
  - all `--app-*` custom properties whose first semantic segment is not one of the accepted primitives documented by the story;
  - all selectors in `App.css` backed only by those properties;
  - no wildcard exception and no broad folder exception.

### F-002

- Application files:
  - `frontend/src/App.css`
  - `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
  - `frontend/src/features/consultations/components/DataCollectionStep.tsx`
  - `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
- Selection rule:
  - exact active consumers of `.precision-badge*`, `.evidence-tags*`, `.evidence-pill*` and their matching `--app-precision-*` / `--app-evidence-*` variables.

## Candidate Summary

## SC-001 - Fermer la taxonomie des variables App restantes

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Fermer la taxonomie des variables App restantes
- Suggested archetype: registry-catalog-refactor
- Primary domain: frontend-app-css-standardization
- Required contracts: Baseline Snapshot, Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence, No Legacy / DRY
- Draft objective: transformer l'inventaire `--app-*` restant en une taxonomie fermee: primitives generiques documentees, owners semantiques acceptes, extractions page/feature existantes, ou suppressions avec consommateurs migres.
- Closure intent: full-closure
- Must include:
  - baseline prefix count reproduisant E-013;
  - table de decision pour chaque prefix `--app-*` encore present;
  - migration ou justification source-backed pour `person`, `people`, `activity`, `premium`, `flow`, `summary`, `precision`, `evidence`, `chat`, `usage`;
  - aucun alias de classe pour preserver un ancien nom;
  - mise a jour de `token-namespace-registry.md` uniquement pour les owners conserves.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
  - `npm run build`
  - scan before/after des prefixes `--app-*`
  - `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" frontend/src/App.css`
- Blockers:
  - stop si un prefix non generique doit rester comme contrat public permanent sans owner documente.
- Required reintroduction guard:
  - guard exact sur la liste des prefixes autorises; exceptions uniquement exactes, datees, et sans wildcard.
- Stop condition:
  - aucun prefix `--app-*` non classe;
  - aucune variable `--app-*` issue d'un owner page/feature n'est conservee dans `App.css` sans justification source-backed;
  - F-001 peut etre marque closed par un scan reproductible.

## SC-002 - Migrer ou garder explicitement `precision/evidence`

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Migrer ou garder explicitement les familles `precision` et `evidence`
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-app-css-standardization
- Required contracts: Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence, No Legacy / DRY
- Draft objective: fermer le residu de SC-003 en migrant `.precision-badge*` et `.evidence-*` vers primitives App existantes ou vers owners feature-scoped explicites, puis durcir la garde CS-124.
- Closure intent: full-closure
- Must include:
  - decision explicite pour `.precision-badge`, `.precision-badge--high|medium|limited|blocked`;
  - decision explicite pour `.evidence-tags`, `.evidence-tags__title`, `.evidence-tags__list`, `.evidence-pill`, `.evidence-pill__dot`, `.evidence-pill--planet|aspect|angle`;
  - migration des consumers exacts listes dans F-002 ou preuve que la classe devient feature-scoped hors `App.css`;
  - scan zero-hit des anciens noms dans `frontend/src/App.css` si migres;
  - extension du guard App si une conservation temporaire est autorisee.
- Validation hints:
  - `npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke`
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
- Blockers:
  - stop si `precision-badge` ou `evidence-pill` est considere comme API CSS publique; dans ce cas, documenter le contrat et l'ajouter comme exception exacte avec sortie.
- Required reintroduction guard:
  - no-wildcard scan for `precision-|evidence-` in `App.css` or exact allowlist entries with expiry.
- Stop condition:
  - F-002 closed by zero-hit or exact source-backed allowlist;
  - no additional follow-up story needed for `precision/evidence`.

## Deferred Non-Domain Context

- CSS page-scoped hors `App.css`, par exemple `Settings.css` ou `AstrologerProfilePage.css`, reste hors domaine sauf si une migration extrait explicitement un owner depuis `App.css`.
- Les gros fichiers TSX d'admin prompts visibles dans les scans de consommateurs sont couverts par les audits/stories de decomposition page/component architecture, pas par ce domaine sauf pour leurs `className` App.
