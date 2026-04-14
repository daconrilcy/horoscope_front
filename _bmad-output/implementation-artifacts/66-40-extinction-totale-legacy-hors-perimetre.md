# Story 66.40: Extinction totale du legacy hors périmètre supporté

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want supprimer ou enclore définitivement tous les chemins legacy encore actifs hors périmètre supporté,
so that le runtime nominal ne puisse plus être contaminé par des résolutions historiques ambiguës, des fallbacks résiduels ou des aliases non gouvernés.

## Contexte

Les stories précédentes de l’epic 66 ont progressivement fermé le runtime nominal :

- la taxonomie canonique a été stabilisée autour de `chat`, `guidance`, `natal` et `horoscope_daily` ;
- l’assembly est devenue obligatoire sur le périmètre supporté ;
- `ExecutionProfile` est désormais une dépendance explicite de l’exécution ;
- les fallbacks historiques ne sont plus censés sauver silencieusement un cas nominal mal configuré ;
- la documentation runtime décrit déjà ces familles comme un périmètre fermé et gouverné.

Le risque résiduel n’est donc plus dans le nominal, mais dans la **persistance de compatibilités legacy hors périmètre supporté** :

- chemins `USE_CASE_FIRST` ou assimilés encore accessibles pour des entrées non nominales ;
- aliases `feature`, `subfeature` ou `use_case` tolérés pour compatibilité ;
- logique de résolution implicite “si la config manque alors retomber sur un comportement historique” ;
- absence de visibilité opérationnelle sur la fréquence réelle d’activation de ces chemins.

Tant que ces chemins existent sans gouvernance centralisée, ils restent une dette d’architecture :

- ils compliquent l’explicabilité du runtime ;
- ils laissent ouverte la réintroduction involontaire d’un comportement non nominal ;
- ils créent une seconde philosophie de résolution à côté de la voie canonique.

66.40 doit donc **transformer le legacy résiduel en objet gouverné, borné, instrumenté et en voie d’extinction**, sans réouvrir le périmètre nominal déjà fermé.

## Portée exacte

Cette story couvre quatre axes et rien de plus :

1. **inventaire canonique** des chemins legacy encore permis ;
2. **instrumentation observable** de leur usage réel ;
3. **mécanisme de blocage progressif** par feature/famille/périmètre ;
4. **garde-fous anti-réintroduction** sur les aliases et fallbacks historiques.

Elle ne doit pas :

- réintroduire une compatibilité supplémentaire sur les familles nominales ;
- créer une seconde gouvernance parallèle distincte du runtime ;
- convertir cette story en refactor massif de toute la taxonomie si ce n’est pas nécessaire ;
- supprimer à l’aveugle des compatibilités sans d’abord les inventorier et mesurer leur usage réel.

## Diagnostic précis à traiter

Les points de faiblesse à traiter explicitement sont les suivants :

1. il n’existe pas encore de registre unique, versionné et exhaustif des tolérances legacy résiduelles ;
2. l’usage réel de ces chemins n’est pas suffisamment visible pour planifier leur extinction ;
3. certaines compatibilités restent implicites dans le code au lieu d’être décrites comme des exceptions gouvernées ;
4. l’anti-régression sur la réintroduction d’aliases ou de fallbacks historiques doit être plus forte ;
5. la documentation runtime décrit la fermeture nominale, mais pas encore toujours la stratégie d’extinction du résiduel hors périmètre.

La priorité d’implémentation est :

- d’abord rendre visible et centraliser ;
- ensuite rendre blocable ;
- enfin rendre impossible la réintroduction silencieuse.

## Cible d'architecture

Conserver la séparation actuelle :

1. **taxonomie canonique** = ce qui est nominalement supporté ;
2. **gouvernance des fallbacks / compatibilités** = ce qui reste toléré de façon bornée ;
3. **observabilité** = preuve de l’usage réel ;
4. **documentation** = contrat explicite décrivant le nominal et le résiduel.

La cible 66.40 est d’ajouter deux propriétés :

- **legacy deny-by-default à terme** : toute tolérance doit être explicitement enregistrée pour exister ;
- **mesurabilité opérationnelle** : aucune compatibilité résiduelle ne doit rester “invisible”.

Le registre du legacy résiduel doit rester proche des composants `llm_orchestration` déjà responsables de la taxonomie et des fallbacks, et non vivre dans un document mort séparé du runtime.

## Acceptance Criteria

1. **AC1 — Registre central exhaustif** : une source de vérité versionnée inventorie tous les chemins legacy encore actifs ou activables. Chaque entrée porte au minimum :
   - identifiant stable ;
   - type (`fallback`, `alias`, `legacy_use_case`, `legacy_resolution_path`, ou taxonomie bornée équivalente) ;
   - périmètre exact ;
   - statut (`allowed`, `deprecated`, `blocked`, `removal_candidate`, ou taxonomie bornée équivalente) ;
   - owner ;
   - justification ;
   - date de revue ou date cible d’extinction.
   Aucune tolérance résiduelle ne reste uniquement implicite dans le code.
2. **AC2 — Alignement runtime du registre** : le runtime consulte ce registre ou une projection directe de celui-ci pour déterminer la gouvernance d’un chemin legacy. Il n’existe pas de seconde matrice équivalente reconstruite localement dans un autre service.
3. **AC3 — Télémétrie d’usage réelle** : l’activation d’un chemin legacy produit une trace observable corrélée au moins à `feature`, `subfeature`, type de chemin, raison d’activation, snapshot/runtime context disponible, et dernière utilisation observée. Cette trace est exploitable dans les surfaces ops existantes ou un rapport dédié.
4. **AC4 — Blocage progressif gouverné** : un mécanisme explicite permet de bloquer progressivement certains chemins legacy par famille, feature ou type de compatibilité, sans modifier le comportement nominal déjà fermé de `chat`, `guidance`, `natal` et `horoscope_daily`.
5. **AC5 — Families nominales intouchables** : aucune activation de fallback ou de chemin legacy résiduel n’est possible sur les familles nominales supportées. Toute tentative échoue avec une erreur stable, orientée review et sans ambiguïté.
6. **AC6 — Anti-réintroduction des fallbacks nominaux** : une suite de non-régression échoue si un fallback nominal interdit réapparaît sur une famille supportée, y compris sous forme d’alias, de mapping implicite ou de compatibilité “temporaire”.
7. **AC7 — Anti-réintroduction des aliases** : une suite de non-régression échoue si un nouvel alias `feature`, `subfeature` ou `use_case` est introduit sans enregistrement explicite dans le registre central et sans métadonnées de gouvernance complètes.
8. **AC8 — Exceptions bornées et complètes** : toute exception legacy résiduelle sans `owner`, justification, statut et date de revue/expiration est refusée au build, au publish ou par la CI selon le point d’intégration choisi.
9. **AC9 — Documentation canonique réalignée** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) décrit l’état réel du legacy résiduel, la stratégie d’extinction et la frontière entre taxonomie canonique et compatibilité transitoire.
10. **AC10 — Cohérence doc ↔ code préservée** : si le registre legacy devient structurel pour l’architecture documentaire, le contrôle doc ↔ code en tient compte et échoue si le registre est modifié sans réalignement documentaire requis.
11. **AC11 — Rapport exploitable pour maintenance** : une sortie lisible identifie au minimum les entrées legacy actives, leur statut, leur périmètre et les violations détectées. Elle est suffisante pour préparer une extinction par lots sans relecture manuelle du code complet.
12. **AC12 — Windows + PowerShell supportés** : les validations locales nécessaires à la story restent compatibles avec le workflow Windows/PowerShell du dépôt.

## Tasks / Subtasks

- [ ] Task 1: Formaliser le registre central du legacy résiduel (AC1, AC2, AC8)
  - [ ] Définir une structure versionnée unique pour les chemins legacy résiduels.
  - [ ] Y modéliser type, périmètre, statut, owner, justification et date de revue/expiration.
  - [ ] Éliminer ou encapsuler toute duplication de gouvernance résiduelle déjà présente dans d’autres modules.

- [ ] Task 2: Aligner le runtime sur ce registre unique (AC2, AC4, AC5)
  - [ ] Brancher la décision runtime de compatibilité legacy sur la source de vérité centrale.
  - [ ] Ajouter un mécanisme explicite de blocage progressif par feature/famille/type.
  - [ ] Garantir qu’aucun blocage progressif ne modifie le nominal déjà fermé des quatre familles supportées.

- [ ] Task 3: Instrumenter l’usage réel du legacy (AC3, AC11)
  - [ ] Émettre une télémétrie normalisée lors de toute activation de chemin legacy.
  - [ ] Corréler cette télémétrie avec les surfaces d’observabilité existantes quand les discriminants sont disponibles.
  - [ ] Produire au moins une vue ou un rapport de maintenance exploitable.

- [ ] Task 4: Verrouiller l’anti-réintroduction (AC5, AC6, AC7, AC8)
  - [ ] Ajouter des tests qui cassent si un fallback nominal interdit réapparaît.
  - [ ] Ajouter des tests qui cassent si un alias non gouverné est introduit.
  - [ ] Ajouter des tests qui cassent si une exception legacy incomplète est enregistrée.

- [ ] Task 5: Réaligner la documentation et la gouvernance doc ↔ code (AC9, AC10)
  - [ ] Mettre à jour la documentation canonique du pipeline LLM.
  - [ ] Décrire explicitement la stratégie `deny-by-default` visée à terme.
  - [ ] Étendre le contrôle doc ↔ code si le nouveau registre fait partie du périmètre structurel.

- [ ] Task 6: Validation locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [ ] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblant gouvernance des fallbacks, taxonomie, observabilité et conformité documentaire.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.40 n’est pas une story de réouverture fonctionnelle ; c’est une story d’**extinction gouvernée** du résiduel legacy.
- Le bon résultat n’est pas “supprimer tout le legacy immédiatement”, mais rendre chaque compatibilité restante explicite, mesurée et blocable.
- Les familles `chat`, `guidance`, `natal` et `horoscope_daily` doivent rester strictement fermées.
- Le registre du legacy doit être un artefact exécutable, pas une note documentaire annexe.

### Ce que le dev ne doit pas faire

- Ne pas créer une seconde matrice de gouvernance à côté de `FallbackGovernanceRegistry` ou de la taxonomie canonique.
- Ne pas traiter “absence de configuration” comme autorisation implicite.
- Ne pas ajouter une nouvelle couche d’alias “temporaire” sans owner ni échéance.
- Ne pas instrumenter le legacy avec des logs libres non exploitables en ops.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/services/config_coherence_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/config_coherence_validator.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.31** a déjà poussé le runtime vers un modèle fail-fast sur les incohérences structurelles.
- **66.36** et **66.38/66.39** ont renforcé la gouvernance exécutable et la traçabilité doc ↔ code.
- La documentation runtime actuelle assume que le nominal est fermé ; 66.40 doit éviter que le résiduel hors périmètre ne contredise cette promesse.
- Les stories antérieures ont rendu le périmètre nominal plus strict ; la suite logique est donc de traiter le legacy résiduel comme dette gouvernée, pas comme compatibilité neutre.

### Git Intelligence

La série récente de commits autour du pipeline LLM montre une dynamique claire :

- fermeture du runtime nominal ;
- suppression des fallbacks historiques sur le périmètre supporté ;
- renforcement de la conformité documentaire et de l’observabilité.

Signal utile :

- le prochain risque majeur n’est plus un manque de règles nominales, mais la persistance d’exceptions non mesurées ;
- cette story doit donc privilégier l’inventaire exécutable, la télémétrie et l’anti-entropie plutôt qu’un refactor dispersé.

### Testing Requirements

- Ajouter une couverture dédiée qui échoue si un fallback nominal interdit réapparaît sur `chat`, `guidance`, `natal` ou `horoscope_daily`.
- Ajouter une couverture qui échoue si un alias `feature`, `subfeature` ou `use_case` est introduit sans enregistrement central.
- Ajouter une couverture de validation du registre central : entrée incomplète, statut invalide, absence d’owner, absence d’échéance/revue.
- Vérifier l’émission d’une télémétrie d’usage legacy exploitable et corrélable.
- Vérifier la cohérence doc ↔ code si le registre central rejoint le périmètre structurel documentaire.

### Project Structure Notes

- Zone principale : `backend/app/llm_orchestration/`
- Zones adjacentes : `backend/tests/`, `docs/`, éventuellement les scripts/CI si le registre devient un artefact gouverné par les quality gates.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [backend/app/llm_orchestration/feature_taxonomy.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/feature_taxonomy.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [66-39-durcissement-fiabilite-multi-contexte-gate-conformite-documentaire.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-39-durcissement-fiabilite-multi-contexte-gate-conformite-documentaire.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
