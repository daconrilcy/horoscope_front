# Story 65.16 : Config prompts LLM — consultation, diff et rollback

Status: ready-for-dev

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

- [ ] Auditer les endpoints existants dans `admin_llm.py` (AC: 1, 2, 4)
  - [ ] Lire `backend/app/api/v1/routers/admin_llm.py` pour identifier les endpoints prompts déjà présents
  - [ ] Identifier ce qui peut être réutilisé vs ce qui manque
  - [ ] Si des endpoints pour consulter/rollback les prompts existent déjà : les intégrer dans la nouvelle navigation, ne pas recréer
- [ ] Créer ou compléter les endpoints dans un nouveau router `admin_prompts.py` (ou enrichir `admin_llm.py`) (AC: 1, 2, 3, 4)
  - [ ] `GET /api/v1/admin/prompts` — liste use cases avec version active
  - [ ] `GET /api/v1/admin/prompts/{use_case}` — détail + historique versions
  - [ ] `POST /api/v1/admin/prompts/{use_case}/rollback` body: `{target_version_id: str}` — rollback + audit
  - [ ] Guard `require_admin_user` sur tous les endpoints
- [ ] Implémenter le diff côte à côte (AC: 3)
  - [ ] **Option backend** : calculer le diff en Python avec `difflib.unified_diff` et retourner une liste de lignes avec type (`added`/`removed`/`unchanged`)
  - [ ] **Option frontend** : comparer les deux versions côté client avec une implémentation simple ligne par ligne
  - [ ] Choisir l'option backend pour éviter une lib JS de diff
- [ ] Créer `frontend/src/pages/admin/AdminPromptsPage.tsx` (AC: 1, 2, 3, 4)
  - [ ] Liste use cases avec version active, statut (badge), persona
  - [ ] Panneau de détail / sous-route : contenu du prompt actif + historique en timeline
  - [ ] Composant diff : affichage côte à côte avec lignes colorées (ajouts `var(--success)`, suppressions `var(--danger)`)
  - [ ] Bouton "Rollback" sur chaque version historique + modale de confirmation
- [ ] CSS dans `AdminPromptsPage.css` (AC: 3)
  - [ ] `.diff-added` : `var(--success)` background léger
  - [ ] `.diff-removed` : `var(--danger)` background léger
  - [ ] Layout côte à côte du diff : deux colonnes

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

### File List
