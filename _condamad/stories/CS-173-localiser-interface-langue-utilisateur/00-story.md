# Story CS-173 localiser-interface-langue-utilisateur: Localiser l'interface selon la langue utilisateur

Status: done

## 1. Objective

Permettre à l'application de choisir la langue d'interface depuis la localisation navigateur par
défaut, puis de prioriser la langue sauvegardée sur le compte utilisateur. Le changement ajoute
aussi la persistance minimale des métadonnées de localisation détectées et un sélecteur de langue
dans le top menu.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-16
- Reason for change: les utilisateurs sont raccordés à la table `languages`, mais le front ne
  propose pas encore un choix de langue synchronisé avec cette source de vérité ni une trace de
  localisation détectée.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: préférences utilisateur et localisation d'interface
- In scope:
  - Exposer les langues depuis la table `languages`.
  - Persister la langue par défaut choisie par l'utilisateur.
  - Persister la localisation navigateur minimale: locale, pays et timezone.
  - Ajouter un bouton de langue dans le top menu avec drapeau.
- Out of scope:
  - Traduire tout le catalogue applicatif en nouvelles langues non encore supportées par les bundles i18n front.
  - Modifier les contenus astrologiques localisés hors préférence utilisateur.
  - Ajouter une géolocalisation GPS ou une demande de permission navigateur.
- Explicit non-goals:
  - Ne pas changer le modèle des profils de naissance ni les champs `current_*` existants.
  - Ne pas ajouter de fallback silencieux vers une langue absente de `languages`.
  - Ne pas créer de constante backend concurrente pour le catalogue des langues.
  - Ne pas modifier les invariants astrology DB-backed `RG-091` à `RG-108`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: api-contract-change
- Archetype reason: la story enrichit un contrat API existant et ajoute une route publique de lecture du référentiel `languages`.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les routes GET/PATCH `/v1/users/me/settings` conservent leurs champs existants.
  - Les nouvelles données de localisation restent optionnelles.
  - Le sélecteur front consomme la table `languages` mais n'affiche que les langues d'interface effectivement supportées par le front courant.
- Deletion allowed: no.
- Replacement allowed: no.
- User decision required if: l'utilisateur veut activer allemand/italien comme langue d'interface complète avant que les bundles i18n correspondants existent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La table `languages` reste la source runtime des langues disponibles. |
| Baseline Snapshot | yes | Les contrats settings et reference-data doivent être vérifiés avant/après par tests. |
| Ownership Routing | yes | Backend API expose les contrats, frontend header consomme via clients API centralisés. |
| Allowlist Exception | no | Aucune exception ou fallback legacy n'est autorisée. |
| Contract Shape | yes | Les champs settings et la route languages sont des contrats publics. |
| Batch Migration | no | Migration unique de colonnes optionnelles utilisateurs. |
| Reintroduction Guard | yes | Tests backend/front empêchent une liste de langues locale non raccordée. |
| Persistent Evidence | yes | Tests et story status conservent l'évidence. |

## 4b. Runtime Source of Truth

- Primary source of truth: schéma DB runtime `users` + table `languages` exposée par `LanguageModel`.
- Secondary evidence: `app.openapi()` doit contenir `/v1/reference-data/languages` et les schémas settings enrichis.
- Static scans alone are not sufficient: ils complètent les tests runtime mais ne remplacent pas les appels API d'intégration.
- Runtime source: table SQL `languages`, modèle `LanguageModel`.
- Required implementation: le frontend doit récupérer les options de langue via `/v1/reference-data/languages`.
- Forbidden source: liste backend hardcodée, fichier JSON front autonome, alias de compatibilité.

## 4c. Baseline / Before-After Rule

- Baseline required: oui.
- Baseline artifact before implementation: évidence textuelle en section 5 montrant `default_language_code` sans localisation détectée ni route `languages`.
- Comparison after implementation: tests API settings/languages + test Header confirmant les nouveaux champs et la sélection.
- Expected invariant: les champs existants `astrologer_profile`, `default_astrologer_id`, `default_language_code` restent présents et compatibles.
- Before evidence: `GET /v1/users/me/settings` expose déjà `default_language_code`, sans localisation détectée ni route publique `languages`.
- After evidence: tests d'intégration settings, languages API, et test Header du sélecteur.
- Allowed differences: ajout de champs optionnels et d'une route de lecture publique.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP-only adapter settings | `backend/app/api/v1/routers/public/users.py` | mutation directe depuis un composant sans client API |
| HTTP-only adapter languages | `backend/app/api/v1/routers/public/reference_data.py` | constante backend ou JSON front autonome |
| Frontend language control | `frontend/src/layouts/components/LanguageSelector.tsx` | logique dupliquée dans pages |
| Frontend shell integration | `frontend/src/layouts/components/Header.tsx` | menus de page locaux |

- Canonical owner: `backend/app/api/v1/routers/public/users.py` pour settings,
  `backend/app/api/v1/routers/public/reference_data.py` pour languages,
  `frontend/src/layouts/components/LanguageSelector.tsx` pour le contrôle de langue,
  `frontend/src/layouts/components/Header.tsx` pour son intégration dans le top menu.
- Routing rule: tout appel front passe par `frontend/src/api/*`, pas par `fetch` local dans le composant.

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable.
- Reason: aucune exception durable n'est créée.

## 4f. Contract Shape

- Contract type:
  - HTTP JSON API + types TypeScript front.
- Fields:
  - `code: string` - code langue issu de `languages`.
  - `name: string` - nom de langue issu de `languages`.
  - `astrologer_profile: string` - préférence existante conservée.
  - `default_astrologer_id: string | null` - préférence existante conservée.
  - `default_language_code: string | null` - langue par défaut utilisateur.
  - `detected_locale: string | null` - locale navigateur détectée.
  - `detected_country_code: string | null` - pays dérivé de la locale navigateur.
  - `detected_timezone: string | null` - timezone IANA navigateur.
- Required fields:
  - `data`
  - `meta.request_id`
  - `code`
  - `name`
- Optional fields:
  - `default_astrologer_id`
  - `default_language_code`
  - `detected_locale`
  - `detected_country_code`
  - `detected_timezone`
- Status codes:
  - `200` - lecture ou mise à jour réussie.
  - `401` - utilisateur non authentifié pour settings.
  - `403` - utilisateur interdit pour settings.
  - `404` - utilisateur introuvable pour settings.
  - `422` - langue par défaut non supportée.
  - `500` - erreur serveur settings existante.
- Serialization names:
  - `default_language_code` -> `UserSettings.default_language_code`
  - `detected_locale` -> `UserSettings.detected_locale`
  - `detected_country_code` -> `UserSettings.detected_country_code`
  - `detected_timezone` -> `UserSettings.detected_timezone`
- Frontend type impact:
  - `UserSettings` est enrichi et `LanguageOption` est ajouté.
- Generated contract impact:
  - OpenAPI doit exposer la route languages et les schémas settings enrichis.
- Affected API contracts:
  - `GET /v1/reference-data/languages` retourne `{ data: [{ code, name }], meta }`.
  - `GET/PATCH /v1/users/me/settings` conserve les champs existants et ajoute `detected_locale`, `detected_country_code`, `detected_timezone`.
- Error contract: les erreurs existantes restent centralisées via `build_error_response`.

## 4g. Batch Migration Plan

- Batch migration: not applicable.
- Reason: colonnes nullables sans backfill requis.

## 4h. Persistent Evidence Artifacts

- Persistent evidence required:
  - `_condamad/stories/story-status.md`
  - tests backend et frontend cités dans le plan de validation

| Artifact | Path | Purpose |
|---|---|---|
| Story contract | `_condamad/stories/CS-173-localiser-interface-langue-utilisateur/00-story.md` | Cadrage et AC exécutables. |
| Story registry | `_condamad/stories/story-status.md` | Numéro et statut de la story. |
| Backend tests | `backend/app/tests/integration/test_users_settings.py`, `backend/app/tests/integration/test_reference_languages_api.py` | Preuve durable settings et languages. |
| Frontend test | `frontend/src/tests/layout/Header.test.tsx` | Preuve durable sélecteur Header. |

## 4i. Reintroduction Guard

- Guard required: oui.
- Guard shape: tests d'intégration API + test Header prouvant la source API des langues et la persistance de `default_language_code`.
- Executable evidence:
  - Depuis `backend/`: `pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py`
  - `npm run test -- Header`
  - Depuis `frontend/`: `rg -n "style=" src/layouts/components src/api/languages.ts` doit rester sans hit.

## 4j. Source Finding Closure

- Closure status: not applicable.
- Reason: la story ne provient pas d'un audit finding.

## 5. Current State Evidence

Le code base courant ou l'audit indique:

- Evidence 1: `backend/app/infra/db/models/user.py` - `UserModel` possède déjà `default_language_id`.
- Evidence 2: `backend/app/api/v1/routers/public/users.py` - `/v1/users/me/settings` lit et met à jour `default_language_code`.
- Evidence 3: `docs/db_seeder/languages.json` - les langues canoniques sont seedées dans `languages`.
- Evidence 4: `frontend/src/layouts/components/Header.tsx` - le top menu contient le thème et l'utilisateur, sans sélecteur de langue.
- Evidence 5: `frontend/src/i18n/astrology.ts` - le front détecte une langue depuis `localStorage` puis `navigator.language`.
- Evidence N: `_condamad/stories/regression-guardrails.md` - les invariants de régression partagés ont été consultés avant la finalisation du périmètre de la story.

## 6. Target State

Après implémentation:

- La table `languages` est exposée via une route publique de lecture.
- Le compte utilisateur persiste la langue par défaut, la locale détectée, le pays détecté et la timezone détectée.
- Le Header affiche un bouton langue avec drapeau et options issues de l'API.
- Une préférence utilisateur sauvegardée prime sur la détection locale navigateur.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-003` - la route publique ajoutée doit rester montée par le routeur API v1 canonique.
  - `RG-004` - les erreurs settings restent centralisées.
  - `RG-083` - le Header modifié doit rester compatible dark mode et sans style inline.
  - `RG-108` - la table `languages` reste la source de vérité du vocabulaire métier.
- Non-applicable invariants:
  - `RG-091` à `RG-107` - la story ne modifie pas les référentiels astrologiques ni le runtime chart.
- Required regression evidence:
  - Tests backend `test_users_settings.py` et `test_reference_languages_api.py`.
  - Test frontend `Header.test.tsx`.
  - Scan ciblé confirmant l'absence de `style=` dans le Header.
- Allowed differences:
  - Ajout de colonnes nullable utilisateurs.
  - Ajout du bouton langue dans le Header.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les langues disponibles pour l'interface sont lues depuis la table `languages`. | Test depuis `backend/`: `pytest --long -q app/tests/integration/test_reference_languages_api.py` |
| AC2 | Le compte utilisateur persiste la localisation détectée optionnelle. | Test depuis `backend/`: `pytest --long -q app/tests/integration/test_users_settings.py` |
| AC3 | Le Header persiste le choix utilisateur via le bouton de langue. | Evidence profile: `component-test`; `npm run test -- Header` |
| AC4 | Aucun style inline n'est ajouté dans les composants du top menu. | Test: `npm run test -- Header`; scan depuis `frontend/`: `rg -n "style=" src/layouts/components src/api/languages.ts` |

## 8. Implementation Tasks

- [x] Task 1 - Enrichir les contrats backend de préférences utilisateur (AC: AC2)
  - [x] Ajouter les colonnes nullable de localisation détectée.
  - [x] Exposer les champs dans GET/PATCH settings.

- [x] Task 2 - Exposer le catalogue `languages` (AC: AC1)
  - [x] Ajouter contrat Pydantic public.
  - [x] Ajouter une route publique de lecture triée.

- [x] Task 3 - Ajouter le sélecteur Header (AC: AC3, AC4)
  - [x] Créer le client API front des langues.
  - [x] Ajouter un composant de sélection sans style inline.
  - [x] Synchroniser langue stockée et préférence backend.

- [x] Task 4 - Couvrir et vérifier (AC: AC1, AC2, AC3, AC4)
  - [x] Tests backend ciblés.
  - [x] Test composant Header.
  - [x] Lint/tests ciblés et démarrage local si possible.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `LanguageModel` pour lire les langues.
  - `useUserSettings` et `useUpdateUserSettings` pour les préférences utilisateur.
  - `useAstrologyLabels` pour changer la langue active.
  - `apiFetch` pour le client HTTP.
- Do not recreate:
  - Une liste backend de langues hors table `languages`.
  - Un second système de persistance front hors `localStorage` existant et settings API.
- Shared abstraction allowed only if:
  - Elle évite la duplication entre GET et PATCH settings.

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

- Liste backend hardcodée des langues à côté de `LanguageModel`.
- Style inline dans `frontend/src/layouts/components/Header.tsx`.
- Appel `fetch` direct depuis le composant Header.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Préférences utilisateur publiques | `backend/app/api/v1/routers/public/users.py` | logique de préférence dans composant React |
| Catalogue langues | table `languages` + `LanguageModel` | constante backend ou JSON front |
| Contrôle de langue du top menu | `frontend/src/layouts/components/LanguageSelector.tsx` | logique de sélection dupliquée dans `Header.tsx` ou dans les pages |
| Intégration top menu | `frontend/src/layouts/components/Header.tsx` | menus de page locaux |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Compatibility Notes

- Compatibility impact: ajout compatible de champs optionnels et d'une route de lecture.
- Migration impact: colonnes utilisateurs nullables sans backfill.
- Frontend compatibility: les langues non supportées par les bundles i18n front restent masquées dans le sélecteur.

## 17. Generated Contract Check

- Generated contract check: applicable
- Required generated-contract evidence:
  - OpenAPI contient `/v1/reference-data/languages`.
  - Les champs settings existants restent présents.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/user.py`
- `backend/app/api/v1/routers/public/users.py`
- `backend/app/services/api_contracts/public/users.py`
- `backend/app/api/v1/routers/public/reference_data.py`
- `frontend/src/layouts/components/Header.tsx`
- `frontend/src/layouts/components/Header.css`
- `frontend/src/api/userSettings.ts`
- `frontend/src/i18n/astrology.ts`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/user.py` - colonnes de localisation détectée.
- `backend/migrations/versions/20260516_0119_add_user_detected_locale.py` - migration schéma.
- `backend/app/api/v1/routers/public/users.py` - lecture/écriture settings.
- `backend/app/api/v1/routers/public/reference_data.py` - route languages.
- `frontend/src/layouts/components/Header.tsx` - insertion du sélecteur.
- `frontend/src/layouts/components/LanguageSelector.tsx` - composant de sélection de langue.
- `frontend/src/layouts/components/Header.css` - styles du menu.
- `frontend/src/api/languages.ts` - client API du catalogue de langues.

Likely tests:

- `backend/app/tests/integration/test_users_settings.py`
- `backend/app/tests/integration/test_reference_languages_api.py`
- `frontend/src/tests/layout/Header.test.tsx`

Files not expected to change:

- `backend/app/domain/astrology/**` - hors domaine.
- `frontend/src/App.css` - le Header a son CSS owner.

## 20. Dependency Policy

- New dependencies: none.
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Exécuter ou justifier tout skip:

```bash
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest --long -q app/tests/integration/test_users_settings.py app/tests/integration/test_reference_languages_api.py
cd ..\frontend
npm run test -- Header
npm run lint
rg -n "style=" src/layouts/components src/api/languages.ts
```

## 22. Regression Risks

- Risk: afficher une langue non traduite complètement.
  - Guardrail: le sélecteur filtre les langues de la table sur les langues d'interface supportées par le bundle front courant.
- Risk: casser le contrat settings existant.
  - Guardrail: tests d'intégration settings conservant les champs existants.
- Risk: contourner la source DB des langues.
  - Guardrail: route API languages et test d'intégration.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- `docs/db_seeder/languages.json` - source seed du référentiel langues.
- `_condamad/stories/regression-guardrails.md` - invariants consultés.
