# Audit backend generation de prompts LLM (post story 70-15)

Date: 2026-04-21
Perimetre: backend uniquement, focus sur le flux runtime de composition/rendu des prompts (hors front, hors infra provider detaillee).

## Methode

- Lecture des points d entree runtime et applicatifs: gateway, adapter, services metier.
- Verification des wrappers de transition documentes.
- Verification rapide des usages par imports/references dans le code.
- Classification en 4 statuts: `actif`, `actif-legacy`, `incertain`, `obsolete`.

## Flux global (vue synthese)

1. Les services metier appellent `app.application.llm.ai_engine_adapter`.
2. L adapter construit `LLMExecutionRequest` puis appelle `app.domain.llm.runtime.gateway`.
3. Le gateway resout config/assembly/persona/schema, compose le developer prompt, puis rend les placeholders.
4. Le gateway construit les messages finaux (system/developer/user) et execute l appel provider.
5. En cas de besoin: chemins de compatibilite legacy (mapping use_case, legacy runtime data, wrappers historiques).

## Inventaire des fichiers backend lies a la generation de prompts LLM

| Fichier | Statut | Fonction dans le flux |
| --- | --- | --- |
| `backend/app/application/llm/ai_engine_adapter.py` | actif | Point d entree applicatif canonique; construit les requetes LLM vers le gateway. |
| `backend/app/domain/llm/runtime/gateway.py` | actif | Orchestrateur principal runtime: resolution config/assembly, rendu prompt, composition messages. |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | actif | Resolution des assemblies (feature/subfeature/plan), concatenation des blocs de prompt. |
| `backend/app/domain/llm/configuration/prompt_version_lookup.py` | actif | Lookup runtime du prompt publie actif (DB) pour un use_case. |
| `backend/app/infrastructure/db/repositories/llm/prompting_repository.py` | actif | Acces DB prompts/releases (source de verite du prompt actif). |
| `backend/app/llm_orchestration/services/prompt_renderer.py` | actif | Moteur effectif de rendu `{{placeholders}}` et controle governance placeholder. |
| `backend/app/llm_orchestration/services/persona_composer.py` | actif | Construction du bloc persona injecte dans le prompt developer. |
| `backend/app/domain/llm/runtime/context_quality_injector.py` | actif | Injection d instructions de compensation selon la qualite de contexte. |
| `backend/app/domain/llm/runtime/composition.py` | actif | Facade canonique runtime pour injecteurs (context quality, length budget, provider params). |
| `backend/app/services/natal_interpretation_service_v2.py` | actif | Consommateur metier qui declenche la generation prompt via adapter (natal). |
| `backend/app/services/ai_engine_adapter.py` | actif-legacy | Wrapper de compatibilite vers l adapter canonique (imports historiques). |
| `backend/app/llm_orchestration/gateway.py` | actif-legacy | Wrapper namespace historique vers gateway canonique domain. |
| `backend/app/domain/llm/legacy/bridge.py` | actif-legacy | Pont explicite nominal -> legacy runtime data/config pour chemins de compatibilite. |
| `backend/app/llm_orchestration/legacy_prompt_runtime.py` | actif-legacy | Registre legacy des use_case/configs/model resolution utilise en fallback transitoire. |
| `backend/app/prompts/catalog.py` | actif-legacy | Catalogue central legacy derive de `legacy_prompt_runtime`, encore utilise par validations/scripts/tests. |
| `backend/scripts/seed_29_prompts.py` | actif-legacy | Entree historique de seed redirigee vers `app.ops.llm.bootstrap.*`. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | actif-legacy | Seed legacy encore present pour bootstrap/migration progressive des prompts. |
| `backend/app/prediction/llm_narrator.py` | actif-legacy | Module marque deprecated mais encore activable par flag (`llm_narrator_enabled`). |
| `backend/app/domain/llm/prompting/renderer.py` | actif | Alias canonique `PromptRenderer` pour usages admin/runtime. |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | obsolete | Alias non reference dans le code scanne; doublon de point d acces du renderer. |

## Points d attention

- Le coeur runtime est bien centre sur `app.domain.llm.runtime.gateway`.
- La migration 70-15 a reduit plusieurs modules a des wrappers, mais ces wrappers restent utilises (runtime, services et tests).
- Une part notable du comportement prompt reste encore dependante du perimetre `legacy_prompt_runtime` (fallback/compatibilite).
- Le fichier `app.domain.llm.prompting.prompt_renderer` apparait non utilise dans ce perimetre et est un candidat de nettoyage.

## Conclusion

- Le flux de generation de prompts est operationnel et majoritairement aligne sur le chemin canonique.
- Le systeme reste en phase de transition, avec plusieurs composants `actif-legacy` legitimes.
- Un premier candidat `obsolete` a ete identifie (`domain/llm/prompting/prompt_renderer.py`), sous reserve d une verification finale CI/tests avant suppression.
