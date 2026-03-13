# Backlog détaillé — Feature « Consultation complète » assistée par LLM

Version: 1.0  
Date: 13 mars 2026  
Source de dérivation: `plan_produit_consultation_complete_llm.md`  
Statut: backlog exploitable pour création d'EPICs et stories de mise en œuvre

---

# 1. Objet du document

Ce document dérive le plan produit de la feature **Consultation complète** en un **backlog structuré EPIC par EPIC**, prêt à être utilisé pour:

- créer les EPICs dans l'outil de gestion de projet,
- générer les stories détaillées de delivery,
- organiser la roadmap MVP puis les incréments suivants,
- répartir les responsabilités produit / backend / front / moteur astro / LLM / QA / analytics.

Le backlog est pensé pour une application qui dispose déjà:

- d'un onboarding utilisateur,
- d'un enregistrement persistant des données natales,
- d'un calcul de thème natal,
- d'une interprétation basique,
- d'un moteur astrologique backend existant,
- d'une couche LLM déjà utilisée sur d'autres parcours.

---

# 2. Hypothèses de cadrage retenues

## 2.1 Hypothèses fonctionnelles

La feature **Consultation complète**:

- réutilise d'abord les données onboarding existantes,
- contrôle la complétude avant toute collecte,
- demande uniquement les données manquantes ou conditionnellement nécessaires,
- supporte les parcours mono-profil, bi-profil et timing,
- expose explicitement les modes dégradés,
- route les prompts LLM selon la qualité de l'information disponible,
- n'autorise pas le LLM à calculer librement l'astrologie,
- applique des garde-fous visibles et des limitations explicites.

## 2.2 Hypothèses de scope MVP

Le MVP couvre prioritairement:

- consultation de période,
- consultation travail / décision pro,
- consultation orientation / mission,
- consultation relationnelle,
- consultation timing en lecture de fenêtre large,
- réutilisation du profil onboarding,
- module autre personne en version MVP,
- modes dégradés principaux,
- restitution structurée,
- safety minimum viable mais robuste,
- observabilité métier.

## 2.3 Hypothèses de scope post-MVP

Hors MVP, à planifier ensuite:

- élective fine par créneau,
- horaire avancée,
- composite très sophistiqué,
- coaching continu multi-session,
- systèmes proactifs de relance,
- scoring relationnel enrichi,
- personnalisation narrative plus poussée par astrologue virtuel.

---

# 3. Convention de lecture du backlog

## 3.1 Structure utilisée

Chaque EPIC contient:

- son objectif,
- sa valeur métier,
- son périmètre,
- ses dépendances,
- ses critères de sortie,
- ses stories candidates,
- les couches impactées,
- les risques spécifiques,
- les arbitrages ouverts.

## 3.2 Convention de codification

- `EPIC-CC-01` à `EPIC-CC-10`
- `STORY-CC-XX-YY` pour les stories
- `SPIKE-CC-XX-YY` pour les spikes / cadrages techniques
- `TASK-CC-XX-YY` pour les tâches de support si besoin

## 3.3 Couches concernées

Abréviations utilisées:

- `PRD` = produit
- `UX` = design / UX
- `API` = backend API
- `DOM` = domaine métier / orchestration
- `ASTRO` = moteur astrologique
- `LLM` = orchestration modèle / prompts
- `WEB` = front web
- `DATA` = analytics / logging / observabilité
- `QA` = qualité / tests

---

# 4. Vue d'ensemble du backlog

## 4.1 Ordre recommandé de livraison

### Tranche 0 — Cadrage et fondations

- EPIC-CC-01 Catalogue produit et taxonomie
- EPIC-CC-02 Précheck de complétude
- EPIC-CC-08 Safety et garde-fous (socle)

### Tranche 1 — Parcours de collecte et fallback

- EPIC-CC-03 Collecte conditionnelle
- EPIC-CC-04 Modes dégradés

### Tranche 2 — Orchestration métier et LLM

- EPIC-CC-05 Routing prompts / orchestration
- EPIC-CC-06 Dossier de consultation / contrats backend

### Tranche 3 — Restitution et UX end-to-end

- EPIC-CC-07 Génération et restitution structurée
- EPIC-CC-09 Intégration UX / front

### Tranche 4 — Stabilisation et pilotage

- EPIC-CC-10 Analytics, QA, observabilité

## 4.2 Dépendances fortes

- EPIC-CC-01 conditionne tous les autres.
- EPIC-CC-02 conditionne EPIC-CC-03 et EPIC-CC-04.
- EPIC-CC-04 conditionne EPIC-CC-05 et EPIC-CC-07.
- EPIC-CC-05 et EPIC-CC-06 conditionnent EPIC-CC-07.
- EPIC-CC-08 doit intervenir avant la mise en production publique.
- EPIC-CC-10 doit démarrer tôt, même si sa finalisation arrive en fin de lot.

---

# 5. EPIC-CC-01 — Catalogue produit et taxonomie de consultation

## 5.1 Objectif

Définir le référentiel fonctionnel commun de la feature afin d'éviter les ambiguïtés sur:

- les types de consultation,
- les méthodes astrologiques autorisées,
- les données requises,
- les fallbacks possibles,
- les promesses UX autorisées,
- le scope MVP vs post-MVP.

## 5.2 Valeur métier

Sans taxonomie stabilisée, le backlog dérive vite en stories incohérentes, le front et le backend divergent, et les prompts ne peuvent pas être routés proprement.

## 5.3 Périmètre

Inclus:

- référentiel `consultation_type`,
- référentiel `profile_quality`,
- référentiel `counterparty_profile_quality`,
- référentiel `fallback_mode`,
- mapping `consultation_type -> allowed_methods`,
- mapping `consultation_type -> required_fields`,
- segmentation MVP / V2,
- promesses UX autorisées par niveau de qualité.

Exclus:

- implémentation des endpoints,
- écrans détaillés,
- prompts complets,
- logique technique de persistance.

## 5.4 Dépendances

Aucune dépendance technique forte. C'est un prérequis de structuration.

## 5.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- les référentiels métier sont figés et versionnés,
- le scope MVP est validé,
- chaque type de consultation a un contrat d'éligibilité clair,
- les modes dégradés sont nommés et documentés,
- les promesses UX autorisées / interdites sont définies,
- les équipes PRD / UX / API / LLM partagent le même vocabulaire.

## 5.6 Stories candidates

### STORY-CC-01-01 — Définir la taxonomie `consultation_type`

But: créer le référentiel officiel des types de consultation.

Sortie attendue:

- liste des types supportés en MVP,
- labels UX,
- descriptions courtes,
- cas d'usage rattachés,
- exclusions documentées.

Critères d'acceptation:

- chaque type a un identifiant stable,
- chaque type possède un libellé métier et un libellé UX,
- aucun doublon fonctionnel n'existe entre deux types.

Couches: `PRD`, `UX`, `DOM`

### STORY-CC-01-02 — Définir les états de qualité de profil

But: figer les états `USER_FULL`, `USER_NO_BIRTH_TIME`, `USER_PARTIAL`, `USER_BLOCKING`, ainsi que les équivalents tiers.

Critères d'acceptation:

- la qualité utilisateur et la qualité tiers sont distinctes,
- les critères de calcul sont documentés,
- chaque état a des conséquences métier explicites.

Couches: `PRD`, `DOM`, `API`

### STORY-CC-01-03 — Définir le référentiel `fallback_mode`

But: nommer et décrire tous les modes dégradés autorisés.

Exemples:

- `user_no_birth_time`,
- `other_no_birth_time`,
- `relation_user_only`,
- `timing_degraded`,
- `blocking_missing_data`,
- `safe_refusal`.

Critères d'acceptation:

- chaque fallback a une règle d'activation,
- chaque fallback a une promesse UX autorisée,
- chaque fallback a une limitation associée.

Couches: `PRD`, `DOM`, `UX`

### STORY-CC-01-04 — Mapper consultation -> méthodes astrologiques autorisées

But: établir le cadre de méthodes utilisables par type de consultation et par niveau de qualité.

Critères d'acceptation:

- le mapping distingue méthode nominale et méthode dégradée,
- les méthodes interdites sont explicites,
- les méthodes sont formulées dans un vocabulaire compatible LLM.

Couches: `PRD`, `ASTRO`, `LLM`, `DOM`

### STORY-CC-01-05 — Définir le scope MVP / post-MVP

But: trancher officiellement ce qui entre en lot 1.

Critères d'acceptation:

- les fonctionnalités MVP sont listées,
- les fonctionnalités différées sont listées,
- les dépendances aux futures phases sont identifiées.

Couches: `PRD`

### STORY-CC-01-06 — Rédiger la matrice promesse UX autorisée / interdite

But: cadrer le langage produit selon la précision réelle.

Critères d'acceptation:

- une consultation avec heure inconnue ne promet jamais un timing fin,
- une consultation relationnelle sans données tiers ne promet jamais une comparaison complète,
- la matrice est exploitable par UX et LLM.

Couches: `PRD`, `UX`, `LLM`

## 5.7 Spikes recommandés

### SPIKE-CC-01-07 — Atelier d'alignement inter-équipes

But: sécuriser le vocabulaire commun avant implémentation.

Livrable:

- compte rendu de décision,
- tableau des états métier,
- arbitrages ouverts / clos.

## 5.8 Risques spécifiques

- taxonomie trop ambitieuse dès le MVP,
- mélange entre méthode astrologique et type de consultation,
- termes métier incompris par le front ou l'équipe prompt.

---

# 6. EPIC-CC-02 — Précheck de complétude profil et éligibilité consultation

## 6.1 Objectif

Déterminer, avant d'engager l'utilisateur, si la consultation est faisable, avec quel niveau de précision, et quelles données manquent.

## 6.2 Valeur métier

Le précheck évite:

- d'ouvrir des parcours non réalisables,
- de demander trop tôt trop d'informations,
- de laisser le LLM travailler sur une base insuffisante,
- de dégrader la confiance utilisateur.

## 6.3 Périmètre

Inclus:

- lecture du profil onboarding,
- lecture du thème natal existant,
- calcul `user_profile_quality`,
- détection des champs manquants,
- détection des modes disponibles selon le type de consultation,
- preview du niveau de précision.

Exclus:

- collecte des compléments,
- persistance des tiers,
- génération LLM.

## 6.4 Dépendances

- dépend de EPIC-CC-01 pour la taxonomie.

## 6.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- un endpoint ou service de précheck existe,
- il retourne la qualité de profil,
- il retourne les données manquantes utiles,
- il retourne les modes consultatifs disponibles,
- il expose les limitations principales avant poursuite du parcours.

## 6.6 Stories candidates

### STORY-CC-02-01 — Exposer le profil onboarding à la feature consultation

But: rendre réutilisables les données déjà présentes dans l'application.

Critères d'acceptation:

- la couche consultation lit les données natales existantes,
- elle ne duplique pas inutilement la source de vérité,
- les cas d'absence de thème natal existant sont gérés proprement.

Couches: `API`, `DOM`, `ASTRO`

### STORY-CC-02-02 — Calculer `user_profile_quality`

But: dériver automatiquement l'état de qualité du profil utilisateur.

Critères d'acceptation:

- la règle tient compte de date, lieu, heure, thème calculé,
- la règle est versionnée,
- le résultat est traçable dans les logs.

Couches: `DOM`, `API`

### STORY-CC-02-03 — Exposer `natal_precision_level`

But: exprimer le niveau de finesse réellement exploitable.

Critères d'acceptation:

- l'indicateur distingue au minimum `high`, `medium`, `low`, `blocking`,
- la logique est cohérente avec la présence ou absence d'heure,
- le front peut l'afficher sans interprétation supplémentaire.

Couches: `DOM`, `API`, `WEB`

### STORY-CC-02-04 — Créer le service / endpoint de précheck consultation

But: centraliser la logique d'éligibilité avant parcours.

Critères d'acceptation:

- l'appel prend un `consultation_type`,
- il retourne `user_profile_quality`, `missing_fields`, `available_modes`, `precision_level`,
- le schéma de réponse est versionné.

Couches: `API`, `DOM`

### STORY-CC-02-05 — Calculer les modes disponibles par consultation

But: savoir si un parcours nominal, dégradé ou bloquant est possible.

Critères d'acceptation:

- la réponse distingue clairement `nominal`, `degraded`, `blocked`,
- les raisons sont renvoyées,
- les suggestions de compléments sont contextualisées.

Couches: `DOM`, `API`

### STORY-CC-02-06 — Préparer la prévisualisation UX de précision

But: fournir au front un message ou statut simple à afficher.

Critères d'acceptation:

- la donnée est compréhensible par l'utilisateur,
- elle ne surestime jamais la précision réelle,
- elle couvre les cas mono-profil et relationnels.

Couches: `UX`, `WEB`, `API`

## 6.7 Risques spécifiques

- calcul de qualité trop naïf,
- divergence entre niveau de qualité et possibilités réelles du moteur astro,
- logique du précheck dupliquée dans plusieurs couches.

---

# 7. EPIC-CC-03 — Collecte conditionnelle des données manquantes

## 7.1 Objectif

Demander uniquement les données strictement nécessaires à la consultation choisie, au bon moment du parcours.

## 7.2 Valeur métier

Une collecte conditionnelle bien faite maximise:

- la conversion,
- la qualité des données,
- la confiance utilisateur,
- la cohérence du parcours.

## 7.3 Périmètre

Inclus:

- collecte des champs utilisateur manquants,
- collecte des données d'un tiers si nécessaire,
- validation des données natales saisies,
- persistance contrôlée,
- réutilisation d'un tiers existant si déjà connu,
- gestion des consentements et de la conservation.

Exclus:

- restitution finale,
- safety thématique avancée,
- logique LLM.

## 7.4 Dépendances

- dépend de EPIC-CC-02 pour le précheck,
- dépend de EPIC-CC-01 pour la liste des champs requis par type.

## 7.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- seuls les champs requis sont demandés,
- la collecte utilisateur et la collecte tiers sont distinctes,
- l'heure de naissance est facultative mais qualifie la précision,
- les données tiers peuvent être saisies ou ignorées selon le mode choisi,
- la réutilisation d'un tiers déjà connu est possible si retenue dans le scope.

## 7.6 Stories candidates

### STORY-CC-03-01 — Construire le formulaire de compléments utilisateur

But: demander uniquement les champs natals utilisateur manquants.

Critères d'acceptation:

- les champs déjà connus ne sont pas redemandés,
- la saisie de l'heure peut être explicitement marquée comme inconnue,
- la validation bloque les formats invalides.

Couches: `UX`, `WEB`, `API`

### STORY-CC-03-02 — Construire le module « autre personne »

But: collecter les informations d'un tiers quand le parcours le requiert.

Critères d'acceptation:

- le module n'apparaît que pour les parcours concernés,
- il distingue données obligatoires et facultatives,
- l'utilisateur peut déclarer ne pas connaître l'heure.

Couches: `UX`, `WEB`, `API`

### STORY-CC-03-03 — Valider les données natales du tiers

But: sécuriser les données saisies avant usage moteur.

Critères d'acceptation:

- les formats date / heure / lieu sont validés,
- les erreurs sont compréhensibles,
- les cas d'informations partielles sont acceptés si autorisés.

Couches: `API`, `DOM`, `WEB`

### STORY-CC-03-04 — Définir la persistance du profil tiers

But: décider et implémenter le stockage éventuel des tiers.

Critères d'acceptation:

- le mode de stockage est explicite,
- la politique de réutilisation est définie,
- les règles de suppression / non-persistance sont documentées.

Couches: `PRD`, `API`, `DATA`

### STORY-CC-03-05 — Permettre la réutilisation d'un tiers existant

But: éviter une ressaisie répétitive.

Critères d'acceptation:

- les profils tiers existants sont sélectionnables si la feature le permet,
- l'utilisateur peut en créer un nouveau,
- l'état de complétude du tiers est visible.

Couches: `WEB`, `API`, `UX`

### STORY-CC-03-06 — Gérer le choix « je ne connais pas ces informations »

But: fluidifier le basculement vers un mode dégradé.

Critères d'acceptation:

- le parcours ne force pas un abandon si l'utilisateur ignore certaines données,
- le système annonce le fallback disponible,
- l'expérience reste cohérente.

Couches: `UX`, `WEB`, `DOM`

## 7.7 Spikes recommandés

### SPIKE-CC-03-07 — Décider la stratégie de geocoding / lieu de naissance

But: cadrer la saisie et la normalisation des lieux pour le tiers.

## 7.8 Risques spécifiques

- sur-friction dans les formulaires,
- collecte trop lourde pour les parcours relationnels,
- stockage trop permissif de données sensibles sur des tiers.

---

# 8. EPIC-CC-04 — Gestion des modes dégradés et parcours de fallback

## 8.1 Objectif

Transformer les situations de données incomplètes en parcours produits assumés, utiles et transparents.

## 8.2 Valeur métier

Les fallbacks bien conçus évitent de perdre l'utilisateur tout en maintenant un niveau d'honnêteté compatible avec la confiance produit.

## 8.3 Périmètre

Inclus:

- fallback sans heure utilisateur,
- fallback sans heure tiers,
- fallback sans données tiers,
- fallback timing large,
- fallback bloquant propre,
- messages UX associés,
- limitations structurées.

Exclus:

- safety thématique,
- prompts détaillés,
- rendu final complet.

## 8.4 Dépendances

- dépend de EPIC-CC-01 et EPIC-CC-02,
- alimente EPIC-CC-05, EPIC-CC-06, EPIC-CC-07, EPIC-CC-09.

## 8.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- chaque situation incomplète a un fallback documenté,
- le backend expose le `fallback_mode`,
- le front sait l'afficher,
- la promesse utilisateur reste cohérente,
- le LLM reçoit explicitement ce contexte.

## 8.6 Stories candidates

### STORY-CC-04-01 — Implémenter `user_no_birth_time`

But: permettre une consultation exploitable sans heure utilisateur.

Critères d'acceptation:

- les limitations de précision sont explicites,
- les méthodes interdites sont retirées du contexte LLM,
- l'UX annonce une lecture moins fine.

Couches: `DOM`, `API`, `LLM`, `WEB`

### STORY-CC-04-02 — Implémenter `other_no_birth_time`

But: permettre une compatibilité simplifiée quand l'autre personne n'a pas d'heure connue.

Critères d'acceptation:

- la comparaison reste possible si la date existe,
- les overlays précis sont neutralisés,
- la limitation est visible dans le résultat.

Couches: `DOM`, `API`, `LLM`, `WEB`

### STORY-CC-04-03 — Implémenter `relation_user_only`

But: replier une consultation bi-profil vers une lecture centrée utilisateur.

Critères d'acceptation:

- le système ne simule jamais une vraie synastrie sans données tiers,
- le résultat recentre l'analyse sur l'utilisateur et sa dynamique relationnelle,
- le changement de mode est clairement annoncé.

Couches: `DOM`, `LLM`, `WEB`, `UX`

### STORY-CC-04-04 — Implémenter `timing_degraded`

But: limiter la consultation timing à des fenêtres larges en cas de précision insuffisante.

Critères d'acceptation:

- aucune granularité trompeuse n'est générée,
- le wording parle de fenêtres et non de certitudes,
- le comportement est testable.

Couches: `DOM`, `LLM`, `API`

### STORY-CC-04-05 — Gérer les cas bloquants avec sortie propre

But: refuser poliment les parcours réellement impossibles.

Critères d'acceptation:

- le système explique ce qui manque,
- il n'affiche pas une fausse consultation,
- il propose une action de complément ou un retour au choix de parcours.

Couches: `UX`, `WEB`, `API`

### STORY-CC-04-06 — Normaliser les messages UX de mode dégradé

But: harmoniser le langage de limitation.

Critères d'acceptation:

- chaque fallback a une formulation standardisée,
- le ton reste clair et non anxiogène,
- les messages sont réutilisables côté front.

Couches: `UX`, `WEB`, `PRD`

## 8.7 Risques spécifiques

- fallback trop punitif,
- fallback trop permissif,
- manque de transparence sur le niveau de fiabilité.

---

# 9. EPIC-CC-05 — Routing des prompts et orchestration LLM

## 9.1 Objectif

Déterminer de façon fiable quel ensemble de prompts, de fragments et de contraintes doit être utilisé selon le type de consultation, la qualité des profils et le contexte safety.

## 9.2 Valeur métier

Le routing est ce qui transforme un système fragile à prompt unique en architecture robuste, explicable et maintenable.

## 9.3 Périmètre

Inclus:

- matrice de routage,
- `route_key` ou équivalent,
- composition de prompts par fragments,
- injection `allowed_methods` / `forbidden_methods`,
- prise en compte du `fallback_mode`,
- versionnement des prompts.

Exclus:

- rendu final UI,
- safety de haut niveau si géré séparément,
- calcul astro.

## 9.4 Dépendances

- dépend de EPIC-CC-01, EPIC-CC-04, EPIC-CC-08.

## 9.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- la matrice de routage est codée,
- chaque consultation majeure a une route nominale,
- chaque fallback a une route dégradée,
- les prompts sont composés par fragments et versionnés,
- les routes sont traçables dans les logs.

## 9.6 Stories candidates

### STORY-CC-05-01 — Définir la matrice `route_key`

But: créer la table de routage consultation x qualité x fallback x safety.

Critères d'acceptation:

- la matrice couvre tous les cas MVP,
- les cas impossibles sont explicitement marqués,
- la matrice est versionnée.

Couches: `PRD`, `LLM`, `DOM`

### STORY-CC-05-02 — Implémenter le `route resolver`

But: calculer automatiquement la route à partir du dossier de consultation.

Critères d'acceptation:

- l'entrée et la sortie du resolver sont documentées,
- le resolver est déterministe,
- les erreurs de résolution sont traçables.

Couches: `DOM`, `API`

### STORY-CC-05-03 — Composer les prompts par fragments

But: éviter les prompts monolithiques.

Critères d'acceptation:

- le système assemble base + consultation + data quality + safety + output,
- les fragments sont indépendamment versionnés,
- l'assemblage est testable.

Couches: `LLM`, `DOM`

### STORY-CC-05-04 — Injecter `allowed_methods` et `forbidden_methods`

But: empêcher le LLM de surinterpréter.

Critères d'acceptation:

- la liste autorisée est issue du backend métier,
- la liste interdite est transmise au prompt,
- les cas de non-conformité sont détectables.

Couches: `DOM`, `LLM`

### STORY-CC-05-05 — Gérer le versionnement des prompts

But: rendre l'architecture opérable dans le temps.

Critères d'acceptation:

- chaque run logue la version du prompt,
- le rollback est possible,
- les modifications sont auditables.

Couches: `LLM`, `DATA`

### STORY-CC-05-06 — Créer des prompts de clarification et de complétion

But: ne pas limiter la couche LLM aux seuls prompts d'interprétation.

Critères d'acceptation:

- il existe des prompts dédiés à la demande de données manquantes,
- il existe des prompts dédiés à l'annonce du mode dégradé,
- les prompts de clarification sont distincts des prompts d'analyse.

Couches: `LLM`, `PRD`

## 9.7 Spikes recommandés

### SPIKE-CC-05-07 — Arbitrer l'administration des prompts

But: décider ce qui vit en base, en seed ou en config.

## 9.8 Risques spécifiques

- explosion combinatoire des routes,
- duplication entre règles métier et règles prompt,
- manque de testabilité des fragments.

---

# 10. EPIC-CC-06 — Dossier de consultation, contrats backend et payload métier

## 10.1 Objectif

Construire un objet métier unique représentant la consultation, utilisable de bout en bout entre précheck, moteur astro, routing LLM et restitution.

## 10.2 Valeur métier

Le dossier de consultation devient la colonne vertébrale de la feature. Sans lui, les informations se dispersent entre couches et la maintenance devient fragile.

## 10.3 Périmètre

Inclus:

- schéma `ConsultationDossier`,
- schémas d'entrées et de sorties,
- sérialisation des données utilisateur / tiers / question / contexte,
- intégration des sorties astro pertinentes,
- exposition `precision_level`, `fallback_mode`, `route_key`,
- versioning des contrats.

Exclus:

- rendu front détaillé,
- wording UX final.

## 10.4 Dépendances

- dépend de EPIC-CC-01, EPIC-CC-02, EPIC-CC-04, EPIC-CC-05.

## 10.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- le dossier de consultation est défini et validé,
- il est alimenté par les bonnes sources de vérité,
- il transporte tous les contextes nécessaires au LLM,
- il est compatible avec les schémas de persistance et de restitution.

## 10.6 Stories candidates

### STORY-CC-06-01 — Définir le schéma `ConsultationDossier`

But: figer l'objet métier central.

Critères d'acceptation:

- le schéma couvre mono-profil, bi-profil et timing,
- le schéma contient qualité, précision, fallback, safety, route,
- le schéma est versionné.

Couches: `DOM`, `API`

### STORY-CC-06-02 — Sérialiser le contexte de question utilisateur

But: normaliser l'intention métier.

Critères d'acceptation:

- la question brute et la question reformulée peuvent coexister,
- l'horizon temporel est représenté,
- les options de décision éventuelles sont sérialisées.

Couches: `DOM`, `API`

### STORY-CC-06-03 — Intégrer les sorties du moteur astro dans le dossier

But: transmettre au LLM uniquement les éléments calculés utiles.

Critères d'acceptation:

- le moteur astro ne renvoie pas tout le thème si inutile,
- les éléments sont structurés et typés,
- le LLM n'a pas besoin d'inférer les faits astrologiques.

Couches: `ASTRO`, `DOM`, `API`

### STORY-CC-06-04 — Exposer les métadonnées de confiance et de précision

But: fournir les données nécessaires au discours prudent.

Critères d'acceptation:

- `precision_level` est présent,
- `fallback_mode` est présent si applicable,
- `limitations` peut être construit automatiquement.

Couches: `DOM`, `API`

### STORY-CC-06-05 — Journaliser les versions modèle / prompt / route

But: rendre chaque consultation audit-able.

Critères d'acceptation:

- le dossier conserve la version de prompt,
- le modèle utilisé est logué,
- la route choisie est persistée.

Couches: `API`, `DATA`, `LLM`

### STORY-CC-06-06 — Définir le contrat de sortie persistable

But: préparer la restitution structurée et le stockage.

Critères d'acceptation:

- le schéma de résultat est strict,
- il distingue contenu interprétatif et métadonnées de confiance,
- il est compatible avec la validation JSON.

Couches: `DOM`, `API`, `LLM`

## 10.7 Risques spécifiques

- dossier trop verbeux,
- couplage excessif au format du prompt,
- difficulté à versionner les contrats sans migration maîtrisée.

---

# 11. EPIC-CC-07 — Génération LLM et restitution structurée

## 11.1 Objectif

Produire une consultation lisible, cohérente, structurée, persistable et compatible avec l'UX attendue.

## 11.2 Valeur métier

C'est la partie visible de la feature: sans qualité de restitution, la valeur perçue s'effondre, même avec une bonne orchestration backend.

## 11.3 Périmètre

Inclus:

- appel LLM,
- validation du JSON de sortie,
- mapping backend -> front,
- sections de contenu,
- affichage des limitations,
- sauvegarde de la consultation.

Exclus:

- landing page d'entrée,
- formulaires de collecte,
- dashboards analytics avancés.

## 11.4 Dépendances

- dépend de EPIC-CC-05 et EPIC-CC-06,
- consomme EPIC-CC-04 et EPIC-CC-08.

## 11.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- le LLM est appelé avec le bon contexte,
- la sortie est validée par schéma,
- la consultation est affichable sans transformation fragile,
- les limitations sont visibles,
- la consultation est sauvegardable et reconsultable.

## 11.6 Stories candidates

### STORY-CC-07-01 — Implémenter l'appel LLM consultation

But: exécuter la route choisie avec le dossier construit.

Critères d'acceptation:

- l'appel reçoit le `route_key`,
- l'appel reçoit les contraintes de méthode,
- les erreurs de modèle sont gérées proprement.

Couches: `LLM`, `API`

### STORY-CC-07-02 — Valider le JSON de sortie

But: sécuriser le stockage et le rendu.

Critères d'acceptation:

- toute réponse est validée par schéma,
- les réponses invalides sont rejetées ou réparées selon stratégie définie,
- les erreurs sont tracées.

Couches: `LLM`, `API`, `QA`

### STORY-CC-07-03 — Mapper la sortie vers un modèle front stable

But: éviter les dépendances directes du front à la structure brute LLM.

Critères d'acceptation:

- le front reçoit un payload stable,
- les sections sont clairement nommées,
- les limitations et métadonnées sont séparées du contenu principal.

Couches: `API`, `WEB`

### STORY-CC-07-04 — Afficher synthèse, analyse, timing et limitations

But: rendre la consultation réellement lisible.

Critères d'acceptation:

- une synthèse courte est toujours présente,
- les thématiques détaillées sont distinctes,
- les limitations de précision sont visibles.

Couches: `WEB`, `UX`

### STORY-CC-07-05 — Sauvegarder et recharger une consultation

But: rendre la feature durable et revisitable.

Critères d'acceptation:

- une consultation peut être persistée,
- elle peut être rechargée sans réinterroger le LLM,
- les métadonnées de run sont conservées.

Couches: `API`, `WEB`, `DATA`

### STORY-CC-07-06 — Gérer les états d'erreur et de retry

But: éviter les expériences cassées.

Critères d'acceptation:

- le front sait gérer un échec de génération,
- un retry contrôlé est possible si autorisé,
- les erreurs ne produisent pas de consultation partiellement incohérente.

Couches: `WEB`, `API`, `LLM`

## 11.7 Risques spécifiques

- sortie LLM trop verbale ou trop floue,
- JSON instable,
- front trop couplé aux formulations générées.

---

# 12. EPIC-CC-08 — Safety, garde-fous et transparence

## 12.1 Objectif

Encadrer les usages sensibles, les demandes interdites, les vulnérabilités émotionnelles et les risques de surpromesse.

## 12.2 Valeur métier

Les safeguards protègent:

- l'utilisateur,
- la crédibilité du produit,
- la conformité interne,
- la soutenabilité de la feature à grande échelle.

## 12.3 Périmètre

Inclus:

- classification safety,
- thèmes interdits ou sensibles,
- refus / recadrage,
- redirections,
- garde-fous de répétition,
- transparence sur IA et précision,
- messages UX associés.

Exclus:

- support humain externe,
- modération conversationnelle avancée hors feature.

## 12.4 Dépendances

- dépend de EPIC-CC-01,
- influence EPIC-CC-05, EPIC-CC-07, EPIC-CC-09, EPIC-CC-10.

## 12.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- les thèmes sensibles sont classifiés,
- le système sait refuser ou recadrer,
- les messages de transparence sont intégrés,
- les limites de précision sont communiquées,
- les usages répétitifs problématiques sont observables et cadrables.

## 12.6 Stories candidates

### STORY-CC-08-01 — Définir la taxonomie safety

But: catégoriser standard / sensible / interdit.

Critères d'acceptation:

- les catégories sont documentées,
- les déclencheurs sont listés,
- les conséquences produit sont définies.

Couches: `PRD`, `LLM`, `DOM`

### STORY-CC-08-02 — Détecter les sujets interdits ou à refuser

But: bloquer santé, diagnostic, mort, juridique sensible, financier sensible, etc.

Critères d'acceptation:

- les demandes explicitement interdites sont détectées,
- la réponse ne lance pas une interprétation standard,
- la redirection ou le refus est traçable.

Couches: `DOM`, `API`, `LLM`

### STORY-CC-08-03 — Détecter la vulnérabilité émotionnelle et ajuster le ton

But: baisser le caractère projectif dans les situations sensibles.

Critères d'acceptation:

- les signaux de détresse ou d'obsession sont identifiables,
- le routeur passe en mode safety adapté,
- le ton de sortie devient plus prudent.

Couches: `DOM`, `LLM`

### STORY-CC-08-04 — Mettre en place les messages de transparence UX

But: afficher clairement la nature symbolique et assistée par IA de la consultation.

Critères d'acceptation:

- le message est visible avant et/ou pendant le parcours,
- la précision est expliquée,
- le périmètre des sujets exclus est communiqué.

Couches: `UX`, `WEB`, `PRD`

### STORY-CC-08-05 — Limiter les usages répétitifs sensibles

But: prévenir la dépendance d'usage sur un même sujet.

Critères d'acceptation:

- un mécanisme de friction ou d'alerte existe,
- il est ciblé sur les sujets / fréquences problématiques,
- il ne bloque pas abusivement les usages sains.

Couches: `PRD`, `API`, `DATA`, `WEB`

### STORY-CC-08-06 — Normaliser les contenus de refus / recadrage

But: rendre les réponses safety cohérentes.

Critères d'acceptation:

- il existe des templates dédiés,
- le ton est ferme mais non agressif,
- les cas standards et sensibles sont distingués.

Couches: `UX`, `LLM`, `PRD`

## 12.7 Risques spécifiques

- surblocage,
- sous-protection,
- messages de transparence trop génériques ou invisibles.

---

# 13. EPIC-CC-09 — Intégration UX / Front de l'expérience end-to-end

## 13.1 Objectif

Implémenter le parcours utilisateur complet depuis l'entrée dans la feature jusqu'à la lecture du résultat et la gestion des états intermédiaires.

## 13.2 Valeur métier

Même avec un bon backend, une UX mal séquencée dégrade fortement la conversion et la perception de qualité.

## 13.3 Périmètre

Inclus:

- landing page consultation,
- choix du type de consultation,
- cadrage de la demande,
- affichage du précheck,
- collecte conditionnelle,
- gestion des modes dégradés,
- écran de chargement,
- page résultat,
- accès à l'historique si supporté.

Exclus:

- design system global hors feature,
- parcours de paiement détaillé sauf si explicitement inclus.

## 13.4 Dépendances

- dépend de EPIC-CC-02, EPIC-CC-03, EPIC-CC-04, EPIC-CC-07, EPIC-CC-08.

## 13.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- le parcours principal est navigable de bout en bout,
- le précheck est visible et compréhensible,
- les formulaires sont dynamiques,
- les états dégradés, loading, erreur et résultat sont tous gérés,
- les messages safety et de précision sont visibles.

## 13.6 Stories candidates

### STORY-CC-09-01 — Créer la landing page consultation

But: présenter la feature et les types de consultation.

Critères d'acceptation:

- les types de consultation sont compréhensibles,
- la promesse produit est claire,
- les limites générales sont visibles.

Couches: `UX`, `WEB`

### STORY-CC-09-02 — Créer l'écran de cadrage de la demande

But: permettre à l'utilisateur d'exprimer son objectif et sa question.

Critères d'acceptation:

- la question peut être saisie en langage naturel,
- le thème prioritaire est identifiable,
- l'horizon temporel peut être précisé si utile.

Couches: `UX`, `WEB`

### STORY-CC-09-03 — Intégrer l'état de précheck dans le parcours

But: rendre visible le niveau de préparation du profil.

Critères d'acceptation:

- l'utilisateur sait si son profil est complet, partiel ou bloquant,
- les champs manquants sont contextualisés,
- le mode disponible est expliqué.

Couches: `WEB`, `API`, `UX`

### STORY-CC-09-04 — Intégrer les écrans de collecte conditionnelle

But: permettre la saisie progressive des compléments utiles.

Critères d'acceptation:

- le formulaire s'adapte au parcours,
- le module tiers n'apparaît que si nécessaire,
- les choix "je ne sais pas" sont gérés.

Couches: `WEB`, `UX`, `API`

### STORY-CC-09-05 — Intégrer les états de mode dégradé

But: rendre le fallback intelligible.

Critères d'acceptation:

- l'utilisateur sait quel mode sera utilisé,
- les limitations ne sont pas cachées,
- l'action de poursuite ou retour est claire.

Couches: `WEB`, `UX`

### STORY-CC-09-06 — Construire la page résultat consultation

But: afficher la restitution structurée.

Critères d'acceptation:

- la synthèse est immédiatement visible,
- les sections détaillées sont hiérarchisées,
- la précision et les limitations apparaissent dans la page.

Couches: `WEB`, `UX`, `API`

### STORY-CC-09-07 — Gérer loading, erreur, rechargement et reprise

But: offrir une expérience stable.

Critères d'acceptation:

- l'état de chargement est rassurant,
- les erreurs ont une issue claire,
- un rechargement de page ne casse pas le parcours si la consultation est persistée.

Couches: `WEB`, `API`

## 13.7 Risques spécifiques

- trop d'étapes visibles,
- confusion avec le chat ou l'horoscope quotidien,
- microcopie insuffisamment claire sur les limitations.

---

# 14. EPIC-CC-10 — Analytics, QA, observabilité et pilotage

## 14.1 Objectif

Rendre la feature testable, pilotable, monitorable et améliorable de manière continue.

## 14.2 Valeur métier

Sans observabilité métier, il sera impossible de savoir:

- où les utilisateurs abandonnent,
- quels fallbacks sont trop fréquents,
- quelles routes LLM sous-performent,
- quels safeguards se déclenchent réellement,
- si le produit tient ses promesses de conversion et de satisfaction.

## 14.3 Périmètre

Inclus:

- événements analytics,
- logs métier structurés,
- métriques LLM / route / fallback,
- scénarios QA,
- fixtures de test,
- tableaux de bord de suivi.

Exclus:

- BI entreprise large hors périmètre feature.

## 14.4 Dépendances

- transverse à tous les EPICs,
- finalisation après EPIC-CC-07 et EPIC-CC-09.

## 14.5 Critères de sortie EPIC

L'EPIC est terminé lorsque:

- les événements principaux sont instrumentés,
- les runs de consultation sont traçables de bout en bout,
- les scénarios QA critiques existent,
- un dashboard minimal de monitoring existe,
- les incidents LLM et safety sont observables.

## 14.6 Stories candidates

### STORY-CC-10-01 — Définir le plan de tracking produit

But: lister les événements utilisateur et métier.

Critères d'acceptation:

- les événements couvrent entrée, précheck, collecte, fallback, génération, résultat,
- chaque événement a un schéma défini,
- les propriétés utiles sont documentées.

Couches: `PRD`, `DATA`, `WEB`, `API`

### STORY-CC-10-02 — Instrumenter les événements analytics front

But: mesurer le comportement utilisateur.

Critères d'acceptation:

- les événements sont émis au bon moment,
- la volumétrie est raisonnable,
- les noms d'événements sont cohérents.

Couches: `WEB`, `DATA`

### STORY-CC-10-03 — Instrumenter les logs métier backend

But: tracer le moteur de consultation.

Critères d'acceptation:

- la route, la qualité profil, le fallback et le safety mode sont logués,
- les erreurs de schéma et de modèle sont loguées,
- la corrélation run / user / consultation est possible.

Couches: `API`, `DATA`, `LLM`

### STORY-CC-10-04 — Construire la matrice QA de parcours

But: couvrir nominal, dégradé, bloquant et safety.

Critères d'acceptation:

- les cas mono-profil, bi-profil et timing sont couverts,
- les cas sans heure sont couverts,
- les cas safety sont couverts.

Couches: `QA`, `PRD`, `API`, `WEB`

### STORY-CC-10-05 — Créer les fixtures et jeux de données de test

But: permettre les tests répétables.

Critères d'acceptation:

- des profils complets et incomplets existent,
- des profils tiers partiels existent,
- les routes et fallbacks critiques sont testables automatiquement.

Couches: `QA`, `API`, `ASTRO`, `LLM`

### STORY-CC-10-06 — Construire le dashboard de monitoring MVP

But: suivre la santé du produit après lancement.

Critères d'acceptation:

- le taux d'entrée, de complétion, de fallback et d'erreur est visible,
- les déclenchements safety sont visibles,
- les runs invalides JSON sont visibles.

Couches: `DATA`, `PRD`

## 14.7 Risques spécifiques

- manque de cohérence de tracking entre front et back,
- logs trop pauvres ou trop verbeux,
- absence de jeux de test réalistes.

---

# 15. Stories transverses à prévoir hors EPIC principal

Certaines stories ne rentrent pas naturellement dans un seul EPIC et peuvent être gérées comme transverse backlog.

## 15.1 Documentation interne

- glossaire métier,
- dictionnaire des états,
- runbook de troubleshooting,
- documentation des contrats API.

## 15.2 Sécurité et conformité données

- politique de stockage des profils tiers,
- modalités de suppression,
- journalisation minimale conforme,
- revue de confidentialité UX.

## 15.3 Performance et coût

- budget LLM par type de consultation,
- stratégie de retry,
- éventuelle mise en cache,
- limites de taille de payload.

## 15.4 Outillage produit

- administration des textes de transparence,
- administration des prompts si applicable,
- feature flags par type de consultation.

---

# 16. Proposition de découpage MVP par incréments

## 16.1 Incrément MVP-A — Fondations métier

Contenu:

- EPIC-CC-01 complété,
- EPIC-CC-02 livrable,
- safety minimum de classification posé,
- schéma `ConsultationDossier` v1 préparé.

Objectif:

- rendre le système capable de dire « ce que l'on peut faire ou non ».

## 16.2 Incrément MVP-B — Parcours mono-profil

Contenu:

- collecte utilisateur conditionnelle,
- fallback `user_no_birth_time`,
- route mono-profil full / degraded,
- restitution structurée simple.

Objectif:

- lancer période / travail / orientation sur profil onboarding.

## 16.3 Incrément MVP-C — Parcours relationnel

Contenu:

- module autre personne,
- fallback `other_no_birth_time`,
- fallback `relation_user_only`,
- restitution relationnelle adaptée.

Objectif:

- lancer amour / relation avec tiers complet ou partiel.

## 16.4 Incrément MVP-D — Timing et stabilisation

Contenu:

- timing dégradé,
- dashboard MVP,
- matrice QA complète,
- friction anti-répétition minimale,
- polishing UX.

Objectif:

- élargir la feature tout en sécurisant l'exploitation.

---

# 17. Dépendances de séquencement story par story

## 17.1 Stories bloquantes de tout le backlog

- STORY-CC-01-01
- STORY-CC-01-02
- STORY-CC-01-03
- STORY-CC-01-04

## 17.2 Stories bloquantes du premier parcours nominal

- STORY-CC-02-01
- STORY-CC-02-02
- STORY-CC-02-04
- STORY-CC-04-01
- STORY-CC-05-01
- STORY-CC-05-02
- STORY-CC-06-01
- STORY-CC-07-01
- STORY-CC-07-02
- STORY-CC-09-02
- STORY-CC-09-03
- STORY-CC-09-06

## 17.3 Stories bloquantes du parcours relationnel

- STORY-CC-03-02
- STORY-CC-03-03
- STORY-CC-04-02
- STORY-CC-04-03
- STORY-CC-05-01
- STORY-CC-06-03
- STORY-CC-07-04

## 17.4 Stories bloquantes du pilotage production

- STORY-CC-08-02
- STORY-CC-08-04
- STORY-CC-10-01
- STORY-CC-10-03
- STORY-CC-10-04
- STORY-CC-10-06

---

# 18. Critères d'acceptation transverses réutilisables dans les stories

## CA-T-01 — Réutilisation des données existantes

La feature ne redemande pas un champ déjà connu sauf action de correction explicite.

## CA-T-02 — Collecte minimale

Seuls les champs nécessaires au parcours courant sont demandés.

## CA-T-03 — Transparence sur la précision

Le niveau de précision réel est visible avant et dans la restitution.

## CA-T-04 — Pas de faux niveau de finesse

Aucune formulation ne laisse croire à une précision indisponible.

## CA-T-05 — Fallback utile et honnête

Quand un mode dégradé existe, il est proposé clairement et ne simule pas une capacité absente.

## CA-T-06 — Safety explicite

Les demandes interdites sont refusées ou recadrées sans ambiguïté.

## CA-T-07 — Contrat JSON valide

Toute réponse persistée valide le schéma attendu.

## CA-T-08 — Observabilité complète

Tout run logue route, qualité, fallback, safety et statut final.

## CA-T-09 — Récupérabilité du parcours

Une consultation persistée peut être rechargée sans perte d'information clé.

## CA-T-10 — Cohérence UX / backend

Les messages affichés par le front correspondent aux états réellement calculés côté backend.

---

# 19. Arbitrages encore ouverts avant raffinement story-level

## 19.1 Produit

- faut-il inclure la consultation argent dans le MVP visible ?
- faut-il inclure un teaser gratuit avant génération complète ?
- faut-il permettre une question de suivi après résultat ?

## 19.2 Data / confidentialité

- stocke-t-on les profils tiers par défaut ou à la demande ?
- quelle durée de conservation pour les tiers ?
- quelle option de suppression granulaire proposer ?

## 19.3 Moteur / LLM

- jusqu'où le timing MVP va-t-il réellement ?
- quelles portions des données astro doivent être injectées au LLM ?
- quelle stratégie de réparation JSON adopte-t-on ?

## 19.4 UX

- le précheck doit-il être visible comme étape dédiée ou comme bandeau inline ?
- faut-il montrer le niveau de précision avant même la saisie de la question ?
- comment différencier visuellement cette feature du chat astrologique libre ?

---

# 20. Recommandation opérationnelle de lancement des EPICs

## 20.1 Lancer immédiatement

- EPIC-CC-01
- EPIC-CC-02
- EPIC-CC-08 en cadrage
- SPIKE-CC-03-07
- SPIKE-CC-05-07

## 20.2 Lancer en parallèle après cadrage

- EPIC-CC-03
- EPIC-CC-04
- EPIC-CC-06

## 20.3 Lancer après stabilisation des contrats

- EPIC-CC-05
- EPIC-CC-07
- EPIC-CC-09

## 20.4 Démarrer en transverse dès le début

- EPIC-CC-10

---

# 21. Format recommandé pour dériver ce backlog en stories de delivery

Pour chaque story, utiliser ensuite la trame suivante:

- **Titre**
- **Contexte**
- **Objectif**
- **Valeur métier**
- **Périmètre inclus**
- **Périmètre exclu**
- **Règles métier**
- **Contrats d'entrée / sortie**
- **Critères d'acceptation**
- **Dépendances**
- **Couches impactées**
- **Risques / points d'attention**
- **Données analytics à tracer**
- **Cas de tests QA**

---

# 22. Conclusion

Le backlog de mise en œuvre de la feature **Consultation complète** doit être piloté comme un assemblage de quatre couches complémentaires:

1. un **socle métier** clair et versionné,  
2. un **moteur d'éligibilité et de fallback** robuste,  
3. une **orchestration LLM strictement contrainte**,  
4. une **expérience utilisateur transparente et sécurisée**.

Le point clé à préserver pendant tout le delivery est le suivant:

> la qualité du produit ne dépend pas seulement du texte généré, mais de la justesse du parcours, du contrôle de complétude, du niveau de précision annoncé, du fallback choisi et des garde-fous visibles.

Ce document peut maintenant servir de base directe pour:

- créer les EPICs dans l'outil projet,
- raffiner les stories par sprint,
- produire les contrats API et schémas techniques,
- lancer les maquettes UX et la matrice QA.
