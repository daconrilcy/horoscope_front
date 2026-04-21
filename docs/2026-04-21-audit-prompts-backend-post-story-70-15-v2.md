# Audit backend génération de prompts LLM (post-story 70-15, AC18-AC40)

Date: 2026-04-21  
Dernière passe de review : 2026-04-21 (post-implémentation AC31-AC40)  
Périmètre : backend, flux runtime prompting/persona/configuration/gateway, consommateurs métier.

## Source de vérité canonique (état visé)

- Adaptateur applicatif: `app.application.llm.ai_engine_adapter`
- Runtime gateway : `app.domain.llm.runtime.gateway`
- Prompt renderer officiel : `app.domain.llm.prompting.prompt_renderer`
- Persona composer officiel : `app.domain.llm.prompting.personas`
- Accès runtime legacy nominal : `app.domain.llm.legacy.bridge` uniquement

## Preuve d’adoption canonique (scan imports)

### Imports historiques supprimés ou bornés

- `app.llm_orchestration.services.persona_composer`
  - usage nominal runtime/configuration: **0**
  - usages restants : **0 (fichier supprimé)**
- `app.domain.llm.prompting.renderer`
  - usage nominal: **0**
  - statut : **supprimé**
- `app.llm_orchestration.legacy_prompt_runtime`
  - usage nominal direct: **0** hors `app.domain.llm.legacy.bridge`

### Imports canoniques vérifiés

- `app.domain.llm.prompting.personas` consommé par :
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
- `app.domain.llm.prompting.prompt_renderer` consommé par :
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
  - `app.api.v1.routers.admin_llm`
- `app.application.llm.ai_engine_adapter` consommé par les services métier :
  - guidance/chat/natal/prediction (+ routes nominales associées)

## Reliquats de compatibilité tolérés (justifiés, liste fermée)

- `backend/app/llm_orchestration/gateway.py`
  - raison : compatibilité namespace historique (tests/patches)
- `backend/app/llm_orchestration/services/*.py` (hors `prompt_renderer.py`, supprimé)
  - raison : shims de transition ciblés vers `app.domain.llm.*` (tests/historique)
- `backend/app/llm_orchestration/legacy_prompt_runtime.py`
  - raison : source de données legacy encore exploitée via `app.domain.llm.legacy.bridge`

## Safe to delete next (AC30) — statut post AC31-AC40

1. `backend/app/domain/llm/prompting/renderer.py`
   - statut : **supprimé**

2. `backend/app/services/ai_engine_adapter.py`
   - statut : **supprimé**

3. `backend/app/llm_orchestration/services/persona_composer.py`
   - statut : **supprimé**

4. `backend/app/llm_orchestration/services/prompt_renderer.py`
   - statut : **supprimé**

## Validation de la passe AC31-AC40

- AC31 confirmé : les trois suppressions candidates ont bien été exécutées.
- AC32/AC33/AC36/AC37 confirmés : aucun import `backend/app` vers `app.llm_orchestration.services.prompt_renderer` ; tests et patches historiques migrés vers `app.domain.llm.prompting.prompt_renderer`.
- AC34/AC35/AC39/AC40 confirmés : registre wrappers et audit alignés sur la suppression effective du shim renderer ; phase de migration renderer explicitement clôturée.
- Import canonique confirmé : `app.domain.llm.prompting.prompt_renderer` est la référence runtime/config/admin.
- Aucun import nominal vers `app.services.ai_engine_adapter`.
- Aucun import nominal vers `app.llm_orchestration.services.persona_composer`.
- Les dépendances vers `legacy_prompt_runtime` restent bornées à `app.domain.llm.legacy.bridge`.

## Points de vigilance restants

- Le registre `backend/app/ops/llm/TRANSITION_WRAPPERS.md` doit rester synchronisé à chaque suppression de shim.
- Prochaine cible prioritaire : réduction des derniers wrappers historiques hors renderer (gateway/services namespace).

## Conclusion

- La source de vérité runtime est maintenant alignée sur `app.application.llm.*` + `app.domain.llm.*`.
- Les dépendances historiques sont bornées à des shims explicites et au bridge legacy nominal.
- Le renderer historique est supprimé ; les reliquats principaux restants sont des wrappers namespace legacy strictement bornés.
