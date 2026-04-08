---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
status: 'draft'
inputDocuments:
  - 'user-specification-inline'
  - '_bmad-output/planning-artifacts/architecture.md'
  - 'docs/architecture/llm-processus-architecture.md'
workflowType: 'epic'
epicNumber: 66
createdAt: '2026-04-06'
owner: Cyril
lastEdited: '2026-04-06'
editHistory:
  - date: '2026-04-06'
    changes: 'Création initiale — spécification fournie directement par Cyril, rédaction BMAD complète'
  - date: '2026-04-06'
    changes: 'Révision architecture — intégration de la migration natal vers une entrée applicative LLM canonique, clarification forte des responsabilités, suppression de la dépendance contractuelle aux dicts génériques'
---

# Epic 66 — Refactoriser l'orchestration LLM pour passer à une plateforme à contrats explicites, responsabilités nettes et point d'entrée applicatif unifié

**Status:** draft
**Créé le:** 2026-04-06
**Owner:** Cyril

---

## Objectif

Faire évoluer l'architecture actuelle d'orchestration LLM d'un système fonctionnel mais fortement basé sur des dictionnaires implicites, des fallbacks successifs, des conventions transverses et des points d'entrée hétérogènes, vers une plateforme à contrats explicites, typés, observables et gouvernés.

L'objectif n'est **pas** de changer le comportement produit visible pour l'utilisateur final, mais de fiabiliser la plateforme interne pour permettre :

- une meilleure maintenabilité ;
- une meilleure lisibilité des responsabilités ;
- une observabilité plus riche des chemins d'exécution ;
- une réduction forte de la dette liée aux conventions `user_input` / `context` ;
- une séparation plus nette entre couche métier, couche applicative LLM, gateway, validation et provider ;
- une évolution plus sûre des use cases `natal`, `chat`, `guidance` et futurs modules ;
- une convergence des parcours vers un **point d'entrée applicatif LLM unifié**, y compris pour `natal`.

---

## Décision d'architecture portée par cet epic

Cet epic acte explicitement la cible suivante :

- `natal`, `chat` et `guidance` ne doivent plus entrer dans la plateforme LLM par des chemins conceptuellement différents ;
- la couche aujourd'hui incarnée par `AIEngineAdapter` doit évoluer pour devenir un **point d'entrée applicatif canonique** pour les use cases LLM, ou être remplacée / renommée par une couche équivalente à responsabilité claire ;
- `natal` doit être migré vers cette couche d'entrée applicative unifiée **après clarification de son périmètre**, et non être “forcé” dans l'adapter actuel en conservant ses ambiguïtés ;
- les contrats cœur ne doivent plus reposer sur des `dict[str, Any]` comme mécanisme principal d'échange inter-couches.

En conséquence, cet epic couvre à la fois :

1. la refonte des contrats ;
2. la clarification des frontières de responsabilité ;
3. l'unification des points d'entrée applicatifs ;
4. la migration du parcours `natal` sur cette cible.

---

## Contexte

L'architecture actuelle présente de vraies qualités :

- séparation routeurs / services métier / gateway / provider ;
- use cases nommés ;
- prompt registry en base ;
- validation structurée ;
- repair automatique ;
- fallback use case ;
- gestion persona ;
- observabilité et métriques.

Mais l'analyse du code a mis en évidence plusieurs limites structurelles :

- Le moteur repose encore largement sur des `dict[str, Any]` enrichis par conventions implicites.
- `LLMGateway.execute()` concentre trop de responsabilités.
- `validate_output()` agit à la fois comme parseur, validateur, normalisateur et sanitizer.
- `CommonContextBuilder` injecte un contexte utile mais variable, sans qualification forte de son état.
- `AIEngineAdapter` mélange intégration technique, normalisation applicative et logique métier légère.
- `natal` contourne partiellement le chemin applicatif suivi par `chat` et `guidance`, ce qui crée une asymétrie structurelle.
- Les métadonnées d'exécution ne permettent pas encore de distinguer clairement un chemin nominal d'un chemin dégradé, réparé ou fallback.
- La plateforme est déjà quasi générique, mais ses contrats cœur ne sont pas encore au niveau de cette ambition.

---

## Problème à résoudre

Aujourd'hui, la plateforme fonctionne grâce à une intelligence distribuée dans plusieurs couches qui se compensent entre elles :

- l'adapter reformate et injecte certaines conventions ;
- le gateway orchestre, résout et rattrape ;
- le validator corrige partiellement ;
- le service natal remappe, désérialise et gère sa compatibilité locale ;
- le common context enrichit au mieux ;
- les types cœur encapsulent encore des `dict` plutôt que de vrais contrats métier.

Ce fonctionnement est efficace, mais trop dépendant de la carte mentale des développeurs.

Le risque principal n'est pas une casse immédiate, mais :

- une augmentation du coût de revue ;
- une dérive des conventions ;
- une difficulté croissante à introduire de nouveaux use cases ;
- une ambiguïté sur la vérité canonique d'une exécution ;
- une observabilité insuffisante des dégradations réelles ;
- une duplication ou un glissement progressif des responsabilités entre services métier, adapter et gateway ;
- une fragmentation durable entre le parcours `natal` et les autres parcours applicatifs LLM.

---

## Vision cible

La cible est une plateforme d'orchestration LLM structurée autour de six principes.

**1. Contrat d'entrée explicite et sans dict générique comme vérité canonique**
Chaque exécution repose sur un objet de requête typé et sur des sous-objets explicites. Les `dict` ne peuvent subsister qu'en compatibilité transitoire ou en payload métier borné, jamais comme contrat d'orchestration principal.

**2. Point d'entrée applicatif LLM unifié**
Tous les parcours applicatifs (`natal`, `chat`, `guidance`, futurs use cases) entrent dans la plateforme via une même couche applicative canonique, à responsabilité claire.

**3. Plan d'exécution résolu et immuable**
Après résolution config, persona, schéma, modèle et contexte commun, le système produit un artefact canonique décrivant exactement comment l'appel sera exécuté.

**4. Pipeline d'orchestration découpé**
Le gateway devient un orchestrateur d'étapes explicites au lieu d'un super-service central.

**5. Responsabilités strictement séparées**
La couche métier décide du besoin produit, la couche applicative LLM construit la requête canonique, le gateway orchestre, la validation valide/normalise de façon explicite, le provider exécute, le common context qualifie son état.

**6. Observabilité enrichie**
Chaque réponse expose le chemin d'exécution réel : nominal, réparé, fallback, contexte dégradé, test fallback, compat legacy, etc.

---

## Périmètre

### Inclus

- Refonte des modèles cœur d'orchestration.
- Introduction d'un contrat d'exécution explicite.
- Suppression de la dépendance architecturale aux `dict` comme contrat principal inter-couches.
- Découpage interne du gateway.
- Clarification des responsabilités service métier / entrée applicative LLM / gateway / validator / common context / provider.
- Transformation de la couche aujourd'hui portée par `AIEngineAdapter` en **entrée applicative canonique**.
- Migration de `natal` vers cette entrée applicative canonique.
- Enrichissement des métadonnées d'exécution.
- Conservation du comportement fonctionnel des use cases existants.
- Compatibilité avec `natal`, `chat_astrologer`, `guidance_daily`, `guidance_weekly`, `guidance_contextual`.

### Exclu

- Refonte UI.
- Changement des contenus métier des prompts.
- Redesign des schémas astrologiques métier eux-mêmes.
- Changement de provider.
- Suppression immédiate de tous les mécanismes legacy sans phase de transition.
- Refonte des modèles DB fonctionnels si elle n'est pas strictement nécessaire à la migration.

---

## Requirements Inventory

### Exigences Fonctionnelles (FR66)

**FR66-1 — Contrat d'exécution typé et explicite :**
Le système doit introduire un modèle de requête canonique pour toute exécution LLM, remplaçant la dépendance directe à des `dict` génériques comme contrat principal.

**FR66-2 — Contrats inter-couches sans `dict` implicite :**
Les échanges entre couche métier, entrée applicative LLM, gateway et validation doivent s'appuyer sur des modèles explicites. Les `dict` libres ne sont autorisés qu'aux frontières techniques ou pour des payloads métier strictement bornés et documentés.

**FR66-3 — Point d'entrée applicatif unifié :**
Le système doit exposer une entrée applicative canonique unique pour les use cases LLM, utilisée par `chat`, `guidance` et `natal`.

**FR66-4 — Plan d'exécution résolu :**
Le système doit produire un objet décrivant la configuration finale résolue avant l'appel provider, incluant au minimum : use case, modèle résolu, source de résolution du modèle, prompt version, schéma, persona résolue, stratégie d'interaction, flags spéciaux d'exécution et état du contexte.

**FR66-5 — Pipeline de gateway explicite :**
Le système doit découper l'exécution gateway en étapes logiques distinctes, testables séparément.

**FR66-6 — Qualification du common context :**
Le common context doit fournir non seulement des données, mais aussi des informations de qualification sur son état : source utilisée, champs absents, niveau de complétude, éventuelles dégradations.

**FR66-7 — Taxonomie claire de validation :**
La couche de validation doit distinguer explicitement : parsing JSON, validation de schéma, normalisation, sanitization, warnings de cohérence.

**FR66-8 — Métadonnées d'exécution enrichies :**
Le résultat gateway doit exposer une taxonomie plus précise du chemin d'exécution.

**FR66-9 — Migration du parcours natal vers la couche applicative canonique :**
Le parcours `natal` doit être migré vers la même entrée applicative LLM que les autres use cases, sans perte de ses spécificités métier.

**FR66-10 — Maintien de compatibilité fonctionnelle :**
Les parcours existants `natal`, `chat` et `guidance` doivent conserver leur comportement produit nominal pendant la refonte.

**FR66-11 — Réduction des conventions implicites :**
Les conventions historiques transportées dans `context` ou `user_input` doivent être progressivement remplacées par des champs explicites dans les modèles de requête, de contexte qualifié ou de plan résolu.

### Exigences Non-Fonctionnelles (NFR66)

**NFR66-1 — Rétrocompatibilité contrôlée :**
La refonte doit être introduite sans casser les use cases publiés existants.

**NFR66-2 — Testabilité :**
Chaque étape du pipeline et chaque contrat clé doit être unitairement testable indépendamment.

**NFR66-3 — Observabilité :**
Les logs, métriques et snapshots doivent permettre d'identifier précisément le chemin réel d'une exécution.

**NFR66-4 — Lisibilité architecture :**
La nouvelle architecture doit réduire les responsabilités implicites et faciliter la review.

**NFR66-5 — Extensibilité :**
La plateforme doit permettre l'ajout de nouveaux use cases avec moins de logique spéciale dispersée.

**NFR66-6 — Non-régression comportementale :**
Les différences introduites par la refonte doivent être mesurables, documentées et limitées aux changements techniques explicitement attendus.

### FR Coverage Map

| FR       | Stories couvrant cette exigence |
|----------|---------------------------------|
| FR66-1   | Stories 66.1, 66.2             |
| FR66-2   | Stories 66.1, 66.2, 66.6       |
| FR66-3   | Stories 66.3, 66.7             |
| FR66-4   | Story 66.2                     |
| FR66-5   | Story 66.4                     |
| FR66-6   | Story 66.5                     |
| FR66-7   | Story 66.5                     |
| FR66-8   | Story 66.6                     |
| FR66-9   | Story 66.7                     |
| FR66-10  | Story 66.7 et toutes           |
| FR66-11  | Stories 66.1 à 66.7            |
| NFR66-1  | Stories 66.1 à 66.7            |
| NFR66-2  | Stories 66.1, 66.2, 66.4, 66.5 |
| NFR66-3  | Story 66.6                     |
| NFR66-4  | Stories 66.3, 66.4, 66.5       |
| NFR66-5  | Stories 66.2, 66.3             |
| NFR66-6  | Story 66.7 et toutes           |

---

## Epic List

- [Story 66.1 — Introduire un contrat canonique `LLMExecutionRequest`](#story-661--introduire-un-contrat-canonique-llmexecutionrequest)
- [Story 66.2 — Introduire un `ResolvedExecutionPlan`](#story-662--introduire-un-resolvedexecutionplan)
- [Story 66.3 — Créer une entrée applicative LLM canonique](#story-663--créer-une-entrée-applicative-llm-canonique)
- [Story 66.4 — Refactoriser `LLMGateway.execute()` en pipeline](#story-664--refactoriser-llmgatewayexecute-en-pipeline)
- [Story 66.5 — Séparer validation, normalisation et sanitization](#story-665--séparer-validation-normalisation-et-sanitization)
- [Story 66.6 — Qualifier le common context et enrichir `GatewayMeta`](#story-666--qualifier-le-common-context-et-enrichir-gatewaymeta)
- [Story 66.7 — Migrer le parcours natal vers l'entrée applicative canonique](#story-667--migrer-le-parcours-natal-vers-lentrée-applicative-canonique)
- [Story 66.9 — Unifier la doctrine d'abonnement dans la couche LLM](#story-669--unifier-la-doctrine-dabonnement-dans-la-couche-llm)
- [Story 66.10 — Définir les bornes stylistiques de la persona astrologue](#story-6610--définir-les-bornes-stylistiques-de-la-persona-astrologue)
- [Story 66.11 — Introduire les ExecutionProfiles administrables](#story-6611--introduire-les-executionprofiles-administrables)

---

## Story 66.1 — Introduire un contrat canonique `LLMExecutionRequest`

**Statut :** draft

En tant que **plateforme d'orchestration**,
Je veux **un modèle d'entrée explicite pour les appels LLM**,
Afin de **remplacer les conventions diffuses transportées dans `user_input` et `context`**.

**Contexte technique :**
Actuellement, les appels au gateway transitent via des `dict[str, Any]` non typés. Les champs critiques (use case, langue, persona override, flags d'exécution, historique, mode d'interaction) sont transmis par convention implicite. Cette story introduit `LLMExecutionRequest` comme contrat canonique d'entrée, avec sous-objets explicites.

**Acceptance Criteria :**

**Given** qu'un service métier veut déclencher un appel LLM
**When** il construit la requête
**Then** il doit utiliser `LLMExecutionRequest`, modèle Pydantic contenant des champs explicites et des sous-objets nommés pour la requête utilisateur, le contexte conversationnel, le contexte de prompt, les flags d'exécution et les métadonnées runtime

**Given** que des champs critiques sont actuellement transmis comme chaînes libres
**When** `LLMExecutionRequest` est défini
**Then** les champs à valeur fermée utilisent des `Literal` / `Enum` partout où le domaine est fini (`interaction_mode`, `question_policy`, `execution_stage`, `locale_strategy` ou équivalent)

**Given** que l'architecture cible interdit les `dict` libres comme contrat principal
**When** `LLMExecutionRequest` est introduit
**Then** les seuls `dict` encore autorisés sont strictement bornés à des payloads métier documentés ou à des frontières techniques temporaires de compatibilité

**Given** que le gateway doit rester fonctionnel pendant la migration
**When** `LLMExecutionRequest` est introduit
**Then** un adaptateur de compatibilité temporaire permet aux appelants legacy de continuer à fonctionner sans modification immédiate

**Given** que le nouveau contrat est en place
**When** une requête est reçue
**Then** aucune étape du pipeline canonique ne dépend d'un accès libre à `context["..."]` ou `user_input["..."]` pour ses champs structurants

**Given** que des tests couvrent l'intégration
**When** les tests existants sont exécutés
**Then** aucun test de parcours `natal`, `chat`, `guidance` n'est en échec

---

## Story 66.2 — Introduire un `ResolvedExecutionPlan`

**Statut :** draft

En tant que **moteur d'orchestration**,
Je veux **matérialiser la config finale réellement résolue avant exécution**,
Afin d'**avoir une vérité canonique de ce qui va être exécuté**.

**Contexte technique :**
Actuellement, modèle, prompt, persona, schéma, stratégie d'interaction et certaines options runtime sont résolus en plusieurs endroits dispersés. Cette story crée `ResolvedExecutionPlan` qui capte cet état une fois pour toutes avant l'appel provider.

**Acceptance Criteria :**

**Given** que le gateway reçoit une requête d'exécution
**When** la phase de résolution est terminée
**Then** un objet `ResolvedExecutionPlan` est produit, contenant au minimum : modèle résolu, source de résolution du modèle, version du prompt, schéma sélectionné, persona résolue, stratégie d'interaction, paramètres provider, état du contexte qualifié, flags d'exécution actifs et origine éventuelle d'un mode dégradé

**Given** que le plan est produit avant l'appel provider
**When** le plan est loggé
**Then** il est sérialisable en JSON et lisible en log structuré

**Given** que le gateway utilise le plan
**When** l'appel provider est effectué
**Then** le gateway exploite les valeurs du plan sans recalcul dispersé dans les étapes suivantes

**Given** qu'un nouveau use case doit être ajouté
**When** la résolution est effectuée
**Then** le `ResolvedExecutionPlan` s'applique sans logique spéciale additionnelle dans le gateway hors extension explicite du résolveur

---

## Story 66.3 — Créer une entrée applicative LLM canonique

**Statut :** draft

En tant qu'**architecte backend**,
Je veux **une couche applicative LLM unique et clairement bornée**,
Afin d'**unifier l'entrée de `chat`, `guidance` et `natal` dans la plateforme**.

**Contexte technique :**
Aujourd'hui, `chat` et `guidance` passent par `AIEngineAdapter`, alors que `natal` appelle plus directement le gateway. Cette asymétrie favorise la dérive des conventions et la duplication. La cible est de transformer la couche actuelle en entrée applicative canonique, ou d'introduire un composant équivalent mieux nommé et mieux borné.

**Acceptance Criteria :**

**Given** que plusieurs parcours utilisent la plateforme LLM
**When** l'architecture cible est mise en place
**Then** une seule couche applicative canonique est responsable de recevoir les demandes métier et de construire `LLMExecutionRequest`

**Given** que `AIEngineAdapter` a aujourd'hui un périmètre ambigu
**When** la story est réalisée
**Then** son rôle est clarifié par refactorisation, renommage ou remplacement, avec documentation explicite de ce qu'il fait et ne fait pas

**Given** que la séparation des responsabilités doit être renforcée
**When** la couche applicative LLM est définie
**Then** elle ne porte ni logique provider, ni logique de validation de sortie, ni logique métier profonde propre à un domaine

**Given** que `chat` et `guidance` utilisent déjà cette couche
**When** la refonte est appliquée
**Then** ils continuent de fonctionner sans régression nominale

**Given** que `natal` doit rejoindre cette cible
**When** sa migration sera réalisée ultérieurement
**Then** aucun contournement direct du gateway par des conventions parallèles n'est requis

---

## Story 66.4 — Refactoriser `LLMGateway.execute()` en pipeline

**Statut :** draft

En tant que **développeur backend**,
Je veux **découper le gateway en étapes explicites**,
Afin de **réduire l'effet "god orchestrator"**.

**Contexte technique :**
`LLMGateway.execute()` orchestre actuellement la résolution, l'appel provider, la validation, le repair et le fallback dans un bloc dense. Cette story le découpe en méthodes/étapes logiques séparées avec des responsabilités claires, opérant sur `LLMExecutionRequest` et `ResolvedExecutionPlan`.

**Acceptance Criteria :**

**Given** que l'exécution gateway doit être lisible
**When** le refactoring est appliqué
**Then** l'exécution est structurée en étapes distinctes et nommées, par exemple : `resolve_plan`, `build_messages`, `call_provider`, `validate_and_normalize`, `handle_repair_or_fallback`, `finalize_result`

**Given** que chaque étape a une responsabilité unique
**When** une étape est testée
**Then** elle peut être testée unitairement sans exécuter les autres étapes

**Given** que la logique fonctionnelle est conservée
**When** les parcours `natal`, `chat`, `guidance` sont exécutés après refactoring
**Then** les résultats restent nominalement équivalents à l'état pré-refactoring

**Given** qu'un échec survient dans une étape
**When** l'erreur est remontée
**Then** elle est associée à l'étape qui l'a produite dans les logs et métriques

**Given** que les contrats sont explicites
**When** une étape consomme ou produit une donnée structurante
**Then** elle le fait via des modèles typés et non via des `dict` libres

---

## Story 66.5 — Séparer validation, normalisation et sanitization

**Statut :** draft

En tant que **plateforme LLM**,
Je veux **que la sortie soit traitée par une chaîne explicite de validation**,
Afin de **rendre visibles les transformations réellement appliquées**.

**Contexte technique :**
`validate_output()` agit actuellement comme une boîte noire multi-rôles : parsing JSON, validation de schéma, normalisation des champs, sanitization des valeurs legacy, warnings de cohérence. Cette story structure ces étapes explicitement.

**Acceptance Criteria :**

**Given** qu'une réponse LLM doit être traitée
**When** la chaîne de traitement est appliquée
**Then** les étapes sont distinctes et appelées séquentiellement : `parse_json` → `validate_schema` → `normalize_fields` → `sanitize_legacy` → `collect_warnings`

**Given** qu'une transformation est appliquée
**When** la réponse est construite
**Then** les normalisations et sanitizations appliquées sont listées dans un artefact structuré exploitable par `GatewayMeta`

**Given** qu'une erreur de parsing survient
**When** l'erreur est remontée
**Then** elle est catégorisée comme erreur de parsing et non confondue avec une erreur de schéma

**Given** que des warnings de cohérence sont détectés
**When** la réponse est produite
**Then** ils sont exposés dans un champ structuré, sans bloquer la réponse sauf politique contraire explicite

**Given** que la chaîne de validation est refactorisée
**When** elle échange des données avec le gateway
**Then** elle consomme et retourne des modèles typés et non des structures libres non documentées

---

## Story 66.6 — Qualifier le common context et enrichir `GatewayMeta`

**Statut :** draft

En tant que **moteur de prompts et équipe de suivi technique**,
Je veux **connaître l'état exact du contexte injecté et du chemin d'exécution réellement suivi**,
Afin de **distinguer un contexte complet d'un contexte dégradé et d'observer correctement le système**.

**Contexte technique :**
`CommonContextBuilder` retourne actuellement un payload "best effort" sans indiquer quels champs sont absents, quelle source a été utilisée, ni si le contexte est complet ou partiel. `GatewayMeta` n'exprime pas encore suffisamment le chemin réel d'exécution.

**Acceptance Criteria :**

**Given** que le builder construit le contexte commun
**When** il retourne son résultat
**Then** il retourne un objet `QualifiedContext` contenant au minimum : payload, source utilisée, liste des champs absents, niveau de complétude, dégradations détectées et indicateur de fiabilité/contextual completeness

**Given** que des champs importants sont absents
**When** le gateway reçoit le `QualifiedContext`
**Then** les absences sont signalées dans les logs avec niveau approprié et répercutées dans les métadonnées d'exécution

**Given** qu'une réponse gateway est produite
**When** les métadonnées sont construites
**Then** `GatewayMeta` inclut des champs explicites de type `execution_path`, `context_quality`, `missing_context_fields`, `normalization_applied`, `repair_attempts`, `fallback_reason` ou équivalent

**Given** qu'un repair ou un fallback a été effectué
**When** les metas sont exposées
**Then** le chemin réel est identifiable sans interprétation implicite des anciens champs booléens seuls

**Given** que des consommateurs existants lisent déjà `GatewayMeta`
**When** les nouveaux champs sont ajoutés
**Then** l'extension reste non-breaking pour les champs historiques

---

## Story 66.7 — Migrer le parcours natal vers l'entrée applicative canonique

**Statut :** draft

En tant que **domaine natal**,
Je veux **bénéficier du point d'entrée applicatif LLM unifié et des nouveaux contrats de plateforme**,
Afin de **réduire la dette locale tout en conservant les exigences fonctionnelles du domaine**.

**Contexte technique :**
`NatalInterpretationServiceV2` contient actuellement de la logique de remapping, désérialisation et gestion de conventions qui doublonnent ou contournent partiellement la logique de plateforme. La cible n'est pas de faire “rentrer natal dans l'adapter actuel” tel quel, mais de migrer `natal` vers la couche applicative LLM canonique définie par la story 66.3.

**Acceptance Criteria :**

**Given** que le service natal déclenche un appel LLM
**When** il construit sa requête
**Then** il passe par la même entrée applicative canonique que `chat` et `guidance`, en fournissant un `LLMExecutionRequest` et des sous-objets typés adaptés à ses besoins métier

**Given** que `natal` a des spécificités fortes
**When** il est migré
**Then** ses responsabilités métier légitimes sont conservées, notamment le choix de use case, la gestion du cache métier, la persistance et le mapping final de ses schémas métier

**Given** que la séparation des responsabilités doit être améliorée
**When** la migration est faite
**Then** `NatalInterpretationServiceV2` ne reconstruit plus de conventions d'orchestration parallèles qui devraient relever de la plateforme

**Given** que le résultat gateway est reçu
**When** le service natal le traite
**Then** il consomme `GatewayMeta` enrichi et les contrats typés sans parsing manuel de conventions legacy

**Given** que le cache natal est actif
**When** une réponse est récupérée depuis le cache
**Then** le cache reste opérationnel et cohérent avec les nouvelles structures et avec une fingerprint d'exécution suffisamment explicite pour éviter des réutilisations ambiguës

**Given** que la persistance natal est active
**When** une interprétation est sauvegardée
**Then** la persistance continue de fonctionner sans modification DB non nécessaire

**Given** qu'un utilisateur demande son thème natal
**When** l'appel est traité avec les nouveaux contrats
**Then** aucun comportement nominal visible pour l'utilisateur n'est dégradé par rapport à l'état pré-migration

---

## Dépendances

| Module / Zone | Rôle dans cet epic |
|---------------|--------------------|
| Modèles LLM orchestration | Nouveaux contrats `LLMExecutionRequest`, `ResolvedExecutionPlan`, `QualifiedContext` |
| Couche applicative LLM (actuel `AIEngineAdapter` ou successeur) | Point d'entrée canonique — stories 66.3 et 66.7 |
| `LLMGateway` | Refactorisation centrale — story 66.4 |
| `OutputValidator` | Pipeline validation — story 66.5 |
| `CommonContextBuilder` | Qualification context — story 66.6 |
| `GatewayMeta` | Enrichissement métadonnées — story 66.6 |
| `NatalInterpretationServiceV2` | Migration use case — story 66.7 |
| Observability layer | Consommateur des nouvelles metas |
| Tests d'intégration (chat / guidance / natal) | Garde-fou de non-régression — toutes stories |

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Régression silencieuse sur les chemins de fallback ou repair | Moyenne | Élevé | Tests dédiés aux chemins dégradés avant et après chaque story |
| Casse partielle sur use cases historiques si conventions legacy non identifiées | Moyenne | Élevé | Audit exhaustif des conventions implicites en amont de 66.1 |
| Surcharge temporaire de complexité pendant la phase hybride | Haute | Moyen | Adaptateur de compatibilité legacy + suppression différée |
| Effet domino sur les tests d'intégration | Moyenne | Moyen | Exécution systématique des tests d'intégration à chaque story |
| Mauvais découpage si frontière plateforme / applicatif / métier non figée | Moyenne | Élevé | Validation explicite de ces frontières avant 66.3 puis revue avant 66.7 |
| Migration natal trop “mécanique” vers l'adapter actuel | Moyenne | Élevé | D'abord clarifier / redéfinir la couche applicative canonique, puis migrer natal |

---

## Stratégie de delivery

Refonte **incrémentale**, en conservant une couche de compatibilité temporaire.

**Ordre recommandé :**

1. **Story 66.1** — `LLMExecutionRequest` et contrats d'entrée
2. **Story 66.2** — `ResolvedExecutionPlan`
3. **Story 66.3** — Couche applicative LLM canonique
4. **Story 66.4** — Pipeline gateway découpé
5. **Story 66.5** — Validation structurée en étapes
6. **Story 66.6** — Common context qualifié + `GatewayMeta` enrichi
7. **Story 66.7** — Migration use case natal
8. *(Post-epic)* Nettoyage final legacy et durcissement observabilité transverse

Chaque story doit :

- passer les tests d'intégration existants (`natal` / `chat` / `guidance`) sans régression ;
- ne pas supprimer les mécanismes legacy avant que tous leurs appelants soient migrés ;
- documenter les conventions remplacées dans la PR ;
- expliciter la frontière de responsabilité modifiée par la story.

---

## Résultat attendu

À la fin de l'epic :

- tout appel à la plateforme LLM passe par un contrat d'exécution explicite ;
- la dépendance aux `dict` libres comme contrat principal d'orchestration a disparu ;
- la couche applicative LLM constitue un point d'entrée canonique unique ;
- `natal`, `chat` et `guidance` convergent vers cette même entrée ;
- la config réellement résolue est matérialisée par un objet dédié (`ResolvedExecutionPlan`) ;
- le pipeline du gateway est découpé en étapes lisibles et testables ;
- la validation distingue clairement parse / validation de schéma / normalisation / sanitization ;
- le common context retourne un contexte qualifié, pas seulement un payload "best effort" ;
- les métadonnées permettent de comprendre précisément le chemin pris par chaque réponse ;
- les services métier conservent leurs responsabilités produit sans porter de conventions d'orchestration parallèles.

---

## Définition of Done

L'epic sera considéré comme terminé lorsque :

- [ ] Les nouveaux modèles cœur (`LLMExecutionRequest`, `ResolvedExecutionPlan`, `QualifiedContext` ou équivalent) sont en place.
- [ ] Les contrats inter-couches structurants n'utilisent plus de `dict` libres comme vérité canonique.
- [ ] Une couche applicative LLM canonique clairement documentée est en place.
- [ ] Le gateway est découpé en pipeline explicite avec étapes nommées.
- [ ] `GatewayMeta` expose le chemin d'exécution réel et la qualité du contexte.
- [ ] Le common context retourne un contexte qualifié.
- [ ] La validation est structurée en étapes explicites.
- [ ] `natal`, `chat` et `guidance` fonctionnent sans régression nominale via la nouvelle architecture cible.
- [ ] Les conventions legacy majeures ont été remplacées ou encapsulées dans des adaptateurs temporaires.
- [ ] Les tests unitaires couvrent chaque étape du pipeline séparément.
- [ ] La documentation d'architecture (`docs/architecture/llm-processus-architecture.md`) est mise à jour.
- [ ] La doctrine d'abonnement (Story 66.9) est appliquée aux use cases éligibles.
- [ ] Les bornes stylistiques de la persona (Story 66.10) sont encodées et validées.
- [ ] Les profils d'exécution (`ExecutionProfile`) sont administrables et décorrélés du prompt (Story 66.11).

---

## Story 66.11 — Introduire les ExecutionProfiles administrables

**Statut :** draft

En tant qu'**administrateur plateforme**,
Je veux **piloter les paramètres d'exécution moteur (provider, modèle, profils reasoning/verbosité) de façon centralisée**,
Afin de **découpler les choix techniques de moteur du texte des prompts et de permettre des changements rapides sans modification de code**.

**Acceptance Criteria :**

**Given** la table `llm_execution_profiles`
**When** une exécution LLM est lancée pour une feature/plan donnée
**Then** le pipeline résout automatiquement le profil le plus spécifique via une cascade (waterfall) : `feature+subfeature+plan` > `feature+subfeature` > `feature`

**Given** un profil d'exécution configuré
**When** résolu par le gateway
**Then** les abstractions internes (`reasoning_profile`, `verbosity_profile`, etc.) sont traduites en paramètres spécifiques au provider (ex: `reasoning_effort` pour OpenAI) via un `ProviderParameterMapper`

**Given** une configuration assembly (`PromptAssemblyConfig`)
**When** elle contient une référence `execution_profile_ref`
**Then** ce profil est prioritaire sur la cascade automatique

**Given** les logs d'exécution (`GatewayMeta`)
**When** un profil d'exécution est appliqué
**Then** son ID, sa source et les paramètres traduits sont explicitement tracés dans la télémétrie

---

## Story 66.10 — Définir les bornes stylistiques de la persona astrologue

**Statut :** draft

En tant qu'**architecte plateforme**,
Je veux **définir et encoder explicitement les dimensions que la persona astrologue peut modifier**,
Afin de **garantir que la persona reste une couche purement stylistique et n'interfère pas avec la logique métier ou la sécurité**.

**Acceptance Criteria :**

**Given** la politique `PersonaBoundaryPolicy`
**When** un bloc persona est composé (via `PersonaComposer`)
**Then** une validation détecte les tentatives de redéfinition de dimensions interdites (ex: schéma JSON, hard policy, choix du modèle)

**Given** l'interface d'administration des personas
**When** une modification est enregistrée
**Then** les violations de bornes sont immédiatement signalées par un avertissement

**Given** une exécution LLM
**When** un bloc persona contient une violation
**Then** un avertissement est loggué dans le backend sans bloquer l'exécution (sauf pour les violations critiques type "bypass security")

**Given** la documentation d'architecture
**When** consultée
**Then** elle liste clairement les dimensions autorisées (ton, vocabulaire, etc.) et interdites

---

## Story 66.9 — Unifier la doctrine d'abonnement dans la couche LLM

**Statut :** draft

En tant qu'**architecte plateforme**,
Je veux **unifier la doctrine de gestion des plans (free/premium) dans la couche LLM**,
Afin de **limiter la duplication de use cases et de favoriser l'usage de l'assembly**.

**Contexte technique :**
Actuellement, certaines variations liées à l'abonnement sont gérées par des use cases distincts (`_free`/`_full`), ce qui multiplie les prompts à maintenir en base. La nouvelle doctrine impose de passer par `plan_rules` dans `PromptAssemblyConfig` quand le contrat de sortie est identique.

**Acceptance Criteria :**

**Given** la doctrine d'abonnement `entitlements > plan assembly > use_case distinct`
**When** un use case est analysé pour migration
**Then** il est migré vers un `plan` assembly si son schéma JSON de sortie est identique à sa variante, sinon il reste un use case distinct

**Given** les use cases `horoscope_daily_free` et `horoscope_daily_full`
**When** ils sont migrés
**Then** ils utilisent la feature `horoscope_daily` avec les plans `free` et `premium`, et les anciens use cases sont marqués `deprecated`

**Given** le gateway LLM
**When** un use case déprécié est appelé
**Then** il est automatiquement redirigé vers la feature et le plan correspondants via un mapping de compatibilité, avec un avertissement dans les logs

**Given** une nouvelle version de prompt publiée
**When** le suffixe `_free` ou `_full` est détecté
**Then** un avertissement de nommage est émis si aucune différence de schéma n'est justifiée

---

## Bénéfices attendus

- Baisse de la dette de conventions implicites.
- Meilleure lisibilité des exécutions LLM.
- Réduction du risque d'érosion architecturelle.
- Meilleure capacité à onboarder de nouveaux développeurs.
- Base plus saine pour ajouter de nouveaux use cases ou providers.
- Alignement structurel entre `natal`, `chat` et `guidance`.
- Meilleure gouvernance de la plateforme LLM.
