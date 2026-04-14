# Story 66.42: Anti-entropie de la taxonomie canonique et des placeholders

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want verrouiller la taxonomie canonique et la gouvernance des placeholders dans un registre central versionné,
so that aucune dérive locale, aucun alias opportuniste et aucun placeholder non gouverné ne puissent réapparaître silencieusement dans le pipeline de prompting.

## Contexte

Le runtime dispose déjà de plusieurs briques de gouvernance :

- familles nominales supportées ;
- normalisation `feature` / `subfeature` ;
- mapping de compatibilité legacy ;
- allowlists de placeholders ;
- validateurs de cohérence au publish et au runtime.

Le problème n’est plus l’absence totale de règles, mais leur **dispersion** :

- une partie de la vérité vit dans la taxonomie ;
- une autre dans le catalogue/assemblies ;
- une autre dans le renderer ;
- une autre encore dans les validateurs de cohérence ;
- certaines exceptions restent possibles sans métadonnées de gouvernance suffisantes.

Cette dispersion crée un risque d’entropie :

- ajout d’un placeholder “temporaire” non gouverné ;
- alias `feature` ou `use_case` introduit localement pour débloquer un cas ;
- divergence entre placeholders autorisés au publish, réellement rendus au runtime, et décrits dans la documentation ;
- multiplication de petites exceptions sans owner ni date de révision.

66.42 doit donc transformer cette gouvernance fragmentée en **registre canonique unique**, branché aux contrôles de publish, de runtime et de CI.

## Portée exacte

Cette story couvre quatre axes et rien de plus :

1. **registre central versionné** pour taxonomie, aliases et placeholders gouvernés ;
2. **branchage de ce registre** sur les validations publish/runtime ;
3. **garde-fous CI** contre l’extension non gouvernée du périmètre ;
4. **gestion explicite des exceptions** avec owner et échéance.

Elle ne doit pas :

- réécrire tout le pipeline de prompting ;
- créer une documentation passive non branchée aux contrôles ;
- confondre compatibilité legacy transitoire et taxonomie canonique ;
- tolérer un placeholder ou alias “provisoire” sans gouvernance.

## Diagnostic précis à traiter

Les dérives prioritaires à neutraliser sont :

1. listes ou allowlists dispersées et susceptibles de diverger ;
2. placeholders autorisés dans un composant mais non gouvernés centralement ;
3. aliases introduits localement sans revue d’architecture ;
4. exceptions non bornées sans owner, justification ni date de revue ;
5. documentation canonique en léger décalage avec la vérité exécutable.

La priorité d’implémentation est :

- d’abord centraliser ;
- ensuite brancher sur les points de contrôle ;
- enfin rendre toute extension non gouvernée impossible ou immédiatement visible.

## Cible d'architecture

Conserver la séparation fonctionnelle existante :

1. **taxonomie** = familles, clés et normalisations canoniques ;
2. **assemblies / catalogues** = contenu et placeholders utilisés ;
3. **renderer / validateurs** = enforcement technique ;
4. **documentation** = contrat explicite.

La cible 66.42 est d’ajouter une **source de vérité unique gouvernée** qui relie ces couches sans les dupliquer :

- taxonomie canonique ;
- aliases autorisés ;
- placeholders autorisés ;
- exceptions explicites et bornées.

Le registre doit être exécutable, versionné et consulté par les validations réelles ; il ne doit pas être un simple tableau de référence pour humains.

## Acceptance Criteria

1. **AC1 — Registre central versionné** : une source de vérité unique versionnée couvre au minimum :
   - familles canoniques ;
   - aliases autorisés ;
   - placeholders autorisés ;
   - exceptions gouvernées ;
   - statut et métadonnées minimales associées.
2. **AC2 — Publish bloquant sur placeholder non gouverné** : une assembly publiée contenant un placeholder non enregistré dans le registre central est refusée avec une erreur stable, orientée correction.
3. **AC3 — CI bloquante sur alias non gouverné** : l’introduction d’un nouvel alias `feature`, `subfeature` ou `use_case` non enregistré fait échouer la CI ou le contrôle de cohérence choisi.
4. **AC4 — Extension de placeholder gouvernée uniquement** : toute extension de placeholder autorisé sans mise à jour du registre central échoue, y compris si le renderer ou le catalogue l’accepte localement.
5. **AC5 — Exceptions explicites et complètes** : toute exception taxonomique ou placeholder exceptionnel porte au minimum owner, justification, périmètre, statut et date d’expiration ou de revue. Une exception incomplète est refusée.
6. **AC6 — Cohérence inter-couches** : les validations de `PromptRenderer`, d’assemblies, de cohérence config et du registre central restent alignées. Aucune allowlist contradictoire ne subsiste.
7. **AC7 — Rapport de violation lisible** : une sortie exploitable identifie clairement les placeholders ou aliases non gouvernés, la source de divergence et la règle violée.
8. **AC8 — Documentation réalignée** : la documentation canonique du pipeline décrit le registre central, la frontière entre canonique et legacy transitoire, et le rôle des exceptions gouvernées.
9. **AC9 — Compatibilité legacy explicitement séparée** : le registre distingue clairement ce qui relève de la taxonomie canonique de ce qui relève d’une compatibilité legacy transitoire, afin d’éviter toute confusion doctrinale.
10. **AC10 — Anti-réintroduction durable** : une suite de non-régression échoue si une allowlist locale contradictoire, un alias opportuniste ou un placeholder non gouverné réapparaît dans une zone critique du runtime.
11. **AC11 — Intégration doc ↔ code si nécessaire** : si le registre central devient un artefact structurel de l’architecture documentaire, le contrôle doc ↔ code l’intègre dans son périmètre.
12. **AC12 — Windows + PowerShell supportés** : les validations locales requises restent compatibles avec le workflow du dépôt.

## Tasks / Subtasks

- [ ] Task 1: Formaliser le registre central taxonomie/placeholders (AC1, AC5, AC9)
  - [ ] Définir une source de vérité unique pour familles, aliases, placeholders et exceptions.
  - [ ] Y modéliser les métadonnées minimales de gouvernance.
  - [ ] Clarifier la séparation entre canonique et compatibilité transitoire.

- [ ] Task 2: Brancher le registre sur les validations publish/runtime (AC2, AC4, AC6)
  - [ ] Rendre le publish des assemblies dépendant du registre central.
  - [ ] Brancher le renderer et/ou les validateurs de cohérence sur cette même source de vérité.
  - [ ] Éliminer les allowlists locales contradictoires.

- [ ] Task 3: Ajouter les garde-fous CI et anti-réintroduction (AC3, AC10, AC11)
  - [ ] Faire échouer la CI sur alias non gouverné.
  - [ ] Faire échouer les contrôles sur placeholder étendu sans gouvernance.
  - [ ] Étendre le garde doc ↔ code si le registre central devient structurel.

- [ ] Task 4: Gérer explicitement les exceptions (AC5, AC7)
  - [ ] Refuser toute exception incomplète.
  - [ ] Produire un rapport lisible des exceptions et violations.
  - [ ] Prévoir une lecture exploitable pour maintenance et review.

- [ ] Task 5: Réaligner la documentation canonique (AC8, AC9)
  - [ ] Mettre à jour `docs/llm-prompt-generation-by-feature.md`.
  - [ ] Décrire le registre central et sa place dans le runtime.
  - [ ] Clarifier la doctrine placeholders vs compatibilité legacy.

- [ ] Task 6: Validation locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [ ] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblant taxonomie, placeholders, cohérence config et doc ↔ code.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- Le vrai problème est la dispersion, pas l’absence totale de règles.
- Le registre central doit être la vérité exécutée par les contrôles, pas un référentiel décoratif.
- Un placeholder non gouverné est un risque de comportement caché dans le prompt final.
- Un alias opportuniste est une réintroduction d’entropie dans un système qui s’est récemment refermé.

### Ce que le dev ne doit pas faire

- Ne pas maintenir plusieurs allowlists locales “temporaires”.
- Ne pas traiter la compatibilité legacy comme une extension normale de la taxonomie canonique.
- Ne pas ajouter des exceptions sans owner, justification et date de revue.
- Ne pas laisser le renderer ou les assemblies accepter plus que ce que le registre central gouverne.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py)
- [backend/app/llm_orchestration/services/assembly_resolver.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- Les stories récentes ont renforcé la taxonomie canonique et l’assembly obligatoire.
- Le pipeline actuel est assez fermé pour rendre visibles les divergences de gouvernance restantes.
- La documentation runtime insiste sur les familles nominales, la séquence de transformation et le caractère gouverné des placeholders ; 66.42 doit aligner cette doctrine avec une source de vérité unique.

### Git Intelligence

Le pattern des stories récentes montre une montée en gouvernance :

- fermeture du nominal ;
- suppression des fallbacks implicites ;
- contrôle de cohérence au publish et au boot ;
- conformité doc ↔ code.

Signal utile :

- l’étape logique suivante est l’anti-entropie des registres de taxonomie et de placeholders ;
- cette story doit surtout éviter la dérive future, pas produire une nouvelle complexité.

### Testing Requirements

- Ajouter une couverture publish bloquante pour placeholder non gouverné.
- Ajouter une couverture CI/cohérence bloquante pour alias non enregistré.
- Vérifier qu’une exception incomplète échoue.
- Vérifier qu’aucune allowlist locale contradictoire ne subsiste dans les composants critiques.
- Vérifier la cohérence doc ↔ code si le registre central rejoint le périmètre structurel documentaire.

### Project Structure Notes

- Zone principale : `backend/app/llm_orchestration/`
- Zone adjacente : `backend/app/prompts/`
- Le registre central doit vivre près du runtime et des validateurs, pas dans une zone générique éloignée.

### References

- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/prompts/catalog.py](/c:/dev/horoscope_front/backend/app/prompts/catalog.py)
- [backend/app/llm_orchestration/services/assembly_resolver.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_resolver.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
