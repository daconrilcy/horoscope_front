# Audit backend génération de prompts LLM (post-story 70-15, AC18-AC52)

Date: 2026-04-21  
Dernière passe de review : 2026-04-21 (post-implémentation AC41-AC52)  
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

## Validation de la passe AC41-AC52

- AC41/AC44/AC45 confirmés : inventaire et classement des wrappers historiques alignés dans `backend/app/ops/llm/TRANSITION_WRAPPERS.md` ("supprimer maintenant" vs "conserver temporairement").
- AC42 confirmé (delta nominal) : les points d’entrée canoniques runtime/configuration migrés vers des imports `app.domain.llm.*` directs pour `composition`, `validation`, `fallback`, `assemblies`, `execution_profiles`, et imports internes `gateway`/`assembly_admin_service`.
- AC43/AC46/AC47 : aucune nouvelle dépendance tests/patches au renderer historique ; les migrations antérieures restent effectives. Les reliquats de tests historiques hors renderer sont explicitement traités comme dette bornée.
- AC48 confirmé (partiel ciblé) : les modules canoniques touchés n’utilisent plus les wrappers historiques simples quand un module canonique existe ; les outils restant en historique sont maintenus avec justification de compatibilité.
- AC49/AC50 confirmés : documentation de transition nettoyée et cohérente ; état résiduel `llm_orchestration` explicite, sans ambiguïté sur la référence canonique.
- AC52 confirmé : la phase "wrappers namespace historiques" est clôturée comme stratégie diffuse ; les reliquats restants sont listés comme dette isolée et datée.

## Analyse dédiée du dossier `backend/app/prompts`

### Inventaire (inclus dans le périmètre AC41-AC52)

- `catalog.py`
- `common_context.py`
- `validators.py`
- `exceptions.py`
- `__init__.py`
- `tests/conftest.py`
- `tests/test_qualified_context.py`

### Constat architecturel actuel

- `catalog.py` s’appuie explicitement sur `app.domain.llm.legacy.bridge` pour hydrater `PROMPT_CATALOG` via `LEGACY_PROMPT_RUNTIME_DATA` : ce module reste un **adaptateur de compatibilité** et non la source de vérité runtime.
- `common_context.py` consomme `get_legacy_use_case_name` depuis `app.domain.llm.legacy.bridge` et conserve un fallback gouverné via `app.llm_orchestration.services.fallback_governance` (`FallbackType.NATAL_NO_DB`) : reliquat historique **borné et justifié**.
- `validators.py` est cohérent avec la cible canonique en validant le catalogue applicatif (`app.prompts.catalog`) contre `LlmUseCaseConfigModel` sans réintroduire le renderer supprimé.
- `exceptions.py` et `__init__.py` restent neutres (pas de dépendances runtime problématiques).
- Les tests locaux du package (`tests/test_qualified_context.py`) valident surtout la dégradation de contexte et la qualité (`full/partial/minimal`) ; pas de réintroduction de dépendance au renderer historique.

### Impact sur la lecture AC41-AC52

- Le dossier `app.prompts` confirme l’état "migration contrôlée" : le runtime canonique est bien déplacé vers `app.domain.llm.*` / `app.application.llm.*`, mais ce package conserve des **points d’entrée de transition**.
- Les dépendances legacy observées dans `app.prompts` sont conformes à la stratégie AC41-AC52 : explicites, traçables, limitées à la compatibilité, et non utilisées comme nouvelle voie nominale.
- Aucune contradiction relevée avec la suppression effective des shims renderer/persona/adapter déjà actée.

### Suivi opérationnel par fichier (statut migration et action suivante)

- `backend/app/prompts/catalog.py` — **Statut**: compatibilité legacy assumée (dépendance `app.domain.llm.legacy.bridge`) — **Action suivante**: préparer un lot de convergence vers une source runtime canonique non-legacy dès que les consommateurs historiques sont retirés.
- `backend/app/prompts/common_context.py` — **Statut**: partiellement convergé, reliquats fallback via `app.llm_orchestration.services.fallback_governance` — **Action suivante**: remplacer la dépendance fallback historique par son équivalent canonique `app.domain.llm.*` lors du prochain lot de décommissionnement wrappers.
- `backend/app/prompts/validators.py` — **Statut**: aligné cible (pas de dépendance au renderer historique) — **Action suivante**: maintenir tel quel, surveillance uniquement.
- `backend/app/prompts/exceptions.py` — **Statut**: neutre / stable — **Action suivante**: aucune.
- `backend/app/prompts/__init__.py` — **Statut**: neutre / stable — **Action suivante**: aucune.
- `backend/app/prompts/tests/conftest.py` — **Statut**: test local package, non bloquant pour migration runtime — **Action suivante**: conserver, puis ajuster uniquement si suppression des adaptateurs `app.prompts`.
- `backend/app/prompts/tests/test_qualified_context.py` — **Statut**: couverture de la dégradation de contexte, sans régression renderer — **Action suivante**: compléter ultérieurement par un test ciblant la disparition du fallback `llm_orchestration` après convergence.

## Points de vigilance restants

- Le registre `backend/app/ops/llm/TRANSITION_WRAPPERS.md` doit rester synchronisé à chaque suppression de shim.
- Reliquats assumés : wrappers `gateway/services` historiques encore nécessaires à la compatibilité tests/outils, à réduire par lots dédiés.
- Reliquat complémentaire à suivre : dépendances legacy de `backend/app/prompts/common_context.py` (fallback governance `llm_orchestration`) à traiter lors d’un lot de convergence final.

## Conclusion

- La source de vérité runtime est maintenant alignée sur `app.application.llm.*` + `app.domain.llm.*`.
- Les dépendances historiques sont bornées à des shims explicites et au bridge legacy nominal.
- Le renderer historique est supprimé ; les reliquats principaux restants sont des wrappers namespace legacy strictement bornés, dont les points de compatibilité encore présents dans `backend/app/prompts`.
