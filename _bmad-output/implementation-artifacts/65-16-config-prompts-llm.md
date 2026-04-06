# Story 65.16 : Config prompts LLM — consultation, diff et rollback

Status: done

## Story

En tant qu'**admin ops**,  
je veux consulter les prompts LLM actifs, voir leur historique et revenir à une version précédente,  
afin d'ajuster la qualité des réponses sans déploiement et de rollback en < 15 min si nécessaire.

## Acceptance Criteria

1. **Given** l'admin accède à `/admin/prompts`  
   **When** la page charge  
   **Then** la liste des use cases est affichée avec pour chacun : version de prompt active, date d'activation, persona associée, statut (`active` / `draft` / `deprecated`)

2. **Given** l'admin clique sur un use case  
   **When** le détail s'ouvre  
   **Then** le prompt actif est affiché avec son contenu complet  
   **And** l'historique des versions précédentes est listé (version, date, auteur de l'activation)

3. **Given** l'admin compare deux versions  
   **When** il sélectionne "Comparer avec la version précédente"  
   **Then** un diff côte à côte est affiché (ajouts en vert `var(--success)`, suppressions en rouge `var(--danger)`)

4. **Given** l'admin décide de revenir à une version précédente  
   **When** il clique "Rollback vers cette version" et confirme dans la modale  
   **Then** la version sélectionnée devient active (NFR21 : rollback exécutable en ≤ 15 min)  
   **And** un audit log : `action: "prompt_rollback"`, `details: {use_case, from_version, to_version}`  
   **And** la page se met à jour avec la nouvelle version active

## Tasks / Subtasks

- [x] Auditer les endpoints existants dans `admin_llm.py` (AC: 1, 2, 4)
  - [x] Lire `backend/app/api/v1/routers/admin_llm.py` pour identifier les endpoints prompts déjà présents
  - [x] Identifier ce qui peut être réutilisé vs ce qui manque
  - [x] Réutiliser les endpoints existants `/v1/admin/llm/use-cases`, `/v1/admin/llm/use-cases/{key}/prompts` et enrichir uniquement le rollback ciblé
- [x] Compléter le router existant `admin_llm.py` (AC: 1, 2, 4)
  - [x] Conserver la liste des use cases et l'historique des versions déjà exposés
  - [x] Étendre `POST /v1/admin/llm/use-cases/{use_case}/rollback` avec un body optionnel `{target_version_id: str}`
  - [x] Générer un audit `llm_prompt_rollback` avec `from_version` et `to_version`
  - [x] Garder `require_admin_user` sur les endpoints admin LLM
- [x] Implémenter le diff côte à côte (AC: 3)
  - [x] Choisir une implémentation frontend simple ligne par ligne pour éviter un nouvel endpoint de diff
  - [x] Afficher les suppressions en fond `var(--error)` léger et les ajouts en fond `var(--success)` léger
- [x] Créer `frontend/src/pages/admin/AdminPromptsPage.tsx` (AC: 1, 2, 3, 4)
  - [x] Liste des use cases avec version active, date d'activation, persona et badge de statut
  - [x] Panneau de détail avec prompt actif complet et historique des versions
  - [x] Composant diff côte à côte pour comparer l'actif à une version historique
  - [x] Bouton "Rollback" avec modale de confirmation et rafraîchissement des données après mutation
- [x] CSS dans `AdminPromptsPage.css` (AC: 3)
  - [x] Layout desktop/mobile sans style inline
  - [x] États visuels pour diff ajouté/supprimé
  - [x] Mise en page des panneaux, historique et modale

## Dev Notes

### PromptRegistryV2 et modèles existants
Le projet utilise `PromptRegistryV2` et les modèles `LlmPromptVersionModel`, `LlmUseCaseConfigModel`. Ces tables ont le versioning des prompts. **Lire `admin_llm.py`** avant d'implémenter — il y a probablement déjà des endpoints de gestion des prompts qui peuvent être réutilisés ou migrés vers la nouvelle structure.

### Rollback ≤ 15 min (NFR21)
Le rollback doit être opérable en < 15 minutes d'un bout à l'autre. L'implémentation doit :
1. Identifier la version cible par ID
2. Mettre `status = "active"` sur la version cible
3. Mettre `status = "deprecated"` sur l'ancienne version active
4. Générer l'audit log
La rapidité d'exécution est garantie si le rollback est une simple mise à jour DB — pas de déploiement requis.

### Diff implementation
Utiliser `difflib` Python stdlib :
```python
import difflib
diff = list(difflib.ndiff(version_a.split('\n'), version_b.split('\n')))
```
Retourner une liste de `{type: "added"|"removed"|"unchanged", text: str}`.

### Intégration navigation
`admin_llm.py` expose actuellement des endpoints sous un prefix non-admin standard. Ces endpoints doivent être accessibles via `/admin/prompts` dans la nouvelle navigation. Deux options :
1. Ajouter un nouveau router `admin_prompts.py` qui réutilise les services de `admin_llm.py`
2. Restructurer `admin_llm.py` avec le bon prefix
Choisir l'option la moins risquée pour la non-régression.

### Project Structure Notes
- Lire `admin_llm.py` en premier
- Nouveau ou enrichi : `admin_prompts.py` (ou wrapper autour d'`admin_llm.py`)
- Nouveau frontend : `AdminPromptsPage.tsx` + `.css`

### References
- `backend/app/api/v1/routers/admin_llm.py` — endpoints prompts existants [Source: session context]
- `LlmPromptVersionModel`, `LlmUseCaseConfigModel`, `PromptRegistryV2` [Source: session context]
- NFR21 (rollback ≤ 15 min) : `_bmad-output/planning-artifacts/epic-65-espace-admin.md`
- Epic 65 FR65-6a : `_bmad-output/planning-artifacts/epic-65-espace-admin.md#Story-65-16`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- 2026-04-06 : la story a été finalisée en réutilisant le router `admin_llm.py` existant au lieu de créer un second router admin prompts.
- Le rollback supporte désormais une cible explicite `target_version_id`, avec audit `from_version`/`to_version`.
- La page `/admin/prompts` expose deux onglets : `Prompts` (liste, détail, diff, rollback) et `Personas` (réutilisation du panneau existant).
- Le diff a été implémenté côté frontend, ligne par ligne, pour limiter le delta backend et éviter une dépendance supplémentaire.

### File List

- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/llm_orchestration/services/prompt_registry_v2.py`
- `backend/app/llm_orchestration/tests/test_admin_llm_api.py`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/api/index.ts`
- `frontend/src/pages/admin/AdminPromptsPage.tsx`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/AdminPromptsPage.test.tsx`

## Senior Developer Review (AI)

- Revue du 2026-04-06 : la story est désormais `done`. Les AC critiques sont couvertes par l'écran `/admin/prompts`, l'historique des versions et le rollback ciblé audité.
