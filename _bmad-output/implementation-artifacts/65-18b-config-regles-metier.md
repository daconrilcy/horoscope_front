# Story 65.18b : Config règles métier — templates éditoriaux et scoring/calibration

Status: done

## Story

En tant qu'**admin ops**,  
je veux consulter et modifier les templates éditoriaux et les règles de scoring/calibration,  
afin d'ajuster la structure et la qualité des contenus générés sans déploiement.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/content` section "Règles métier"  
   **When** la page charge  
   **Then** deux sous-sections sont visibles : "Templates éditoriaux" et "Règles de calibration"

2. **Given** l'admin consulte un template éditorial  
   **When** le détail s'ouvre  
   **Then** la structure du template est visible (sections, balises attendues, exemple de rendu)  
   **And** le template actif est identifié avec sa version et sa date d'activation

3. **Given** l'admin modifie un template éditorial  
   **When** il sauvegarde après modification  
   **Then** la nouvelle version est enregistrée en DB (versionnée, pas d'écrasement)  
   **And** un audit log : `action: "editorial_template_updated"`, `details: {template_code, before_version, after_version}`  
   **And** le rollback vers la version précédente est disponible

4. **Given** l'admin consulte les règles de calibration  
   **When** la liste s'affiche  
   **Then** chaque règle est présentée avec : code, valeur courante, type (numérique / booléen / enum), description de l'effet

5. **Given** l'admin modifie une règle de calibration  
   **When** il confirme dans la modale  
   **Then** la valeur est mise à jour en DB  
   **And** un audit log : `action: "calibration_rule_updated"`, `details: {rule_code, before, after}`

## Tasks / Subtasks

- [x] Explorer les tables existantes avant tout (AC: 1, 2, 3, 4, 5)
  - [x] Chercher `consultation_template`, `editorial_template`, ou tables similaires dans `backend/app/infra/db/models/`
  - [x] Chercher les modèles de calibration : `calibration.py`, `ruleset`, `calibration_rule` dans les modèles DB
  - [x] Epic 31-42 ont créé des tables de calibration et de règles — identifier les tables utilisables
  - [x] Si aucune table n'est adaptée pour les templates éditoriaux : créer `EditorialTemplateVersionModel` suivant le pattern de `LlmPromptVersionModel`
- [x] Créer/adapter les endpoints dans `admin_content.py` (AC: 2, 3, 4, 5)
  - [x] `GET /api/v1/admin/content/editorial-templates` — liste templates avec version active
  - [x] `GET /api/v1/admin/content/editorial-templates/{template_code}` — détail + historique versions
  - [x] `POST /api/v1/admin/content/editorial-templates/{template_code}/versions` body: `{content: str}` — nouvelle version (pas de PUT/PATCH — versionnage append-only)
  - [x] `POST /api/v1/admin/content/editorial-templates/{template_code}/rollback` body: `{version_id: str}` — rollback
  - [x] `GET /api/v1/admin/content/calibration-rules` — liste règles de calibration
  - [x] `PATCH /api/v1/admin/content/calibration-rules/{rule_code}` body: `{value: Any}` — update + audit
  - [x] Guard `require_admin_user` sur tous les endpoints
- [x] Créer les migrations si nécessaire (AC: 2, 3)
  - [x] Si `EditorialTemplateVersionModel` doit être créé : migration Alembic
  - [x] Si tables calibration déjà existantes : aucune migration
- [x] Adapter `frontend/src/pages/admin/AdminContentPage.tsx` (AC: 1, 2, 3, 4, 5)
  - [x] Ajouter l'onglet/section "Règles métier" à la page créée en Story 65-18
  - [x] Sous-section "Templates éditoriaux" : liste + détail + éditeur + bouton rollback
  - [x] Sous-section "Règles de calibration" : liste + édition inline ou modale

## Dev Notes

### Investigation obligatoire en premier
Avant d'écrire une seule ligne de code, **explorer les modèles existants** :

```
backend/app/infra/db/models/
├── editorial_template*.py ?
├── calibration*.py ?
├── ruleset*.py ?
```

Epic 38 a créé des "templates éditoriaux paramétrables" — chercher les modèles liés. Epic 31-42 ont des tables de calibration et de rulesets. Ces tables peuvent être réutilisées directement.

### Pattern de versionnage
Si `EditorialTemplateVersionModel` doit être créé, suivre exactement le pattern de `LlmPromptVersionModel` :
- Table avec `id`, `template_code`, `content` (TEXT), `status` (`active`/`draft`/`deprecated`), `created_at`, `created_by_user_id`
- Pas d'écrasement : chaque modification crée une nouvelle ligne
- Le rollback change juste `status = "active"` sur l'ancienne version et `status = "deprecated"` sur la courante

### Calibration — tables Epic 37/42
Les tables de calibration ont été créées dans les épics 37, 39, 42. Ces tables contiennent des paramètres numériques (percentiles, seuils, etc.). Identifier la table principale et sa structure avant d'implémenter les endpoints d'édition.

### Périmètre de cette story
Distinct de Story 65-18 (textes paywalls + feature flags). Cette story couvre uniquement les templates éditoriaux et les règles de scoring/calibration.

### Project Structure Notes
- Modifier : `admin_content.py` (ajout endpoints templates et calibration)
- Modifier : `AdminContentPage.tsx` (ajout sous-section "Règles métier")
- Créer si nécessaire : `EditorialTemplateVersionModel` + migration Alembic
- Prerequisite : Story 65-18 doit être livrée ou en cours

### References
- Epic 38 — templates éditoriaux paramétrables [Source: sprint-status.yaml]
- Epic 37 — calibration percentiles [Source: sprint-status.yaml]
- Epic 42 — scoring relatif, calibration [Source: sprint-status.yaml]
- `LlmPromptVersionModel` — pattern de versionnage à suivre [Source: session context]
- Epic 65 FR65-6d : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-18b`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Vérification initiale du 2026-04-06: les templates éditoriaux et règles de calibration n'étaient pas exposés dans `/admin/content`.
- Implémentation réalisée dans le même périmètre que la story 65-18:
  - versionnage DB des templates éditoriaux via `EditorialTemplateVersionModel`
  - endpoints admin pour liste, détail, publication de nouvelle version et rollback
  - exposition des règles de calibration depuis le ruleset actif avec édition et audit
  - sous-section `Règles métier` dans `AdminContentPage.tsx`
- Vérifications exécutées:
  - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_admin_content_api.py`
  - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/api/v1/routers/admin_content.py app/tests/integration/test_admin_content_api.py`
  - `cd frontend; npm test -- src/tests/AdminContentPage.test.tsx`
  - `cd frontend; npx tsc --noEmit`

### File List

- backend/app/api/v1/routers/admin_content.py
- backend/app/infra/db/models/editorial_template.py
- backend/app/tests/integration/test_admin_content_api.py
- backend/migrations/versions/fe2d4b3a1c01_add_admin_content_tables.py
- frontend/src/api/adminContent.ts
- frontend/src/pages/admin/AdminContentPage.tsx
- frontend/src/pages/admin/AdminContentPage.css
- frontend/src/tests/AdminContentPage.test.tsx
