---
stepsCompleted:
  - 1
  - 2
  - 3
inputDocuments:
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\architecture.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\ux-design-specification.md'
  - 'C:\dev\horoscope_front\docs\llm-prompt-generation-by-feature.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\66-45-vue-catalogue-canonique-prompts-actifs.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\66-46-vue-detail-resolved-prompt-assembly.md'
lastEdited: '2026-04-16'
editHistory:
  - date: '2026-04-16'
    changes: 'Creation du backlog BMAD dedie a la refonte admin LLM preview runtime et execution'
---

# horoscope_front - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for horoscope_front, focused on the admin LLM prompt inspection, runtime preview, sample payload management, and controlled live execution workflow.

## Requirements Inventory

### Functional Requirements

FR1: L’admin peut consulter un catalogue canonique des configurations LLM gouverné par `feature/subfeature/plan/locale` et identifié par `manifest_entry_id`.
FR2: L’admin peut distinguer explicitement la source de vérité d’une cible canonique entre `active_snapshot` et `live_table_fallback`.
FR3: L’admin peut ouvrir une vue détaillée d’une cible et inspecter séparément les sources de composition, le pipeline de transformation et le résultat résolu.
FR4: L’admin peut comprendre quels placeholders et quelles données runtime sont nécessaires pour rendre un prompt exécutable.
FR5: L’admin peut visualiser un prompt rendu avec un jeu de données d’exemple sans dépendre de données personnelles réelles d’utilisateur.
FR6: L’admin peut déclencher volontairement une exécution LLM à partir d’un prompt rendu en mode contrôle, puis consulter le retour brut et structuré.
FR7: L’admin peut gérer ou sélectionner des jeux de données d’exemple réutilisables pour prévisualiser les prompts par feature.
FR8: L’admin peut distinguer clairement les modes `assembly preview`, `runtime preview` et `live execution` sans ambiguïté sémantique.
FR9: L’admin peut vérifier que la chaîne complète `hard policy -> assembly -> injecteurs -> rendu -> paramètres provider -> réponse LLM` est fonctionnelle et lisible depuis une seule surface.

### NonFunctional Requirements

NFR1: La page admin doit rester en lecture déterministe et sans appel provider tant qu’aucune exécution explicite n’est déclenchée.
NFR2: Les données sensibles et placeholders non sûrs doivent rester redacted selon la politique admin existante.
NFR3: Les interactions critiques de la page admin doivent afficher un feedback visible rapidement et distinguer clairement chargement, vide, erreur, preview incomplète et exécution.
NFR4: L’exécution LLM manuelle doit respecter les garde-fous runtime existants: timeout, retries contrôlés, erreurs explicites et observabilité corrélée.
NFR5: Les vues principales doivent rester utilisables desktop/mobile sans style inline et avec cohérence CSS existante.
NFR6: Les surfaces critiques de preview/exécution admin doivent rester testables automatiquement côté backend et frontend.
NFR7: Le vocabulaire UI doit éviter les libellés trompeurs comme un faux “prompt final” lorsqu’il s’agit d’une preview incomplète ou d’un rendu best-effort.

### Additional Requirements

- La clé nominale de toutes les vues doit rester `manifest_entry_id`; `use_case` reste au mieux une information de compatibilité.
- La résolution doit continuer à réutiliser la logique canonique existante du gateway et ne jamais recréer une chaîne parallèle spécifique à l’admin.
- Les sample payloads doivent alimenter les placeholders runtime comme `chart_json`, sans détourner l’usage réel des données utilisateur.
- La preview et l’exécution doivent être séparées par des endpoints et des états UI distincts.
- Toute exécution admin doit être corrélée avec les métadonnées runtime existantes: modèle, provider, paramètres résolus, request/correlation id, snapshot si applicable.
- La solution doit réutiliser les services existants de rendering, injecteurs, redaction et observabilité.
- Les jeux de données d’exemple doivent être bornés par feature/locale et ne pas devenir un stockage fourre-tout de faux comptes utilisateurs.

### UX Design Requirements

UX-DR1: La page doit être structurée en zones lisibles et stables, au minimum `construction logique`, `prompts`, `données d’exemple`, `retour LLM`.
UX-DR2: Une visualisation de pipeline type graphe doit montrer l’ordre logique des couches et l’origine des données nécessaires.
UX-DR3: Les placeholders doivent être affichés avec un statut compréhensible métier, par exemple `résolu`, `attendu en preview`, `fallback`, `bloquant en exécution`.
UX-DR4: L’UI doit proposer un mode de preview avec sample data clairement distinct du mode exécution réelle.
UX-DR5: Les formulaires de sample data doivent être guidés, contextualisés par feature et conçus pour limiter les erreurs de saisie.
UX-DR6: La réponse LLM affichée après exécution doit être lisible en double format: réponse brute et réponse structurée/interprétée si applicable.

### FR Coverage Map

FR1: Epic 67 - catalogue canonique et lecture par `manifest_entry_id`
FR2: Epic 67 - distinction `active_snapshot` / `live_table_fallback`
FR3: Epic 67 - vue structurée sources / pipeline / résultat
FR4: Epic 67 / Epic 68 - compréhension des placeholders requis puis résolution via sample data
FR5: Epic 68 - rendu réaliste avec données d’exemple
FR6: Epic 69 - exécution LLM manuelle et inspection du retour
FR7: Epic 68 - gestion et sélection de jeux de données d’exemple
FR8: Epic 67 / Epic 68 / Epic 69 - séparation claire preview assembly / runtime preview / live execution
FR9: Epic 67 / Epic 68 / Epic 69 - lisibilité et vérification bout-en-bout de la chaîne runtime

## Epic List

### Epic 67: Comprendre la construction logique d’un prompt canonique
Permettre à un admin de lire visuellement comment une cible canonique LLM est construite, quelles briques composent le prompt, et quelles données runtime sont nécessaires pour le rendre exécutable.
**FRs covered:** FR1, FR2, FR3, FR4, FR8, FR9

### Epic 68: Prévisualiser un prompt avec des données d’exemple réutilisables
Permettre à un admin de sélectionner ou gérer des jeux de données d’exemple par feature afin d’obtenir une preview réaliste et exécutable du prompt, sans dépendre de données personnelles réelles.
**FRs covered:** FR4, FR5, FR7, FR8, FR9

### Epic 69: Déclencher une exécution contrôlée et inspecter le retour LLM
Permettre à un admin de lancer explicitement une exécution LLM depuis la surface de contrôle, puis de consulter le prompt effectivement envoyé, les paramètres provider, la réponse brute, la réponse structurée et les métadonnées d’exécution.
**FRs covered:** FR6, FR8, FR9

## Epic 67: Comprendre la construction logique d’un prompt canonique

Permettre à un admin de lire visuellement comment une cible canonique LLM est construite, quelles briques composent le prompt, et quelles données runtime sont nécessaires pour le rendre exécutable.

### Story 67.1: Clarifier les modes de preview et les statuts de placeholders

As an admin ops / LLM operator,
I want que la vue detail distingue explicitement `assembly preview`, `runtime preview` et `live execution`,
So that je ne confonde plus une preview statique incomplète avec une erreur fonctionnelle.

**Acceptance Criteria:**

**Given** une cible canonique ouverte dans la vue detail
**When** aucun jeu de données runtime n’est fourni
**Then** l’UI affiche un mode explicite `assembly preview`
**And** les placeholders runtime attendus ne sont pas présentés comme une panne d’exécution.

**Given** un placeholder requis seulement pour l’exécution runtime
**When** il est absent en mode preview statique
**Then** son statut est affiché avec un libellé du type `expected_missing_in_preview` ou équivalent stable
**And** il n’est plus assimilé à un `render_error` bloquant sans contexte.

**Given** un placeholder reste réellement bloquant pour un rendu runtime
**When** un sample payload est utilisé mais reste incomplet
**Then** le backend renvoie un statut explicitement bloquant pour la runtime preview
**And** l’UI distingue clairement ce cas de l’absence attendue en preview statique.

**Given** la vue detail affiche les étapes du pipeline
**When** un prompt n’est pas entièrement rendu
**Then** le libellé de la zone correspondante évite le terme ambigu `prompt final`
**And** utilise un vocabulaire stable du type `best-effort rendered prompt` ou `runtime rendered prompt`.

### Story 67.2: Exposer la construction logique sous forme de graphe inspectable

As an admin ops / prompt designer,
I want voir la chaîne logique de composition d’une cible canonique sous forme de graphe,
So that je comprenne immédiatement quelles briques et quelles données alimentent le prompt.

**Acceptance Criteria:**

**Given** une cible canonique ouverte dans la vue detail
**When** la page charge correctement
**Then** une section `Construction logique` affiche un graphe de pipeline
**And** le graphe relie au minimum `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider messages` et `runtime inputs`.

**Given** une cible avec templates, policy, execution profile et placeholders
**When** le graphe est généré
**Then** il visualise les couches `feature template`, `subfeature template`, `plan rules`, `persona block`, `hard policy`, `execution profile`
**And** il montre où interviennent les placeholders runtime.

**Given** des placeholders de plusieurs natures existent
**When** le graphe est affiché
**Then** il distingue les entrées issues du système, des fallbacks de registre et des sample payloads
**And** la légende reste compréhensible sans lecture du code.

**Given** la page est utilisée en desktop ou mobile
**When** l’espace disponible varie
**Then** le graphe reste lisible via scroll horizontal, réduction contrôlée ou rendu textuel alternatif
**And** aucun style inline n’est introduit.

### Story 67.3: Refondre la vue detail en zones pédagogiques et opérables

As an admin ops / release operator,
I want une vue detail structurée en zones distinctes et lisibles,
So that je puisse comprendre rapidement le prompt sans parser un JSON brut.

**Acceptance Criteria:**

**Given** la vue detail d’une cible canonique
**When** elle s’affiche
**Then** elle est organisée au minimum en `Construction logique`, `Prompts`, `Données d’exemple`, `Retour LLM`
**And** l’ordre suit la progression réelle preview puis exécution.

**Given** la zone `Prompts`
**When** l’admin la consulte
**Then** elle sépare `assembled prompt`, `post injectors prompt`, `rendered prompt`, `system hard policy`, `developer content`, `persona block`
**And** chaque bloc porte un titre explicite.

**Given** la zone placeholders
**When** l’admin la consulte
**Then** chaque placeholder affiche son nom, son statut, sa source de résolution, sa classification et son niveau de redaction
**And** les valeurs non sûres restent masquées.

**Given** un état vide, une erreur de chargement ou une preview partielle
**When** la page l’affiche
**Then** chaque état a un message de premier rang compréhensible
**And** ne réutilise pas un message d’erreur d’exécution LLM pour une simple absence de données runtime.

## Epic 68: Prévisualiser un prompt avec des données d’exemple réutilisables

Permettre à un admin de sélectionner ou gérer des jeux de données d’exemple par feature afin d’obtenir une preview réaliste et exécutable du prompt, sans dépendre de données personnelles réelles.

### Story 68.1: Définir le modèle admin des sample payloads par feature

As an admin platform operator,
I want disposer d’un modèle de `sample payload` réutilisable par feature et locale,
So that je puisse prévisualiser les prompts avec des données runtime réalistes mais non sensibles.

**Acceptance Criteria:**

**Given** le besoin de prévisualiser plusieurs features LLM
**When** un sample payload est créé
**Then** il porte au minimum un `name`, une `feature`, une `locale`, un `payload_json`, une `description` et un statut d’activation
**And** il peut être ciblé sans créer un faux compte utilisateur complet.

**Given** un sample payload pour `natal`
**When** il est enregistré
**Then** il peut contenir `chart_json` et tout autre placeholder runtime requis par la feature
**And** sa validation vérifie la cohérence minimale du JSON fourni.

**Given** plusieurs sample payloads existent
**When** l’admin consulte la liste
**Then** il peut filtrer par `feature` et `locale`
**And** identifier clairement lequel est par défaut ou recommandé.

**Given** des données d’exemple sont stockées
**When** elles sont affichées ou journalisées côté admin
**Then** elles respectent les règles de redaction et de non-sensibilité déjà en vigueur
**And** ne contiennent pas de secrets ni de données personnelles réelles.

### Story 68.2: Rendre la runtime preview avec un sample payload sélectionné

As an admin ops / prompt reviewer,
I want sélectionner un sample payload et obtenir un vrai rendu runtime du prompt,
So that je voie exactement ce qui serait envoyé au provider sans exécuter encore le LLM.

**Acceptance Criteria:**

**Given** une cible canonique ouverte dans la vue detail
**When** l’admin sélectionne un sample payload compatible
**Then** la page bascule en mode `runtime preview`
**And** affiche le prompt rendu avec les placeholders effectivement résolus.

**Given** un sample payload incomplet
**When** la runtime preview est demandée
**Then** le backend renvoie la liste des placeholders encore manquants
**And** l’UI les présente comme bloquants pour la preview runtime.

**Given** un sample payload complet
**When** la runtime preview est calculée
**Then** la page montre clairement les valeurs résolues par `runtime_context`, `fallback` ou `sample payload`
**And** les métadonnées de rendu restent séparées des messages provider.

**Given** la runtime preview ne doit pas exécuter le LLM
**When** elle est demandée
**Then** aucun appel provider n’est lancé
**And** le rendu reste déterministe à partir des services internes de composition et de rendering.

### Story 68.3: Permettre la gestion admin des sample payloads depuis la surface de contrôle

As an admin platform operator,
I want créer, modifier, dupliquer et supprimer des sample payloads depuis l’interface admin,
So that la preview runtime soit maintenable sans passage par la base ou des fixtures cachées.

**Acceptance Criteria:**

**Given** la zone `Données d’exemple` de la page admin
**When** l’admin veut préparer une nouvelle preview
**Then** il peut créer un sample payload depuis l’UI avec validation guidée.

**Given** un sample payload existant
**When** l’admin veut le réutiliser pour une variante
**Then** il peut le dupliquer puis le modifier sans écraser l’original.

**Given** un sample payload obsolète
**When** l’admin le supprime ou le désactive
**Then** il disparaît des sélections actives
**And** l’action reste traçable côté audit admin si une telle journalisation existe déjà pour cette surface.

**Given** une feature donnée
**When** plusieurs samples sont disponibles
**Then** l’UI propose un sample par défaut ou recommandé
**And** garde une navigation simple sans noyer l’admin dans des payloads non pertinents.

## Epic 69: Déclencher une exécution contrôlée et inspecter le retour LLM

Permettre à un admin de lancer explicitement une exécution LLM depuis la surface de contrôle, puis de consulter le prompt effectivement envoyé, les paramètres provider, la réponse brute, la réponse structurée et les métadonnées d’exécution.

### Story 69.1: Exécuter manuellement une cible canonique depuis un sample payload

As an admin ops / LLM operator,
I want déclencher explicitement une exécution LLM à partir d’une runtime preview valide,
So that je puisse vérifier le comportement réel du provider sur une cible canonique contrôlée.

**Acceptance Criteria:**

**Given** une runtime preview valide avec un sample payload complet
**When** l’admin clique sur `Exécuter avec le LLM`
**Then** un appel provider réel est lancé avec le prompt et les paramètres résolus
**And** cette exécution reste distincte de la preview simple.

**Given** une runtime preview incomplète
**When** l’admin tente d’exécuter
**Then** l’action est bloquée avec un message explicite listant les données manquantes
**And** aucun appel provider n’est lancé.

**Given** une exécution admin manuelle
**When** elle est déclenchée
**Then** elle transporte les métadonnées runtime pertinentes, dont au minimum `manifest_entry_id`, provider, modèle et paramètres d’exécution résolus
**And** elle reste corrélable dans l’observabilité existante.

**Given** le système de garde-fous runtime existe déjà
**When** l’exécution admin est lancée
**Then** elle respecte timeout, retries, classification d’erreurs et redaction existants
**And** ne contourne pas le chemin nominal du gateway.

### Story 69.2: Afficher le retour LLM brut, structuré et les métadonnées d’exécution

As an admin ops / release operator,
I want consulter le résultat complet d’une exécution manuelle,
So that je puisse comprendre à la fois ce qui a été envoyé et ce que le LLM a renvoyé.

**Acceptance Criteria:**

**Given** une exécution admin terminée
**When** la zone `Retour LLM` s’affiche
**Then** elle montre au minimum le statut, la durée, le provider, le modèle, les paramètres d’exécution, le prompt envoyé et la réponse brute.

**Given** la sortie attendue est structurée
**When** la réponse est parseable
**Then** l’UI affiche aussi une vue structurée ou prettifiée du résultat
**And** distingue clairement réponse brute et réponse interprétée.

**Given** l’exécution échoue
**When** le backend retourne une erreur
**Then** la page affiche un état d’erreur exploitable avec code ou message stable
**And** ne masque pas si l’échec vient du rendu, du provider ou de la validation de sortie.

**Given** des valeurs sensibles existent dans la requête ou la réponse
**When** elles sont affichées dans la surface admin
**Then** la politique de redaction admin reste appliquée
**And** les champs non sûrs sont masqués ou tronqués.

### Story 69.3: Sécuriser la surface d’exécution manuelle et verrouiller sa QA

As an admin platform owner,
I want encadrer l’exécution manuelle par des garde-fous UX, sécurité et tests,
So that la surface reste utile sans devenir une source d’erreur opératoire ou de fuite de données.

**Acceptance Criteria:**

**Given** une exécution manuelle potentiellement coûteuse ou risquée
**When** l’admin déclenche l’action
**Then** une confirmation explicite précise qu’il s’agit d’un appel provider réel
**And** le mode courant (`runtime preview` versus `live execution`) reste toujours visible.

**Given** un utilisateur non autorisé ou insuffisamment habilité
**When** il accède à la surface
**Then** l’action d’exécution n’est pas disponible
**And** le backend refuse l’appel même si l’UI est contournée.

**Given** la page admin évolue
**When** la suite de tests est exécutée
**Then** des tests backend couvrent le chemin d’exécution manuelle, les erreurs et la redaction
**And** des tests frontend couvrent les états preview, exécution, succès et échec.

**Given** l’observabilité d’exploitation existe
**When** une exécution manuelle est lancée
**Then** les événements et logs permettent de distinguer clairement une exécution admin volontaire d’un trafic produit nominal.
