# Story 66.28: Fermeture canonique de `daily_prediction` ou suppression définitive de son statut transitoire

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want supprimer la dernière famille officiellement active en `transitional_governance` autour de `daily_prediction`,
so that le pipeline LLM daily ne porte plus de double lecture structurelle entre `horoscope_daily` et `daily_prediction`, et que la gouvernance canonique soit enfin fermée à 100% sur les surfaces runtime, observabilité, documentation et tests.

## Contexte

La documentation canonique [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) indique encore aujourd’hui que :

- `chat`, `guidance`, `natal` et `horoscope_daily` sont en `nominal_canonical` ;
- `daily_prediction` reste une famille active mais en `transitional_governance` ;
- cette famille passe par `AIEngineAdapter.generate_horoscope_narration()` quand `variant_code` n’est ni `summary_only` ni `full` ;
- elle arrive souvent avec `plan=None`, puis le gateway la normalise de fait en `free`, sans que cela suffise à la fermer nominalement.

L’état réel du dépôt confirme cette situation hybride :

- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py) route encore le chemin par défaut vers `feature="daily_prediction"`, `subfeature="narration"`, `plan=None`.
- [backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py) publie encore une assembly `daily_prediction / narration / plan=None`.
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) calcule `pipeline_kind="nominal_canonical"` uniquement pour `chat`, `guidance`, `natal`, `horoscope_daily`, ce qui laisse `daily_prediction` en `transitional_governance`.
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py) ne considère comme familles canoniques fermées que `chat`, `guidance`, `natal`, `horoscope_daily`.
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) infère pourtant déjà `daily_prediction` comme appartenant à la famille `horoscope_daily` pour certains garde-fous de fallback, ce qui montre qu’une convergence conceptuelle est déjà partiellement actée.
- [backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py) fige encore l’hypothèse `request.user_input.plan is None` sur le chemin `daily_prediction`.

Le problème n’est donc plus un manque de mécanisme. C’est une dette de clôture de gouvernance :

- soit `daily_prediction` mérite d’exister comme famille canonique nominale fermée, avec `plan` explicite et tous les garde-fous des autres familles ;
- soit sa distinction n’est pas structurelle, et il faut alors l’absorber proprement dans `horoscope_daily` avec un mapping de compatibilité résiduel si nécessaire.

Pour cette story, la cible n’est pas de préserver l’ambiguïté. La cible est de la fermer. À l’issue de l’implémentation, aucune famille officiellement active ne doit encore rester en `transitional_governance` à cause de ce chemin daily narratif.

## Décision d’architecture attendue

Le dev doit commencer par une décision explicite, courte et traçable, puis implémenter un seul chemin cible cohérent.

### Option A — Canonicaliser complètement `daily_prediction`

Choisir cette option uniquement si `daily_prediction` porte encore une sémantique produit ou technique distincte de `horoscope_daily` qui justifie :

- un `feature` propre ;
- une assembly dédiée ;
- un `ExecutionProfile` dédié ;
- une présence propre dans la doc, l’observabilité et les matrices d’évaluation ;
- mais **sans** rester en `transitional_governance`.

Dans ce cas, la famille doit devenir officiellement `nominal_canonical`, avec plan résolu explicitement et mêmes garanties de fermeture que `horoscope_daily`.

### Option B — Absorber `daily_prediction` dans `horoscope_daily`

Choisir cette option si `daily_prediction` n’est plus qu’un reliquat historique du narrator et ne porte pas de différence structurelle suffisante.

Dans ce cas :

- le chemin runtime par défaut est rebranché sur `horoscope_daily`;
- la distinction résiduelle éventuelle devient une compatibilité legacy via `use_case` ou alias déprécié ;
- `daily_prediction` cesse d’être documenté comme famille active autonome.

### Règle de choix

Le critère n’est pas “ce qui change le moins de code”, mais “ce qui retire proprement l’ambiguïté sans recréer un nouveau transitoire”.

En l’absence de différence structurelle **prouvée** sur le contrat de sortie, l’assembly, le profil d’exécution ou l’observabilité, **l’option B est la cible par défaut**. Le dépôt et la documentation disponibles poussent déjà dans ce sens : mêmes campagnes d’évaluation, normalisation de fait du plan en `free`, convergence partielle dans la gouvernance de fallback, et absence de justification structurelle explicite documentée pour maintenir `daily_prediction` comme famille autonome.

Le résultat attendu, dans les deux cas, est identique :

- plus aucune famille active n’apparaît en `transitional_governance` pour ce parcours ;
- le `plan` n’est plus laissé implicitement à `None` sur le chemin nominal ;
- la doc, l’observabilité, les fallbacks, les seeds et les tests racontent tous la même vérité.

## Acceptance Criteria

1. **AC1 — Fermeture du statut transitoire** : après implémentation, le parcours daily narratif ne laisse plus `daily_prediction` comme famille officiellement active en `transitional_governance`. Soit `daily_prediction` devient une famille nominale fermée, soit elle cesse d’être une famille active autonome.
2. **AC2 — Décision d’architecture explicite et appliquée** : le change set implémente clairement une seule cible stable parmi les deux variantes autorisées (canonicalisation complète ou absorption dans `horoscope_daily`) ; il ne laisse pas le dépôt dans un état mixte où plusieurs vérités concurrentes coexistent.
3. **AC3 — Plan explicite sur le chemin nominal** : le chemin runtime nominal ne repose plus sur `plan=None` comme état fonctionnel toléré. Le plan final utilisé par assembly/execution profile/observabilité est explicite et cohérent avec la doctrine `free/premium`. Le `LLMExecutionRequest` du parcours daily nominal arrive soit avec un plan déjà explicite depuis l’adapter, soit avec une règle de normalisation précoce documentée et assumée comme mécanisme canonique, et non comme reliquat toléré d’un état transitoire.
4. **AC4 — Taxonomie runtime réalignée** : `AIEngineAdapter`, le gateway, les seeds, les mappings de compatibilité et la documentation portent tous la même taxonomie finale pour ce parcours.
5. **AC5 — Observabilité sans reliquat transitoire** : `obs_snapshot.pipeline_kind`, les dashboards, métriques, logs et tests associés ne signalent plus `transitional_governance` pour ce parcours nominal daily après la correction.
6. **AC6 — Gouvernance des fallbacks cohérente** : `FallbackGovernanceRegistry` et les garde-fous connexes infèrent et appliquent la famille finale de façon cohérente, sans maintenir un alias implicite non documenté entre `daily_prediction` et `horoscope_daily`.
7. **AC7 — Documentation canonique à jour** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) ne documente plus `daily_prediction` comme famille officiellement active en `transitional_governance` si cette situation est fermée. La table `Familles et points d’entrée réels` est explicitement réalignée avec la taxonomie cible, et ne conserve plus `daily_prediction` comme famille active distincte si l’option B est retenue.
8. **AC8 — Tests réalignés sur la cible finale** : les suites introduites par 66.19, 66.20, 66.24 et 66.25 n’assertent plus un comportement transitoire obsolète (`daily_prediction` autonome + `plan=None` + `pipeline_kind=transitional_governance`) si ce comportement n’est plus voulu.
9. **AC9 — Compatibilité legacy bornée** : si un alias legacy `daily_prediction` doit subsister pour compatibilité, il est explicitement classé comme compatibilité dépréciée et non comme seconde famille officiellement active.
10. **AC10 — Aucun nouveau transitoire compensatoire** : la story n’introduit ni taxonomie intermédiaire, ni nouveau flag du type `daily_prediction_canonicalized`, ni double mapping durable. La fermeture s’appuie sur les primitives canoniques existantes.
11. **AC11 — Matrice d’évaluation sans seconde famille active** : la matrice d’évaluation canonique ne contient plus `daily_prediction` comme famille active distincte en `transitional_governance`. Si un alias legacy subsiste, il est traité hors matrice canonique ou explicitement classé comme compatibilité dépréciée, sans cellule autonome concurrente avec la famille finale.

## Tasks / Subtasks

- [x] Task 1: Trancher la cible structurelle et l’encoder une seule fois (AC1, AC2, AC10)
  - [x] Inspecter les différences encore réellement portées par `daily_prediction` face à `horoscope_daily` : contrat de sortie, longueur, assembly, profile, observabilité, produit attendu.
  - [x] Formaliser brièvement dans la PR et/ou les notes de story la décision retenue : `daily_prediction` famille nominale autonome ou alias absorbé dans `horoscope_daily`.
  - [x] Refuser toute implémentation hybride où `daily_prediction` reste actif dans certaines surfaces mais absorbé dans d’autres.

- [x] Task 2: Réaligner le point d’entrée applicatif daily (AC1, AC3, AC4, AC9)
  - [x] Mettre à jour [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py) pour que le chemin `variant_code` par défaut reflète la cible finale.
  - [x] Supprimer l’hypothèse nominale `plan=None` sur ce chemin ; si un plan implicite métier subsiste, le convertir en plan explicite au bon niveau.
  - [x] Vérifier et documenter précisément le rôle de `_normalize_plan_for_assembly()` sur ce parcours : soit il devient un mécanisme canonique explicite, soit il cesse de compenser un `plan=None` hérité de l’état transitoire.
  - [x] Vérifier le traitement de `uc_to_report` et des erreurs pour qu’il reflète la famille finale, sans reliquat sémantique contradictoire.

- [x] Task 3: Fermer la taxonomie gateway / renderer / fallback / observabilité (AC1, AC4, AC5, AC6, AC10)
  - [x] Mettre à jour [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py) pour que `pipeline_kind` et les chemins dérivés reflètent la cible finale.
  - [x] Mettre à jour [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py) si la famille finale doit être considérée comme fermée nominalement pour la politique placeholders.
  - [x] Réaligner [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py) pour que l’inférence de famille ne porte plus de contradiction cachée entre ce qui est documenté et ce qui est gouverné.
  - [x] Vérifier que `ExecutionObservabilitySnapshot.pipeline_kind` n’expose plus un reliquat `transitional_governance` sur le chemin nominal concerné.

- [x] Task 4: Réaligner seeds, assemblies et profils d’exécution (AC2, AC3, AC4, AC9)
  - [x] Mettre à jour [backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py) pour qu’il reflète la taxonomie cible.
  - [x] Si `daily_prediction` reste autonome, publier une assembly fermée avec plan explicite et garder une doctrine cohérente avec `ExecutionProfile`.
  - [x] Si `daily_prediction` est absorbé, retirer ou déclasser les artefacts seed qui la maintiennent comme famille active distincte ; aucune assembly nominale active propre à `daily_prediction` ne doit subsister.
  - [x] Vérifier l’impact éventuel sur `UseCaseConfig`, `PromptVersion`, `ExecutionProfile` et compatibilités seedées au démarrage.

- [x] Task 5: Réaligner documentation et matrices de lecture (AC1, AC5, AC7, AC9, AC11)
  - [x] Corriger [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) dans les sections `Résumé exécutable`, `Cartographie des familles`, `Familles et points d’entrée réels`, `Doctrine d’abonnement`, `Observabilité runtime` et `Matrice d’évaluation`.
  - [x] Vérifier que la documentation ne conserve pas de phrases du type “`daily_prediction` arrive avec `plan=None` puis normalisé en `free` mais reste transitoire” si cette situation est supprimée.
  - [x] Vérifier que la matrice d’évaluation n’expose plus `daily_prediction` comme famille active distincte si un alias legacy subsiste encore.
  - [x] Ajuster si nécessaire les artefacts 66.19, 66.20, 66.24 ou 66.25 uniquement pour lever une contradiction documentaire explicite, sans réécrire leur intention historique.

- [x] Task 6: Réaligner les tests de non-régression sur le vrai contrat final (AC3, AC5, AC8, AC9, AC11)
  - [x] Mettre à jour [backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py) pour supprimer l’assertion devenue legacy `request.user_input.plan is None` si la cible finale ne la justifie plus.
  - [x] Ajouter ou adapter des tests sur `pipeline_kind` et/ou `_resolve_plan()` pour prouver que le chemin daily n’est plus classé `transitional_governance`.
  - [x] Vérifier les suites issues de 66.20, 66.24 et 66.25 qui lisent la gouvernance canonique, les matrices d’évaluation ou `obs_snapshot`.
  - [x] Si une compatibilité `daily_prediction` est conservée, ajouter un test qui prouve qu’elle est traitée comme alias déprécié borné, et non comme famille active concurrente ni comme cellule autonome de matrice canonique.

- [x] Task 7: Vérification locale obligatoire (AC1 à AC10)
  - [x] Après activation du venv PowerShell, exécuter `ruff format .` puis `ruff check .` dans `backend/`.
  - [x] Exécuter `pytest -q` dans `backend/`.
  - [x] Exécuter au minimum les suites ciblées liées à 66.19, 66.20, 66.24, 66.25 et à la nouvelle story si une suite dédiée est créée.
  - [x] Vérifier que la documentation finale et le runtime se racontent strictement la même histoire sur le statut daily.

### Review Findings

- [x] [Review][Patch] Invalid variant_code in adapter [backend/app/services/ai_engine_adapter.py:878]
- [x] [Review][Patch] Hardcoded string "daily_prediction" [feature_taxonomy.py, gateway.py]
- [x] [Review][Patch] Brittle Persona lookup in seeds [seed_horoscope_narrator_assembly.py:153]
- [x] [Review][Patch] Brittle test setup in conftest.py [conftest.py]
- [x] [Review][Patch] Redundant logic in gateway.py [gateway.py]
- [x] [Review][Patch] Missing logging for legacy daily_prediction path [ai_engine_adapter.py]
- [x] [Review][Patch] Hardcoded CANONICAL_FAMILIES in test [test_story_66_28_closure.py]
- [x] [Review][Patch] Confusing chart_json in chat test [test_resolved_execution_plan.py]
- [x] [Review][Patch] Whitespace in feature name [feature_taxonomy.py:58]
- [x] [Review][Defer] Brittle seed logic for existing DB [seed_horoscope_narrator_assembly.py] — deferred, pre-existing

## Dev Notes

### Diagnostic exact à préserver

- La dette ne porte pas seulement sur le code ; elle porte sur la dissonance entre code, doc, observabilité et tests.
- `daily_prediction` est aujourd’hui le dernier exemple explicitement documenté d’une famille encore active mais non entièrement fermée.
- Le vrai signal de dette n’est pas seulement `feature="daily_prediction"`, mais le triplet :
  - `feature="daily_prediction"`
  - `plan=None` sur le point d’entrée
  - `pipeline_kind="transitional_governance"` dans la lecture canonique
- Le dépôt montre déjà une convergence incomplète :
  - l’adapter garde `daily_prediction` autonome ;
  - le fallback governance la rabat déjà partiellement sur `horoscope_daily` ;
  - la doc la présente encore comme exception active ;
  - les tests 66.19 figent l’état transitoire.
- Sauf preuve contraire trouvée dans le code, le biais de décision doit être en faveur de l’absorption dans `horoscope_daily`, pas du maintien conservateur d’une famille autonome.

### Ce que le dev ne doit pas faire

- Ne pas créer une troisième catégorie entre `nominal_canonical` et `transitional_governance`.
- Ne pas garder `daily_prediction` comme “famille active mais aliasée partout” sans l’assumer explicitement comme compatibilité dépréciée.
- Ne pas conserver `plan=None` comme comportement nominal tout en déclarant la fermeture canonique.
- Ne pas corriger seulement la doc ou seulement les tests : la vérité runtime doit être corrigée en premier.
- Ne pas multiplier les mappings cachés entre adapter, gateway, fallback governance et observabilité.
- Si un alias `daily_prediction` subsiste, “borné” signifie au minimum :
  - plus aucune assembly nominale active propre à `daily_prediction` ;
  - plus aucun `pipeline_kind` nominal ou transitoire spécifique à `daily_prediction` ;
  - alias accepté uniquement à l’entrée pour compatibilité historique puis remappé immédiatement vers la famille canonique finale ;
  - aucune nouvelle publication admin ne peut cibler `daily_prediction` comme famille autonome.

### Fichiers à inspecter en priorité

- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py)
- [backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.19** a branché `horoscope_daily` et `daily_prediction` dans le gateway canonique, mais a explicitement laissé `daily_prediction` comme chemin par défaut distinct avec `plan=None`.
- **66.20** a fermé nominalement `chat`, `guidance`, `natal` et `horoscope_daily` ; le résidu `daily_prediction` apparaît maintenant comme l’exception restante.
- **66.21** a déjà fait converger la gouvernance de fallback en inférant `daily_prediction` sous la famille `horoscope_daily`, ce qui est un signal fort qu’une fermeture complète est attendue.
- **66.24** a étendu la matrice d’évaluation aux chemins encore non convergés et a documenté `daily_prediction` comme cas transitoire observé.
- **66.25** a fixé `pipeline_kind` comme axe canonique d’observabilité ; cette story doit donc supprimer le reliquat transitoire à la source, pas le masquer en reporting.
- **66.26** impose que le document canonique reste aligné avec le code réel.
- **66.27** a encore renforcé la doctrine “une seule vérité runtime propagée jusqu’à l’observabilité”, doctrine qui s’applique ici à la gouvernance daily.
- La documentation canonique actuelle oriente déjà implicitement vers l’option B : mêmes campagnes d’évaluation, normalisation de plan en `free`, convergence partielle dans les garde-fous, mais aucune justification structurelle explicite pour maintenir `daily_prediction` comme vraie famille canonique autonome.

### Git Intelligence

Commits récents pertinents observés :

- `e3a38dd6` : `test(llm): harden story 66.27 integration persistence checks`
- `7b622be8` : `fix(llm): resolve signature mismatch in ContextQualityInjector and improve observability logging`
- `50d0fb0a` : `feat(llm): story 66.27 - propagate context_quality_handled_by_template to observability`
- `68c93e77` : `docs(llm): reflect story 66.26 in canonical pipeline guide`
- `d9b4ad6c` : `docs(bmad): align story 66.26 artifacts with review fixes`

Pattern récent à réutiliser :

- une source de vérité runtime unique ;
- une correction portée dans le code puis propagée aux tests et à la doc ;
- un focus sur la fermeture des écarts canoniques, pas sur des refactors larges ;
- des tests ciblés qui prouvent le comportement réel, pas des constructions artificielles.

### Testing Requirements

- Ajouter au minimum un test qui prouve le statut final du chemin daily dans `_build_result()` / `obs_snapshot.pipeline_kind`.
- Ajouter ou adapter un test de routing adapter qui prouve que le `plan` nominal final n’est plus `None` si la fermeture retenue l’interdit.
- Ajouter ou adapter un test sur `_normalize_plan_for_assembly()` ou sur son effet observable pour prouver que la normalisation éventuelle du plan sur ce parcours relève d’une règle canonique explicite et non d’un reliquat transitoire masqué.
- Vérifier qu’aucun test n’attend encore `daily_prediction` comme famille active `transitional_governance` si ce n’est plus vrai.
- Si l’option absorption est choisie, couvrir la compatibilité d’un éventuel alias `daily_prediction` sans le traiter comme famille active autonome.
- Vérifier que la matrice d’évaluation canonique ne porte plus `daily_prediction` comme famille active distincte si un alias legacy subsiste encore.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest app/llm_orchestration/tests/test_story_66_19_narrator_migration.py -q`
  - ajouter toute suite ciblée créée pour 66.28

### Project Structure Notes

- Travail backend + documentation uniquement.
- Aucun changement frontend n’est attendu.
- Les changements doivent rester concentrés dans `backend/app/services/`, `backend/app/llm_orchestration/`, `backend/app/llm_orchestration/tests/` et `docs/`.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/services/ai_engine_adapter.py](/c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/seeds/seed_horoscope_narrator_assembly.py)
- [backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_story_66_19_narrator_migration.py)
- [backend/app/llm_orchestration/ARCHITECTURE.md](/c:/dev/horoscope_front/backend/app/llm_orchestration/ARCHITECTURE.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-19-migrer-horoscope-daily-daily-prediction-gateway-canonique.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-19-migrer-horoscope-daily-daily-prediction-gateway-canonique.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-26-durcissement-discipline-maintenance-documentaire-pipeline-llm.md)
- [66-27-propagation-complete-context-quality-handled-by-template-observabilite.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-27-propagation-complete-context-quality-handled-by-template-observabilite.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Plan

**Decision: Option B — Absorber `daily_prediction` dans `horoscope_daily`**

Rationale: `daily_prediction` is currently a legacy alias for the daily narrator, with no structural difference from `horoscope_daily` (same assemblies, same evaluation targets). Absorbing it removes the last `transitional_governance` status and simplifies the taxonomy.

**Steps:**
1. **Research:** Map current usages of `daily_prediction` in `AIEngineAdapter`, `Gateway`, `Seeds`, and `FallbackGovernance`.
2. **Red:** Update tests to expect `horoscope_daily` instead of `daily_prediction` for daily narrative flows.
3. **Green:**
    - Update `AIEngineAdapter.generate_horoscope_narration` to use `feature="horoscope_daily"`.
    - Update `Gateway` to calculate `pipeline_kind="nominal_canonical"` and use `horoscope_daily` for both narrative and summary flows.
    - Update `Seeds` to merge/redirect `daily_prediction` assemblies to `horoscope_daily`.
    - Update `FallbackGovernance` to treat `daily_prediction` as a legacy alias.
4. **Refactor:** Ensure `plan` is explicitly passed and not `None`.
5. **Documentation:** Update `docs/llm-prompt-generation-by-feature.md`.

### Debug Log References

### Completion Notes List

- L’option B a été mise en oeuvre : `daily_prediction` est absorbé dans `horoscope_daily` comme alias legacy borné.
- Les artefacts runtime legacy `daily_prediction` ont été déclassés ou archivés ; aucune publication nominale nouvelle ne doit plus pouvoir ressusciter cette famille.
- Les routes admin `create/update/publish/rollback` et `PromptRegistryV2` bloquent explicitement les usages nominaux interdits de `daily_prediction` avec contrat d’erreur `forbidden_feature`.
- La matrice d’évaluation et les fixtures de contrat ne portent plus `daily_prediction` comme famille active distincte.
- Des tests ciblés couvrent désormais le verrou `publish/rollback` legacy aux niveaux route admin et registry.
- `sprint-status.yaml` n’a pas été modifié car aucune entrée `66-28-*` n’y existe encore à la date de clôture.

### File List

- `_bmad-output/implementation-artifacts/66-28-fermeture-canonique-daily-prediction-ou-suppression-statut-transitoire.md`
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
- `backend/app/llm_orchestration/tests/test_prompt_registry_v2.py`
- `docs/llm-prompt-generation-by-feature.md`
