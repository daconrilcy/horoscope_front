# Story 65.14 : Supervision IA — tableau de bord métier des use cases LLM

Status: ready-for-dev

## Story

En tant qu'**admin ops ou product**,  
je veux voir les performances métier des use cases LLM (volume, coût, latence, taux d'échec),  
afin de détecter rapidement une dérive ou une surconsommation avant qu'elle impacte les coûts ou l'expérience.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/ai-generations`  
   **When** la page charge  
   **Then** un tableau de bord affiche pour chaque use case actif (sur la période sélectionnée) :
   - Volume total d'appels
   - Coût tokens estimé (prompt + completion tokens × prix unitaire configuré)
   - Temps de réponse moyen (p50 et p95)
   - Taux d'échec (calls avec status `error` / total)
   - Taux de retry (calls avec `retry_count > 0` / total)
   - Persona et prompt version les plus utilisés

2. **Given** l'admin applique un filtre de période (7j / 30j)  
   **When** le filtre change  
   **Then** tous les métriques recalculent pour la période choisie

3. **Given** un use case a un taux d'échec > seuil (ex : 5%)  
   **When** il apparaît dans le tableau  
   **Then** sa ligne est surlignée avec `var(--danger)` ou un indicateur visuel d'alerte

4. **Given** l'admin clique sur un use case  
   **When** le détail s'ouvre  
   **Then** un graphe de tendance temporelle du volume et du taux d'échec est affiché  
   **And** les 10 derniers appels en échec sont listés avec leurs métadonnées (timestamp, error_code, user_id masqué)

## Tasks / Subtasks

- [ ] Créer le router `backend/app/api/v1/routers/admin_ai.py` (AC: 1, 2, 4)
  - [ ] `GET /api/v1/admin/ai/metrics?period=7d` — guard `require_admin_user`
  - [ ] Agréger depuis `llm_call_logs` (ou `llm_observability`) : GROUP BY `use_case`
  - [ ] Calculer : count, sum(tokens_prompt + tokens_completion), avg(duration_ms), p50/p95 (percentile approximatif en SQL), count(status='error'), count(retry_count > 0), mode(persona_id), mode(prompt_version_id)
  - [ ] Coût estimé : `sum(tokens) × prix_unitaire_configuré` — prix unitaire en config ou constante (ex : GPT-4o : 0.01$/1K tokens — vérifier la config du projet)
  - [ ] `GET /api/v1/admin/ai/metrics/{use_case}?period=7d` — détail avec trend + derniers appels en échec
  - [ ] Masquer `user_id` : retourner seulement les 3 premiers caractères + "..." (protection partielle)
- [ ] Créer les schémas `backend/app/api/v1/schemas/admin_ai.py` (AC: 1, 4)
  - [ ] `UseCaseMetrics` : use_case, call_count, estimated_cost_cents, p50_ms, p95_ms, error_rate, retry_rate, top_persona, top_prompt_version
  - [ ] `UseCaseDetailResponse` : métriques + trend_data + failed_calls
- [ ] Créer `frontend/src/pages/admin/AdminAiGenerationsPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Sélecteur de période (7j / 30j)
  - [ ] Tableau des use cases avec métriques
  - [ ] Ligne rouge/alerte si taux d'échec > 5% (`var(--danger)`)
  - [ ] Clic sur ligne → panneau de détail ou sous-route avec graphe + liste échecs
- [ ] CSS dans `AdminAiGenerationsPage.css` (AC: 3)
  - [ ] `.row--alert` avec background `var(--danger)` léger
  - [ ] Tableau responsive

## Dev Notes

### Source de données — LlmCallLogModel
- Table `llm_call_logs` ou `llm_observability` (vérifier le nom exact dans `backend/app/infra/db/models/`)
- `LlmCallLogModel` : champs attendus : `use_case`, `status` (success/error), `duration_ms`, `tokens_prompt`, `tokens_completion`, `retry_count`, `persona_id`, `prompt_version_id`, `user_id`, `created_at`
- Si certains champs n'existent pas exactement sous ces noms, adapter le code aux champs réels

### P50/P95 en PostgreSQL
Pour le p50/p95 approximatif sans extension dédiée :
```sql
percentile_cont(0.5) WITHIN GROUP (ORDER BY duration_ms) AS p50_ms,
percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms
```
Ces fonctions sont disponibles nativement en PostgreSQL — pas de lib externe nécessaire.

### Coût tokens
Le prix unitaire des tokens doit être en configuration (pas hardcodé). Vérifier si le projet a une config de prix LLM (`settings.llm_token_price` ou équivalent). Si absent, utiliser une constante documentée en attente de configuration.

### Distinction avec Story 65-15
Ce panneau est **métier** : volume, coût, qualité — pas les incidents techniques. La story 65-15 couvre les erreurs applicatives, les logs filtrables détaillés et le replay. Ne pas dupliquer la liste des logs LLM ici — juste les agrégats.

### Masquage user_id
Pour les 10 derniers appels en échec (AC: 4), masquer le `user_id` : `str(user_id)[:3] + "..."`. Objectif : permettre le diagnostic sans exposer l'identité complète.

### Project Structure Notes
- Nouveaux fichiers : `admin_ai.py` router + schemas
- Nouveau frontend : `AdminAiGenerationsPage.tsx` + `.css`
- Endpoint existant dans `admin_llm.py` : vérifier s'il y a des requêtes d'agrégation réutilisables

### References
- `backend/app/api/v1/routers/admin_llm.py` — endpoints LLM existants [Source: session context]
- `LlmCallLogModel` : `backend/app/infra/db/models/` [Source: architecture]
- Epic 65 FR65-5 : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-14`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
