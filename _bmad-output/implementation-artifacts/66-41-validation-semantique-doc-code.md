# Story 66.41: Validation sémantique doc ↔ code du pipeline de génération de prompt

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want faire évoluer le contrôle documentaire doc ↔ code d’un garde surtout structurel vers un garde sémantique,
so that une dérive architecturale réelle du pipeline soit détectée même si les marqueurs textuels superficiels restent apparemment cohérents.

## Contexte

Les stories **66.38** et **66.39** ont déjà transformé la conformité documentaire en garde exécutable :

- manifeste structurel unique ;
- validateur réutilisable ;
- CLI unique pour local et CI ;
- contrôle PR bloquant ;
- qualité du changeset et des diagnostics renforcée.

Ce dispositif couvre bien les **divergences structurelles** :

- fichiers clés modifiés sans mise à jour de la doc ;
- absence de bloc de preuve documentaire ;
- motifs PR non conformes ;
- lints ciblés sur taxonomie, provider, fallback et `obs_snapshot`.

Mais il reste une zone de risque plus subtile : la **dérive sémantique**.

Exemples de dérives qui peuvent rester invisibles à un contrôle surtout structurel :

- l’ordre réel de transformation du prompt change ;
- la priorité snapshot actif vs tables live dérive ;
- un nouveau provider nominal ou une nouvelle famille apparaît sans gouvernance ;
- un fallback réapparaît sous une forme différente sans casser les motifs textuels simples ;
- des discriminants critiques cessent d’être propagés dans `ResolvedExecutionPlan`, `ExecutionObservabilitySnapshot` ou les surfaces de persistance.

66.41 doit donc ajouter une couche de vérification **conceptuelle mais bornée** : suffisamment forte pour attraper une dérive d’architecture réelle, sans tomber dans un parseur fragile de tout le codebase.

## Portée exacte

Cette story couvre cinq axes et rien de plus :

1. **modèle sémantique minimal versionné** du pipeline LLM ;
2. **détection de dérives d’ordre de transformation** du prompt ;
3. **détection de dérives de source de vérité runtime** ;
4. **détection de l’introduction non gouvernée** de familles, providers, fallbacks ou aliases ;
5. **fixtures de sabotage volontaire** prouvant que le garde sémantique casse bien quand l’architecture dérive réellement.

Elle ne doit pas :

- remplacer le validateur structurel existant ;
- tenter de parser narrativement toute la documentation ou tout le code ;
- créer un second système de gouvernance documentaire sans réutiliser le CLI et les surfaces 66.38/66.39 ;
- transformer le garde en outil flou, trop intelligent ou trop fragile.

## Diagnostic précis à traiter

Les dérives prioritaires à rendre détectables sont :

1. changement de l’ordre doctrinal `assembly -> length budget -> context_quality -> verbosité -> rendu placeholders -> composition messages` ;
2. perte de priorité du snapshot actif comme source de vérité runtime ;
3. réintroduction d’un provider nominal non gouverné ;
4. extension non documentée des familles supportées ;
5. retour d’un fallback ou alias historique sous une nouvelle forme ;
6. perte de propagation d’un discriminant critique dans le plan résolu, l’observabilité ou la persistance ;
7. faux sentiment de sécurité produit par un garde qui ne vérifie que des chaînes textuelles.

La priorité d’implémentation est :

- d’abord capturer les invariants qui gouvernent réellement le pipeline ;
- ensuite prouver qu’ils cassent sur sabotage ;
- enfin exposer des erreurs lisibles pour la revue.

## Cible d'architecture

Conserver le triptyque déjà en place :

1. **manifeste structurel** = périmètre de fichiers, marqueurs et règles doc ↔ code ;
2. **validateur / CLI existants** = point d’entrée unique local et CI ;
3. **documentation canonique** = contrat de référence du pipeline.

La cible 66.41 est d’ajouter un quatrième artefact :

4. **registre d’invariants sémantiques bornés** = modèle minimal de ce qui doit rester vrai dans l’architecture du pipeline.

Ce registre ne doit pas être un “jumeau complet” du code, mais un contrat exécutable concentré sur les invariants réellement critiques du runtime.

## Acceptance Criteria

1. **AC1 — Modèle sémantique minimal versionné** : une source de vérité versionnée capture les invariants critiques du pipeline au minimum sur :
   - ordre de transformation du prompt ;
   - source de vérité runtime ;
   - familles nominales ;
   - provider nominal ;
   - fallbacks/aliases gouvernés ;
   - discriminants de propagation critiques.
   Ce modèle reste borné et maintenable.
2. **AC2 — Dérive d’ordre détectée** : une modification de l’ordre doctrinal des transformations majeures du prompt fait échouer le contrôle sémantique avec une erreur stable identifiant l’invariant brisé.
3. **AC3 — Dérive de source de vérité détectée** : une perte de priorité du snapshot actif, une inversion de priorité ou une ambiguïté entre snapshot actif et tables live fait échouer le contrôle sémantique.
4. **AC4 — Dérive provider/famille détectée** : l’introduction non gouvernée d’un nouveau provider nominal, d’une nouvelle famille supportée ou d’un nouvel alias/fallback fait échouer le contrôle sémantique.
5. **AC5 — Propagation des discriminants critiques vérifiée** : la perte de propagation de champs critiques vers `ResolvedExecutionPlan`, `ExecutionObservabilitySnapshot`, `llm_call_logs` ou surfaces équivalentes ciblées fait échouer le contrôle sémantique quand cette propagation fait partie du contrat documentaire.
6. **AC6 — Fixtures de sabotage réelles** : une suite de sabotage volontaire démontre explicitement que le garde casse sur plusieurs dérives ciblées : ordre, source de vérité, provider, fallback, alias, propagation critique.
7. **AC7 — Erreurs orientées review** : les erreurs remontées sont structurées, lisibles, stables et indiquent au minimum quel invariant sémantique a été violé, dans quel composant ou contrat, et avec quel constat.
8. **AC8 — Réutilisation du pipeline de conformité existant** : la validation sémantique réutilise le point d’entrée doc ↔ code existant ou s’y intègre proprement. Elle ne crée pas une seconde CLI concurrente ou un workflow parallèle désynchronisé.
9. **AC9 — Documentation canonique réalignée** : si l’architecture change volontairement, la documentation canonique et le registre d’invariants sémantiques sont mis à jour ensemble.
10. **AC10 — Faux positifs bornés** : le garde sémantique reste centré sur des invariants bornés et machine-vérifiables ; il ne dérive pas vers des heuristiques narratives fragiles ou une analyse “intelligente” non stable.
11. **AC11 — Sortie exploitable en CI** : les erreurs sémantiques sont exposées dans un format réutilisable par la CI et suffisamment précis pour guider la correction sans inspection manuelle large.
12. **AC12 — Windows + PowerShell supportés** : les validations locales requises restent compatibles avec le workflow du dépôt.

## Tasks / Subtasks

- [x] Task 1: Formaliser le registre d’invariants sémantiques (AC1, AC10)
  - [x] Définir une source de vérité bornée des invariants critiques du pipeline.
  - [x] Séparer explicitement ce registre du manifeste purement structurel.
  - [x] Limiter ce registre aux invariants réellement documentés et gouvernés.

- [x] Task 2: Vérifier l’ordre doctrinal du prompt (AC2)
  - [x] Encoder l’ordre doctrinal attendu des transformations critiques.
  - [x] Ajouter une validation qui détecte une dérive de cet ordre.
  - [x] Produire des erreurs explicites pour les inversions, suppressions ou insertions non gouvernées.

- [x] Task 3: Vérifier la source de vérité runtime et la propagation critique (AC3, AC5)
  - [x] Contrôler la priorité runtime du snapshot actif.
  - [x] Vérifier la cohérence `AssemblyRegistry` / `ExecutionProfileRegistry` / runtime effectif.
  - [x] Vérifier la propagation des discriminants critiques documentés.

- [x] Task 4: Vérifier providers, familles, fallbacks et aliases (AC4, AC10)
  - [x] Détecter les nouveaux providers nominaux non gouvernés.
  - [x] Détecter les nouvelles familles supportées non documentées.
  - [x] Détecter les nouveaux fallbacks et aliases hors gouvernance.

- [x] Task 5: Construire les fixtures de sabotage volontaire (AC6, AC7, AC11)
  - [x] Créer des cas de sabotage ciblés par invariant.
  - [x] Vérifier que chaque sabotage produit une erreur stable et compréhensible.
  - [x] Séparer clairement ces cas des tests purement structurels.

- [x] Task 6: Intégrer le garde sémantique au flux de conformité existant (AC8, AC9, AC11)
  - [x] Brancher la validation sémantique au CLI et aux workflows existants.
  - [x] Vérifier l’absence de seconde commande concurrente.
  - [x] Mettre à jour la documentation canonique si un changement volontaire est introduit.

- [x] Task 7: Validation locale obligatoire
  - [x] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [x] Dans `backend/`, exécuter `ruff format .`.
  - [x] Dans `backend/`, exécuter `ruff check .`.
  - [x] Exécuter `pytest -q`.
  - [x] Exécuter au minimum les suites de conformité documentaire existantes et la nouvelle suite sémantique.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.41 complète 66.38/66.39 ; elle ne les remplace pas.
- L’objectif n’est pas de “comprendre tout le système”, mais de verrouiller quelques invariants d’architecture très critiques.
- Le garde doit être plus proche d’un contrat exécutable que d’un audit narratif.
- Les sabotages volontaires sont indispensables : sans eux, la story ne prouve pas que le garde attrape de vraies dérives.

### Ce que le dev ne doit pas faire

- Ne pas créer un moteur d’analyse du codebase entier.
- Ne pas ajouter une CLI parallèle de validation sémantique débranchée du flux doc ↔ code.
- Ne pas encoder des règles molles ou subjectives impossibles à stabiliser en CI.
- Ne pas dupliquer les invariants déjà présents dans le code sans borne ni maintenance réaliste.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py)
- [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py)
- [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.38** a créé le garde structurel doc ↔ code exécutable.
- **66.39** a rendu ce garde fiable sur les contextes Git/CI réels et plus explicable.
- La documentation runtime fixe désormais une chaîne canonique précise ; cette précision rend possible un garde sémantique borné.
- La suite logique est de protéger les invariants d’architecture qui, s’ils dérivent, rendraient la doc techniquement “à jour” en surface mais fausse sur le fond.

### Git Intelligence

Les commits récents autour de 66.38/66.39 montrent un pattern :

- une première livraison structurelle ;
- puis plusieurs durcissements ciblés sur les cas réels et les diagnostics.

Signal utile :

- 66.41 doit être pensée comme un hardening de second niveau ;
- les vrais risques sont les faux négatifs sémantiques, pas l’absence de structure.

### Testing Requirements

- Ajouter une suite de sabotage volontaire couvrant au minimum :
  - dérive d’ordre de transformation ;
  - dérive snapshot actif vs tables live ;
  - introduction d’un provider non gouverné ;
  - introduction d’une famille non gouvernée ;
  - réapparition d’un fallback ou alias non gouverné ;
  - perte de propagation d’un discriminant critique.
- Vérifier que les erreurs sont structurées et réutilisables en CI.
- Vérifier que le garde sémantique reste borné et n’échoue pas pour des changements non doctrinaux.

### Project Structure Notes

- Zone principale : `backend/app/llm_orchestration/`
- Le registre d’invariants sémantiques doit rester proche du validateur documentaire et du runtime, pas dans une couche éloignée purement documentaire.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/doc_conformity_manifest.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/doc_conformity_manifest.py)
- [backend/app/llm_orchestration/services/doc_conformity_validator.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/doc_conformity_validator.py)
- [backend/scripts/check_doc_conformity.py](/c:/dev/horoscope_front/backend/scripts/check_doc_conformity.py)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/assembly_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/assembly_registry.py)
- [backend/app/llm_orchestration/services/execution_profile_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/execution_profile_registry.py)
- [66-39-durcissement-fiabilite-multi-contexte-gate-conformite-documentaire.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-39-durcissement-fiabilite-multi-contexte-gate-conformite-documentaire.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Registre versionné `SEMANTIC_INVARIANTS_VERSION` + tuples d’ordre (gateway / assemble) dans `semantic_invariants_registry.py`.
- `SemanticConformityValidator` : ordre des transformations (`_resolve_plan`, `assemble_developer_prompt`) ; **AC3** : analyse AST — aucun `select` sur le modèle ORM « live » avant ou dans la branche `if snapshot:` ; présence d’un `select` sur ce modèle dans le `else` ; **AC4** : égalité stricte registre ↔ `SUPPORTED_FAMILIES`, `NOMINAL_SUPPORTED_PROVIDERS`, aliases legacy documentés, et noms `FallbackType` ; champs critiques sur `ResolvedExecutionPlan` / `ExecutionObservabilitySnapshot` ; marqueurs snapshot dans `log_call` (async).
- Intégration au script unique `check_doc_conformity.py` ; sortie JSON avec champs structurés par violation sémantique (`semantic_code`, `invariant_id`, `component`, `detail`, …) pour la CI.
- Tests d’intégration : sabotages ordre, snapshot (plusieurs formes), alignement gouvernance ; exécution verte sur l’arbre courant.
- Doc canonique : section registre sémantique (comportement détaillé) + bloc Date/SHA de vérification.

### File List

- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/66-41-validation-semantique-doc-code.md`
- `backend/app/llm_orchestration/doc_conformity_manifest.py`
- `backend/app/llm_orchestration/semantic_invariants_registry.py`
- `backend/app/llm_orchestration/services/semantic_conformity_validator.py`
- `backend/scripts/check_doc_conformity.py`
- `backend/tests/integration/test_story_66_41_semantic_conformity.py`
- `backend/tests/integration/test_story_66_39_doc_conformity_hardening.py`
- `docs/llm-prompt-generation-by-feature.md`

### Change Log

- 2026-04-14 : Implémentation du garde sémantique borné (registre + validateur + CLI + tests + doc + sprint status).
- 2026-04-14 : Durcissement revue — AC4 alignement explicite registre/code, AC3 contrôle AST snapshot/branches, JSON CI structuré pour les violations sémantiques ; stories 66-40 / 66-41 passées en done.
