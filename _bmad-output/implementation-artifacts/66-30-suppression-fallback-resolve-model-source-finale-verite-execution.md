# Story 66.30: Suppression du fallback `resolve_model()` comme source finale de vérité d'exécution

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want supprimer `resolve_model()` comme filet final de résolution runtime sur les chemins de production supportés,
so that toute exécution supportée repose sur un `ExecutionProfile` explicitement résolu depuis l'assembly ou le registre canonique, et échoue clairement si aucun profil valide n'est disponible au lieu d'inventer silencieusement un modèle final hors gouvernance.

## Contexte

La story 66.29 a fermé le fallback `USE_CASE_FIRST` sur les chemins supportés. Le dépôt garde pourtant encore une seconde vérité de secours au niveau de l'exécution finale :

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) continue de basculer vers `resolve_model(use_case, fallback_model=config.model)` quand aucun `ExecutionProfile` n'est trouvé, quand un provider de profil n'est pas supporté, ou quand le mapping provider n'est pas implémenté.
- Ce reliquat est encodé explicitement dans la taxonomie runtime avec `profile_source = "fallback_resolve_model"` et `profile_source = "fallback_provider_unsupported"`, puis recyclé en `ExecutionPathKind.LEGACY_EXECUTION_PROFILE_FALLBACK` ou `ExecutionPathKind.NON_NOMINAL_PROVIDER_TOLERATED` dans `_build_result()`.
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) classe encore `FallbackType.RESOLVE_MODEL` comme `TRANSITORY` avec justification "Filet de sécurité si ExecutionProfile est manquant", ce qui contredit la cible annoncée par l'epic 66 et la fermeture progressive déjà opérée par 66.20, 66.21 et 66.29.
- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py) expose toujours `source: Literal["explicit", "waterfall", "assembly_ref", "fallback_resolve_model"]` pour le profil résolu, ce qui institutionnalise un mode de résolution non canonique.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) décrit encore un waterfall valide `ExecutionProfileRegistry -> resolve_model()` hors profil explicite, alors même que la même documentation affirme qu'il faut éviter les vérités concurrentes entre assembly, `ExecutionProfile` et paramètres provider.
- Les tests existants prouvent surtout la convergence `USE_CASE_FIRST` (66.29) et la stabilité du waterfall `ExecutionProfile` (66.11/66.18), mais ils n'imposent pas encore que l'absence ou l'inexploitabilité d'un profil canonique devienne une erreur explicite sur les chemins supportés.

Le problème restant n'est donc plus la composition de prompt. Le problème est la dernière échappatoire d'exécution :

- la composition peut être canonique ;
- le schéma d'entrée peut être canonique ;
- mais le modèle final peut encore être choisi via `resolve_model()` sans `ExecutionProfile` valide.

Cette story ferme cette divergence.

## Cible d'architecture

Pour tout chemin de production supporté par la plateforme LLM moderne :

- un `ExecutionProfile` valide doit être résolu explicitement ;
- sa source doit être soit `assembly_ref`, soit `waterfall` canonique, ou un équivalent explicite stable si la taxonomie est renommée ;
- `resolve_model()` ne doit plus être utilisé comme source finale de vérité d'exécution ;
- l'absence de profil, l'usage d'un provider non supporté, ou un mapping provider non implémenté doivent produire une erreur de configuration/runtime explicite et traçable.

La compatibilité legacy éventuellement conservée avec `resolve_model()` doit être strictement bornée hors périmètre supporté, documentée comme telle, et ne doit plus contaminer les chemins supportés, les snapshots canoniques ni les modèles admin.

## Périmètre supporté à retenir

Pour cette story, le périmètre supporté doit être déterminé par une règle centrale unique, fondée d'abord sur la taxonomie canonique normalisée du runtime (`chat`, `guidance`, `natal`, `horoscope_daily`), avec prise en charge explicite des alias legacy immédiatement normalisés vers ces familles.

Conséquence de design :

- gateway, gouvernance des fallbacks, observabilité, admin, seeds, matrices d'évaluation et parcours applicatifs consomment cette même règle ;
- aucun de ces composants ne doit redéfinir localement ce qu'est un chemin supporté ;
- les seeds, campagnes et parcours métier s'alignent sur la règle centrale, mais ne la définissent jamais.

Conséquence directe :

- un chemin supporté sans `ExecutionProfile` valide n'est plus "toléré" ;
- un provider non nominalement supporté ne doit plus être récupéré par `resolve_model()/openai` sur ce périmètre ;
- un défaut de mapping provider ne doit plus masquer l'absence d'une configuration exploitable ;
- `config.model` et `resolve_model()` peuvent rester des artefacts legacy hors support, mais jamais comme vérité finale nominale sur ce périmètre.

## Acceptance Criteria

1. **AC1 — Interdiction de `resolve_model()` sur les chemins supportés** : le gateway n'utilise plus `resolve_model()` comme issue nominale ou tolérée pour déterminer le modèle final d'un chemin supporté, y compris lorsque aucun `ExecutionProfile` n'est trouvé, qu'un provider de profil n'est pas supporté, ou que le mapping provider n'est pas implémenté.
2. **AC2 — `ExecutionProfile` obligatoire et explicite** : tout chemin supporté doit disposer d'un `ExecutionProfile` explicitement résolu depuis l'assembly active (`assembly_ref`) ou depuis la cascade canonique du registre (`waterfall` ou taxonomie stable équivalente). Aucune issue `fallback_resolve_model` n'est encore acceptée sur ce périmètre.
3. **AC3 — Erreur claire si aucun profil ne correspond** : lorsque le runtime ne trouve aucun `ExecutionProfile` applicable sur un chemin supporté, il lève une erreur explicite de configuration/runtime (`GatewayConfigError` ou équivalent stable) avec `error_code` stable et détails structurés incluant au minimum `feature`, `subfeature`, `plan`, `use_case`, `pipeline_kind` et la raison d'échec. Les codes attendus sont au minimum de la forme `missing_execution_profile`, `unsupported_execution_provider`, `provider_mapping_not_implemented`, ou équivalents stables validés par tests.
4. **AC4 — Provider unsupported sans fallback implicite** : si un `ExecutionProfile` résolu demande un provider non nominalement supporté sur un chemin supporté, le runtime échoue explicitement ; il ne retombe plus sur `resolve_model()/openai` comme compensation silencieuse.
5. **AC5 — Mapping provider non implémenté sans faux succès** : si le mapping provider des paramètres stables n'est pas implémenté pour un profil résolu sur un chemin supporté, le runtime échoue explicitement avec une erreur de configuration/exécution stable, au lieu de recycler `fallback_resolve_model`.
6. **AC6 — Taxonomie runtime/admin réalignée** : les représentations canoniques (`ResolvedExecutionPlan`, `GatewayMeta`, modèles admin, observabilité, métriques) ne publient plus `fallback_resolve_model` comme source valide sur un chemin supporté. Toute taxonomie résiduelle legacy est bornée hors support.
7. **AC7 — Gouvernance centralisée du périmètre** : la qualification d'un chemin comme supporté ou legacy hors support est portée par une API, fonction ou règle centrale unique consommée par gateway, gouvernance des fallbacks, observabilité, admin et tests ; les campagnes, seeds et parcours métier s'alignent sur cette règle et ne la redéfinissent jamais.
8. **AC8 — Observabilité d'erreur distincte du fallback** : un chemin supporté rejeté faute d'`ExecutionProfile` valide émet un événement structuré dédié et un compteur dédié de rejet/configuration ; ce scénario reste distinct de `FallbackType.RESOLVE_MODEL`, `legacy_execution_profile_fallback` et `non_nominal_provider_tolerated`, et n'est jamais requalifié en `fallback_kind` ni en `execution_path_kind` de succès.
9. **AC9 — Documentation canonique sans waterfall terminal** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) ne décrit plus `resolve_model()` comme dernier recours normal du pipeline d'exécution sur les chemins supportés ; elle documente un `ExecutionProfile` obligatoire et l'échec explicite en cas d'absence/inexploitabilité.
10. **AC10 — Compatibilité legacy bornée** : si `resolve_model()` subsiste encore pour des chemins legacy hors support, cette exception est explicitement documentée, télémétrée et testée comme compatibilité résiduelle non nominale ; la liste des compatibilités où `resolve_model()` reste autorisé est finie, explicitement déclarée par la gouvernance centrale, et toute nouvelle activation est interdite.
11. **AC11 — Couverture tests non-régression** : des tests couvrent au minimum l'absence de profil, le provider unsupported et le mapping provider non implémenté sur `chat`, `guidance`, `natal` et `horoscope_daily`, en prouvant que l'issue est une erreur explicite sans passage par `resolve_model()`.
12. **AC12 — Cohérence snapshot/runtime** : `obs_snapshot.execution_path_kind`, `fallback_kind`, `execution_profile_source` et les champs admin associés ne publient plus `fallback_resolve_model` ni `fallback_provider_unsupported` comme résultat acceptable sur un chemin supporté ; le résultat attendu est soit un profil canonique explicite, soit un rejet explicite.

## Tasks / Subtasks

- [ ] Task 1: Fermer la résolution finale implicite dans le gateway (AC1, AC2, AC3, AC4, AC5)
  - [ ] Inspecter dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) tous les appels à `resolve_model()` encore utilisés après résolution assembly/config.
  - [ ] Séparer explicitement les cas "profil absent", "provider unsupported" et "mapping provider non implémenté", puis convertir ces cas en erreurs explicites sur les chemins supportés.
  - [ ] Auditer aussi tous les chemins qui construisent encore une `UseCaseConfig` stub, dérivée ou legacy sans `ExecutionProfile` exploitable, afin d'éviter un faux plan d'exécution déjà dégradé avant l'appel à `resolve_model()`.
  - [ ] Préserver uniquement une compatibilité legacy bornée hors périmètre supporté, sans la laisser réapparaître comme issue nominale.
  - [ ] Stabiliser les `error_code` et les détails structurés pour exploitation ops/tests.

- [ ] Task 2: Réaligner la gouvernance, la taxonomie et les modèles admin (AC6, AC7, AC8, AC12)
  - [ ] Mettre à jour [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) pour que `FallbackType.RESOLVE_MODEL` ne soit plus considéré comme fallback toléré sur le périmètre supporté.
  - [ ] Réaligner [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py) et [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py) afin que `execution_profile_source` et les taxonomies associées ne normalisent plus `fallback_resolve_model` comme issue canonique supportée.
  - [ ] Vérifier `_build_result()` et `obs_snapshot` pour distinguer proprement réussite canonique et rejet explicite.
  - [ ] Centraliser la règle de périmètre supporté si elle est encore dupliquée entre gateway, gouvernance, observabilité, admin, seeds et tests.
  - [ ] Introduire la télémétrie de rejet dédiée selon un format stable : événement structuré, compteur dédié, et absence de requalification en chemin de succès.

- [ ] Task 3: Réaligner la documentation canonique et les lectures de plateforme (AC7, AC8, AC9, AC10, AC12)
  - [ ] Corriger [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) dans les sections pipeline, profils d'exécution, verrou provider, observabilité et matrice d'évaluation.
  - [ ] Retirer du diagramme nominal toute branche `ExecutionProfile -> resolve_model()` sur les chemins supportés.
  - [ ] Documenter explicitement ce qui reste éventuellement permis hors support et pourquoi.
  - [ ] Vérifier la cohérence avec [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md), qui pose déjà `ExecutionProfile` comme source de vérité technique.

- [ ] Task 4: Ajouter la couverture de non-régression ciblée (AC3, AC4, AC5, AC8, AC11, AC12)
  - [ ] Étendre ou créer des tests d'intégration autour de [backend/tests/integration/test_story_66_29_extinction.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_29_extinction.py) pour couvrir explicitement l'absence d'`ExecutionProfile`.
  - [ ] Ajouter des tests sur les chemins `provider unsupported` et `provider mapping not implemented` pour prouver l'absence de fallback `resolve_model()` sur familles supportées.
  - [ ] Réaligner les tests qui attendent encore `execution_profile_source == "fallback_resolve_model"` ou `fallback_provider_unsupported` sur un chemin supporté.
  - [ ] Ajouter un cas de non-régression sur alias legacy normalisé, en particulier un alias daily remappé vers `horoscope_daily`, pour prouver qu'un alias d'entrée n'ouvre pas une échappatoire vers `resolve_model()`.
  - [ ] Ajouter au besoin une suite dédiée 66.30 couvrant `chat`, `guidance`, `natal`, `horoscope_daily` et un cas legacy hors support explicitement autorisé.

- [ ] Task 5: Vérification locale obligatoire (AC1 à AC12)
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblées liées à 66.11, 66.18, 66.20, 66.22, 66.25, 66.29 et à la nouvelle story 66.30.
  - [ ] Vérifier que les snapshots/metrics reflètent bien "profil explicite canonique" ou "rejet explicite", jamais `fallback_resolve_model` sur chemin supporté.

## Dev Notes

### Diagnostic exact à préserver

- 66.29 a fermé le fallback de composition `USE_CASE_FIRST`, mais pas le fallback terminal de choix de modèle. La dette restante est plus avale et plus subtile.
- Le reliquat le plus important vit dans [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py), où trois issues distinctes utilisent encore `resolve_model()` :
  - absence de `profile_db` ;
  - provider de profil non supporté ;
  - `ProviderParameterMapper.map()` non implémenté.
- La story ne doit pas simplement "forcer OpenAI" partout. Le vrai objectif est de rendre obligatoire une source canonique d'exécution. Un provider unsupported sur chemin supporté doit devenir une erreur explicite, pas un remap implicite vers OpenAI.
- La taxonomie admin/runtime actuelle entérine encore ce reliquat (`fallback_resolve_model`, `fallback_provider_unsupported`). La fermeture doit être end-to-end : code, observabilité, admin models, tests et doc.
- `ExecutionProfileRegistry` peut conserver sa cascade `feature+subfeature+plan -> feature+subfeature -> feature`, mais l'échec de cette cascade sur chemin supporté doit désormais être bloquant.
- Les erreurs attendues doivent être testables sans assertions fragiles sur le texte libre ; l'implémentation doit donc exposer des `error_code` et des détails structurés stables.
- Le rejet d'un chemin supporté faute de profil exploitable doit suivre le même esprit que `supported_perimeter_rejection` : événement structuré dédié, compteur dédié, et aucune requalification en succès nominal.
- La doctrine locale [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md) dit déjà que le choix du moteur relève du `ExecutionProfile`. La story 66.30 met enfin le runtime au même niveau d'exigence.

### Ce que le dev ne doit pas faire

- Ne pas remplacer `resolve_model()` par un autre fallback implicite codé en dur (`settings.openai_model_default`, `config.model`, provider forcé) sur les chemins supportés.
- Ne pas traiter le cas "provider non supporté" comme simple warning avec bascule silencieuse vers OpenAI.
- Ne pas conserver `fallback_resolve_model` dans les types admin/snapshots pour les familles supportées "au cas où".
- Ne pas laisser des `UseCaseConfig` stubs ou dérivées continuer l'exécution comme si un profil canonique avait été effectivement résolu.
- Ne pas corriger uniquement la documentation ou uniquement les tests : la suppression doit partir du runtime réel.
- Ne pas rouvrir une divergence entre assembly obligatoire et exécution implicite ; `ExecutionProfile` doit devenir la seule vérité technique finale sur le périmètre supporté.
- Ne pas dupliquer la définition du périmètre supporté dans plusieurs fichiers.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/provider_parameter_mapper.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/provider_parameter_mapper.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
- [backend/tests/integration/test_story_66_29_extinction.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_29_extinction.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [backend/app/llm_orchestration/tests/test_story_66_11_execution_profiles.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_11_execution_profiles.py)
- [backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py)
- [backend/app/llm_orchestration/tests/test_story_66_15_convergence.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_15_convergence.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)

### Previous Story Intelligence

- **66.20** a rendu l'assembly obligatoire sur les familles canoniques. La fermeture 66.30 doit prolonger cette exigence jusqu'au choix final du moteur.
- **66.21** a introduit la gouvernance explicite des fallbacks. 66.30 doit reclasser `RESOLVE_MODEL` dans cette matrice pour le périmètre supporté.
- **66.22** a verrouillé le provider nominal supporté. La logique actuelle "provider unsupported -> `resolve_model()/openai`" est précisément le reliquat qui contredit cette fermeture sur les chemins supportés.
- **66.25** a imposé un snapshot canonique unique. 66.30 doit empêcher que `fallback_resolve_model` ou `fallback_provider_unsupported` restent lisibles comme chemins acceptables sur les familles supportées.
- **66.28** a absorbé `daily_prediction` dans `horoscope_daily`, donc un alias legacy daily ne doit pas rouvrir un filet `resolve_model()`.
- **66.29** a fermé `USE_CASE_FIRST` et introduit le rejet explicite d'assembly manquante sur chemins supportés. 66.30 ferme la même logique au niveau du `ExecutionProfile`.

### Git Intelligence

Commits récents pertinents observés :

- `1a8e85db` : `docs(llm): clarify canonical rejection observability`
- `3515c29c` : `docs(llm): align prompt pipeline guide with story 66.29`
- `cec6bea4` : `test(llm): cover assembly input_schema migration backfill`
- `b9986725` : `feat(llm): add migration backfill and auto-heal for assembly input_schema (Story 66.29 closure)`
- `fe4ad22f` : `feat(llm): add input_schema migration and propagation for canonical assemblies (Story 66.29)`

Pattern à réutiliser :

- fermer le reliquat runtime avant d'aligner la documentation ;
- transformer les états transitoires en erreur explicite plutôt qu'en compatibilité silencieuse ;
- prouver la fermeture par tests d'intégration et par observabilité canonique.

### Testing Requirements

- Ajouter un test où un chemin supporté a une assembly valide mais aucun `ExecutionProfile` applicable, et vérifier l'erreur explicite sans appel à `resolve_model()`.
- Ajouter un test où un `ExecutionProfile` supporté référence un provider non nominalement supporté sur un chemin canoniquement supporté, et vérifier l'échec explicite.
- Ajouter un test où `ProviderParameterMapper.map()` lève `NotImplementedError` sur un chemin supporté, et vérifier l'erreur explicite au lieu d'un faux succès `fallback_resolve_model`.
- Ajouter des assertions sur `error_code` et détails structurés, pas seulement sur le message libre.
- Adapter les assertions d'observabilité qui attendent aujourd'hui `fallback_provider_unsupported` ou `fallback_resolve_model` comme résultats lisibles pour des chemins supportés.
- Ajouter un test sur alias legacy normalisé, notamment `daily_prediction` remappé vers `horoscope_daily`, pour prouver qu'un alias d'entrée n'autorise pas un retour vers `resolve_model()`.
- Conserver un test borné prouvant que le fallback legacy éventuel ne peut subsister hors périmètre supporté que pour une liste explicite de compatibilités autorisées par la gouvernance centrale.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest tests/integration/test_story_66_29_extinction.py -q`
  - `pytest tests/integration/test_story_66_25_observability.py -q`
  - `pytest app/llm_orchestration/tests/test_story_66_11_execution_profiles.py -q`
  - `pytest app/llm_orchestration/tests/test_story_66_18_stable_profiles.py -q`
  - ajouter la suite dédiée 66.30 si elle est créée

### Project Structure Notes

- Travail backend + documentation uniquement.
- Aucun changement frontend n'est attendu.
- Les modifications doivent rester concentrées dans `backend/app/llm_orchestration/`, `backend/tests/` et `docs/`.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/provider_parameter_mapper.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/provider_parameter_mapper.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/admin_models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/admin_models.py)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [backend/tests/integration/test_story_66_29_extinction.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_29_extinction.py)
- [backend/tests/integration/test_story_66_25_observability.py](/c:/dev/horoscope_front/backend/tests/integration/test_story_66_25_observability.py)
- [backend/app/llm_orchestration/tests/test_story_66_11_execution_profiles.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_11_execution_profiles.py)
- [backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_18_stable_profiles.py)
- [backend/app/llm_orchestration/tests/test_story_66_15_convergence.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_15_convergence.py)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-29-extinction-definitive-fallback-use-case-first-tous-chemins-supportes.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-29-extinction-definitive-fallback-use-case-first-tous-chemins-supportes.md)

### Review Findings

- [x] [Review][Patch] Redundant Logic and Desynchronization Risk [gateway.py:1125]
- [x] [Review][Patch] Inconsistent is_nominal definition [gateway.py:1149]
- [x] [Review][Patch] Absolute Documentation vs. Coded Exceptions [ARCHITECTURE.md]
- [x] [Review][Patch] Null-Safety for feature [gateway.py:1015]
- [x] [Review][Patch] Catch broader mapping failures [gateway.py:1072]

### Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée pour fermer le reliquat restant après 66.29 : `resolve_model()` encore utilisé comme vérité finale d'exécution quand le `ExecutionProfile` manque ou n'est pas exploitable.
- Le cœur de la story n'est pas la composition assembly mais l'obligation d'un `ExecutionProfile` explicite sur tous les chemins supportés.
- La story impose une fermeture end-to-end : runtime, gouvernance, observabilité, admin models, tests et documentation.
- La compatibilité legacy éventuelle avec `resolve_model()` est explicitement bornée hors périmètre supporté.

### File List

- `_bmad-output/implementation-artifacts/66-30-suppression-fallback-resolve-model-source-finale-verite-execution.md`
