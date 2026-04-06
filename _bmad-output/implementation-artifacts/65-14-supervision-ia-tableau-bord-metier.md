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
   **Then** les 10 derniers appels en échec sont listés avec leurs métadonnées d'observabilité disponibles (timestamp, identifiant masqué)

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

### Completion Notes List

- **Fix (code review)** : Les types `float` et `int` dans l'interface TypeScript `UseCaseMetrics` (`estimated_cost_usd`, `avg_latency_ms`, `error_rate`, `retry_rate`) ont été corrigés en `number`. `float` et `int` sont des types Python invalides en TypeScript — ils se résolvent silencieusement en `any` quand `strict` est désactivé.
- **Fix (Epic 65 review)** : le détail des échecs expose `request_id_masked`, la table d'observabilité actuelle ne stockant pas de `user_id`.
- **Fix (Epic 65 review)** : `error_code` n'est plus un placeholder `GENERIC_ERROR` systématique ; il est désormais dérivé de l'état réel du log LLM (`FALLBACK_TRIGGERED`, `REPAIR_FAILED`, `VALIDATION_ERROR`, sinon `LLM_CALL_ERROR`).
- **Clarification métier (admin ops)** : l'endpoint `GET /v1/admin/ai/metrics` ne remonte plus seulement les `use_case` techniques bruts. Les logs LLM sont agrégés en catégories lisibles pour l'admin :
  - `natal_theme_short_free`
  - `natal_theme_short_paid`
  - `natal_theme_complete_paid`
  - `thematic_consultations`
  - `astrologer_chat`
  - `daily_horoscope`
  - `weekly_horoscope`
- **Couverture complète** : les catégories métier attendues sont toujours présentes dans la réponse, même quand leur volume est nul sur la période sélectionnée. Cela évite les trous d'affichage dans le tableau de supervision.
- **Natal par offre** : les métriques de thèmes natals sont désormais regroupées selon les trois variantes métier attendues côté produit :
  - short free
  - short basic/premium
  - complete basic/premium
- **Regroupements additionnels** : les consultations thématiques, le chat astrologue et les horoscopes quotidien/hebdomadaire agrègent chacun plusieurs `use_case` techniques pour produire une vue opérationnelle stable côté admin.
- **UI admin** : `AdminAiGenerationsPage` affiche désormais le libellé métier (`display_name`) renvoyé par l'API au lieu du code technique interne.
