# Story 70.13: Cleaner le backend generation de prompt et fermer les compatibilites legacy

Status: draft

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want retirer du runtime backend LLM les derniers chemins catalog-centric, use-case-first et auto-heal legacy qui continuent a piloter la generation de prompt,
so that la generation de prompt repose uniquement sur la chaine canonique `assembly -> execution profile -> rendering -> provider payload`, avec un echec explicite si une configuration canonique manque au lieu d une compatibilite silencieuse.

## Contexte

Le depot a deja fait une grande partie du travail de convergence canonique :

- `AssemblyRegistry` et `ExecutionProfileRegistry` resolvent d abord depuis le snapshot actif, puis seulement via les tables publiees ;
- `ConfigCoherenceValidator` pousse deja une logique fail-fast sur la coherence assembly/profile/persona/schema ;
- la documentation runtime [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) affirme que la chaine canonique doit partir d une assembly et d un execution profile gouvernes ;
- les stories `66.30` et `66.40` ont deja ferme une partie des fallbacks nominaux et encadre le legacy residuel.

Mais le code garde encore plusieurs verites concurrentes de generation de prompt :

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) contient encore `USE_CASE_STUBS`, `_resolve_config()`, des branches legacy dans `_resolve_plan()`, et des chemins qui tolerent encore une execution sans assembly/profile canoniques sur des features pourtant supportees ;
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) reste une source de verite runtime implicite via `PROMPT_CATALOG`, `PromptEntry` et `resolve_model()` alors que ces decisions devraient deja etre sorties du catalogue Python ;
- [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py) conserve `validate_catalog_vs_db()`, qui fige un monde ou la base doit rester alignee sur un catalogue Python global ;
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) continue d auto-reparer en local/dev le registre LLM via `_ensure_llm_registry_seeded()`, au prix de reseeds historiques qui peuvent masquer une incoherence canonique ;
- [backend/app/llm_orchestration/services/prompt_registry_v2.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_registry_v2.py) est encore consomme comme pivot de lecture par l admin legacy autour de `use_case_key`, alors que le runtime cible vit sur des blocs versionnes references depuis les assemblies et snapshots ;
- l admin backend [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) utilise encore `PromptRegistryV2` pour des vues listees et de publication historique ; il faut donc distinguer ce qui peut etre conserve comme surface de maintenance historique de ce qui doit sortir du chemin runtime nominal.

Le probleme n est plus seulement un probleme de fallback ponctuel. C est un probleme de gouvernance de la source de verite :

- la chaine canonique existe ;
- la documentation l annonce ;
- mais plusieurs points d entree peuvent encore contourner cette chaine ou la masquer.

Cette story a pour but de fermer definitivement ce double systeme sur la partie generation de prompt backend.

## Cible d'architecture

Pour toute feature nominalement supportee par la plateforme LLM moderne :

- une assembly canonique doit etre resolue ;
- un execution profile canonique doit etre resolu ;
- le rendu final doit etre derive de ces artefacts et de leurs references gouvernees ;
- l absence d assembly ou de profile doit produire un echec explicite, stable, observable et testable ;
- aucun catalogue Python global ni `UseCaseConfig` stub ne doit rester source finale de verite d execution.

Les artefacts historiques peuvent subsister uniquement s ils sont :

- strictement bornes a des surfaces admin de maintenance legacy ;
- documentes comme tels ;
- hors chemin nominal d execution runtime ;
- non requis pour demarrer localement une stack canonique saine.

## Acceptance Criteria

1. **AC1 - Echec explicite sur feature canonique supportee sans assembly** : dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py), toute `feature` canonique supportee et normalisee par la taxonomie runtime echoue explicitement si aucune assembly canonique n est resolue. Aucun fallback `use_case-first`, `_resolve_config()` ou `USE_CASE_STUBS` ne peut encore sauver ce cas sur le nominal. Les entrees historiques sans `feature` ne doivent pas rouvrir cette ambiguite ; elles doivent soit etre normalisees immediatement vers une feature canonique, soit rester explicitement hors support.
2. **AC2 - Echec explicite sur feature canonique supportee sans execution profile exploitable** : toute `feature` canonique supportee et normalisee echoue explicitement si aucun `ExecutionProfile` canonique exploitable n est resolu, y compris en cas d absence, de reference invalide, de provider non supporte, ou de mapping provider impossible. Aucun `resolve_model()` ni `config.model` issu du legacy ne peut encore devenir la source finale de verite.
3. **AC3 - `_resolve_config()` sort du chemin nominal sans casser la validation** : `_resolve_config()` n est plus utilise comme mecanisme de resolution nominale pour une feature supportee, mais peut subsister transitoirement pour des chemins legacy bornes sans `feature` canonique ou pour des validations transitoires explicitement documentees. Les etapes de validation Stage 0 et Stage 1.5 continuent de fonctionner avec des sources canoniques stables pour `input_schema`, `persona_strategy` et `output_schema`.
4. **AC4 - Suppression des stubs runtime** : `USE_CASE_STUBS`, les `UseCaseConfig` stubs historiques et l entree `execute()` legacy de [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) sont supprimes du chemin nominal, ou reduits a une compatibilite explicitement legacy hors support, documentee et testee comme telle.
5. **AC5 - `prompts/catalog.py` n est plus une source de verite runtime** : [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) ne pilote plus la resolution nominale du modele, du schema ou du use case runtime. `resolve_model()` est supprime du chemin nominal et toute constante utile restante est deplacee vers des modules a responsabilite explicite.
6. **AC6 - Migration des schemas hors `PROMPT_CATALOG` avant suppression** : toute dependance schema encore lue via `PROMPT_CATALOG` est migree vers `LlmOutputSchemaModel`, une reference snapshot, ou une source canonique equivalente avant suppression du vieux catalogue runtime. Aucune suppression de `PROMPT_CATALOG` ne peut faire disparaitre silencieusement un `output_schema` nominal.
7. **AC7 - Validation recentree sur le canonique** : [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py) ne contient plus de validation bloquante `catalog vs db` pour le runtime nominal. Les validateurs conserves ne parlent que d assemblies, execution profiles, persona, placeholders gouvernes, snapshots et schemas.
8. **AC8 - Boot local avec seed canonique minimal explicite** : [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) ne reseed plus silencieusement des couches historiques de prompts/use cases pour masquer une incoherence canonique. Hors production, le boot doit soit s appuyer sur un seed canonique minimal explicite et idempotent, soit echouer clairement si la configuration canonique minimale est absente ou invalide. Toute tolerance legacy restante doit etre gardee derriere un flag explicite de type `DEV_ALLOW_LEGACY_SEED`.
9. **AC9 - `PromptRegistryV2` sort du runtime nominal** : [backend/app/llm_orchestration/services/prompt_registry_v2.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_registry_v2.py) n est plus requis pour l execution nominale. S il subsiste, sa responsabilite est explicitement reduite a l historique/versioning de prompts legacy ou a l admin de maintenance, sans influencer la resolution runtime assembly-first.
10. **AC10 - Dependances admin et UI auditees** : les ecrans admin et les endpoints backend dependants de `PromptRegistryV2`, `PROMPT_CATALOG`, `fallback_use_case_key` ou d anciens `use_case_key` sont soit migres vers la lecture canonique, soit explicitement classes comme surface legacy de maintenance. Aucun appel frontend/admin critique ne casse silencieusement lors de la coupure.
11. **AC11 - Alias et use cases historiques bornes** : les anciens `use_case_key` tels que `horoscope_daily_free`, `horoscope_daily_full`, `daily_prediction`, `chat` et equivalents ne circulent plus comme cles runtime nominales. S il reste une adaptation a l entree API, elle est minimale, centralisee, testee et ne reouvre pas les chemins catalog-centric.
12. **AC12 - Observabilite de rejet et de coupure** : quand un chemin supporte echoue faute d assembly/profile canonique, le rejet est observable via des `error_code` stables et la telemetrie existante. Le resultat ne doit jamais etre requalifie en succes degrade via un fallback legacy de prompt generation.
13. **AC13 - Documentation runtime realignee** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et toute documentation de reference ne presentent plus `_resolve_config()`, `PROMPT_CATALOG`, `resolve_model()` ou `PromptRegistryV2` comme elements nominaux du pipeline de generation de prompt.
14. **AC14 - Aucun fallback implicite de modele** : aucun chemin nominal ne peut utiliser `config.model`, `settings.openai_model_default` ou `resolve_model()` comme source finale de modele. Le modele execute doit toujours provenir d un `ExecutionProfile` canonique.
15. **AC15 - Couverture tests de coupure** : des tests couvrent au minimum la resolution assembly depuis snapshot, la resolution execution profile, le rendu, la persona, le schema de sortie, l appel provider, l observabilite, et le rejet explicite si l assembly ou le profile manquent ; des tests complementaires prouvent que l admin ou les adaptateurs d entree n ont pas besoin du vieux catalogue Python pour fonctionner nominalement.

## Tasks / Subtasks

- [ ] Task 1: Fermer les derniers chemins runtime legacy dans le gateway (AC1, AC2, AC3, AC4, AC12, AC14)
  - [ ] Cartographier dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) tous les usages de `USE_CASE_STUBS`, `_resolve_config()`, `execute()`, `resolve_model()` et des branches `fallback_*` encore actives.
  - [ ] Rendre explicite la regle nominale dans `_resolve_plan()` : `feature supportee -> assembly obligatoire -> execution profile obligatoire -> sinon erreur`.
  - [ ] Sortir `_resolve_config()` du chemin nominal sans casser Stage 0 et Stage 1.5 ; le conserver uniquement pour des chemins legacy bornes sans `feature` canonique si cette compatibilite est encore necessaire.
  - [ ] Supprimer la tolerance legacy pour les features supportees dans `_resolve_plan()`.
  - [ ] Stabiliser les `error_code` et `details` structures pour les cas `missing_assembly`, `missing_execution_profile`, `unsupported_execution_provider`, `provider_mapping_failed` ou equivalents stables.
  - [ ] Unifier les codes d erreur entre resolution du plan, resolution du profile et runtime provider pour les rejets canoniques.
  - [ ] Eliminer tout fallback implicite de modele via `config.model`, `settings.openai_model_default` ou `resolve_model()` sur le nominal.
  - [ ] Preserver uniquement une compatibilite legacy finie, explicite et hors support si elle reste necessaire.

- [ ] Task 2: Sortir `prompts/catalog.py` du pilotage runtime (AC5, AC6, AC11, AC13)
  - [ ] Identifier les elements de [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) encore utilises au runtime nominal.
  - [ ] Migrer toute dependance schema encore lue depuis `PROMPT_CATALOG` vers `LlmOutputSchemaModel`, le snapshot actif ou une source canonique equivalente avant suppression.
  - [ ] Supprimer `resolve_model()` du pipeline nominal.
  - [ ] Deplacer les constantes encore utiles vers des modules nommes selon leur vraie responsabilite.
  - [ ] Eliminer l ambiguite entre catalogue legacy de maintenance et gouvernance canonique JSON/snapshot.

- [ ] Task 3: Recentrer les validateurs et la coherence de boot sur le canonique (AC7, AC8, AC12, AC13)
  - [ ] Retirer `validate_catalog_vs_db()` du chemin nominal et remplacer ce garde-fou par des controles centres sur assembly/profile/snapshot/persona/schema.
  - [ ] Supprimer explicitement l appel startup correspondant dans [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py), ou le remplacer par une validation canonique snapshot-first equivalente.
  - [ ] Nettoyer [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) pour remplacer l auto-heal legacy par un seed canonique minimal explicite et idempotent.
  - [ ] Introduire si necessaire un flag explicite de tolerance locale du type `DEV_ALLOW_LEGACY_SEED`, au lieu d un reseed legacy implicite.
  - [ ] Verifier que le boot local est possible avec les seuls seeds canoniques minimaux et qu une incoherence canonique echoue clairement en dev.

- [ ] Task 4: Sortir `PromptRegistryV2` du runtime nominal et auditer l admin (AC7, AC8)
  - [ ] Identifier dans [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) ce qui depend encore de `PromptRegistryV2`.
  - [ ] Distinguer les surfaces admin a migrer vers la lecture canonique de celles qui restent volontairement legacy.
  - [ ] Supprimer toute dependance de `PromptRegistryV2` a l execution nominale du gateway.
  - [ ] Verifier si le frontend admin consomme encore implicitement `use_case_key`, `fallback_use_case_key`, `PROMPT_CATALOG` ou des libelles derives du vieux modele.

- [ ] Task 5: Verrouiller les alias d entree et les compatibilites minimales (AC8, AC9, AC12)
  - [ ] Auditer les routeurs/backend services qui reçoivent encore des `use_case_key` historiques.
  - [ ] Conserver au maximum une adaptation a l entree API, centralisee et testee, sans reutiliser le vieux pipeline de generation.
  - [ ] Ajouter des tests de non-regression pour les cles historiques encore acceptees en entree mais normalisees immediatement.

- [ ] Task 6: Realigner la documentation et l observabilite (AC10, AC11, AC12)
  - [ ] Mettre a jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) pour supprimer la presentation des chemins catalog-centric comme partie nominale du pipeline.
  - [ ] Verifier la coherence avec les artefacts `66.30`, `66.40` et les controles doc/code deja existants.
  - [ ] Confirmer que les metadonnees runtime et admin ne publient plus de source finale legacy pour les chemins supportes.
  - [ ] Verifier que `missing_assembly`, `missing_execution_profile`, `unsupported_execution_provider` et `provider_mapping_failed` remontent dans les metriques, logs structures et metadonnees runtime sans fallback de requalification.

- [ ] Task 7: Validation locale obligatoire (AC1 a AC15)
  - [ ] Activer le venv avant toute commande Python : `.\.venv\Scripts\Activate.ps1`
  - [ ] Installer/mettre a jour les dependances backend si necessaire via `cd backend ; pip install -e ".[dev]"`
  - [ ] Executer `cd backend ; ruff format .`
  - [ ] Executer `cd backend ; ruff check .`
  - [ ] Executer `cd backend ; pytest -q`
  - [ ] Ajouter un passage cible sur les tests LLM/gateway/admin impactes par la coupure.

## Dev Notes

### Diagnostic exact a preserver

- `66.30` a deja ferme `resolve_model()` comme verite finale sur une partie du perimetre supporte, mais [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) garde encore du materiel legacy structurant : `USE_CASE_STUBS`, `_resolve_config()` et des branches de compatibilite runtime.
- `_resolve_config()` ne peut pas etre supprime brutalement tant qu il reste branche sur Stage 0 et Stage 1.5 pour `input_schema`, `persona_strategy` ou `output_schema`. La bonne cible est de le sortir du nominal d abord, puis de reduire son role residuel.
- `66.40` a encadre le legacy residuel, mais n a pas pour autant retire les reliquats catalog-centric et use-case-centric encore presents dans le code de generation de prompt.
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) continue de melanger metadonnees, schemas, mapping deprecated et resolution runtime. Ce melange est exactement ce que la cible snapshot/assembly/profile cherche a eliminer.
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) porte encore des schemas runtime ; leur migration vers `LlmOutputSchemaModel` ou snapshot est un prealable de suppression propre.
- Sortir [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py) du runtime nominal ne signifie pas necessairement supprimer immediatement le fichier ; cela signifie d abord supprimer son role de decision d execution. Le fichier peut subsister transitoirement comme support legacy/admin tant qu il n influence plus la resolution nominale.
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) auto-seed aujourd hui des couches heterogenes (`seed_use_cases`, `seed_prompts`, `seed_30_8_v3_prompts`, `seed_chat_prompt_v2`, `seed_66_20_taxonomy`, `seed_horoscope_narrator_assembly`). Ce mecanisme est pratique pour le local, mais il peut masquer des trous dans le canonique ; il doit etre remplace par un seed canonique minimal explicite.
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py) appelle aussi encore des validations startup issues du monde catalog-centric ; nettoyer `validators.py` sans retirer ou remplacer ces call-sites laisserait une incoherence au boot.
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) consomme encore `PromptRegistryV2` pour lister des use cases et gerer l historique. Cette surface doit etre auditée avant suppression franche.
- Des tests existent deja pour une partie du sujet : [backend/tests/integration/test_story_66_30_suppression.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_30_suppression.py) et [backend/tests/integration/test_story_66_40_legacy_residual.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_40_legacy_residual.py). Ils doivent servir de base plutot que repartir de zero.

### Ce que le dev ne doit pas faire

- Ne pas remplacer le legacy supprime par un autre fallback implicite base sur `settings.openai_model_default`, `config.model` ou un provider code en dur.
- Ne pas supprimer `_resolve_config()` en une fois tant qu une source canonique equivalente n a pas repris proprement les besoins de validation Stage 0 et Stage 1.5.
- Ne pas supprimer `PromptRegistryV2` ou `PROMPT_CATALOG` a l aveugle sans auditer les surfaces admin encore branchees dessus.
- Ne pas conserver `_ensure_llm_registry_seeded()` comme auto-heal fourre-tout qui reseed indistinctement le vieux et le canonique.
- Ne pas garder des aliases `use_case_key` historiques en circulation interne si une normalisation immediate d entree suffit.
- Ne pas rouvrir un chemin `catalog -> runtime` pour sauver un test ou une surface admin ; si une compatibilite reste necessaire, elle doit etre explicite, nommee et bornee.

### Fichiers a inspecter en priorite

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py)
- [backend/app/prompts/validators.py](/c:/dev/horoscope_front/backend/app/prompts/validators.py)
- [backend/app/main.py](/c:/dev/horoscope_front/backend/app/main.py)
- [backend/app/llm_orchestration/services/prompt_registry_v2.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_registry_v2.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [backend/app/llm_orchestration/providers/provider_runtime_manager.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/providers/provider_runtime_manager.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.30** a deja ferme `resolve_model()` comme source finale de verite d execution sur le perimetre supporte. Cette story va plus loin en retirant aussi les briques structurelles qui rendent encore ce monde legacy possible dans le code de generation de prompt.
- **66.40** a transforme le legacy residuel en objet gouverne. La presente story doit utiliser cette gouvernance pour borner les exceptions restantes, pas la contourner.
- **70.12** existante dans le depot traite d une refonte front/admin des couches observables. La presente story est volontairement backend-only et n ecrase pas cet artefact.

### Testing Requirements

- Ajouter ou etendre des tests d integration qui prouvent l echec explicite si une feature supportee n a pas d assembly.
- Ajouter ou etendre des tests qui prouvent l echec explicite si une feature supportee n a pas d execution profile.
- Ajouter des tests sur les alias legacy d entree (`daily_prediction`, `horoscope_daily_free`, `horoscope_daily_full`, `chat`) pour verifier la normalisation immediate ou le rejet explicite selon la politique retenue.
- Ajouter des tests de boot/validation qui prouvent qu un environnement dev canonique demarre sans reseed legacy fourre-tout, et echoue clairement si le canonique est incoherent.
- Ajouter des tests admin/backend pour verifier que les surfaces qui doivent survivre ne dependent plus du vieux catalogue Python pour le runtime nominal.

### Project Structure Notes

- Story backend dominante, avec impact possible sur documentation et admin backend.
- Aucun changement frontend produit n est requis a priori sauf si l audit montre encore une dependance explicite a d anciens `use_case_key`.
- Le plus petit delta coherent est attendu : couper le runtime d abord, puis nettoyer les validateurs et les seeds, puis traiter les restes admin.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md)
- [66-40-extinction-totale-legacy-hors-perimetre.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-40-extinction-totale-legacy-hors-perimetre.md)
- [backend/tests/integration/test_story_66_30_suppression.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_30_suppression.py)
- [backend/tests/integration/test_story_66_40_legacy_residual.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_40_legacy_residual.py)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Demande utilisateur : generer une story `70-13` pour nettoyer le backend sur la generation de prompt et supprimer franchement le legacy restant.
- Intelligence recueillie depuis le code reel : `gateway.py`, `prompts/catalog.py`, `prompts/validators.py`, `main.py`, `prompt_registry_v2.py`, `config_coherence_validator.py`, `assembly_registry.py`, `execution_profile_registry.py`, `admin_llm.py`, plus les stories `66.30` et `66.40`.

### Completion Notes List

- Story redigee pour cadrer une suppression finale du legacy runtime cote backend, en continuité directe de `66.30` et `66.40`.
- Le cadrage distingue clairement ce qui doit etre supprime du runtime nominal et ce qui peut rester comme surface admin legacy de maintenance.
- La story force un audit explicite des dependances admin/UI avant suppression franche de `PROMPT_CATALOG` et `PromptRegistryV2`.
- Le plan recommande de couper d abord le gateway, puis le catalogue runtime, puis les seeds/validateurs, puis les restes admin.

### File List

- _bmad-output/implementation-artifacts/70-13-cleaner-le-backend-generation-de-prompt-et-fermer-les-compatibilites-legacy.md

### Change Log

- 2026-04-20 : creation de la story backend autonome `70.13` pour cadrer le nettoyage final du runtime de generation de prompt et la fermeture des compatibilites legacy restantes.
