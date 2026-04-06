# Story 65.17 : Config personas — consultation et activation/désactivation

Status: done

## Story

En tant qu'**admin ops**,  
je veux consulter et activer/désactiver les personas d'astrologues,  
afin d'ajuster le comportement conversationnel sans déploiement.

## Acceptance Criteria

1. **Given** l'admin accède à l'onglet "Personas" dans `/admin/prompts` (ou sous-section dédiée)  
   **When** la page charge  
   **Then** la liste des personas est affichée avec : nom, statut (active/inactive), description, date de dernière modification

2. **Given** l'admin clique sur une persona  
   **When** le détail s'ouvre  
   **Then** les paramètres complets sont visibles (nom, description, contraintes de comportement, use cases associés)

3. **Given** l'admin désactive une persona active  
   **When** il confirme dans la modale  
   **Then** la persona passe en statut `inactive`  
   **And** un audit log : `action: "persona_deactivated"`, `details: {persona_id, persona_name}`  
   **And** si la persona est assignée à des utilisateurs actifs, un avertissement est affiché avant confirmation

## Tasks / Subtasks

- [x] Auditer les endpoints existants dans `admin_llm.py` et `PersonasAdmin.tsx` (AC: 1, 2, 3)
  - [x] Lire `backend/app/api/v1/routers/admin_llm.py` pour identifier les endpoints personas existants
  - [x] Lire `frontend/src/pages/admin/PersonasAdmin.tsx` (déjà existant) — comprendre ce qui est fait
  - [x] Identifier ce qui peut être réutilisé/migré vs recréé
- [x] Vérifier si un endpoint de désactivation persona existe, sinon créer (AC: 3)
  - [x] `PATCH /api/v1/admin/personas/{persona_id}` body: `{status: "active"|"inactive"}` — avec guard `require_admin_user`
  - [x] Vérifier les utilisateurs assignés à cette persona avant désactivation : `SELECT count(*) FROM users WHERE default_astrologer_id = persona_id AND (subscription active)`
  - [x] Si count > 0 → retourner `{ warning: true, affected_users_count: N }` dans la réponse (le frontend affiche l'avertissement)
  - [x] Générer audit log via `AuditService`
- [x] Adapter `AdminPromptsPage.tsx` pour inclure les personas en sous-section ou onglet (AC: 1, 2, 3)
  - [x] Onglets ou sous-menu dans `/admin/prompts` : "Prompts" + "Personas"
  - [x] Ou sous-page `/admin/prompts/personas` — choisir selon la structure de la page créée en Story 65-16
  - [x] Migrer/adapter le composant `PersonasAdmin.tsx` existant dans la nouvelle structure de navigation
- [x] Ajouter l'audit log sur la désactivation/activation (AC: 3)
  - [x] `action: "persona_deactivated"` ou `"persona_activated"` selon l'action

## Dev Notes

### PersonasAdmin.tsx existant
`frontend/src/pages/admin/PersonasAdmin.tsx` existe déjà (créé en Epic 16). **Lire ce fichier avant toute modification** pour comprendre :
- Ce qui est déjà implémenté
- Les endpoints qu'il consomme
- Le style CSS existant

L'objectif est de **migrer** ce composant dans la nouvelle structure de navigation (sous `/admin/prompts`) sans le recréer.

### LlmPersonaModel existant
`LlmPersonaModel` est dans `backend/app/infra/db/models/`. Les endpoints de gestion des personas sont dans `admin_llm.py`. Ne pas créer de nouveaux endpoints si les existants couvrent déjà les ACs.

### Avertissement utilisateurs affectés
Si une persona est assignée à des utilisateurs (`users.default_astrologer_id = persona_id`), afficher dans la modale :
> "⚠️ Cette persona est utilisée par N utilisateurs actifs. La désactiver peut affecter leur expérience."

Ce champ `affected_users_count` peut être retourné par le `GET /api/v1/admin/personas/{persona_id}` (dans les détails) ou par un endpoint dédié de pre-check.

### Project Structure Notes
- **Ne pas recréer** ce qui existe dans `admin_llm.py` et `PersonasAdmin.tsx`
- Migrer/adapter `PersonasAdmin.tsx` dans la nouvelle navigation
- Modifier : `AdminPromptsPage.tsx` (ajout onglet Personas)
- Prerequisite : Story 65-16 (page Prompts créée)

### References
- `backend/app/api/v1/routers/admin_llm.py` — endpoints personas [Source: session context]
- `frontend/src/pages/admin/PersonasAdmin.tsx` — composant existant à migrer [Source: session context]
- `LlmPersonaModel` : `backend/app/infra/db/models/` [Source: architecture]
- Epic 65 FR65-6b : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-17`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Vérification réalisée le 2026-04-06: la story n'était pas implémentée malgré la présence de l'onglet Personas dans `/admin/prompts`.
- Réutilisation de la structure existante `AdminPromptsPage.tsx` avec remplacement de `PersonasAdmin.tsx` par un écran de gestion réel:
  - liste des personas avec nom, statut, description et date de dernière modification
  - détail avec contraintes, marqueurs de style, use cases associés et paramètres de format
  - modale d'activation/désactivation avec avertissement si des utilisateurs actifs sont impactés
- `AdminPromptsPage.tsx` n'a pas nécessité de modification supplémentaire dans cette story car l'onglet `Personas` était déjà en place; la story s'est branchée sur cette intégration existante.
- Côté backend, ajout du détail `GET /v1/admin/llm/personas/{id}` et enrichissement de l'audit sur activation/désactivation.
- Vérifications exécutées:
  - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_persona_endpoints.py`
  - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/api/v1/routers/admin_llm.py app/tests/integration/test_admin_persona_endpoints.py`
  - `cd frontend; npm test -- src/tests/PersonasAdmin.test.tsx src/tests/AdminPromptsPage.test.tsx`
  - `cd frontend; npx tsc --noEmit`

### File List

- backend/app/api/v1/routers/admin_llm.py
- backend/app/tests/integration/test_admin_persona_endpoints.py
- frontend/src/api/adminPrompts.ts
- frontend/src/api/index.ts
- frontend/src/pages/admin/AdminPromptsPage.tsx
- frontend/src/pages/admin/PersonasAdmin.tsx
- frontend/src/pages/admin/PersonasAdmin.css
- frontend/src/tests/PersonasAdmin.test.tsx
