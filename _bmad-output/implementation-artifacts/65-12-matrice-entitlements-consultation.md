# Story 65.12 : Matrice entitlements — vue canonique consultation (plans × features)

Status: done

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

- [x] Créer le router `backend/app/api/v1/routers/admin_entitlements.py` (AC: 1, 3, 4)
  - [x] `GET /api/v1/admin/entitlements/matrix` — guard `require_admin_user`
  - [x] Requête avec `.unique()` pour gérer les `joinedload` de collections
  - [x] Détecter les incohérences : mode `quota` sans quota défini ou à 0
- [x] Créer les schémas Pydantic `backend/app/api/v1/schemas/admin_entitlements.py`
- [x] Créer `frontend/src/pages/admin/AdminEntitlementsPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Matrice dynamique Plans x Features
  - [x] Tooltip au survol (CSS/JS)
  - [x] Indicateurs visuels (icones, couleurs)
- [x] CSS dans `AdminEntitlementsPage.css` (AC: 1, 2, 4)
  - [x] Sticky columns pour navigation facilitée
  - [x] Styles des types de cellules
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_entitlements_api.py`

### File List
- `backend/app/api/v1/routers/admin_entitlements.py`
- `backend/app/api/v1/schemas/admin_entitlements.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminEntitlementsPage.tsx`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `backend/app/tests/integration/test_admin_entitlements_api.py`
