# Story 65.18 : Config contenus & paywalls — textes et feature flags

Status: ready-for-dev

## Story

En tant qu'**admin ops ou product**,  
je veux modifier les textes des paywalls, le wording marketing in-app et activer/désactiver des feature flags,  
afin d'ajuster l'expérience produit sans déploiement.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/content`  
   **When** la page charge  
   **Then** trois sections sont visibles : "Textes paywalls", "Messages transactionnels", "Feature flags"

2. **Given** l'admin édite un texte de paywall  
   **When** il modifie le contenu et sauvegarde  
   **Then** la modification est persistée en DB  
   **And** un audit log : `action: "content_text_updated"`, `details: {content_key, before, after}`  
   **And** un indicateur de version (timestamp de dernière modification) est affiché

3. **Given** l'admin accède à la section "Feature flags"  
   **When** la liste s'affiche  
   **Then** chaque flag est présenté avec : code, description, état courant (activé/désactivé), scope (tous plans / plan spécifique)

4. **Given** l'admin bascule un feature flag  
   **When** il confirme dans la modale  
   **Then** l'état du flag change en DB  
   **And** un audit log : `action: "feature_flag_toggled"`, `details: {flag_code, before: false, after: true}`

## Tasks / Subtasks

- [ ] **Migration Alembic — OBLIGATOIRE EN PREMIER** : créer `ConfigTextModel` (AC: 2)
  - [ ] Table `config_texts` : `id`, `key` (unique), `value` (TEXT), `category` (`paywall`/`transactional`/`marketing`), `updated_at`, `updated_by_user_id` (FK users)
  - [ ] Créer le modèle SQLAlchemy `ConfigTextModel` dans `backend/app/infra/db/models/config_text.py`
  - [ ] Migration Alembic `add_config_texts_table`
  - [ ] Seed initial : quelques clés paywall de test pour le dev (optionnel mais recommandé)
- [ ] Créer le router `backend/app/api/v1/routers/admin_content.py` (AC: 1, 2, 3, 4)
  - [ ] `GET /api/v1/admin/content/texts?category=paywall` — liste textes filtrés
  - [ ] `PATCH /api/v1/admin/content/texts/{key}` body: `{value: str}` — mise à jour texte + audit
  - [ ] `GET /api/v1/admin/content/feature-flags` — liste flags depuis ops router existant ou DB
  - [ ] `PATCH /api/v1/admin/content/feature-flags/{flag_code}` body: `{enabled: bool}` — toggle + audit
  - [ ] Guard `require_admin_user` sur tous les endpoints
- [ ] Vérifier le router `ops_feature_flags.py` existant (AC: 3, 4)
  - [ ] Lire le router existant — si les endpoints feature flags existent déjà, les wrapper plutôt que dupliquer
  - [ ] S'assurer que le guard passe à `require_admin_user`
- [ ] Créer `frontend/src/pages/admin/AdminContentPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Trois sections en onglets : "Textes paywalls", "Messages transactionnels", "Feature flags"
  - [ ] Section textes : liste clés + valeurs éditables (textarea inline ou édition en place)
  - [ ] Indicateur `updated_at` visible pour chaque texte édité
  - [ ] Section feature flags : liste avec toggle (switch ou bouton) + scope
  - [ ] Modale de confirmation avant chaque toggle de flag (AC: 4)
- [ ] CSS dans `AdminContentPage.css` (AC: 1)

## Dev Notes

### Nouveau modèle ConfigTextModel — CRITIQUE
**Ce modèle n'existe pas encore** — la migration doit être créée avant les endpoints. Structure minimale :
```sql
CREATE TABLE config_texts (
  id SERIAL PRIMARY KEY,
  key VARCHAR(255) UNIQUE NOT NULL,
  value TEXT NOT NULL,
  category VARCHAR(64) NOT NULL,  -- 'paywall', 'transactional', 'marketing'
  updated_at TIMESTAMPTZ DEFAULT now(),
  updated_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);
```

### Feature flags existants
L'Epic 11 et d'autres epics ont probablement implémenté des feature flags. Chercher `ops_feature_flags.py` ou un service `feature_flag_service.py`. Ne pas recréer un système de feature flags — utiliser l'existant.

### Édition de texte en place
Pour l'édition des textes paywalls, deux options UI :
1. **Édition inline** : clic sur le texte → input/textarea in-place → save on blur/Enter
2. **Panneau latéral** : clic → panneau avec textarea + bouton Save

Choisir l'option 1 (inline) pour la simplicité — vérifier si le projet a un composant d'édition inline existant.

### Périmètre de cette story
**Textes paywalls + messages transactionnels + feature flags uniquement.** Les templates éditoriaux et règles de scoring/calibration sont dans Story 65-18b. Ne pas les inclure ici.

### Project Structure Notes
- **OBLIGATOIRE en premier** : migration `config_texts` + `ConfigTextModel`
- Nouveaux fichiers backend : `admin_content.py` router + schemas
- Nouveau frontend : `AdminContentPage.tsx` + `.css`
- Vérifier `ops_feature_flags.py` avant d'implémenter les feature flags

### References
- `backend/app/api/v1/routers/` — chercher `ops_feature_flags.py` [Source: architecture]
- Epic 11 — feature flags [Source: sprint-status.yaml]
- Epic 65 FR65-6c, FR65-6e : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-18`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

## Senior Developer Review (AI)

- Constat du 2026-04-06 : la story est correctement laissée `ready-for-dev`. `frontend/src/pages/admin/AdminContentPage.tsx` est encore un placeholder et aucun modèle/router admin de contenu (`ConfigTextModel`, `admin_content.py`) n'est présent côté backend. L'epic ne doit pas présenter cette story comme livrée tant que ces éléments n'existent pas.
