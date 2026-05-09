<!-- Candidats stories pour fermer la standardisation de App.css. -->

# Story Candidates - frontend-app-css-standardization

## Exhaustive Files To Modify

### F-001

- Application files:
  - `frontend/src/App.css`
  - `frontend/src/styles/design-tokens.css`
  - `frontend/src/styles/utilities.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/typography-roles.md`
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `_condamad/stories/story-status.md`

### F-002

- Application files:
  - `frontend/src/App.css`
  - `frontend/src/App.tsx`
  - `frontend/src/layouts/**/*.tsx`
  - `frontend/src/pages/**/*.tsx`
  - `frontend/src/features/**/*.tsx`
  - `frontend/src/components/**/*.tsx`
- Selection rule: only consumers using classes currently styled in `frontend/src/App.css`; do not touch CSS files outside `App.css` except tests/registries required by guards.
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - targeted page/component tests touched by className changes

### F-003

- Application files:
  - `frontend/src/App.css`
  - TSX consumers of App.css classes matching `astrologer-*`, `consultation-*`, `dashboard-summary-*`, `settings-*`, `modal-*`, `precision-*`, `evidence-*`, `wizard-*`.
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - targeted tests for pages/components touched

### F-004

- Application files:
  - `frontend/src/App.css`
  - `frontend/src/styles/token-namespace-registry.md`
  - `frontend/src/styles/legacy-style-surface-registry.md`
- Governance/test files:
  - `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/design-system-allowlist.ts` only for exact, expiring exceptions

## Candidate Summary

## SC-001 - Definir les primitives CSS generiques App

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Definir les primitives CSS generiques App
- Suggested archetype: registry-catalog-refactor
- Primary domain: frontend-app-css-standardization
- Required contracts: Baseline Snapshot, Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence
- Draft objective: creer la taxonomie App de classes generiques reutilisables, declarer les tokens/roles autorises et documenter les arrondis de spacing, radius, typographie, elevation et etats.
- Closure intent: phased-with-map
- Must include:
  - dictionnaire de primitives comme `.app-page`, `.app-section`, `.app-stack`, `.app-grid`, `.app-card`, `.app-panel`, `.app-action`, `.app-state`, `.app-badge`, `.app-avatar`, `.app-modal`;
  - mapping des classes specifiques existantes vers ces primitives;
  - decision explicite pour chaque namespace `--app-*` conserve, promu ou supprime;
  - aucun nom de primitive lie a une page, service, astrologer, consultation, dashboard, settings ou wizard.
- Validation hints:
  - `npm run test -- design-system theme-tokens legacy-style`
  - scan des noms de primitives et registre.
- Blockers:
  - stop si une difference visuelle substantielle est necessaire au lieu d'un arrondi raisonnable.

## SC-002 - Migrer layouts, etats et actions vers les primitives App

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Migrer layouts, etats et actions vers les primitives App
- Suggested archetype: dead-code-removal
- Primary domain: frontend-app-css-standardization
- Required contracts: Baseline Snapshot, Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence
- Draft objective: migrer les consumers structurels vers les primitives SC-001 puis supprimer les anciens selecteurs devenus morts.
- Closure intent: phased-with-map
- Must include:
  - migration des consommateurs TSX des classes structurelles App;
  - suppression des variables one-shot associees;
  - preuve before/after du nombre de classes specifiques restantes;
  - preservation des routes et comportements.
- Validation hints:
  - `npm run test -- design-system visual-smoke App router`
  - tests cibles des pages modifiees.
- Blockers:
  - stop si une classe structurelle est consommee par un CSS externe non inventorie.

## SC-003 - Migrer cartes, listes, badges et modales vers les primitives App

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Migrer cartes, listes, badges et modales vers les primitives App
- Suggested archetype: dead-code-removal
- Primary domain: frontend-app-css-standardization
- Required contracts: Baseline Snapshot, Ownership Routing, Batch Migration, Reintroduction Guard, Persistent Evidence
- Draft objective: migrer les families visuelles vers variantes generiques puis supprimer les classes et variables page-specific devenues inutiles.
- Closure intent: phased-with-map
- Must include:
  - lots distincts cartes, listes, badges/pills, avatars/media, modales;
  - migration TSX exacte des consumers;
  - aucun wrapper ou alias de classe pour preserver les anciens noms;
  - artefact des classes/variables supprimees.
- Validation hints:
  - `npm run test -- design-system visual-smoke AstrologersPage ConsultationsPage SettingsPage DashboardPage`
  - scans zero-hit des anciens prefixes migres.
- Blockers:
  - stop si un ancien nom de classe est expose comme contrat externe documente.

## SC-004 - Bloquer les selecteurs et variables App specifiques

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Bloquer les selecteurs et variables App specifiques
- Suggested archetype: architecture-guard-hardening
- Primary domain: frontend-app-css-standardization
- Required contracts: Runtime Source of Truth, Allowlist Exception, Reintroduction Guard, Persistent Evidence
- Draft objective: ajouter la garde finale qui interdit les nouveaux selecteurs ou variables `--app-*` specifiques dans `App.css` et plafonne la surface autorisee aux primitives generiques documentees.
- Closure intent: full-closure
- Must include:
  - garde deterministe sur `App.css` pour prefixes interdits et mots de domaine;
  - allowlist exacte et expiree uniquement pour les surfaces que SC-002/SC-003 ne peuvent pas supprimer sans decision;
  - scan zero-hit du commentaire `OLD` et du vocabulaire No Legacy non classe;
  - stop condition: aucun finding F-001 a F-004 ne reste ouvert dans le domaine.
- Validation hints:
  - `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`
  - `npm run lint`
- Blockers:
  - stop si une exception permanente de classe page-specific est demandee.

## Deferred Non-Design-System Context

- Performance bundle-size Vite: deja identifiee par l'audit `frontend-design-system/2026-05-08-0054`; hors domaine.
- CSS files hors `App.css`: peuvent beneficier des primitives, mais la fermeture de cet audit ne doit pas migrer les CSS page-scoped existants hors demande explicite.
