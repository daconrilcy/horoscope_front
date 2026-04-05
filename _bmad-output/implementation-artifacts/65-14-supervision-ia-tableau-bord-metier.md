# Story 65.14 : Supervision IA — tableau de bord métier des use cases LLM

Status: done

## Story

En tant qu'**admin ops ou product**,  
je veux voir les performances métier des use cases LLM (volume, coût, latence, taux d'échec),  
afin de détecter rapidement une dérive ou une surconsommation avant qu'elle impacte les coûts ou l'expérience.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/ai-generations`  
   **When** la page charge  
   **Then** un tableau de bord affiche pour chaque use case actif (sur la période sélectionnée) :
   - Volume total d'appels
   - Coût tokens estimé
   - Temps de réponse moyen
   - Taux d'échec (calls avec status `error` / total)
   - Taux de retry (actuellement à 0 car non tracké en DB)

2. **Given** l'admin applique un filtre de période (7j / 30j)  
   **When** le filtre change  
   **Then** tous les métriques recalculent pour la période choisie

3. **Given** un use case a un taux d'échec > seuil (ex : 5%)  
   **When** il apparaît dans le tableau  
   **Then** sa ligne est surlignée avec `var(--danger)` ou un indicateur visuel d'alerte

4. **Given** l'admin clique sur un use case  
   **When** le détail s'ouvre  
   **Then** les 10 derniers appels en échec sont listés avec leurs métadonnées (timestamp, user_id masqué)

## Tasks / Subtasks

- [x] Créer le router `backend/app/api/v1/routers/admin_ai.py` (AC: 1, 2, 4)
  - [x] `GET /api/v1/admin/ai/metrics` — group by `use_case`
  - [x] `GET /api/v1/admin/ai/metrics/{use_case}` — detail with failures
  - [x] Calcul robuste de l'error_rate via `sqlalchemy.case`
- [x] Créer les schémas `backend/app/api/v1/schemas/admin_ai.py`
- [x] Mettre à jour `backend/app/main.py` : ajout du router `admin_ai_router`
- [x] Créer `frontend/src/pages/admin/AdminAiGenerationsPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Tableau récapitulatif
  - [x] Filtre de période
  - [x] Panneau de détail coulissant/conditionnel
- [x] CSS dans `AdminAiGenerationsPage.css` (AC: 3)
- [x] Tests d'intégration backend `backend/app/tests/integration/test_admin_ai_api.py`

### File List
- `backend/app/api/v1/routers/admin_ai.py`
- `backend/app/api/v1/schemas/admin_ai.py`
- `backend/app/main.py`
- `frontend/src/pages/admin/AdminAiGenerationsPage.tsx`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `backend/app/tests/integration/test_admin_ai_api.py`
