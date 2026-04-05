# Story 65.12 : Matrice entitlements — vue canonique consultation (plans × features)

Status: in-progress

## Story

En tant qu'**admin ops ou business**,  
je veux consulter une matrice visuelle des droits par plan,  
afin d'avoir en un seul écran la source de vérité sur ce que chaque plan permet, sans ambiguïté entre DB, backend et frontend.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/entitlements`  
   **When** la page charge  
   **Then** une matrice est affichée avec :
   - Colonnes : plans (free / basic / premium + tout plan actif en DB)
   - Lignes : chaque feature/use case (horoscope_daily, natal_interpretation, chat, etc.)
   - Cellules : pour chaque plan × feature : mode d'accès (disabled / quota / unlimited), valeur du quota, période de reset, règles trial/lifetime, variant de génération LLM attendu, indicateur teaser (oui/non)

2. **Given** la matrice est affichée  
   **When** l'admin survole une cellule  
   **Then** un tooltip affiche les détails complets de l'entitlement correspondant (valeurs exactes depuis DB)

3. **Given** les données sont issues de la DB (`plan_catalog` + `product_entitlements`)  
   **When** la matrice est construite  
   **Then** toutes les valeurs reflètent exactement ce qui est en base — pas de valeurs hardcodées frontend  
   **And** une section "Règles backend / comportement frontend attendu" est visible en bas de page pour chaque feature (annotation éditoriale, non éditée via cette vue)

4. **Given** un plan a une valeur incohérente (ex : quota à 0 avec mode `quota`)  
   **When** la cellule est affichée  
   **Then** un indicateur visuel d'alerte est présent sur la cellule (icône + couleur `var(--danger)`)

## Tasks / Subtasks

- [ ] Créer le router `backend/app/api/v1/routers/admin_entitlements.py` (AC: 1, 3, 4)
  - [ ] `GET /api/v1/admin/entitlements/matrix` — guard `require_admin_user`
  - [ ] Requête cross-table : `SELECT * FROM plan_catalog` + `SELECT * FROM product_entitlements ORDER BY plan_code, feature_code`
  - [ ] Structurer la réponse en matrice : `{ plans: [...], features: [...], cells: { "plan_code:feature_code": { access_mode, quota_value, reset_period, ... } } }`
  - [ ] Détecter les incohérences : `access_mode = "quota" AND quota_value = 0` → flag `is_incoherent: true`
- [ ] Créer les schémas Pydantic `backend/app/api/v1/schemas/admin_entitlements.py` (AC: 1)
  - [ ] `EntitlementMatrixResponse` avec plans, features, cells
  - [ ] `EntitlementCell` : access_mode, quota_value, reset_period, is_trial, is_lifetime, llm_variant, is_teaser, is_incoherent
- [ ] Explorer les modèles entitlements canoniques (AC: 1, 3)
  - [ ] Vérifier `plan_catalog`, `product_entitlements`, `PlanCatalogModel`, `ProductEntitlements` dans `backend/app/infra/db/models/`
  - [ ] Epic 61 a créé le modèle canonique — vérifier les champs exacts disponibles
- [ ] Créer `frontend/src/pages/admin/AdminEntitlementsPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Tableau HTML avec plans en colonnes, features en lignes
  - [ ] Cellules avec valeur principale + indicateurs visuels (teaser, quota, unlimited)
  - [ ] Tooltip au survol : afficher les détails complets de la cellule
  - [ ] Indicateur d'alerte sur les cellules incohérentes (`var(--danger)`)
  - [ ] Section "Annotations" en bas de page (texte statique ou données editoriales)
  - [ ] Bouton "Mode édition" visible mais inactif si `canEdit("entitlements") = false` (Story 65-21 finalise, mais préparer la prop)
- [ ] CSS dans `frontend/src/pages/admin/AdminEntitlementsPage.css` (AC: 1, 2, 4)
  - [ ] Layout tableau responsive : `overflow-x: auto` pour petits écrans
  - [ ] `.cell--incoherent` avec `var(--danger)` background light
  - [ ] `.cell--teaser` avec indicateur visuel
  - [ ] Tooltip CSS ou JS minimal
  - [ ] Variables : `var(--glass)`, `var(--line)`, `var(--text-1)`, `var(--text-2)`

## Dev Notes

### Modèle entitlements canonique (Epic 61)
L'Epic 61 a refactorisé intégralement le modèle d'entitlements. Les tables clés sont :
- `plan_catalog` (`PlanCatalogModel`) : plans tarifaires avec codes, prix, flags
- `product_entitlements` (`ProductEntitlements`) : règles par plan × feature : access_mode, quota_value, reset_period, trial_quota, etc.

**Lire les modèles avant d'écrire le endpoint** pour connaître les champs exacts disponibles. Ne pas hardcoder de noms de features.

### Vue canonique = aucun hardcoding
La matrice doit être 100% driven par la DB — les plans et features affichés doivent venir de `plan_catalog` et `product_entitlements`, pas d'une liste statique dans le frontend.

### Tooltip
Implémenter un tooltip simple en CSS pur (`:hover` + `position: absolute`) ou avec un state React (`useState`) — ne pas installer une lib de tooltip.

### Distinction consultation / édition (FR65-15)
Cette story couvre uniquement le **mode consultation** (lecture seule). Le mode édition est dans Story 65-13. Le bouton "Mode édition" peut être préparé dans cette story mais il sera fonctionnel en Story 65-13.

### Project Structure Notes
- Nouveaux fichiers backend : `admin_entitlements.py` router + schemas
- Nouveau fichier frontend : `AdminEntitlementsPage.tsx` + `.css`

### References
- Modèles Epic 61 : `PlanCatalogModel`, `ProductEntitlements` dans `backend/app/infra/db/models/` [Source: sprint-status.yaml — epic 61 done]
- Epic 65 FR65-4a, FR65-15 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-12`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
