---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
inputDocuments:
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\architecture.md'
lastEdited: '2026-02-21T14:39:07+01:00'
editHistory:
  - date: '2026-02-21T14:39:07+01:00'
    changes: 'Epics rebaseline after PRD/Architecture finalization (FR38-42 + NFR SMART alignment)'
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
FR38: Les clients entreprise peuvent creer et gerer des identifiants API pour leur compte.  
FR39: Les clients entreprise peuvent consommer du contenu astrologique via un acces API authentifie.  
FR40: Les clients entreprise peuvent gerer les limites de leur plan et consulter leurs metriques de consommation.  
FR41: Les clients entreprise peuvent demander des ajustements de style de contenu alignes avec leurs besoins editoriaux.  
FR42: L entreprise peut facturer les clients entreprise via un modele combinant abonnement fixe et composante variable a l usage.

### NonFunctional Requirements

NFR1: Le systeme doit permettre la generation d un premier theme astral en <= 2 min 30 apres soumission complete des donnees de naissance.  
NFR2: Le parcours inscription -> premiere reponse utile doit etre realisable en < 5 min pour un utilisateur standard.  
NFR3: Les actions d interface critiques (navigation interne SPA, envoi message, ouverture historique) doivent afficher un feedback visuel en <= 200 ms dans 95% des cas et ne jamais bloquer l interface utilisateur plus de 1 s sans indicateur de chargement.  
NFR4: Le service conversationnel doit fournir une premiere unite de reponse en <= 3 s (p95) et terminer la reponse complete en <= 15 s (p95) pour une requete standard.  
NFR5: Les donnees sensibles doivent etre chiffrees en transit (TLS 1.2+) et au repos (AES-256 ou equivalent), avec verification trimestrielle documentee de la configuration.  
NFR6: 100% des requetes envoyees aux LLM doivent etre pseudonymisees pour exclure les identifiants personnels directs (email, telephone, nom complet, adresse postale), avec controle automatique en pre-envoi.  
NFR7: Le systeme doit permettre l export des donnees utilisateur en format structure (JSON ou CSV) sous <= 72 h apres demande validee, et la suppression complete sous <= 30 jours calendaires avec confirmation d execution.  
NFR8: Les actions sensibles (suppression donnees, regeneration cles, changements d offre) doivent etre journalisees avec horodatage, acteur, type d action et identifiant de ressource, avec conservation des journaux pendant au moins 12 mois.  
NFR9: Les secrets d integration (cles API, credentials) doivent etre stockes dans un gestionnaire de secrets dedie, jamais en clair dans le code ou les logs, et tournes au minimum tous les 90 jours.  
NFR10: Le systeme doit supporter au moins 2 000 utilisateurs payants actifs/mois en maintenant une latence API p95 <= 2 s sur les endpoints critiques et un taux d erreur serveur mensuel < 1%.  
NFR11: Les composants critiques doivent permettre une montee en charge horizontale d au moins x2 du trafic moyen observe sur les 30 derniers jours, sans refonte fonctionnelle et sans regression des SLO definis (latence p95 et taux d erreur).  
NFR12: Le systeme doit appliquer des quotas configurables par plan (messages/jour et appels API/jour) avec blocage automatique au depassement et remise a zero periodique documentee.  
NFR13: Les parcours critiques doivent atteindre la conformite WCAG 2.1 niveau AA sur 100% des ecrans MVP audites avant mise en production.  
NFR14: 100% des interactions principales doivent etre utilisables au clavier (navigation tabulation + activation Entree/Espace) et compatibles lecteur d ecran sur Chrome et Edge.  
NFR15: Les composants critiques doivent respecter un contraste minimum de 4.5:1 pour le texte normal et 3:1 pour les elements UI non textuels.  
NFR16: Le systeme doit integrer les APIs LLM avec timeout <= 20 s par appel, au maximum 2 retries exponentiels sur erreurs transitoires, et fallback explicite vers une reponse degradee en cas d echec final.  
NFR17: Le systeme doit exposer des interfaces d integration B2B versionnees (ex. /v1, /v2) avec politique de compatibilite retroactive d au moins 6 mois apres annonce de depreciation.  
NFR18: Les integrations externes doivent publier au minimum les metriques disponibilite, taux d erreur et latence p95, avec une fenetre d observation continue et un tableau de bord operationnel mis a jour en temps reel.  
NFR19: Le systeme doit maintenir une disponibilite mensuelle >= 99.5% sur les services critiques orientes utilisateur.  
NFR20: Le systeme doit detecter et tracer les reponses hors-scope avec un taux de classification automatique >= 90% sur jeu de validation interne, et produire un rapport hebdomadaire de suivi.  
NFR21: Le mecanisme de rollback de configuration doit permettre un retour a la derniere configuration stable en <= 15 minutes apres declenchement.  
NFR22: Chaque resultat astrologique doit inclure un identifiant de version du moteur logique et des regles utilisees, afin de garantir une tracabilite de 100% des calculs restitues.

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

### Epic 12: Profil natal — saisie des donnees de naissance et generation du theme
Permettre a l utilisateur de renseigner ses donnees de naissance depuis le frontend et de declencher la generation de son theme natal, avec feedback adequat pendant le calcul.
**FRs covered:** FR10, FR11, FR14

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

### Story 2.6: Interface utilisateur signin, signup et signout

As a user,
I want acceder a une page d accueil, un formulaire d inscription, un formulaire de connexion et un bouton de deconnexion,
So that je puisse creer mon compte, m authentifier et me deconnecter depuis l interface de l application.

**Acceptance Criteria:**

**Given** un utilisateur non authentifie
**When** il ouvre l application
**Then** une page d accueil est affichee avec deux actions : Se connecter et Creer un compte
**And** le clic sur Se connecter affiche le formulaire SignInForm
**And** le clic sur Creer un compte affiche le formulaire SignUpForm

**Given** le formulaire SignInForm affiche
**When** l utilisateur soumet son email et son mot de passe
**Then** le formulaire valide les champs avec React Hook Form + Zod
**And** les etats loading/error sont geres explicitement
**And** en cas d identifiants incorrects, un message d erreur non technique est affiche
**And** en cas de succes, setAccessToken() est appele et l interface personnalisee est affichee
**And** un lien Creer un compte permet de naviguer vers SignUpForm

**Given** le formulaire SignUpForm affiche
**When** l utilisateur soumet son email et un mot de passe d au moins 8 caracteres
**Then** le formulaire valide les champs avec React Hook Form + Zod
**And** POST /v1/auth/register est appele via registerApi()
**And** en cas de succes, setAccessToken() est appele et l interface personnalisee est affichee
**And** en cas d email deja utilise, un message explicite est affiche
**And** un lien Se connecter permet de revenir a SignInForm

**Given** un utilisateur authentifie
**When** il navigue dans l application
**Then** un bouton Se deconnecter est accessible dans l interface
**And** le clic appelle clearAccessToken() et retourne a la page d accueil
**And** la navigation clavier est fonctionnelle (NFR14 - WCAG 2.1 AA)

**Implementation notes:**
- `frontend/src/pages/HomePage.tsx` : page d accueil avec props onSignIn / onRegister
- `frontend/src/components/SignInForm.tsx` : prop optionnelle onRegister pour lien croisement
- `frontend/src/components/SignUpForm.tsx` : nouveau composant avec prop onSignIn
- `frontend/src/api/auth.ts` : loginApi() + registerApi() via helper postAuth()
- `frontend/src/App.tsx` : state authView (home | signin | register), reset sur logout

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

## Epic 12: Profil natal — saisie des donnees de naissance et generation du theme

Permettre a l utilisateur de renseigner ses donnees de naissance depuis le frontend (date, heure, lieu, fuseau horaire) et de declencher la generation de son theme natal, avec un feedback adequat pendant le calcul long.

**FRs covered:** FR10, FR11, FR14

### Story 12.1: Formulaire de saisie du profil natal

As a utilisateur inscrit,
I want renseigner mes donnees de naissance (date, heure, lieu, fuseau horaire) via un formulaire dedie,
So that le systeme dispose des informations necessaires pour generer mon theme astral.

**Acceptance Criteria:**

**Given** un utilisateur authentifie naviguant vers la page de profil natal
**When** la page se charge
**Then** le formulaire est pre-rempli avec les donnees existantes issues de `GET /v1/users/me/birth-data`
**And** les champs vides sont affichés sans valeur par defaut

**Given** un utilisateur soumettant le formulaire avec des donnees valides
**When** la requete `PUT /v1/users/me/birth-data` reussit
**Then** un message de confirmation de sauvegarde est affiche
**And** les donnees mises a jour restent dans le formulaire

**Given** un utilisateur soumettant une heure de naissance au mauvais format
**When** l API retourne `invalid_birth_time`
**Then** un message d erreur specifique est affiche sous le champ heure

**Given** un utilisateur soumettant un fuseau horaire invalide
**When** l API retourne `invalid_timezone`
**Then** un message d erreur specifique est affiche sous le champ fuseau horaire

**Given** n importe quel champ invalide cote client
**When** l utilisateur tente de soumettre
**Then** la validation RHF+Zod bloque la soumission et affiche les erreurs inline
**And** les attributs aria-invalid et aria-describedby sont correctement positionnes

**Notes techniques:**
- Nouveau fichier: `frontend/src/api/birthProfile.ts` avec `getBirthData()` et `saveBirthData()`
- Nouveau fichier: `frontend/src/pages/BirthProfilePage.tsx`
- Validation Zod: `birth_date` (date ISO), `birth_time` (HH:MM optionnel), `birth_place` (string non vide), `birth_timezone` (IANA string non vide)
- Pattern RHF + Zod conforme a l architecture du projet
- Accessibilite WCAG 2.1 AA: labels associes, aria-invalid, role="alert" sur les erreurs

### Story 12.2: Declenchement et feedback de la generation du theme natal depuis l UI

As a utilisateur ayant sauvegarde ses donnees de naissance,
I want declencher la generation de mon theme natal depuis le frontend et voir un feedback clair pendant le calcul,
So that je sais que le calcul est en cours et je suis notifie du succes ou de l echec.

**Acceptance Criteria:**

**Given** un utilisateur sur la page de profil natal avec des donnees de naissance sauvegardees
**When** il clique sur le bouton "Generer mon theme astral"
**Then** le bouton est desactive et un indicateur de chargement est affiche
**And** une requete `POST /v1/users/me/natal-chart` est envoyee

**Given** la generation qui se termine avec succes
**When** l API retourne 200 avec les donnees du theme
**Then** l utilisateur est redirige ou navigue vers la page du theme natal
**And** les donnees du theme sont affichees via le composant existant `NatalChartPage`

**Given** la generation qui depasse le delai (NFR1: ≤ 2min30)
**When** l API retourne 503 avec `natal_generation_timeout`
**Then** un message d erreur non technique est affiche ("La generation a pris trop de temps, veuillez reessayer.")
**And** le bouton de generation redevient actif

**Given** le moteur natal indisponible
**When** l API retourne 503 avec `natal_engine_unavailable`
**Then** un message d erreur non technique est affiche ("Le service de generation est temporairement indisponible.")
**And** le bouton de generation redevient actif

**Given** n importe quelle erreur reseau (fetch rejete)
**When** la requete echoue sans reponse serveur
**Then** un message generique est affiche ("Une erreur est survenue. Veuillez reessayer.")

**Notes techniques:**
- Appel `POST /v1/users/me/natal-chart` via `birthProfile.ts` ou `natalChart.ts`
- Timeout UX: afficher le spinner pendant toute la duree du calcul (jusqu a 2min30)
- Pas de polling necessaire: la reponse HTTP est synchrone cote backend
- Integration avec `useLatestNatalChart()` pour invalider le cache TanStack Query apres generation reussie
- NFR1: latence p95 ≤ 2min30 pour la generation complete

## Epic 13: Stabilisation post-MVP — corrections des flux utilisateur critiques

Corriger les bugs bloquants identifies en test manuel apres le MVP, notamment l'erreur 422 lors de la generation du theme natal, afin de livrer un flux utilisateur complet et fonctionnel de bout en bout.

**FRs covered:** FR10, FR11 (correction de regression)

### Story 13.1: Correction erreur 422 lors de la generation du theme natal

As a utilisateur ayant sauvegarde ses donnees de naissance,
I want pouvoir declencher la generation de mon theme natal sans obtenir une erreur 422,
So that le flux de creation du theme fonctionne de bout en bout comme prevu.

**Root Cause identifie:** La fonction `generateNatalChart` dans `frontend/src/api/natalChart.ts` envoie un POST sans header `Content-Type: application/json`. FastAPI retourne systematiquement 422 Unprocessable Content pour les POST sans Content-Type correct, meme quand le corps est vide. De plus, le format de reponse 422 natif FastAPI (`{"detail": [...]}`) n'est pas gere par `handleResponse` (qui attend `{"error": {...}}`), causant un double-bug : l'erreur n'est pas parsee correctement et remontee comme `unknown_error`.

**Acceptance Criteria:**

**Given** un utilisateur ayant sauvegarde son profil natal
**When** il clique sur "Generer mon theme astral"
**Then** la requete POST /v1/users/me/natal-chart inclut le header `Content-Type: application/json`
**And** le backend repond 200 avec le theme genere

**Given** le backend retourne une erreur 422 (donnees invalides ou incompletes)
**When** la generation echoue avec code HTTP 422
**Then** un message clair est affiche : "Vos données de naissance sont invalides ou incomplètes. Veuillez vérifier votre profil natal."
**And** le bouton de generation redevient actif

**Given** le backend retourne un 422 au format FastAPI natif (`{"detail": [...]}`)
**When** `handleResponse` tente de parser l'erreur
**Then** le message est extrait ou un fallback generique est utilise (pas de crash silencieux)

**Notes techniques:**
- Fix principal: ajouter `"Content-Type": "application/json"` aux headers de `generateNatalChart` dans `natalChart.ts`
- Fix secondaire: dans `handleResponse`, ajouter un fallback pour parser `{"detail": [...]}` en plus de `{"error": {...}}`
- Fix UX: dans `BirthProfilePage.tsx` `generationMutation.onError`, ajouter le cas `code === "unprocessable_entity"` ou HTTP status 422 avec message utilisateur adapte
- Tests a ajouter: test 422 pendant generation dans `BirthProfilePage.test.tsx`, test du parsing `{"detail": [...]}` dans `natalChart.ts`

## Epic 14: Géocodage du lieu de naissance et précision astronomique du thème natal

Enrichir le profil natal avec la saisie structurée ville + pays, le géocodage automatique via Nominatim (OpenStreetMap open data) pour obtenir les coordonnées GPS, puis transmettre ces coordonnées au backend pour un calcul astronomique précis des maisons et des aspects. Gérer les modes dégradés (lieu absent, heure absente) avec feedback UX explicite. Fournir une table de traduction des termes astrologiques (maisons, signes, planètes) en FR/EN/ES, extensible à d'autres langues.

**FRs covered:** FR3, FR4, FR5, FR10, FR11, FR14, FR15

**Contrat API étendu (backend) :**
- `PUT /v1/users/me/birth-data` accepte les nouveaux champs : `birth_city` (string), `birth_country` (string), `birth_lat` (float, nullable), `birth_lon` (float, nullable)
- `birth_place` (free text) est déprécié mais maintenu pour rétrocompatibilité
- `POST /v1/users/me/natal-chart` body peut inclure `{ "birth_lat": float, "birth_lon": float }` optionnel ; si absent, le backend utilise les coordonnées stockées ou le mode dégradé Equal House
- Quand `birth_lat` / `birth_lon` sont fournis, le backend utilise Placidus (système de maisons par défaut) et calcule les aspects planétaires
- Quand les coordonnées sont absentes, le backend utilise Equal House (mode dégradé géographique)
- Quand `birth_time` est absent ou marqué "unknown", le backend utilise Solar chart (Soleil en Ascendant, heure forcée à midi) et l'indique dans `metadata.degraded_mode`

**Architecture open data géocodage :**
- API : Nominatim (OpenStreetMap) `https://nominatim.openstreetmap.org/search`
- Appel depuis le frontend (navigateur), pas de proxy backend nécessaire
- Paramètres : `?q={city},{country}&format=json&limit=1`
- Politique Nominatim : User-Agent obligatoire, max 1 req/s, pas de géocodage en masse
- Fallback : si Nominatim échoue ou ne trouve pas de résultat, mode dégradé Equal House

### Story 14.1: Refonte formulaire profil natal — ville, pays et géocodage Nominatim

As a utilisateur,
I want saisir ma ville et mon pays de naissance et obtenir automatiquement les coordonnées GPS,
So that mon theme natal puisse etre calcule avec precision geographique.

**Acceptance Criteria:**

**Given** un utilisateur sur la page de profil natal
**When** il renseigne la ville et le pays puis clique sur "Valider les coordonnées"
**Then** le frontend appelle Nominatim avec `?q={ville},{pays}&format=json&limit=1`
**And** les coordonnées (lat, lon, label résolu) sont affichées en confirmation
**And** les coordonnées sont incluses dans le payload `PUT /v1/users/me/birth-data` avec `birth_city`, `birth_country`, `birth_lat`, `birth_lon`
**And** en cas de succès de sauvegarde, le message "Profil natal sauvegardé." s'affiche

**Given** Nominatim ne trouve pas de résultat pour la ville/pays saisis
**When** la recherche retourne un tableau vide
**Then** un message d'alerte s'affiche : "Lieu introuvable. Vérifiez la ville et le pays, ou laissez le lieu vide pour utiliser le mode dégradé (maisons égales)."
**And** aucune coordonnée n'est envoyée au backend

**Given** Nominatim est indisponible (erreur réseau ou timeout)
**When** la requête échoue
**Then** un message d'alerte s'affiche : "Service de géocodage indisponible. Vous pouvez sauvegarder sans coordonnées (mode dégradé)."
**And** le bouton "Sauvegarder" reste actif pour permettre une sauvegarde sans coordonnées

**Notes techniques:**
- Nouveau service `frontend/src/api/geocoding.ts` — fonction `geocodeCity(city: string, country: string): Promise<{lat: number, lon: number, display_name: string} | null>`
- User-Agent header : `"User-Agent": "horoscope-app/1.0 (contact: admin@horoscope.app)"` (requis par Nominatim)
- `BirthProfilePage.tsx` : ajouter champs `birth_city` (requis si coordonnées souhaitées), `birth_country` (requis si coordonnées souhaitées), bouton "Valider les coordonnées", état `geocodingState` (idle | loading | success | error), affichage du `display_name` résolu
- `birthProfile.ts` : étendre `saveBirthData` pour inclure `birth_city`, `birth_country`, `birth_lat?`, `birth_lon?`
- Zod schema : `birth_city` et `birth_country` non requis mais conditionnellement requis ensemble
- Tests : test géocodage succès, lieu introuvable, Nominatim indisponible, sauvegarde avec et sans coordonnées

### Story 14.2: Modes dégradés — lieu absent et heure de naissance absente

As a utilisateur,
I want pouvoir utiliser l'application même si je ne connais pas mon heure ou mon lieu de naissance exact,
So that j'obtiens quand même un theme natal partiel avec un avertissement clair sur les limitations.

**Acceptance Criteria:**

**Given** un utilisateur qui ne renseigne pas de lieu de naissance (ou dont le géocodage a échoué)
**When** il génère son thème natal
**Then** le backend utilise le mode Equal House (sans coordonnées géographiques)
**And** `metadata.degraded_mode` contient `"no_location"` dans la réponse
**And** un bandeau d'avertissement est affiché sur la page du thème natal : "⚠ Thème calculé en maisons égales — lieu de naissance non renseigné ou non trouvé. Pour un calcul précis, renseignez votre ville et pays dans votre profil."

**Given** un utilisateur qui ne renseigne pas d'heure de naissance (champ laissé vide ou coché "inconnue")
**When** il génère son thème natal
**Then** le backend utilise Solar chart (Soleil en Ascendant, heure forcée à 12:00 UTC)
**And** `metadata.degraded_mode` contient `"no_time"` dans la réponse
**And** un bandeau d'avertissement est affiché : "⚠ Thème calculé en thème solaire — heure de naissance non renseignée. Les positions des maisons et de la Lune peuvent être inexactes."

**Given** un utilisateur sans lieu ET sans heure
**When** il génère son thème natal
**Then** les deux avertissements sont affichés simultanément
**And** `metadata.degraded_mode` contient `"no_location_no_time"`

**Given** un utilisateur sans date de naissance
**When** il tente de sauvegarder son profil natal
**Then** le formulaire bloque la soumission avec un message : "La date de naissance est indispensable pour calculer votre thème natal."
**And** aucune requête n'est envoyée au backend

**Notes techniques:**
- `BirthProfilePage.tsx` : ajouter une case à cocher "Heure inconnue" qui vide `birth_time` et envoie `birth_time: null` au backend
- `NatalChartPage.tsx` : lire `metadata.degraded_mode` et afficher le bandeau approprié
- `birth_date` reste obligatoire côté Zod (validation inchangée)
- Tests : test bandeau "no_location", test bandeau "no_time", test bandeau combiné, test date obligatoire

### Story 14.3: Table de traduction des termes astrologiques (FR/EN/ES)

As a utilisateur,
I want voir les termes astrologiques (maisons, signes, planètes) dans ma langue,
So that je comprenne facilement mon thème natal sans termes techniques en anglais.

**Acceptance Criteria:**

**Given** un thème natal affiché en français (langue par défaut)
**When** l'utilisateur consulte la page `NatalChartPage`
**Then** les noms des signes sont affichés en français (ex: "Bélier" au lieu de "aries")
**And** les noms des planètes sont affichés en français (ex: "Soleil" au lieu de "sun")
**And** les maisons sont affichées avec leur nom traditionnel en français (ex: "Maison I — Identité")

**Given** l'architecture i18n des termes astrologiques
**When** un développeur veut ajouter une nouvelle langue (ex: allemand)
**Then** il suffit d'ajouter une clé de langue dans `frontend/src/i18n/astrology.ts` sans modifier aucun composant

**Given** un code inconnu retourné par l'API (ex: nouveau planète ou signe non répertorié)
**When** la traduction est absente
**Then** le code brut est affiché en fallback (ex: "chiron") sans erreur

**Notes techniques:**
- Nouveau fichier `frontend/src/i18n/astrology.ts` — dictionnaire indexé par langue puis par code
- Langues initiales : `fr` (par défaut), `en`, `es`
- Entrées : signs (12), planets (10 : sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto), houses (12 maisons avec nom symbolique)
- Maisons : numéro + nom symbolique FR/EN/ES (ex: I — Identité/Identity/Identidad, II — Valeurs/Values/Valores...)
- Hook `useAstrologyLabels(lang: string)` retourne les dictionnaires traduits
- Langue détectée depuis `navigator.language` ou `localStorage`, avec fallback `fr`
- Tests : test traduction FR/EN/ES pour signs, planets, houses; test fallback code inconnu

## Epic 15: AI Text Engine — Moteur de génération de texte IA (OpenAI Gateway)

Centraliser tous les appels aux APIs LLM (OpenAI initialement) dans un module backend unique, gérant la robustesse (retries, timeouts, rate-limit), la traçabilité (trace_id) et le contrôle des coûts/tokens. Ce moteur supporte le chat (option streaming), la génération one-shot (thème astral, interprétation cartes/runes), et est extensible à d'autres providers.

**FRs covered:** FR19, FR20, FR22 (amélioration de la couche LLM existante)

### Story 15.1: AI Text Engine — Moteur de génération de texte IA (OpenAI Gateway)

As a service métier (chat, thème astral, tirage),
I want appeler un moteur centralisé de génération de texte IA,
So that je bénéficie d'une abstraction stable, robuste et traçable pour tous mes appels LLM.

**Acceptance Criteria:**

**Given** le backend Python existant
**When** le module `ai_engine` est créé avec une interface `ProviderClient`
**Then** l'implémentation OpenAI est isolée dans `openai_client.py`
**And** un autre provider peut être ajouté sans modifier les services appelants

**Given** un service métier appelant `/v1/ai/generate` avec un `use_case` valide
**When** la requête contient `use_case`, `locale`, `input`, `context` et `output`
**Then** le moteur sélectionne le prompt approprié depuis le Prompt Registry
**And** appelle le provider OpenAI avec les paramètres adéquats
**And** retourne une réponse JSON avec `text`, `usage` (tokens), `meta` (latency, cached)

**Given** un service chat appelant `/v1/ai/chat` avec `messages` et `stream: true`
**When** le moteur traite la requête
**Then** la réponse est envoyée en SSE (Server-Sent Events)
**And** chaque chunk contient `{ "delta": "..." }`
**And** le dernier événement contient `{ "done": true, "text": "..." }`

**Given** le Prompt Registry configuré
**When** un `use_case` est demandé (`chat`, `natal_chart_interpretation`, `card_reading`)
**Then** le template Jinja2 correspondant est chargé et rendu
**And** un `use_case` inconnu retourne une erreur 400 explicite

**Given** une erreur upstream (timeout, 429, 5xx)
**When** le provider OpenAI échoue
**Then** le moteur applique retries exponentiels (2-3 tentatives max)
**And** les erreurs sont traduites en codes HTTP standard (429, 502, 504)
**And** le body d'erreur contient `error.type`, `error.message`, `retry_after_ms`

**Notes techniques:**
- Nouveau module `backend/app/ai_engine/` avec structure: `config.py`, `schemas.py`, `routes.py`, `providers/`, `prompts/`, `services/`
- Dépendances: `openai>=1.0.0`, `jinja2>=3.0.0`
- Configuration: `OPENAI_API_KEY`, `OPENAI_MODEL_DEFAULT`, `AI_ENGINE_TIMEOUT_SECONDS`
- Endpoints: `POST /v1/ai/generate` (sync), `POST /v1/ai/chat` (sync + streaming SSE)
- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Spécification complète

### Story 15.2: AI Text Engine — Rate limiting, observabilité et déploiement Docker

As a platform engineer,
I want que le moteur AI soit protégé par rate limiting, observable via logs structurés, et déployable en production Docker,
So that le service soit robuste, monitorable et prêt pour le déploiement VPS.

**Acceptance Criteria:**

**Given** le module `ai_engine` existant (story 15.1)
**When** un utilisateur dépasse le quota de requêtes (ex: 30 req/min par user_id)
**Then** le moteur retourne une erreur 429 avec `error.type: "RATE_LIMIT_EXCEEDED"` et `retry_after_ms`
**And** le compteur est stocké en Redis (ou mémoire en dev)

**Given** une requête traitée par le moteur AI
**When** la requête est complétée (succès ou erreur)
**Then** un log structuré JSON est émis avec `request_id`, `trace_id`, `user_id`, `use_case`, `latency_ms`, `status`, `tokens_used`
**And** les données sensibles (birth_data, contenu conversation) ne sont pas loggées en clair

**Given** l'environnement de production Docker
**When** le déploiement est exécuté via `docker compose -f docker-compose.prod.yml up -d`
**Then** les services `api` (backend + ai_engine), `web` (Nginx), et `redis` démarrent correctement
**And** le frontend React buildé est servi par Nginx sur `/`
**And** les endpoints `/v1/ai/*` sont accessibles via le reverse proxy

**Given** un développeur ou ops consultant la documentation
**When** il lit le README de déploiement
**Then** il trouve les instructions pour : configuration `.env`, build des images, démarrage prod, vérification des logs
**And** les commandes de troubleshooting sont documentées

**Given** le cache optionnel activé
**When** une requête identique (même `use_case` + hash `input+context`) est reçue dans le TTL
**Then** la réponse est servie depuis le cache Redis
**And** `meta.cached: true` est retourné dans la réponse

**Notes techniques:**
- Fichiers à créer/modifier :
  - `backend/app/ai_engine/services/rate_limiter.py` — Rate limiting par user_id avec Redis/mémoire
  - `backend/app/ai_engine/services/cache_service.py` — Cache optionnel des réponses
  - `backend/app/ai_engine/middleware/logging_middleware.py` — Logs structurés JSON
  - `docker-compose.prod.yml` — Configuration production avec services api, web, redis
  - `Dockerfile` (backend) — Image Python optimisée
  - `frontend/Dockerfile` — Build React + copie vers Nginx
  - `nginx/nginx.conf` — Reverse proxy configuration
  - `docs/deploy-vps.md` — Documentation déploiement
- Configuration : `AI_ENGINE_RATE_LIMIT_PER_MIN`, `AI_ENGINE_CACHE_TTL_SECONDS`, `REDIS_URL`
- Redis requis en prod pour rate limiting distribué et cache partagé
- [Source: docs/agent/story-15-ai-text-engine-bmad.md#sections-7-8-9-11-12] — Spécification complète

### Story 15.3: Migration des services Chat et Guidance vers le AI Engine

As a utilisateur du chat et des guidances astrologiques,
I want que mes conversations et guidances soient générées par le vrai moteur OpenAI,
So that je reçoive des réponses astrologiques de qualité au lieu de simples échos de prompt.

**Acceptance Criteria:**

**Given** le service `ChatGuidanceService` existant
**When** un utilisateur envoie un message dans le chat
**Then** le service utilise le nouveau AI Engine (`/v1/ai/chat` ou appel direct au module)
**And** la réponse est générée par OpenAI avec le prompt `chat` du Prompt Registry
**And** le streaming SSE est supporté si configuré

**Given** le service `GuidanceService` existant
**When** un utilisateur demande une guidance (daily/weekly/contextual)
**Then** le service utilise le nouveau AI Engine avec `use_case=guidance_daily` ou `guidance_weekly` ou `guidance_contextual`
**And** les templates de prompts appropriés sont utilisés depuis le Prompt Registry
**And** les garde-fous hors-scope existants sont préservés via le AI Engine

**Given** l'ancien `LLMClient` stub dans `infra/llm/client.py`
**When** la migration est terminée
**Then** l'ancien stub est supprimé ou déprécié
**And** tous les imports de `LLMClient` sont remplacés par des appels au AI Engine

**Given** les tests existants des services Chat et Guidance
**When** ils sont exécutés après la migration
**Then** ils passent avec le nouveau AI Engine (mode mock/test)
**And** aucune régression n'est introduite dans le comportement fonctionnel

**Given** le frontend React existant
**When** l'utilisateur utilise le chat
**Then** le frontend peut consommer les réponses streaming SSE du AI Engine
**And** les états loading/error/empty sont correctement gérés

**Notes techniques:**
- Créer nouveaux use_cases dans le Prompt Registry : `guidance_daily`, `guidance_weekly`, `guidance_contextual`
- Créer templates Jinja2 correspondants dans `ai_engine/prompts/`
- Modifier `ChatGuidanceService.send_message()` pour appeler `ai_engine.services.chat_service`
- Modifier `GuidanceService.request_guidance()` et `request_contextual_guidance()` pour appeler `ai_engine.services.generate_service`
- Conserver la logique de récupération hors-scope (peut être déléguée au AI Engine ou maintenue dans les services)
- Adapter les tests pour mocker le AI Engine au lieu de `LLMClient`
- Option frontend : soit appeler directement `/v1/ai/chat`, soit garder l'endpoint existant `/v1/chat` qui délègue au AI Engine
- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Objectif #3 : "Réduire le couplage des services métier à OpenAI"

### Story 15.4: Interprétation textuelle du thème natal via AI Engine

As a utilisateur ayant généré son thème natal,
I want recevoir une interprétation textuelle riche et personnalisée de mon thème,
So that je comprenne la signification de mes positions planétaires, aspects et maisons.

**Acceptance Criteria:**

**Given** un utilisateur avec un thème natal calculé (NatalResult)
**When** il demande l'interprétation de son thème
**Then** le AI Engine est appelé avec `use_case=natal_chart_interpretation`
**And** le contexte contient le résumé du thème (positions, aspects, maisons, ascendant)
**And** une interprétation textuelle structurée est retournée (synthèse, points clés, conseils, disclaimer)

**Given** le template `natal_chart_interpretation_v1.jinja2` existant
**When** le AI Engine génère l'interprétation
**Then** le texte suit la structure définie (synthèse, points clés Soleil/Lune/Ascendant, conseils, prudence)
**And** le ton est bienveillant et non-alarmiste
**And** aucun diagnostic médical/juridique/financier n'est fait

**Given** l'endpoint `/v1/users/me/natal-chart`
**When** l'utilisateur génère ou récupère son thème natal
**Then** l'interprétation textuelle peut être incluse dans la réponse (champ `interpretation`)
**And** l'interprétation est optionnelle (paramètre `include_interpretation=true`)

**Given** un thème natal avec des données incomplètes (heure ou lieu manquant)
**When** l'interprétation est demandée
**Then** le AI Engine adapte l'interprétation avec les limitations appropriées
**And** un avertissement est inclus concernant les données manquantes

**Notes techniques:**
- Créer `backend/app/services/natal_interpretation_service.py` — Service d'interprétation du thème
- Utiliser le AI Engine avec `use_case=natal_chart_interpretation`
- Convertir `NatalResult` en `natal_chart_summary` exploitable par le template
- Champs du résumé : sun_sign, moon_sign, ascendant, dominant aspects, house placements
- Modifier `UserNatalChartService` ou créer endpoint dédié `/v1/users/me/natal-chart/interpretation`
- Cache possible : l'interprétation pour un même thème (même input_hash) peut être cachée
- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Use case `natal_chart_interpretation`

## Epic 16: Refonte Architecture Frontend — Information Architecture et Navigation

Refactoriser le frontend pour décomposer l'application en pages/sections dédiées avec React Router, un layout global cohérent, un chat messenger-style, et une navigation fluide. Cette refonte améliore l'UX sans modifier le backend.

**FRs covered:** FR10, FR11, FR12, FR14, FR15, FR19, FR20, FR21, FR24, FR26, FR29, FR30 (amélioration de la couche présentation)

### Story 16.1: React Router et Layout Foundation

As a utilisateur de l'application horoscope,
I want que l'application utilise React Router avec des URLs propres et un layout global cohérent,
So that je puisse naviguer avec back/forward, partager des liens directs, et avoir une interface structurée.

**Acceptance Criteria:**
- Routes fonctionnelles avec URLs significatives
- Protection des routes (AuthGuard, RoleGuard)
- Layout responsive (sidebar desktop, bottom nav mobile)
- Rétrocompatibilité des pages existantes

**Notes:** Installation react-router-dom@6, création guards, refactoring AppShell
[Source: _bmad-output/implementation-artifacts/16-1-react-router-layout-foundation.md]

### Story 16.2: Dashboard Page — Hub d'accueil

As a utilisateur connecté,
I want voir un dashboard d'accueil avec des raccourcis vers toutes les fonctionnalités,
So that je puisse accéder rapidement à ce que je cherche.

**Acceptance Criteria:**
- Page `/dashboard` avec cartes de raccourci
- Navigation vers : thème natal, chat, consultations, astrologues, paramètres
- Accessibilité clavier

[Source: _bmad-output/implementation-artifacts/16-2-dashboard-page.md]

### Story 16.3: Chat Messenger-Style — Layout 3 colonnes

As a utilisateur du chat astrologue,
I want une interface de chat style messenger avec liste de conversations, fenêtre de chat et détails astrologue,
So that je puisse naviguer facilement entre mes conversations et voir le contexte.

**Acceptance Criteria:**
- Layout 3 colonnes desktop, 1 colonne mobile
- Sélection conversation avec deep link `/chat/:conversationId`
- Envoi message avec état "typing"
- Auto-scroll intelligent
- Empty state avec CTA

[Source: _bmad-output/implementation-artifacts/16-3-chat-messenger-style.md]

### Story 16.4: Catalogue et Profil Astrologues

As a utilisateur,
I want parcourir un catalogue d'astrologues et voir leur profil détaillé,
So that je puisse choisir l'astrologue qui me correspond pour démarrer une conversation.

**Acceptance Criteria:**
- Page `/astrologers` avec grille de vignettes
- Page `/astrologers/:id` avec profil détaillé
- CTAs : démarrer conversation, consultation thématique
- Mock data si API non disponible

[Source: _bmad-output/implementation-artifacts/16-4-astrologers-pages.md]

### Story 16.5: Consultations Thématiques — Pages et Wizard

As a utilisateur,
I want créer des consultations thématiques (dating, pro, événement) avec option tirage cartes/runes,
So that je puisse obtenir des guidances spécialisées et les partager dans le chat.

**Acceptance Criteria:**
- Page `/consultations` avec types et historique
- Wizard multi-step : type → astrologue → tirage → validation
- Page résultat avec CTAs "Ouvrir dans le chat", "Sauvegarder"

[Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]

### Story 16.6: Settings Pages — Compte, Abonnement, Usage

As a utilisateur,
I want accéder à mes paramètres de compte, abonnement et usage dans des pages dédiées,
So that je puisse gérer mon profil et mes données facilement.

**Acceptance Criteria:**
- Page `/settings` avec sous-routes account, subscription, usage
- Double confirmation pour suppression compte
- Migration des composants existants (BillingPanel, PrivacyPanel)

[Source: _bmad-output/implementation-artifacts/16-6-settings-pages.md]

### Story 16.7: Admin Pages — Pricing, Monitoring, Personas

As a utilisateur ops/admin,
I want accéder à des pages d'administration dédiées,
So that je puisse gérer les tarifs, le monitoring et les personas astrologues.

**Acceptance Criteria:**
- Protection RoleGuard pour ops/admin uniquement
- Hub `/admin` avec navigation
- Sous-pages : pricing, monitoring, personas, reconciliation
- Migration des composants existants

[Source: _bmad-output/implementation-artifacts/16-7-admin-pages.md]

### Story 16.8: Correction du parcours Thème Natal

As a utilisateur souhaitant générer son thème natal,
I want un parcours fluide de saisie des données de naissance avec gestion claire des erreurs et accessibilité depuis plusieurs points d'entrée,
So that je puisse compléter mes informations sans friction et comprendre les problèmes éventuels.

**Acceptance Criteria:**
- Message d'alerte clair si données de naissance manquantes (pas d'ID de requête technique)
- Lien vers `/profile` depuis : menu navigation, page `/natal`, page `/settings`
- Champs ville + pays séparés avec géocodage Nominatim transparent
- Feedback utilisateur si ville/pays introuvable
- Fuseau horaire détecté automatiquement (timezone utilisateur ou UTC par défaut)
- Sélection du fuseau horaire via liste déroulante avec recherche
- Correction du bug de validation des données de naissance
- Suppression de l'affichage des request_id côté utilisateur (log console uniquement)

[Source: _bmad-output/implementation-artifacts/16-8-correction-parcours-theme-natal.md]

## Epic 19: Comment lire ton thème natal dans l'app

Rendre la lecture du thème natal explicite et traçable dans l'interface, avec une pédagogie claire sur les signes, les maisons, les planètes, et les conventions de calcul.

### Story 19.1: Guide de lecture du thème natal dans l'app

As a utilisateur qui consulte son thème natal,
I want une section claire "Comment lire ton thème natal dans l'app" avec conventions explicites et exemples concrets,
So that je comprenne pourquoi chaque planète est affichée dans un signe et une maison donnés.

**Acceptance Criteria:**
- Explication claire des 3 briques: signes, maisons, planètes
- Exemple de conversion exact: `Soleil 34.08° -> Taureau 4°05'`
- Convention de maisons `[debut, fin)` explicitée
- Exemple de wrap maison (`348.46° -> 18.46°`) documenté
- Mode sans heure de naissance explicite: ascendant non calculé
- Métadonnées visibles: date/heure de génération, version référentiel, version ruleset, système de maisons
- Cohérence visuelle et métier entre liste des planètes et roue des maisons

[Source: _bmad-output/implementation-artifacts/19-1-comment-lire-ton-theme-natal-dans-l-app.md]
