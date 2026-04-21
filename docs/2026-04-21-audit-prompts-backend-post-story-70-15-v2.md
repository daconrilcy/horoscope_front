# Audit backend generation de prompts LLM (post story 70-15, AC18-AC31)

Date: 2026-04-21  
Perimetre: backend, flux runtime prompting/persona/configuration/gateway, consommateurs metier.

## Source de verite canonique (etat vise)

- Adaptateur applicatif: `app.application.llm.ai_engine_adapter`
- Runtime gateway: `app.domain.llm.runtime.gateway`
- Prompt renderer officiel: `app.domain.llm.prompting.prompt_renderer`
- Persona composer officiel: `app.domain.llm.prompting.personas`
- Legacy runtime access nominal: `app.domain.llm.legacy.bridge` uniquement

## Preuve d adoption canonique (scan imports)

### Imports historiques supprimes ou bornes

- `app.llm_orchestration.services.persona_composer`
  - usage nominal runtime/configuration: **0**
  - usages restants: shims/tests legacy uniquement
- `app.domain.llm.prompting.renderer`
  - usage nominal: **0**
  - statut: **supprime**
- `app.llm_orchestration.legacy_prompt_runtime`
  - usage nominal direct: **0** hors `app.domain.llm.legacy.bridge`

### Imports canoniques verifies

- `app.domain.llm.prompting.personas` consomme par:
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
- `app.domain.llm.prompting.prompt_renderer` consomme par:
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
  - `app.api.v1.routers.admin_llm`
- `app.application.llm.ai_engine_adapter` consomme par services metier:
  - guidance/chat/natal/prediction (+ routes nominales associees)

## Reliquats de compatibilite toleres (justifies)

- `backend/app/llm_orchestration/gateway.py`
  - raison: compatibilite namespace historique (tests/patches)
- `backend/app/llm_orchestration/services/*.py`
  - raison: shims de transition cibles vers `app.domain.llm.*`
- `backend/app/llm_orchestration/legacy_prompt_runtime.py`
  - raison: source data legacy encore exploitee via `app.domain.llm.legacy.bridge`

## Safe to delete next (AC30) — statut apres passe immediate

1. `backend/app/domain/llm/prompting/renderer.py`
   - statut: **supprime**

2. `backend/app/services/ai_engine_adapter.py`
   - statut: **supprime**

3. `backend/app/llm_orchestration/services/persona_composer.py`
   - statut: **supprime**

4. `backend/app/llm_orchestration/services/prompt_renderer.py`
   - raison: shim historique vers canonique
   - import nominal production: aucun
   - usage CI bloquant: oui (tests legacy)
   - statut propose: suppression apres migration tests namespace historique

## Conclusion

- La source de verite runtime est maintenant alignee sur `app.application.llm.*` + `app.domain.llm.*`.
- Les dependances historiques sont bornees a des shims explicites et au bridge legacy nominal.
- Le reliquat principal est des shims historiques strictement bornes (notamment `llm_orchestration/services/prompt_renderer.py` et wrappers namespace legacy).
