---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
inputDocuments:
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\architecture.md'
---

# horoscope_front - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for horoscope_front, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Product and engineering teams can establish the Astrology Logic Engine as a prerequisite foundation before MVP application features.  
FR2: The system can provide a dedicated astrology logic engine as an independent core capability.  
FR3: The astrology logic engine can compute astrological results from user birth inputs.  
FR4: The astrology logic engine can use and maintain a reference database of celestial entities (planets, signs, houses, aspects).  
FR5: The astrology logic engine can store and expose astrological characteristics linked to reference entities.  
FR6: The astrology logic engine can version its computation rules and reference data.  
FR7: Product and operations users can manage updates to astrological reference data and rule definitions.  
FR8: The system can trace which rule and data version produced a given astrological output.  
FR9: Users can create an account and authenticate to access personalized features.  
FR10: Users can manage their profile data required for personalized astrology services.  
FR11: Users can provide and update birth data (date, time, place) used for astrological outputs.  
FR12: Users can access account settings and subscription status.  
FR13: Support agents can access user account context needed to resolve user requests.  
FR14: Users can request generation of a natal chart from their birth data.  
FR15: Users can view a structured natal chart interpretation.  
FR16: Users can request daily or weekly astrological guidance derived from their profile.  
FR17: Users can request contextualized guidance tied to their current situation.  
FR18: The system can produce astrology outputs using a consistent ruleset across sessions.  
FR19: Users can interact with a virtual astrologer through conversational messaging.  
FR20: The system can preserve conversation context to avoid repeated user re-explanation.  
FR21: Users can continue prior conversations and retrieve relevant conversation history.  
FR22: The system can provide guided recovery when a response is flagged as irrelevant or off-scope.  
FR23: Product operations can configure astrologer persona behavior boundaries.  
FR24: Users can subscribe to an entry paid plan.  
FR25: The system can enforce daily message quotas according to the user’s active plan.  
FR26: Users can view remaining quota and usage for the current period.  
FR27: Users can upgrade or modify subscription plans when additional tiers are enabled.  
FR28: The business can define and manage pricing plans and associated usage policies.  
FR29: Users can request export of their personal data.  
FR30: Users can request deletion of their personal data and account data.  
FR31: The system can process user data for LLM interactions without exposing direct personal identifiers.  
FR32: Support and operations can track completion of privacy-related requests.  
FR33: The system can provide audit visibility for sensitive account and data-rights actions.  
FR34: Support users can manage incidents related to account, subscription, and content issues.  
FR35: Operations users can monitor product quality indicators related to conversational relevance.  
FR36: Operations users can apply and revert configuration changes affecting response quality behavior.  
FR37: Operations users can monitor usage indicators needed for product and business decisions.  
FR38: Enterprise clients can create and manage API credentials for their account.  
FR39: Enterprise clients can consume astrology content through authenticated API access.  
FR40: Enterprise clients can manage plan limits and view consumption metrics.  
FR41: Enterprise clients can request content style adjustments aligned with editorial needs.  
FR42: The business can bill enterprise clients using fixed subscription and usage-based components.

### NonFunctional Requirements

NFR1: Le systeme doit permettre la generation d un premier theme astral en <= 2 min 30 apres soumission complete des donnees de naissance.  
NFR2: Le parcours inscription -> premiere reponse utile doit etre realisable en < 5 min pour un utilisateur standard.  
NFR3: Les actions d interface critiques (navigation interne SPA, envoi message, ouverture historique) doivent fournir un feedback utilisateur immediat et eviter les blocages percus.  
NFR4: Le service conversationnel doit supporter des reponses progressives (streaming ou equivalent) pour reduire la latence percue.  
NFR5: Les donnees sensibles doivent etre chiffrees en transit et au repos selon standards reconnus.  
NFR6: Les echanges envoyes aux LLM doivent exclure les identifiants personnels directs.  
NFR7: Le systeme doit fournir des mecanismes operationnels d export et suppression des donnees utilisateur.  
NFR8: Les actions sensibles (suppression donnees, regeneration cles, changements d offre) doivent etre journalisees de maniere tracable.  
NFR9: Les secrets d integration (cles API, credentials) doivent etre geres via un mecanisme dedie de gestion des secrets.  
NFR10: Le systeme doit pouvoir absorber une croissance progressive vers l objectif de ~2 000 utilisateurs payants sans degradation majeure de l experience percue.  
NFR11: Les composants critiques doivent permettre une montee en charge incrementale (scale out ou equivalent) sans refonte fonctionnelle.  
NFR12: Le systeme doit permettre la mise en place de limites d usage (quotas/messages) afin de maitriser la charge et les couts LLM.  
NFR13: Les parcours critiques doivent viser la conformite WCAG 2.1 AA.  
NFR14: Les interactions principales doivent etre utilisables au clavier et comprehensibles par lecteur d ecran.  
NFR15: Les contrastes et libelles des composants critiques doivent respecter les bonnes pratiques d accessibilite.  
NFR16: Le systeme doit integrer de maniere fiable les APIs LLM avec gestion d erreurs, retries controles et fallback defini.  
NFR17: Le systeme doit exposer des interfaces d integration versionnables pour les usages B2B (post-MVP).  
NFR18: Les integrations externes doivent etre observables via metriques minimales (disponibilite, erreurs, latence).  
NFR19: Le systeme doit maintenir une disponibilite compatible avec un service utilisateur 24/7.  
NFR20: Le systeme doit detecter, tracer et remonter les reponses hors-scope afin de soutenir l amelioration continue.  
NFR21: Le systeme doit disposer d un mecanisme de rollback de configuration pour restaurer rapidement la qualite de service.  
NFR22: Le systeme doit conserver une tracabilite entre resultats astrologiques et version du moteur logique utilisee.

### Additional Requirements

- Starter template impose pour demarrer: Split starter en monorepo (`backend/` FastAPI + `frontend/` Vite React TypeScript), a traiter explicitement dans Epic 1 Story 1.
- Initialisation recommandee: `uv` pour backend Python et Vite pour frontend; cette initialisation doit preceder le developpement fonctionnel.
- Architecture cible en couches backend: `api`, `core`, `domain`, `services`, `infra`, avec separation stricte des responsabilites.
- Stack data imposee: PostgreSQL + SQLAlchemy + Pydantic + Alembic, et Redis pour cache/compteurs/rate limiting.
- API REST versionnee (`/v1`) avec modele d erreur unifie, contrats OpenAPI, et compatibilite de version.
- Authentification et securite MVP: JWT access+refresh, RBAC minimal (`user`, `support`, `ops`), chiffrement donnees transit/repos et champs sensibles.
- Rate limiting obligatoire a deux niveaux: global et par utilisateur/plan.
- Observabilite MVP obligatoire: logs structures, metriques techniques et suivi des erreurs.
- Garde-fous IA obligatoires: anonymisation avant appel LLM, controles hors-scope, fallback/retry maitrises.
- Exigences infra/deploiement initial: Docker Compose single host, separation d environnements via variables d environnement.
- Contraintes de qualite produit: etats loading/error/empty explicites sur les parcours critiques et experience chat fluide.
- Tracabilite metier obligatoire: versionnement des regles/donnees astrologiques et lien entre version et sortie calculee.

### FR Coverage Map

FR1: Epic 1 - fondation moteur astrologique  
FR2: Epic 1 - moteur astrologique dedie  
FR3: Epic 1 - calcul astrologique depuis donnees natales  
FR4: Epic 1 - referentiel planetes/signes/maisons/aspects  
FR5: Epic 1 - caracteristiques astrologiques liees au referentiel  
FR6: Epic 1 - versioning des regles et donnees astro  
FR7: Epic 1 - gestion des mises a jour des regles/referentiels  
FR8: Epic 1 - tracabilite version regles/donnees vers sortie  
FR9: Epic 2 - creation de compte et authentification utilisateur  
FR10: Epic 2 - gestion du profil utilisateur  
FR11: Epic 2 - saisie/mise a jour date-heure-lieu de naissance  
FR12: Epic 2 - consultation parametres compte/abonnement  
FR13: Epic 6 - acces support au contexte compte utilisateur  
FR14: Epic 2 - demande de generation du theme natal  
FR15: Epic 2 - restitution d un theme natal structure  
FR16: Epic 3 - guidance astrologique quotidienne/hebdomadaire  
FR17: Epic 3 - guidance contextuelle selon situation utilisateur  
FR18: Epic 2 - coherence des sorties avec un ruleset stable  
FR19: Epic 3 - conversation avec astrologue virtuel  
FR20: Epic 3 - persistance du contexte conversationnel  
FR21: Epic 3 - reprise des conversations et historique  
FR22: Epic 3 - recuperation guidee apres reponse hors-scope  
FR23: Epic 3 - configuration des bornes de persona astrologue  
FR24: Epic 4 - souscription au plan payant d entree  
FR25: Epic 4 - application des quotas messages selon plan  
FR26: Epic 4 - affichage du quota restant et consommation  
FR27: Epic 4 - upgrade/modification de plan  
FR28: Epic 4 - gestion du catalogue tarifaire et policies  
FR29: Epic 5 - export des donnees personnelles  
FR30: Epic 5 - suppression des donnees personnelles/compte  
FR31: Epic 5 - anonymisation des donnees envoyees au LLM  
FR32: Epic 5 - suivi des demandes privacy par support/ops  
FR33: Epic 5 - audit des actions sensibles  
FR34: Epic 6 - gestion des incidents support  
FR35: Epic 6 - monitoring de la qualite conversationnelle  
FR36: Epic 6 - application/rollback des configurations qualite  
FR37: Epic 6 - suivi des indicateurs usage produit/business  
FR38: Epic 7 - gestion des credentials API entreprise  
FR39: Epic 7 - consommation API B2B authentifiee  
FR40: Epic 7 - gestion des limites et metrics de consommation  
FR41: Epic 7 - demandes de personnalisation editoriale  
FR42: Epic 7 - facturation hybride fixe + volume

## Epic List

### Epic 1: Fondation pour des calculs astrologiques fiables et tracables
Fournir un moteur astrologique central, tracable et gouvernable, capable de produire des resultats coherents a partir des donnees natales.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8

### Epic 2: Compte Utilisateur et Premiere Valeur (Theme Natal)
Permettre a un utilisateur de creer son compte, renseigner ses donnees de naissance et obtenir un theme natal structure.
**FRs covered:** FR9, FR10, FR11, FR12, FR14, FR15, FR18

### Epic 3: Guidance Astrologique Conversationnelle Contextuelle
Permettre une guidance quotidienne/hebdomadaire et contextuelle via chat, avec continuite de conversation et garde-fous de pertinence.
**FRs covered:** FR16, FR17, FR19, FR20, FR21, FR22, FR23

### Epic 4: Abonnement B2C et gestion des quotas
Permettre l abonnement utilisateur et le controle transparent de la consommation.
**FRs covered:** FR24, FR25, FR26, FR27, FR28

### Epic 5: Privacy, RGPD et audit de conformite
Permettre l exercice des droits donnees et la conformite des traitements sensibles.
**FRs covered:** FR29, FR30, FR31, FR32, FR33

### Epic 6: Support client et pilotage operations
Permettre aux equipes support/ops de traiter les incidents et maintenir la qualite de service.
**FRs covered:** FR13, FR34, FR35, FR36, FR37

### Epic 7: Offre B2B API et Self-Service Entreprise
Permettre aux clients entreprise de consommer le moteur via API, gerer leurs acces/offres et etre factures en fixe + volume.
**FRs covered:** FR38, FR39, FR40, FR41, FR42

## Epic 1: Fondation pour des calculs astrologiques fiables et tracables

Fournir un moteur astrologique central, tracable et gouvernable, capable de produire des resultats coherents a partir des donnees natales.

### Story 1.1: Set up initial project from starter template

As a product engineer,
I want initialiser le monorepo depuis le starter template retenu (FastAPI backend + React/Vite frontend),
So that l equipe dispose d une base executable et standardisee pour developper le moteur astrologique.

**Acceptance Criteria:**

**Given** un repository vide ou non initialise pour le produit
**When** le starter template est applique, les dependances installees et la configuration initiale renseignee
**Then** les applications backend et frontend demarrent localement avec la structure cible
**And** la structure en couches backend (`api/core/domain/services/infra`) est en place pour accueillir les stories suivantes

### Story 1.2: Gerer les donnees natales et les conversions temporelles

As a user,
I want que mes donnees de naissance soient validees et converties correctement (date/heure/lieu -> UT/JD),
So that les calculs astrologiques soient fiables.

**Acceptance Criteria:**

**Given** une date/heure/lieu de naissance valides
**When** le moteur prepare les donnees d entree
**Then** les conversions temporelles necessaires sont produites de facon deterministe
**And** les entrees invalides retournent des erreurs explicites et testables

### Story 1.3: Mettre en place le referentiel astrologique versionne

As a operations user,
I want gerer un referentiel astro (planetes, signes, maisons, aspects, caracteristiques) versionne,
So that le moteur s appuie sur des donnees metier controlees.

**Acceptance Criteria:**

**Given** une base PostgreSQL disponible
**When** les entites de referentiel sont creees et peuplees initialement
**Then** le moteur peut lire ces donnees pour les calculs
**And** chaque modification est liee a une version de referentiel

### Story 1.4: Calculer un resultat natal de base

As a user,
I want obtenir un calcul natal de base (positions, maisons, aspects principaux),
So that je recois un resultat astrologique coherent.

**Acceptance Criteria:**

**Given** des donnees natales valides et un referentiel versionne
**When** la generation de calcul natal est lancee
**Then** le moteur produit un resultat structure conforme au ruleset actif
**And** le calcul est reproductible a entrees identiques

### Story 1.5: Assurer la tracabilite regle/donnee -> resultat

As a support or operations user,
I want connaitre precisement quelles versions de regles et de referentiel ont produit un resultat,
So that je peux auditer et expliquer les sorties moteur.

**Acceptance Criteria:**

**Given** un resultat astrologique calcule
**When** il est persiste et restitue
**Then** il contient les identifiants de version regle + referentiel
**And** un audit permet de retrouver cette correspondance sans ambiguite

## Epic 2: Compte Utilisateur et Premiere Valeur (Theme Natal)

Permettre a un utilisateur de creer son compte, renseigner ses donnees de naissance et obtenir un theme natal structure.

### Story 2.1: Inscription et authentification utilisateur (JWT)

As a user,
I want creer un compte et me connecter de facon securisee,
So that j accede a mes fonctionnalites personnalisees.

**Acceptance Criteria:**

**Given** un utilisateur non authentifie
**When** il cree un compte puis se connecte
**Then** le systeme emet des tokens d acces/refresh valides
**And** les echecs d authentification retournent des erreurs coherentes

### Story 2.2: Saisie et gestion des donnees natales

As a user,
I want renseigner et modifier mes donnees de naissance (date, heure, lieu),
So that le moteur puisse produire mon theme de maniere personnalisee.

**Acceptance Criteria:**

**Given** un utilisateur authentifie
**When** il enregistre ses donnees natales
**Then** les donnees sont validees et persistees
**And** toute donnee invalide est rejetee avec message explicite

### Story 2.3: Generation du theme natal initial

As a user,
I want lancer la generation de mon theme natal depuis mon profil,
So that j obtiens ma premiere valeur rapidement.

**Acceptance Criteria:**

**Given** des donnees natales completes et valides
**When** l utilisateur declenche la generation
**Then** le moteur retourne un resultat structure
**And** la reponse inclut les metadonnees de version du moteur/referentiel
**And** si le moteur est indisponible ou depasse le delai cible, le systeme retourne une erreur explicite avec option de relance sans perte de contexte

### Story 2.4: Restitution lisible du theme natal

As a user,
I want consulter un theme natal clair et structure,
So that je peux comprendre facilement mes informations astrologiques.

**Acceptance Criteria:**

**Given** un theme natal genere
**When** l utilisateur ouvre la vue de restitution
**Then** les sections sont presentees de facon lisible et coherente
**And** les etats `loading/error/empty` sont geres explicitement

### Story 2.5: Coherence inter-sessions des resultats

As a support user,
I want garantir qu a entrees identiques le resultat reste coherent entre sessions,
So that la confiance utilisateur soit maintenue.

**Acceptance Criteria:**

**Given** un meme profil natal et une meme version de regles
**When** le theme est regenere
**Then** la sortie reste coherente
**And** tout ecart est tracable via versioning/audit

## Epic 3: Guidance Astrologique Conversationnelle Contextuelle

Permettre une guidance quotidienne/hebdomadaire et contextuelle via chat, avec continuite de conversation et garde-fous de pertinence.

### Story 3.1: Chat astrologue avec envoi/reception de messages

As a user,
I want echanger par messages avec un astrologue virtuel,
So that je peux poser mes questions au fil de mes besoins.

**Acceptance Criteria:**

**Given** un utilisateur authentifie avec acces au chat
**When** il envoie un message
**Then** le systeme retourne une reponse astrologique
**And** les erreurs techniques sont gerees avec un feedback clair
**And** si le fournisseur LLM ne repond pas dans le delai attendu, un fallback/retry controle est applique puis un message actionnable est affiche

### Story 3.2: Persistance du contexte conversationnel

As a user,
I want que le chat conserve le contexte de mes echanges,
So that je n aie pas besoin de tout reexpliquer.

**Acceptance Criteria:**

**Given** une conversation active
**When** l utilisateur envoie de nouveaux messages
**Then** les reponses tiennent compte du contexte precedent
**And** le contexte est persiste de maniere tracable

### Story 3.3: Historique et reprise des conversations

As a user,
I want retrouver et reprendre mes conversations passees,
So that je continue mes echanges sans perte d information.

**Acceptance Criteria:**

**Given** plusieurs conversations existantes
**When** l utilisateur consulte son historique et rouvre un fil
**Then** les messages precedents sont restaures
**And** la reprise se fait sur le bon contexte conversationnel

### Story 3.4: Guidance quotidienne et hebdomadaire

As a user,
I want obtenir des guidances periodiques liees a mon profil,
So that je dispose d un accompagnement utile au bon moment.

**Acceptance Criteria:**

**Given** un profil utilisateur complet
**When** il demande une guidance journaliere ou hebdomadaire
**Then** la reponse est adaptee a son profil et a la temporalite demandee
**And** le format de sortie reste coherent avec les garde-fous metier

### Story 3.5: Guidance contextuelle sur situation critique

As a user,
I want demander une guidance contextuelle sur ma situation du moment,
So that je recois des conseils personnalises pour une decision immediate.

**Acceptance Criteria:**

**Given** un profil utilisateur complet et un contexte saisi
**When** l utilisateur demande une guidance contextuelle
**Then** la reponse prend en compte le contexte explicite fourni
**And** les recommandations restent actionnables, prudentes et coherentes avec les garde-fous metier

### Story 3.6: Detection hors-scope et recuperation guidee

As a user,
I want que le systeme gere les reponses hors-scope avec reformulation,
So that l experience reste pertinente et fiable.

**Acceptance Criteria:**

**Given** une reponse detectee comme hors-scope/incoherente
**When** le mecanisme de controle qualite s active
**Then** une strategie de recovery (retry/reformulation/fallback) est appliquee
**And** l evenement est journalise pour suivi ops

### Story 3.7: Parametrage des bornes de persona astrologue

As a operations user,
I want configurer les limites de comportement du persona astrologue,
So that je controle le ton, le perimetre et la qualite des reponses.

**Acceptance Criteria:**

**Given** une interface/configuration ops disponible
**When** un parametre de persona est modifie
**Then** la nouvelle configuration est appliquee au chat
**And** un rollback est possible en cas de derive qualite

## Epic 4: Abonnement B2C et gestion des quotas

Permettre l abonnement utilisateur et le controle transparent de la consommation.

### Story 4.1: Souscription au plan payant d entree

As a user,
I want souscrire au plan payant de base,
So that je peux acceder au service astrologique selon mon abonnement.

**Acceptance Criteria:**

**Given** un utilisateur authentifie sans abonnement actif
**When** il souscrit au plan d entree
**Then** son statut d abonnement devient actif
**And** le plan est visible dans son espace compte
**And** en cas d echec paiement, l abonnement reste inactif avec motif clair et possibilite immediate de reessayer

### Story 4.2: Quotas journaliers et suivi de consommation

As a user,
I want voir mon quota restant et que le systeme applique mes limites,
So that je comprends clairement mes droits d usage.

**Acceptance Criteria:**

**Given** un utilisateur avec plan actif
**When** il envoie des messages
**Then** le quota journalier est decremente correctement
**And** au depassement, l acces est bloque avec message explicite

### Story 4.3: Upgrade/modification de plan

As a user,
I want modifier mon abonnement quand des niveaux supplementaires sont disponibles,
So that mon offre correspond a mon usage reel.

**Acceptance Criteria:**

**Given** un utilisateur avec plan actif
**When** il demande un changement de plan
**Then** le nouveau plan est applique selon les regles de facturation
**And** les nouvelles limites d usage sont effectives sans ambiguite

## Epic 5: Privacy, RGPD et audit de conformite

Permettre l exercice des droits donnees et la conformite des traitements sensibles.

### Story 5.1: Export et suppression des donnees personnelles

As a user,
I want exporter et supprimer mes donnees facilement,
So that je garde le controle de mes informations.

**Acceptance Criteria:**

**Given** un utilisateur authentifie
**When** il demande un export ou une suppression
**Then** la demande est traitee via un workflow tracable
**And** une confirmation de traitement est disponible cote compte/support

### Story 5.2: Anonymisation LLM et audit des actions sensibles

As a operations user,
I want garantir l anonymisation avant envoi LLM et auditer les actions critiques,
So that la confidentialite et la conformite sont assurees.

**Acceptance Criteria:**

**Given** un appel sortant vers un LLM
**When** la requete est preparee
**Then** les identifiants directs sont retires/pseudonymises
**And** les actions sensibles sont journalisees avec contexte d audit

## Epic 6: Support client et pilotage operations

Permettre aux equipes support/ops de traiter les incidents et maintenir la qualite de service.

### Story 6.1: Outillage support (compte, incidents, demandes privacy)

As a support user,
I want acceder au contexte compte et gerer incidents/demandes RGPD,
So that je peux resoudre les demandes client efficacement.

**Acceptance Criteria:**

**Given** un agent support autorise
**When** il consulte un dossier utilisateur
**Then** il voit les informations necessaires (compte, abonnement, demandes privacy)
**And** ses actions sont limitees par RBAC et tracees

### Story 6.2: Monitoring qualite conversationnelle et pilotage ops

As a operations user,
I want suivre les KPI qualite/usage et appliquer un rollback de configuration,
So that je maintiens la qualite de service.

**Acceptance Criteria:**

**Given** une couche d observabilite active
**When** des derives sont detectees (hors-scope, erreurs, latence)
**Then** les indicateurs remontent dans les outils ops
**And** une configuration peut etre revertee rapidement avec tracabilite

## Epic 7: Offre B2B API et Self-Service Entreprise

Permettre aux clients entreprise de consommer le moteur via API, gerer leurs acces/offres et etre factures en fixe + volume.

### Story 7.1: Espace compte entreprise et gestion des credentials API

As an enterprise admin,
I want creer/regenerer mes cles API depuis mon espace compte,
So that je gere l acces securise de mon organisation.

**Acceptance Criteria:**

**Given** un compte entreprise actif
**When** l admin genere ou regenere une cle API
**Then** une nouvelle cle valide est fournie selon les regles de securite
**And** l operation est auditee

### Story 7.2: Consommation API astrologie authentifiee

As an enterprise client,
I want appeler l API pour recuperer le contenu astrologique contractuel,
So that je l integre dans mon offre (ex: page astrologie hebdo).

**Acceptance Criteria:**

**Given** une cle API valide et un plan actif
**When** le client appelle les endpoints B2B
**Then** les reponses sont authentifiees, versionnees, et coherentes
**And** les erreurs de quota/auth sont renvoyees de maniere standardisee

### Story 7.3: Gestion des limites de plan et suivi de consommation B2B

As an enterprise admin,
I want consulter mes volumes consommes et limites contractuelles,
So that je pilote mon usage et mes couts.

**Acceptance Criteria:**

**Given** un contrat B2B actif
**When** l admin consulte le tableau de consommation
**Then** les metriques de volume/quotas sont visibles et a jour
**And** les depassements declenchent les regles prevues (blocage/overage)

### Story 7.4: Personnalisation editoriale du contenu B2B

As an enterprise client,
I want demander des ajustements de style editorial,
So that le contenu astrologique respecte ma ligne de marque.

**Acceptance Criteria:**

**Given** un client B2B avec parametres editoriaux configurables
**When** il soumet/modifie ses preferences de style
**Then** les sorties API respectent ce cadrage
**And** les changements sont versionnes et auditables

### Story 7.5: Facturation hybride fixe + volume

As a business operator,
I want facturer les clients B2B avec un abonnement fixe et une composante volume,
So that le modele economique reflete l usage reel.

**Acceptance Criteria:**

**Given** un client B2B et un modele tarifaire hybride
**When** la periode de facturation est cloturee
**Then** la facture combine composante fixe et usage mesure
**And** les elements de calcul sont tracables

## Epic 8: Production Readiness et Fiabilite

Durcir la plateforme pour une exploitation production robuste avec qualite verifiable.

### Story 8.1: Pipeline CI/CD avec quality gates obligatoires

As a tech lead,  
I want automatiser lint/tests/migrations/build/deploy dans un pipeline controle,  
So that chaque changement respecte un niveau de qualite constant.

**Acceptance Criteria:**

**Given** une branche de travail et une pull request
**When** le pipeline CI/CD s execute
**Then** les quality gates (lint + tests + verifications migrations + build) sont obligatoires
**And** aucun deploiement n est autorise si un gate echoue

### Story 8.2: Observabilite operationnelle (dashboards + alertes)

As an operations user,  
I want disposer de dashboards et alertes sur les parcours critiques,  
So that je detecte rapidement les degradations de service.

**Acceptance Criteria:**

**Given** des metriques et logs structures emis par les services
**When** les dashboards et regles d alerting sont configures
**Then** les KPI critiques (latence, erreurs, disponibilite, quotas) sont visibles
**And** les alertes sont actionnables avec contexte minimal exploitable

### Story 8.3: Sauvegarde/restauration et runbooks incidents

As an operations user,  
I want valider des procedures de backup/restore et de gestion incident,  
So that la recuperation soit maitrisee en cas de panne.

**Acceptance Criteria:**

**Given** un environnement de production cible
**When** un exercice de restauration est execute
**Then** la restauration des donnees critiques est verifiee
**And** un runbook incident documente est disponible pour les scenarios majeurs

### Story 8.4: Tests de charge et de concurrence des flux critiques

As a platform engineer,  
I want mesurer le comportement sous charge des endpoints critiques,  
So that nous validions la tenue en charge et les limites.

**Acceptance Criteria:**

**Given** un plan de tests de charge cible
**When** les scenarios chat/privacy/b2b/billing sont executes
**Then** les resultats de performance et points de saturation sont traces
**And** des actions de tuning priorisees sont produites

## Epic 9: Security et Conformite Operationnelle

Renforcer la securite applicative et la conformite operationnelle au-dela du socle MVP.

### Story 9.1: Durcissement de la gestion des secrets et rotation

As a security engineer,  
I want formaliser la gestion des secrets et leur rotation,  
So that le risque de compromission soit reduit.

**Acceptance Criteria:**

**Given** les secrets applicatifs et integrations externes
**When** la politique de stockage/rotation est appliquee
**Then** aucun secret n est expose en clair dans le code ou logs
**And** une procedure de rotation periodique est documentee et testee

### Story 9.2: Pack de verification securite (SAST/deps/pentest)

As a security engineer,  
I want executer des controles securite standardises,  
So that les vulnérabilites soient identifiees et traitees.

**Acceptance Criteria:**

**Given** la base de code et ses dependances
**When** les scans securite sont executes
**Then** les findings sont classes par severite et traces
**And** un plan de remediation est etabli pour les points critiques

### Story 9.3: Preuves operationnelles RGPD (export/suppression/audit)

As a compliance stakeholder,  
I want produire des preuves de conformite RGPD sur les flux implementes,  
So that la conformite puisse etre demontree en audit.

**Acceptance Criteria:**

**Given** les parcours privacy et audit actifs
**When** un dossier de preuve est genere
**Then** il inclut export, suppression, et traces d audit associees
**And** le processus de collecte est reproductible

## Epic 10: Scale B2B/B2C et Excellence Operationnelle

Elever la maturite de la plateforme pour le scale, la fiabilite business et la pilotabilite.

### Story 10.1: Couverture tests frontend B2B completee

As a frontend engineer,  
I want couvrir les clients API B2B avec des tests dedies,  
So that les regressions front B2B soient detectees tot.

**Acceptance Criteria:**

**Given** les modules frontend B2B existants
**When** les tests sont ajoutes/executés
**Then** les chemins nominaux et erreurs sont couverts
**And** la couverture front B2B est alignee avec le niveau de criticite

### Story 10.2: Reconciliation usage/facturation B2B pour ops

As an operations user,  
I want suivre la coherence entre consommation et facturation B2B,  
So that les ecarts soient detectes avant impact client.

**Acceptance Criteria:**

**Given** les donnees usage et billing B2B
**When** la vue de reconciliation est consultee
**Then** les ecarts sont identifies et traces
**And** les actions de correction sont explicites

### Story 10.3: Tuning performance guide par SLO

As a platform engineer,  
I want optimiser DB/cache/retries selon des SLO explicites,  
So that la performance reste stable sous croissance.

**Acceptance Criteria:**

**Given** des SLO definis pour les parcours critiques
**When** les optimisations sont appliquees
**Then** les metriques montrent un gain mesurable
**And** les arbitrages (cout/latence) sont documentes

## Epic 11: Expansion Produit Post-MVP

Etendre l offre fonctionnelle pour soutenir la retention et la croissance business.

### Story 11.1: Raffinement multi-persona astrologue

As a product owner,  
I want enrichir les personas astrologues et leurs parametres,  
So that l experience conversationnelle gagne en personnalisation.

**Acceptance Criteria:**

**Given** la configuration persona existante
**When** de nouveaux profils sont introduits
**Then** ils sont parametrables, testables et rollbackables
**And** leur impact qualite est mesurable via KPI

### Story 11.2: Modules tarot/runes derriere feature flags

As a product owner,  
I want introduire tarot/runes de maniere controlee,  
So that nous puissions iterer sans destabiliser le coeur MVP.

**Acceptance Criteria:**

**Given** une strategie de feature flags en place
**When** un module est active pour un segment cible
**Then** le flux est disponible sans impacter les utilisateurs non cibles
**And** la desactivation immediate reste possible

### Story 11.3: Instrumentation des experiments packaging/pricing

As a growth stakeholder,  
I want instrumenter les experiments d offres et pricing,  
So that les decisions commerciales reposent sur des donnees fiables.

**Acceptance Criteria:**

**Given** plusieurs variantes d offres activables
**When** les utilisateurs interagissent avec ces offres
**Then** les KPI conversion/retention/revenu sont traces par variante
**And** les resultats sont exploitables pour arbitrage produit
