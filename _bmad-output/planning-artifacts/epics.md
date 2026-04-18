---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
inputDocuments:
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\prd.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\architecture.md'
  - 'C:\dev\horoscope_front\_bmad-output\planning-artifacts\ux-design-specification.md'
  - 'C:\dev\horoscope_front\docs\llm-prompt-generation-by-feature.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\66-45-vue-catalogue-canonique-prompts-actifs.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\66-46-vue-detail-resolved-prompt-assembly.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\67-1-clarifier-modes-preview-et-statuts-placeholders.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\67-2-exposer-construction-logique-graphe-inspectable.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\67-3-refondre-vue-detail-zones-pedagogiques-operables.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\68-1-definir-modele-admin-sample-payloads-par-feature.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\68-2-rendre-runtime-preview-avec-sample-payload.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\68-3-gerer-sample-payloads-depuis-surface-admin.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\69-1-executer-manuellement-cible-canonique-depuis-sample-payload.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\69-2-afficher-retour-llm-brut-structure-metadonnees-execution.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\69-3-securiser-surface-execution-manuelle-et-qa.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\67-To-69-deferred-work.md'
  - 'C:\dev\horoscope_front\_bmad-output\implementation-artifacts\70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md'
  - 'user-specification-inline-admin-prompts-ux-refactor-2026-04-18'
lastEdited: '2026-04-18'
editHistory:
  - date: '2026-02-21T14:39:07+01:00'
    changes: 'Epics rebaseline after PRD/Architecture finalization (FR38-42 + NFR SMART alignment)'
  - date: '2026-04-06'
    changes: 'Ajout Epic 66 — Refactorisation orchestration LLM vers contrats explicites'
  - date: '2026-04-16'
    changes: 'Ajout des epics/stories admin LLM preview runtime sample payloads et execution controlee'
  - date: '2026-04-18'
    changes: 'Extraction des exigences ciblees pour la refonte UX/UI de /admin/prompts a partir des stories 67-69, du plan UX fourni par Cyril et des contraintes PRD/Architecture'
  - date: '2026-04-18'
    changes: 'Clarifications step-01: legacy/release/consumption en routes dediees; schema visuel LLM explicite ajoute aux exigences'
  - date: '2026-04-18'
    changes: 'Step-02 approuve: ajout Epic 70 et couverture FR43-FR51'
  - date: '2026-04-18'
    changes: 'Step-03: generation initiale des stories de l Epic 70'
  - date: '2026-04-18'
    changes: 'Epic 70 enrichi avec edition des prompts via formulaires et historisation des sauvegardes'
  - date: '2026-04-18'
    changes: 'Clarification step-02: le schema visuel LLM doit utiliser une bibliotheque React reconnue'
  - date: '2026-04-18'
    changes: 'Validation finale Epic 70: workflow de sauvegarde precise (nouvelle version draft/inactive puis publication), statut explicite des prompts et inactivation automatique de l ancienne version publiee'
  - date: '2026-04-18'
    changes: 'Story 70.5 livree : lien artefact implementation et trace dans epics (route legacy refondue)'
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
FR43: Les operations admin peuvent inspecter les prompts canoniques via une experience master-detail combinant liste filtrable et panneau detail sticky sur une meme surface.  
FR44: Les operations admin peuvent distinguer explicitement les modes `assembly preview`, `runtime preview` et `live execution` avec une semantique stable des placeholders et du rendu.  
FR45: Les operations admin peuvent lire la composition d une cible canonique dans des sections progressives comprenant au minimum resume, prompts, placeholders, retour LLM et graphe logique.  
FR46: Les operations admin peuvent selectionner, creer, modifier, dupliquer, desactiver et supprimer des sample payloads par feature/locale pour alimenter des previews runtime non sensibles.  
FR47: Les operations admin peuvent declencher une execution LLM reelle uniquement depuis une runtime preview valide et consulter le retour brut, structure et les metadonnees associees.  
FR48: Les operations admin peuvent acceder a l historique legacy, a l historique release et a la consommation comme routes dediees et univers de travail separes du catalogue canonique.  
FR49: Les operations admin peuvent executer les actions sensibles (rollback legacy, gestion sample payloads, execution manuelle) dans une zone d actions dediee avec niveau de risque et confirmation explicites.  
FR50: Les operations admin disposent d une interface `/admin/prompts` entierement coherente en francais produit, avec libelles metier stabilises et actions contextuelles explicites.  
FR51: Les operations admin peuvent consulter la chaine logique des processus LLM sous forme de schema visuel pedagogique reliant sources de composition, pipeline de transformation, donnees runtime et resultat operateur.
FR52: Les operations admin peuvent modifier les prompts canoniques via des formulaires admin guides et toute sauvegarde cree une nouvelle version historisee, comparable et auditée.

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
NFR23: La preview admin des prompts doit rester deterministe et locale, sans appel provider tant qu aucune execution manuelle explicite n a ete confirmee.  
NFR24: L interface `/admin/prompts` doit rester operable sur desktop et mobile, avec adaptation responsive des grilles denses vers des composants replis et sans styles inline.  
NFR25: 100% des controles critiques de `/admin/prompts` doivent avoir des labels visibles, des etats focus explicites, une navigation clavier complete et une semantique tabs/panels correcte, conformes a WCAG 2.1 AA.  
NFR26: Toute execution manuelle admin doit etre explicitement identifiable en UI, en audit et en observabilite, et distincte du trafic produit nominal.  
NFR27: Les surfaces de preview et d execution manuelle doivent maintenir la redaction/anonymisation des champs sensibles affiches ou renvoyes a l operateur.

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
- La taxonomie canonique `manifest_entry_id` et le quatuor `feature/subfeature/plan/locale` restent la verite nominale de `/admin/prompts`; ne pas reintroduire `use_case` comme axe principal d exploration.
- La refonte UX/UI de `/admin/prompts` doit preserver les capacites deja livrees par les stories 67.1 a 69.3: semantique des modes preview, graphe logique, preview runtime via sample payload, CRUD sample payloads, execution manuelle, retour LLM, audit et observabilite.
- La separation fonctionnelle entre `catalogue`, `legacy`, `release`, `consumption`, `personas` et `echantillons runtime` doit etre maintenue, mais le catalogue ne doit plus porter l ergonomie des autres univers.
- `legacy`, `release` et `consumption` doivent evoluer vers des routes dediees plutot qu etre conserves comme simples sous-onglets du catalogue.
- Les previews et executions admin doivent reutiliser les endpoints et pipelines existants (`resolved`, sample payloads, `execute-sample`, gateway nominal) sans moteur parallele ad hoc cote frontend.
- Les actions sensibles de l interface admin doivent etre regroupees dans des surfaces dediees, confirmees explicitement et alimentees par les garde-fous backend existants.
- La mise en oeuvre frontend doit rester conforme aux regles du monorepo: React/TypeScript, CSS dedie sans style inline, reutilisation des variables et tokens admin existants.
- L edition des prompts doit creer une nouvelle version historisee a chaque sauvegarde, sans ecrasement silencieux de la version precedente, et rester compatible avec les mecanismes existants de diff, rollback, audit et publication.
- Le workflow d edition des prompts suit obligatoirement la sequence `creation d une nouvelle version draft/inactive -> publication explicite -> passage automatique de l ancienne version publiee au statut inactive`.
- Le schema visuel LLM doit etre rendu via une bibliotheque React connue et maintenable (par exemple React Flow), plutot qu un rendu artisanal ad hoc.

### UX Design Requirements

UX-DR1: La page `/admin/prompts` doit etre restructuree autour d un vrai mode master-detail avec liste canonique filtrable a gauche et panneau detail sticky a droite sur desktop.  
UX-DR2: Le catalogue canonique doit etre simplifie a 4 ou 5 colonnes de premier niveau maximum (`tuple`, `snapshot actif`, `provider/modele`, `sante`, `action`) et deporter les metadonnees secondaires dans le detail.  
UX-DR3: Les filtres du catalogue doivent devenir une barre compacte avec labels visibles, chips actives, bouton `Reinitialiser` et section `Filtres avances` repliable.  
UX-DR4: Le panneau detail doit etre recompose en sections progressives dans l ordre `Resume`, `Mode d inspection`, `Etat d execution`, `Prompts`, `Placeholders`, `Retour LLM`, `Graphe logique`.  
UX-DR5: Les blocs textuels longs du detail doivent etre affiches via accordions, onglets secondaires ou mecanismes de repli equivalents afin d eviter l ecrasement visuel.  
UX-DR6: Les actions sensibles (`Executer avec le LLM`, rollback legacy, gestion des sample payloads) doivent etre regroupees dans une zone `Actions` distincte des contenus de lecture, avec niveau de risque visible.  
UX-DR7: Tous les libelles de la page doivent etre harmonises en francais produit coherent, avec suppression des intitulés techniques ambigus et des libelles errones du type `Ouvrir 66.46`.  
UX-DR8: Les tabs et panneaux de `/admin/prompts` doivent etre semantiquement complets (`tablist`, `tab`, `tabpanel`, associations explicites) et utilisables integralement au clavier.  
UX-DR9: Les grilles et tables denses doivent se replier proprement sur mobile en cartes, panneaux empiles ou sections collapsibles sans perte des informations critiques.  
UX-DR10: Les etats `loading`, `error`, `empty`, `preview partielle`, `runtime incomplete` et `execution en cours` doivent etre de premier rang, comprehensibles sans lecture de JSON brut.  
UX-DR11: La logique LLM doit etre rendue sous forme de schema visuel lisible et pedagogique, avec noeuds et relations explicites plutot qu une simple liste textuelle.  
UX-DR12: `legacy`, `release` et `consumption` doivent etre accessibles par navigation dediee (routes ou sous-pages) avec un modele d interaction adapte a leur usage propre, et non plus comme extensions du catalogue.  
UX-DR13: L edition des prompts doit se faire via des formulaires guides et comprehensibles, avec champs structures, validation explicite, resume des changements et confirmation de creation d une nouvelle version historisee.  
UX-DR14: Le statut de chaque prompt doit etre visible explicitement dans l interface (`draft`, `inactive`, `published` ou equivalent stabilise) et le workflow de publication doit etre comprehensible sans connaissance technique.
UX-DR13: Le schema visuel LLM doit utiliser une bibliotheque React reconnue pour garantir lisibilite, interactivite, maintenabilite et comportement responsive/accessible.

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
FR43: Epic 70 - catalogue admin prompts en master-detail operable  
FR44: Epic 70 - clarification explicite des modes preview et execution  
FR45: Epic 70 - detail progressif de la cible canonique  
FR46: Epic 70 - gestion operable des sample payloads  
FR47: Epic 70 - execution manuelle depuis runtime preview valide  
FR48: Epic 70 - univers legacy, release et consommation en routes dediees  
FR49: Epic 70 - zone d actions sensibles dediee et confirmee  
FR50: Epic 70 - harmonisation complete des libelles FR de la surface admin prompts  
FR51: Epic 70 - schema visuel des processus LLM  
FR52: Epic 70 - edition formulaire des prompts et historisation des sauvegardes

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

### Epic 70: Refonte UX/UI operable de l espace Admin Prompts LLM
Permettre aux equipes ops/admin d explorer, comprendre, previsualiser et executer les prompts canoniques via une interface plus ergonomique, plus lisible et plus sure, organisee autour d un master-detail, de routes dediees pour les univers secondaires, et d un schema visuel explicite des processus LLM rendu avec une bibliotheque React dediee.
**FRs covered:** FR43, FR44, FR45, FR46, FR47, FR48, FR49, FR50, FR51, FR52

### Epic 12: Profil natal — saisie des donnees de naissance et generation du theme
Permettre a l utilisateur de renseigner ses donnees de naissance depuis le frontend et de declencher la generation de son theme natal, avec feedback adequat pendant le calcul.
**FRs covered:** FR10, FR11, FR14

### Epic 29: Interprétation Natale via LLMGateway
Brancher le parcours d'interprétation natale sur l'infrastructure LLMGateway avec gestion des personas, validation AstroResponse_v1 et observabilité.
**FRs covered:** FR15, FR22, FR23, FR35, FR36

### Epic 30: Configuration Flexible des Modèles LLM
Permettre de surcharger les modèles LLM utilisés par chaque service via des variables d'environnement pour faciliter le testing et l'optimisation des coûts/qualité sans modifier la base de données.
**FRs covered:** FR36, FR37, NFR16

### Story 30.8: Mise à niveau globale de l’interprétation thème natal (GPT-5 / Responses API / Structured Outputs)

As a product and tech team,
I want industrialiser le flux `natal_interpretation` avec un contrat strict Structured Outputs, une gestion des disclaimers hors LLM et un contrôle evidence côté serveur,
So that la qualité premium augmente, les coûts tokens baissent et les erreurs de validation disparaissent en production.

**Acceptance Criteria:**
- Aucune réponse LLM ne contient de disclaimer textuel généré; le disclaimer est géré côté application.
- Tous les appels `natal_interpretation` utilisent un payload Responses conforme au format JSON Schema strict.
- Les réponses finales passent la validation schéma en mode strict.
- Le mode erreur renvoie une structure valide strictement compatible avec le schéma.
- Les réponses complètes respectent des minima de densité (summary, sections, highlights, advice).
- Le champ `evidence` final est un sous-ensemble strict de `allowed_evidence` calculé côté serveur.

[Source: _bmad-output/implementation-artifacts/30-8-mise-a-niveau-globale-interpretation-theme-natal-gpt5-responses-structured-outputs.md]

### Story 30.9: Historique multi-interprétations, suppression traçable et export PDF templatisable

## Epic 70: Refonte UX/UI operable de l espace Admin Prompts LLM

Permettre aux equipes ops/admin d explorer, comprendre, previsualiser et executer les prompts canoniques via une interface plus ergonomique, plus lisible et plus sure, organisee autour d un master-detail, de routes dediees pour les univers secondaires, et d un schema visuel explicite des processus LLM rendu avec une bibliotheque React dediee.

### Story 70.1: Reorganiser la navigation admin prompts en routes dediees

As a admin ops,
I want acceder a des routes dediees pour le catalogue, le legacy, le release et la consommation,
So that chaque univers de travail ait une navigation claire et un modele d interaction adapte.

**Acceptance Criteria:**

**Given** l utilisateur admin accede a l espace prompts
**When** il navigue entre les univers `catalogue`, `legacy`, `release`, `consumption`, `personas` et `echantillons runtime`
**Then** chaque univers est accessible via une route dediee stable
**And** la navigation active indique clairement la section courante sans melanger les contenus dans un seul ecran.

**Given** l univers `catalogue`
**When** il est affiche
**Then** il ne porte plus les contenus `legacy`, `release` et `consumption`
**And** ces contenus ne sont plus relies a la logique interne du tableau catalogue.

**Given** un lien profond existant vers `/admin/prompts`
**When** la refonte est livree
**Then** la route catalogue reste accessible
**And** les nouvelles routes dediees sont atteignables sans casser l acces admin existant.

### Story 70.2: Refaire le catalogue canonique en mode master-detail

As a admin ops,
I want un catalogue canonique simplifie avec liste filtrable et panneau detail sticky,
So that je puisse inspecter rapidement une cible sans perdre le contexte de la selection.

**Acceptance Criteria:**

**Given** l admin ouvre la route catalogue prompts
**When** la page charge sur desktop
**Then** la surface affiche une liste canonique filtrable a gauche et un panneau detail sticky a droite
**And** la selection courante reste visible pendant la lecture du detail.

**Given** le tableau catalogue
**When** il est affiche
**Then** il n expose que les colonnes de premier niveau `tuple`, `snapshot actif`, `provider/modele`, `sante` et `action`
**And** les metadonnees secondaires sont reservees au panneau detail.

**Given** les filtres catalogue
**When** l admin les utilise
**Then** ils sont presentes dans une barre compacte avec labels visibles
**And** les filtres actifs sont resumes visuellement
**And** un bouton `Reinitialiser` et une zone `Filtres avances` repliable sont disponibles.

**Artefact d’implémentation :** [`70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md`](../implementation-artifacts/70-2-refaire-le-catalogue-canonique-en-mode-master-detail.md) — statut **done** (2026-04-18) ; implémentation master-detail + filtres + tests Vitest ; revues code (correctifs a11y / reset / assertion layout) puis 2ᵉ passe sans finding résiduel.

### Story 70.3: Recomposer le detail prompts en lecture progressive et zone d actions

As a admin ops,
I want un detail structure en sections progressives et une zone d actions dediee,
So that je distingue immediatement ce que je lis de ce que je peux executer.

**Acceptance Criteria:**

**Given** une cible canonique est selectionnee
**When** le panneau detail est rendu
**Then** les sections apparaissent dans l ordre `Resume`, `Mode d inspection`, `Etat d execution`, `Prompts`, `Placeholders`, `Retour LLM`, `Graphe logique`
**And** cette hierarchie est stable quel que soit le mode de preview.

**Given** les blocs de texte longs du detail
**When** ils depassent un volume de lecture confortable
**Then** ils sont presentes dans des accordions, onglets secondaires ou sections repliables equivalentes
**And** la page reste lisible sans scroll excessif dans un seul bloc.

**Given** des actions sensibles sont disponibles
**When** le detail est affiche
**Then** elles sont regroupees dans une zone `Actions` distincte du contenu de lecture
**And** le niveau de risque et les preconditions d execution sont explicitement visibles.

### Story 70.4: Rendre le schema visuel des processus LLM avec React Flow

As a admin ops,
I want un schema visuel interactif des processus LLM,
So that je comprenne rapidement la chaine de composition et les dependances runtime sans parser du texte brut.

**Acceptance Criteria:**

**Given** une cible canonique est ouverte dans le detail
**When** la section `Graphe logique` est affichee
**Then** elle rend un schema visuel avec une bibliotheque React reconnue
**And** la bibliotheque retenue est `React Flow` ou equivalent de meme niveau de robustesse.

**Given** le schema visuel
**When** il est rendu
**Then** il relie au minimum `manifest_entry_id`, `composition_sources`, `transformation_pipeline`, `provider_messages`, `runtime inputs` et le resultat operateur
**And** il distingue visuellement templates, policy, execution profile, sample payloads et fallbacks.

**Given** la densite du graphe devient trop forte ou le rendu est contraint
**When** le composant ne peut plus rester lisible
**Then** un fallback texte ou une vue simplifiee reste disponible
**And** aucune information critique n est perdue pour l operateur.

### Story 70.5: Refondre la route legacy pour la comparaison et le rollback

As a admin ops,
I want une route legacy dediee avec comparaison et rollback plus lisibles,
So that je puisse investiguer l historique legacy sans polluer l experience du catalogue canonique.

**Acceptance Criteria:**

**Given** l admin ouvre la route legacy
**When** la page charge
**Then** l univers legacy est presente comme un ecran autonome avec son propre contexte de lecture
**And** le choix du use case et des versions a comparer est immediatement comprehensible.

**Given** l admin compare deux versions legacy
**When** il ouvre le diff
**Then** le diff est lisible, clairement annote et dissocie de l inspection canonique
**And** les actions de rollback sont presentes dans une zone dediee.

**Given** une action de rollback legacy est disponible
**When** l admin la declenche
**Then** la confirmation explicite reste obligatoire
**And** le libelle de l action et ses consequences sont formules en francais produit coherent.

**Artefact d’implémentation :** [`70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md`](../implementation-artifacts/70-5-refondre-la-route-legacy-pour-la-comparaison-et-le-rollback.md) — statut **done** (2026-04-18) ; surface `admin-prompts-legacy` (en-tête, toolbar cas d’usage, liste versions, diff annoté avec métadonnées, modale restauration FR) ; i18n titres d’en-tête de page FR / EN / ES ; tests Vitest (`AdminPromptsPage`, `AdminPromptsRouting`) ; revue code (kicker hors `dl`, alignement ES).

### Story 70.6: Refondre la route release pour l investigation snapshot

As a admin ops,
I want une route release dediee pour la timeline et les diffs de snapshots,
So that je puisse comprendre l historique de release sans naviguer dans le catalogue principal.

**Acceptance Criteria:**

**Given** l admin ouvre la route release
**When** la page charge
**Then** la timeline snapshots est affichee dans une interface autonome orientee investigation
**And** les preuves, statuts et changements sont hierarchises visuellement.

**Given** l admin compare deux snapshots
**When** il ouvre le diff
**Then** les changements assembly, execution profile et output contract sont lisibles sans ambiguite
**And** les actions de navigation vers le catalogue utilisent un libelle contextuel coherent en francais.

**Given** un bouton de navigation vers une cible canonique est affiche
**When** l admin l active
**Then** il ouvre le detail catalogue approprie
**And** aucun libelle parasite ou numerique ambigu de type `Ouvrir 66.46` n apparait.

### Story 70.7: Refondre la route consommation pour le pilotage operable

As a admin ops,
I want une route consommation dediee plus claire pour les vues, filtres et drill-down,
So that je puisse analyser les usages LLM sans surcharge cognitive.

**Acceptance Criteria:**

**Given** l admin ouvre la route consommation
**When** la page charge
**Then** les vues `utilisateur`, `abonnement` et `feature/subfeature` sont presentes dans un ecran autonome
**And** les filtres temporels, la granularite et l export sont clairement regroupes.

**Given** la table de consommation
**When** elle est rendue sur mobile ou sur largeur contrainte
**Then** elle se replie en composants lisibles sans perdre l acces au drill-down
**And** les actions `Voir logs recents` restent disponibles.

**Given** un drill-down de consommation est ouvert
**When** l admin consulte les appels recents
**Then** les logs correles sont affiches dans une presentation claire et distincte de la table d agregats
**And** l operateur conserve son contexte de filtre courant.

### Story 70.8: Harmoniser les libelles, l accessibilite et le responsive de la surface admin prompts

As a admin ops,
I want une interface admin prompts coherente, accessible et responsive,
So that je puisse l utiliser efficacement sur tous les ecrans et avec les technologies d assistance.

**Acceptance Criteria:**

**Given** les controles critiques de l espace admin prompts
**When** ils sont rendus
**Then** ils ont tous des labels visibles et des etats focus explicites
**And** la navigation clavier couvre les tabs, panneaux, formulaires et actions sensibles.

**Given** l ensemble des routes de l epic 70
**When** elles sont relues
**Then** les libelles sont harmonises en francais produit coherent
**And** les termes techniques bruts ou ambigus sont remplaces par des formulations metier stables.

**Given** la surface est ouverte sur mobile ou largeur reduite
**When** les composants master-detail, tableaux et panneaux deviennent contraints
**Then** ils se replient proprement en sections empilees ou collapsibles
**And** l interface reste conforme aux exigences WCAG 2.1 AA et sans style inline.

### Story 70.9: Editer les prompts canoniques via des formulaires admin guides

As a admin ops,
I want modifier les prompts canoniques depuis des formulaires structures,
So that je puisse faire evoluer les contenus sans passer par des editions brutes ou ambiguës.

**Acceptance Criteria:**

**Given** une cible canonique editable est ouverte
**When** l admin choisit `Modifier le prompt`
**Then** un formulaire guide s ouvre avec les champs pertinents structures
**And** les blocs editables sont distingues clairement des metadonnees non editables.

**Given** le formulaire d edition
**When** l admin modifie un ou plusieurs champs
**Then** les validations de forme et de coherence sont explicites
**And** les erreurs sont affichees en francais produit avant toute sauvegarde.

**Given** l admin prepare une sauvegarde
**When** il relit son edition
**Then** un resume des changements et de la portee de la modification est visible
**And** l action de sauvegarde est distincte des autres actions sensibles de la page.

**Given** l admin sauvegarde une modification de prompt
**When** la sauvegarde reussit
**Then** une nouvelle version est creee avec un statut explicite `draft` ou `inactive` non publie
**And** la version actuellement publiee reste active tant qu aucune publication explicite n a ete confirmee.

### Story 70.10: Historiser, comparer et auditer chaque sauvegarde de prompt

As a admin ops,
I want que chaque sauvegarde de prompt cree une nouvelle version historisee, comparable et auditée,
So that je puisse revenir sur une modification et comprendre quand, pourquoi et par qui elle a ete effectuee.

**Acceptance Criteria:**

**Given** un prompt est sauvegarde depuis le formulaire admin
**When** la sauvegarde reussit
**Then** une nouvelle version historisee est creee
**And** la version precedente n est jamais ecrasee silencieusement.

**Given** une nouvelle version vient d etre creee
**When** l admin consulte l historique du prompt
**Then** il voit au minimum la date, l auteur, le statut et un acces au diff avec la version precedente
**And** cette version est exploitable par les mecanismes existants de comparaison et rollback.

**Given** une sauvegarde de prompt est effectuee
**When** l operation est journalisee
**Then** un audit event persistant est cree avec les metadonnees utiles
**And** la surface admin confirme visuellement qu une nouvelle version historisee a ete enregistree.

**Given** l admin publie explicitement une nouvelle version de prompt
**When** la publication est confirmee
**Then** la nouvelle version passe au statut `published`
**And** l ancienne version qui etait `published` passe automatiquement au statut `inactive`.

**Given** l historique des versions d un prompt
**When** il est affiche
**Then** le statut de chaque version est visible explicitement
**And** il n existe jamais plus d une version `published` simultanement pour un meme prompt canonique.

As a utilisateur,
I want pouvoir basculer entre mes interprétations SHORT/COMPLETE, sélectionner une version précise, supprimer une interprétation et télécharger un PDF personnalisable,
So that je garde le contrôle de mon historique et je peux exporter un rendu premium adapté à mes besoins.

**Acceptance Criteria:**
- Si plusieurs interprétations existent pour un même thème natal, l’UI affiche un sélecteur de niveau (short/complete) et un menu listant les versions disponibles (horodatées, persona, module éventuel).
- L’utilisateur peut afficher n’importe quelle interprétation existante sans regénération LLM et sans perte de contexte de page.
- L’UI propose un bouton de suppression de l’interprétation affichée avec confirmation explicite; la suppression est effective en backend et la liste est rafraîchie.
- Chaque suppression est journalisée avec traçabilité opérationnelle: acteur, ressource, horodatage, type d’action, request_id.
- Le backend expose un moteur d’export PDF pour une interprétation sélectionnée avec au moins un template actif.
- Les templates PDF sont administrables (CRUD + activation/désactivation + version), et l’utilisateur peut choisir un style/template avant téléchargement.
- Le bouton de téléchargement PDF est disponible sur la page Natal; le fichier généré contient les sections d’interprétation visibles et les mentions légales applicatives.
- Le flux respecte les garde-fous sécurité/privacy existants (auth obligatoire, RBAC admin pour gestion templates, pas de fuite de données inter-utilisateurs).

[Source: user requirements 2026-03-04]

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

## Epic 29: Interprétation Natale via LLMGateway

Brancher le parcours d'interprétation natale sur l'infrastructure LLMGateway avec gestion des personas, validation AstroResponse_v1 et observabilité.

### Story 29.1: N1 — chart_json canonique + evidence_catalog

As a service d'interprétation,
I want disposer d'un export JSON stable et d'un catalogue de preuves astrologiques,
So that le gateway LLM reçoive des données structurées et ancrées pour l'interprétation.

**Acceptance Criteria:**
- Fonction `build_chart_json` produit un dictionnaire stable avec meta, planets, houses, aspects, angles.
- Mode dégradé (no_time, no_location) géré avec angles null.
- `longitude_in_sign` et `sign` calculés correctement pour chaque corps.
- Fonction `build_evidence_catalog` produit des IDs UPPER_SNAKE_CASE conformes au pattern regex.
- Couverture de tests unitaires >= 90%.

[Source: docs/agent/story-29-N1-chart-json-canon.md]

### Story 29.2: N2 — NatalInterpretationServiceV2 + Endpoint

As a utilisateur,
I want demander une interprétation natale (SIMPLE ou COMPLETE) via un nouvel endpoint,
So that je bénéficie de l'orchestration LLMGateway avec gestion des personas et fallbacks.

**Acceptance Criteria:**
- Endpoint `POST /v1/natal/interpretation` implémenté.
- Support des niveaux `short` (SIMPLE) et `complete` (COMPLETE).
- Résolution du persona_name en DB avant appel Gateway pour le mode COMPLETE.
- Injection automatique du `chart_json` et `evidence_catalog` dans l'appel Gateway.
- Fallback automatique COMPLETE -> SHORT géré par le gateway.
- Tests d'intégration validant les contrats API.

[Source: docs/agent/story-29-N2-natal-interpretation-gateway.md]

### Story 29.3: N3 — Prompts DB + lint + publish

As a product owner,
I want gérer les prompts d'interprétation natale en base de données,
So that je puisse itérer sur le contenu sans redéployer le code.

**Acceptance Criteria:**
- Script de seed pour les contrats et prompts `natal_interpretation` et `short`.
- Linting des prompts natals (vérification des placeholders {{chart_json}}, etc.).
- Publication en DB via script d'admin.
- Validation des contrats avec `AstroResponse_v1`.

[Source: docs/agent/story-29-N3-prompts-db-publish.md]

### Story 29.4: N4 — UI AstroResponse_v1 + upsell

As a utilisateur,
I want voir mon interprétation natale structurée dans l'UI avec une option d'upgrade,
So that je profite d'une lecture claire et je découvre les avantages du mode Premium.

**Acceptance Criteria:**
- Composant `NatalInterpretation` affichant titre, résumé, sections, highlights et conseils.
- Gestion du chargement avec Skeleton.
- CTA Upsell visible après une interprétation SHORT.
- Sélectionneur de persona pour le passage en mode COMPLETE.
- Navigation fluide entre le thème brut et l'interprétation.

[Source: docs/agent/story-29-N4-ui-rendu-upsell.md]

### Story 29.5: N5 — Eval fixtures + publish gate

As a QA engineer,
I want valider la qualité de l'interprétation via des fixtures de test et une gate de publication,
So that aucune régression qualitative n'atteigne la production.

**Acceptance Criteria:**
- Jeu de fixtures YAML couvrant les cas (full chart, no time, no location, minimal).
- Test de validation via `eval_harness.py` sur les sorties LLM.
- Gate de publication bloquant si le taux de succès < 80%.
- Traces d'évaluation disponibles pour analyse.

[Source: docs/agent/story-29-N5-eval-fixtures-gate.md]

## Epic 39: Versionning métier explicite du ruleset de prédiction

Supprimer l'ambiguïté entre `reference_version` et `ruleset_version` dans la pile de prédiction quotidienne, en introduisant un ruleset canonique aligné sur la référence active, sans casser les données historiques ni les jobs existants.

**FRs covered:** FR6, FR7, FR8, FR18, FR36, FR37, NFR17, NFR22

### Story 39.1: Introduire un ruleset canonique 2.0.0 et préserver la rétrocompatibilité

As a platform engineer,
I want créer un ruleset canonique `2.0.0` rattaché à la référence `2.0.0` sans supprimer le ruleset legacy `1.0.0`,
So that la plateforme dispose d'un versionning métier lisible tout en restant compatible avec l'historique et les environnements locaux existants.

**Acceptance Criteria:**
- Un nouveau ruleset `2.0.0` est seedé en base avec le même contenu fonctionnel initial que le ruleset `1.0.0`.
- Le ruleset legacy `1.0.0` reste lisible pour les runs, calibrations et artefacts déjà persistés.
- Le seed/runtime empêche la création ambiguë de plusieurs rulesets actifs non documentés pour la même référence.
- Les services lisant les rulesets continuent à fonctionner avec `1.0.0` et `2.0.0` pendant la phase de transition.

[Source: user request 2026-03-08; backend/scripts/seed_31_prediction_reference_v2.py; docs/calibration/dataset-spec.md]

### Story 39.2: Basculer la configuration runtime et centraliser les versions actives

As a backend maintainer,
I want centraliser les versions actives de prédiction et basculer la configuration par défaut vers le ruleset canonique,
So that les environnements local/dev/test n'utilisent plus de paire de versions ambiguë ou implicite.

**Acceptance Criteria:**
- La configuration active de prédiction est centralisée dans un point unique réutilisable par les services, jobs et tests.
- `backend/.env.example` et la documentation runtime exposent explicitement la paire active supportée.
- Les services de prédiction quotidienne, de calibration et de QA consomment la source de vérité centrale plutôt que des strings dispersées.
- Une incohérence runtime entre ruleset actif et référence active est détectable explicitement.

[Source: user request 2026-03-08; backend/app/core/config.py; backend/README.md]

### Story 39.3: Migrer les jobs, fixtures et tests vers le nouveau versionning métier

As a QA and data engineer,
I want réaligner les seeds, fixtures, jobs de calibration et suites de test sur le nouveau ruleset canonique,
So that la validation automatique reflète le contrat métier cible sans dépendre d'une dette de nommage historique.

**Acceptance Criteria:**
- Les jobs de calibration et de QA utilisent la source de vérité centrale pour résoudre `reference_version` / `ruleset_version`.
- Les tests backend et les fixtures critiques n'utilisent plus de strings dispersées quand une constante de version active existe.
- Les suites ciblées de daily prediction restent vertes après la bascule.
- Les cas legacy nécessaires continuent à couvrir la lecture de données `1.0.0`.

[Source: user request 2026-03-08; backend/app/jobs/calibration/natal_profiles.py; backend/app/tests/integration/test_daily_prediction_qa.py]

### Story 39.4: Documenter, monitorer et déprécier le ruleset legacy

As a product operations lead,
I want documenter la transition de versionning et tracer l'usage du ruleset legacy,
So that l'équipe peut piloter la bascule vers le ruleset canonique puis planifier proprement la dépréciation du legacy.

**Acceptance Criteria:**
- La documentation backend/calibration/QA explique clairement la relation entre référence `2.0.0`, ruleset canonique et ruleset legacy.
- Les environnements non prod disposent d'un runbook de transition simple.
- L'observabilité permet d'identifier si des calculs ou jobs utilisent encore le ruleset legacy.
- Une stratégie de dépréciation explicite du ruleset legacy est écrite, sans suppression immédiate des données historiques.

[Source: user request 2026-03-08; docs/qa/daily-prediction-qa-report-2026-03-08.md; backend/README.md]

## Epic 41: Fenêtres décisionnelles intraday pour la prédiction quotidienne

Transformer la timeline intraday de la prédiction quotidienne en un produit réellement orienté décision utilisateur: moins de bruit, moins de répétition, et des moments de la journée clairement exploitables pour agir, temporiser, communiquer ou éviter un mauvais timing.

**FRs covered:** FR16, FR18, FR36, FR37, NFR17, NFR22

### Story 41.1: Réaligner la taxonomie et la hiérarchie des événements intraday

As a backend maintainer,
I want aligner les `event_type`, priorités et poids entre le seed ruleset et le moteur runtime,
So that le moteur sache distinguer un vrai signal intraday d'un simple bruit technique et que les pivots forts reposent sur une hiérarchie cohérente.

**Acceptance Criteria:**
- Les types d'événements utilisés par `EventDetector` correspondent explicitement aux types seedés dans le ruleset actif, sans fallback silencieux systématique vers `priority=50` / `base_weight=1.0`.
- Les priorités différencient clairement les événements structurants (`exact`, ingressions majeures) des événements secondaires (`enter_orb`, `exit_orb`, `planetary_hour_change`).
- Un événement secondaire isolé ne peut plus, à lui seul, produire un pivot “critique” utilisateur.
- Des tests unitaires et d'intégration valident la cohérence seed/runtime et la hiérarchie de priorité.

[Source: audit produit 2026-03-09; backend/app/prediction/event_detector.py; backend/scripts/seed_31_prediction_reference_v2.py]

### Story 41.2: Propager l'influence temporelle des événements sur de vraies fenêtres utiles

As a prediction engine designer,
I want étaler l'influence d'un événement sur une fenêtre temporelle montante / culminante / descendante au lieu d'un seul pas de 15 minutes,
So that les tendances intraday reflètent des créneaux réellement exploitables par l'utilisateur plutôt que des impulsions ponctuelles difficiles à interpréter.

**Acceptance Criteria:**
- Les contributions d'un événement ne sont plus affectées uniquement au `nearest_step_index`; elles se propagent sur plusieurs steps selon un profil temporel déterministe.
- Les aspects exacts ont une influence plus durable que les événements secondaires.
- Les scores intraday par catégorie montrent une montée, un pic et une retombée quand un événement significatif traverse la journée.
- La logique reste déterministe, testable et compatible avec le debug explainability.

[Source: audit produit 2026-03-09; backend/app/prediction/engine_orchestrator.py; backend/app/prediction/temporal_sampler.py]

### Story 41.3: Remplacer la timeline rigide par des fenêtres décisionnelles et des pivots filtrés

As a product owner de la fonctionnalité daily prediction,
I want que le moteur produise quelques fenêtres décisionnelles fortes et des pivots filtrés par valeur utilisateur,
So that l'utilisateur voit clairement quand agir, attendre, communiquer ou éviter une décision, sans être noyé par des changements mineurs.

**Acceptance Criteria:**
- Le découpage intraday n'est plus fondé sur une grille horaire fixe par défaut; les blocs sont fusionnés tant que le signal reste équivalent.
- Les pivots sont détectés à partir du signal brut ou semi-brut pertinent, pas seulement via des différences de notes entières arrondies.
- L'API expose un nombre limité de fenêtres décisionnelles de forte valeur, avec type (`favorable`, `prudence`, `pivot`) et niveau de confiance.
- Le “meilleur créneau” est choisi via un score d'actionnabilité, pas seulement un recouvrement avec le top 3 global.

[Source: audit produit 2026-03-09; backend/app/prediction/block_generator.py; backend/app/prediction/turning_point_detector.py; backend/app/prediction/editorial_builder.py]

### Story 41.4: Recentrer le contrat API et l'UI TodayPage sur l'aide à la décision

As a utilisateur consultant `/dashboard`,
I want voir quelques fenêtres claires avec des libellés actionnables et des drivers humanisés,
So that je comprenne rapidement à quels moments de la journée lancer une action, prendre une décision ou rester prudent.

**Acceptance Criteria:**
- Le contrat `/v1/predictions/daily` expose des champs lisibles et stables pour les fenêtres décisionnelles et leurs drivers principaux.
- Les labels techniques (`enter_orb`, etc.) ne sont plus visibles dans le rendu utilisateur final.
- `TodayPage` met visuellement en avant 3 à 6 fenêtres maximum, avec hiérarchie claire, ton exploitable et messages orientés action.
- La timeline détaillée historique peut subsister, mais comme vue secondaire et non comme élément principal de décision.

[Source: audit produit 2026-03-09; frontend/src/components/prediction/TurningPointsList.tsx; frontend/src/utils/predictionI18n.ts; frontend/src/pages/TodayPage.tsx]

### Story 41.5: Valider la qualité produit intraday avec un budget de bruit explicite

As a QA engineer,
I want mesurer automatiquement la qualité décisionnelle de la sortie intraday,
So that les futures itérations n'introduisent pas de timeline bruyante, répétitive ou non exploitable pour l'utilisateur.

**Acceptance Criteria:**
- Une suite de fixtures et cas QA couvre plusieurs journées contrastées avec attentes explicites sur le nombre de pivots et de fenêtres.
- Un budget de bruit est défini et testé automatiquement (ex: max pivots critiques, max répétitions de blocs identiques, max drivers techniques visibles).
- Les rapports QA distinguent “signal utile” et “bruit intraday”.
- La décision go/no-go produit sur l'intraday peut s'appuyer sur ces indicateurs objectifs.

[Source: audit produit 2026-03-09; docs/qa/daily-prediction-qa-report-2026-03-08.md; backend/app/tests/integration/test_daily_prediction_qa.py]

### Story 41.12: Introduire une baseline utilisateur 12 mois pour la calibration relative

As a backend maintainer,
I want persister une baseline utilisateur simulée sur 12 mois par catégorie,
So that la plateforme puisse comparer une journée donnée à l’historique personnel de l’utilisateur sans recalcul coûteux à chaque requête.

**Acceptance Criteria:**
- Une baseline 12 mois par utilisateur/catégorie est stockée en base avec moyenne, écart-type, percentiles, fenêtre temporelle et versions métier.
- Le modèle de données est versionné et distinct par `reference_version`, `ruleset_version` et `house_system_effective`.
- La génération de baseline reste découplée du routeur API et du frontend.
- Les cas variance nulle, historique incomplet et baseline absente sont explicitement gérés.

[Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]

### Story 41.13: Calculer un scoring relatif journalier à partir de la baseline

As a prediction engine designer,
I want calculer des métriques relatives utilisateur pour chaque catégorie quotidienne,
So that une journée neutre puisse faire émerger des dominantes personnelles légères sans altérer le scoring absolu existant.

**Acceptance Criteria:**
- Le backend calcule au minimum `relative_z_score`, `relative_percentile` et `relative_rank` par catégorie.
- Les fallbacks couvrent variance nulle, baseline absente et échantillon insuffisant.
- Le scoring absolu existant (`note_20`, `raw_score`, `power`, `volatility`) reste inchangé.
- La logique relative est centralisée dans une couche dédiée réutilisable par service et projection publique.

[Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]

### Story 41.14: Exposer des micro-tendances sur les journées plates sans faux signaux forts

As a utilisateur consultant le daily,
I want voir quelques micro-tendances lisibles quand la journée est globalement calme,
So that je distingue une journée neutre uniforme d’une journée neutre avec quelques dominantes relatives, sans faux créneaux d’action.

**Acceptance Criteria:**
- Le contrat `/v1/predictions/daily` ajoute de façon additive `flat_day`, `relative_top_categories`, `relative_summary` et `micro_trends`.
- Une journée plate reste plate: pas de `best_window`, pas de `turning_points` publics, pas de `decision_windows`.
- Les micro-tendances restent secondaires et n’alimentent jamais la timeline décisionnelle.
- Les journées actives continuent à être pilotées par le scoring absolu et les fenêtres existantes.

[Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]

### Story 41.15: Générer et rafraîchir les baselines utilisateur de manière asynchrone

As a platform engineer,
I want générer et rafraîchir les baselines utilisateur de façon asynchrone,
So that la calibration relative soit disponible sans bloquer l’inscription ni la consultation du daily.

**Acceptance Criteria:**
- Un job peut générer la baseline après disponibilité du thème natal.
- Un refresh explicite est déclenchable lors des changements de versions métier, de `house_system_effective` ou de données natales.
- Le job est idempotent et observable.
- Le produit continue de fonctionner proprement si la baseline n’est pas encore disponible.

[Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]

### Story 41.16: Verrouiller la QA et les garde-fous produit de la calibration relative

As a QA engineer,
I want valider que la calibration relative enrichit les journées plates sans créer de faux signaux forts,
So that le daily reste honnête, lisible et conforme au budget de bruit Epic 41.

**Acceptance Criteria:**
- Les suites QA distinguent journée plate sans micro-tendance, journée plate avec micro-tendances, et journée active inchangée.
- Aucun faux `best_window`, faux `turning_point` ou wording trompeur n’est introduit.
- Le budget de bruit intraday Epic 41.5 reste respecté.
- Les cas baseline absente ou obsolète sont couverts sans dégrader le comportement nominal.

[Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]

## Epic 42: Refonte du moteur daily v3 orienté signal continu

Faire évoluer le moteur daily d'une architecture majoritairement `event-driven` vers une architecture `signal-driven`, afin de calculer d'abord des courbes astro cohérentes dans le temps, puis d'en dériver des notes, fenêtres, pivots et textes plus crédibles.

**FRs covered:** FR16, FR18, FR36, FR37, FR38, NFR17, NFR22

### Story 42.1: Formaliser le modèle de signal daily v3

As a backend architect,
I want introduire un contrat de calcul v3 explicite pour le daily,
So that le moteur puisse manipuler des couches de signal continues (`B`, `T`, `A`, `E`) sans casser immédiatement la pile v2.

**Acceptance Criteria:**
- Le backend introduit des types/schemas v3 distincts pour le signal quotidien, les métriques dérivées et les sorties intermédiaires.
- Un feature flag ou sélecteur runtime permet de choisir explicitement entre moteur v2 et moteur v3.
- Le backend supporte aussi un mode `dual` pour exécuter v2 et v3 sur une même entrée et comparer les sorties.
- `engine_version` est défini explicitement dans le cycle de vie du run.
- `engine_orchestrator` et `daily_prediction_service` peuvent accueillir le nouveau pipeline sans casser les appels existants.
- Les contrats internes v3 restent découplés du DTO public actuel.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.2: Construire la susceptibilité natale structurelle du thème

As a prediction engine designer,
I want calculer une susceptibilité natale structurelle robuste par thème,
So that la composante `B(c)` reflète réellement le thème natal au lieu d'un simple modulateur décoratif.

**Acceptance Criteria:**
- `B(c)` prend en compte au minimum maisons pertinentes, maîtres, angularité, occupation et aspects natals utiles.
- Le score natal par thème est borné, centré et explicable.
- La couche natale reste indépendante des activations de transit et intrajournalières.
- Des tests verrouillent la stabilité et l'explicabilité du calcul.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.3: Construire un climat de transit continu par thème et par pas de temps

As a prediction engine designer,
I want remplacer la logique de transit purement événementielle par une couche continue,
So that la composante `T(c,t)` exprime un fond de journée cohérent qui monte, culmine puis redescend.

**Acceptance Criteria:**
- Les transits pertinents sont évalués à chaque pas de temps avec une fonction continue d'orbe.
- `T(c,t)` prend en compte nature des corps, type d'aspect, phase et polarité contextuelle.
- Les exactitudes cessent d'être la seule source de signal fort.
- Les courbes de transit produites sont déterministes et testables.
- Un budget de performance explicite borne le coût de calcul de la couche `T`.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.4: Construire la couche d'activation intrajournalière locale

As a product owner du daily,
I want une activation locale continue à l'intérieur de la journée,
So that la composante `A(c,t)` donne du relief horaire sans traiter chaque modulateur comme un pivot.

**Acceptance Criteria:**
- `A(c,t)` intègre les activations lunaires, angulaires et de maisons locales pertinentes.
- Les signaux comme `asc_sign_change` et `planetary_hour_change` deviennent des modulateurs secondaires.
- Le résultat reste une série temporelle continue par thème.
- Les tests distinguent clairement activation locale et impulsion ponctuelle.
- Un budget de performance explicite borne le coût de calcul de la couche `A`.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.5: Repositionner les exactitudes comme couche impulsionnelle

As a backend maintainer,
I want conserver les événements ponctuels comme une couche d'accentuation locale,
So that `E(c,t)` mette en évidence les moments forts sans porter seule toute la narration quotidienne.

**Acceptance Criteria:**
- Les événements ponctuels restent détectés, mais leur rôle est borné à une accentuation locale.
- Un exact event isolé ne crée plus à lui seul un récit de journée “vivante”.
- La fusion `B/T/A/E` produit une courbe composite lissable.
- Les tests montrent qu'un signal de fond faible ne devient pas artificiellement fort par simple exactitude.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.6: Produire orientation, intensité, confiance et rareté par thème

As a product designer,
I want que chaque thème quotidien expose plusieurs dimensions de lecture,
So that le produit distingue enfin une journée neutre, une journée faible, une journée active et une journée instable.

**Acceptance Criteria:**
- Le moteur calcule au minimum `score_20`, `intensity_20`, `confidence_20` et `rarity_percentile` par thème.
- `score_20` ne mélange plus orientation et intensité.
- La formule de `confidence` est explicitement définie avant usage par blocs, pivots et fenêtres.
- `rarity_percentile` est explicitement distingué d'un simple percentile relatif utilisateur.
- Les nouvelles métriques sont dérivées des courbes lissées, pas uniquement du raw day v2.
- Les tests métier couvrent plusieurs profils de journées contrastées.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.7: Refaire la calibration absolue à partir des courbes lissées

As a backend maintainer,
I want recalibrer les notes journalières à partir de métriques continues plus riches,
So that les notes cessent de s'écraser autour du neutre quand la dynamique intrajournalière existe réellement.

**Acceptance Criteria:**
- La formule v3 s'appuie au minimum sur `level_day`, `intensity_day`, `dominance_day` et `stability_day`.
- Une journée intense mais ambivalente n'est plus assimilée à une journée plate.
- Le moteur garde une note publique lisible sur 20.
- Des comparaisons v2/v3 permettent de mesurer le gain de discrimination.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.8: Étendre le snapshot et la persistance pour le daily v3

As a platform engineer,
I want persister les nouvelles métriques du moteur v3 sans casser la lecture existante,
So that le backend puisse comparer, auditer et projeter v2 et v3 pendant la transition.

**Acceptance Criteria:**
- Le snapshot quotidien supporte les métriques v3 par thème et les nouvelles sorties de bloc/fenêtre.
- La persistance reste backward compatible avec les consommateurs actuels.
- Les migrations et modèles restent versionnés et auditables.
- `engine_version` et `snapshot_version` sont persistés et utilisés par la réutilisation et la lecture repository.
- Les tests de lecture/écriture couvrent coexistence v2/v3.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.9: Segmenter la journée par changement de régime plutôt que par pivot

As a prediction engine designer,
I want découper la journée en régimes cohérents dérivés des courbes,
So that les blocs horaires soient les résumés d'un signal continu et non la simple conséquence d'un pivot ou d'une grille artificielle.

**Acceptance Criteria:**
- La segmentation part des courbes lissées et non d'une grille fixe ou des seuls turning points.
- Les blocs sont ensuite fusionnés pour produire 4 à 8 segments lisibles maximum.
- Chaque bloc expose orientation, intensité et confiance.
- La segmentation reste déterministe et testable.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.10: Détecter les turning points comme des changements de régime persistants

As a QA engineer,
I want que les turning points représentent des bascules durables et non de simples événements,
So that le produit ne montre plus de faux pivots sur des journées faibles ou ambiguës.

**Acceptance Criteria:**
- Un turning point requiert une amplitude minimale avant/après et une durée minimale du régime suivant.
- Les pivots sont déclenchés par changement de régime sur les courbes, pas par simple exactitude.
- Le nombre de pivots publics baisse sur les journées faibles.
- Les tests couvrent faux positif, vrai pivot et cas ambivalent.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.11: Refaire les fenêtres décisionnelles à partir des blocs v3

As a utilisateur consultant le daily,
I want voir des créneaux vraiment utiles parce qu'ils résument des régimes cohérents,
So that les fenêtres proposées aient une personnalité propre et une valeur décisionnelle crédible.

**Acceptance Criteria:**
- Les `decision_windows` sont dérivées des blocs de régime v3.
- Chaque fenêtre expose au minimum orientation, intensité, confiance et thèmes dominants.
- `best_window` n'émerge que si une fenêtre est réellement exploitable.
- Les journées faibles ne génèrent plus de fenêtres artificiellement riches.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.12: Étendre la baseline utilisateur en baseline day, slot et saison

As a platform engineer,
I want enrichir la baseline utilisateur pour tenir compte du jour, de l'heure et de la saison,
So that la calibration personnelle compare des choses comparables et puisse servir le scoring v3.

**Acceptance Criteria:**
- La persistance supporte au minimum `baseline_day`, `baseline_slot` et `baseline_month` ou `baseline_season`.
- Les nouvelles baselines sont versionnées par utilisateur, thème, fenêtre et versions métier.
- La story couvre prioritairement le modèle, la migration, le repository et une génération minimale déterministe.
- La résolution runtime avancée des bonnes baselines selon le contexte est traitée dans la story suivante.
- Un budget de performance explicite borne le coût de génération de baseline enrichie.
- Les tests couvrent lecture, écriture et génération minimale déterministe.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.13: Refaire le scoring relatif v3 autour d'absolu, slot, confiance et rareté

As a prediction engine designer,
I want calculer un scoring relatif plus fin que le simple z-score journalier,
So that le produit puisse comparer un jour, un créneau et une intensité de manière cohérente avec le moteur v3.

**Acceptance Criteria:**
- Le backend expose au minimum `z_abs`, `z_slot`, `pct_abs`, `pct_rel` et une notion de rareté.
- Le fallback variance nulle reste robuste.
- Le scoring relatif devient compatible avec les blocs/fenêtres v3.
- Le scoring absolu demeure la vérité produit principale.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.14: Refaire la logique de flat day et de micro-tendances dans le moteur v3

As a product owner,
I want distinguer une journée plate, une journée faible et une journée intense mais neutre,
So that les micro-tendances et les signaux publics restent honnêtes et réellement utiles.

**Acceptance Criteria:**
- `flat_day` dépend des métriques v3 et non d'un simple manque de pivots.
- Les micro-tendances ne sont exposées que si le relatif apporte une vraie nuance.
- Une journée intense mais neutre n'est plus traitée comme plate.
- Le budget de bruit public reste respecté.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.15: Introduire un evidence pack expert v3

As a backend architect,
I want produire un evidence pack expert indépendant du JSON public,
So that l'interprétation future et la projection publique consomment une structure cohérente, auditable et riche.

**Acceptance Criteria:**
- Le backend produit un `evidence_pack` avec profil global, thèmes, blocs, pivots et drivers.
- L'evidence pack distingue ce qui est structurel, ponctuel, favorable, tendu et fiable.
- `evidence_pack_version` est explicite dans le contrat.
- Le format est déterministe, typé et testable.
- L'evidence pack n'impose pas encore l'usage d'un LLM.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.16: Brancher la projection publique et la future interprétation sur l'evidence pack

As a product platform team,
I want faire de l'evidence pack la source de vérité interprétable,
So that le JSON public et un futur prompt expert ne dérivent plus directement d'une agrégation fragile de signaux.

**Acceptance Criteria:**
- `public_projection` dérive ses résumés structurants de l'evidence pack.
- L'éditorialisation ne peut plus inventer du relief absent du moteur.
- Le backend prépare un contrat propre pour une future couche LLM.
- Les tests verrouillent la cohérence entre evidence pack et payload public.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

### Story 42.17: Verrouiller QA, backtesting et migration progressive du moteur v3

As a QA engineer,
I want sécuriser la coexistence v2/v3 par des fixtures, des métriques et des gates explicites,
So that la bascule vers le moteur daily v3 soit objectivable et réversible.

**Acceptance Criteria:**
- Le backend capitalise sur le mode `dual` introduit tôt dans l'epic pour comparer v2 et v3.
- Des fixtures couvrent journées plates, actives, ambiguës et intensives.
- Les rapports comparent nombre de pivots, dispersion des notes, fenêtres publiques, stabilité et budgets de performance.
- Des critères go/no-go explicites de migration sont documentés.

[Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]

## Epic 43: Moments clés du jour explicables et localisés

Faire évoluer les `Moments clés du jour` d'un simple affichage de bascule vers une explication structurée, compréhensible et localisable, afin que l'utilisateur voie clairement la cause astrologique principale, la transition avant/après et son implication concrète.

**FRs covered:** FR16, FR18, FR22, FR23, FR36

### Story 43.1: Structurer côté backend une sémantique explicable des bascules

As a backend maintainer,
I want enrichir les turning points publics avec une sémantique structurée de changement,
So that le frontend puisse afficher pourquoi une bascule existe sans reconstruire la logique métier à partir de phrases fragiles.

**Acceptance Criteria:**
- Le backend expose de manière additive, pour chaque moment clé public, un `change_type` explicite au minimum parmi `emergence`, `recomposition`, `attenuation`.
- Le backend expose un diff structuré entre `previous_categories`, `next_categories` et `impacted_categories`, sans imposer de phrase localisée.
- Le backend expose un `primary_driver` structuré dérivé des drivers existants, avec type d’événement, corps, aspect, cible et métadonnées utiles filtrées.
- Le backend distingue les bascules réelles des frontières synthétiques de début/fin de journée.
- Le contrat reste backward compatible avec le payload actuel de `/v1/predictions/daily`.

[Source: user request 2026-03-12 — “expliquer pourquoi ce sont des bascules” ; backend/app/prediction/public_projection.py ; frontend/src/utils/dailyAstrology.ts]

### Story 43.2: Introduire un wording i18n piloté par données structurées pour les moments clés

As a frontend architect,
I want composer le wording des moments clés via i18n à partir de données structurées,
So that le français, l’anglais et les futures langues restent cohérents sans figer des phrases métier dans le backend.

**Acceptance Criteria:**
- Le backend ne renvoie plus de phrase finale localisée comme source primaire pour les moments clés enrichis.
- Le frontend introduit des clés i18n dédiées pour les causes astrologiques, les transitions `avant/après`, les libellés d’impact et les implications.
- Le wording distingue au minimum les cas `emergence`, `recomposition` et `attenuation`.
- Les règles de formulation gèrent l’absence d’un `primary_driver`, un driver unique et plusieurs drivers secondaires sans casser l’UX.
- Les helpers i18n restent centralisés et testables.

[Source: user request 2026-03-12 — “le wording doit etre gerer avec i18n” ; frontend/src/utils/predictionI18n.ts ; frontend/src/i18n/predictions.ts]

### Story 43.3: Refaire le rendu UI des moments clés autour de “Pourquoi / Ce qui change / Implication”

As a utilisateur consultant le daily,
I want lire chaque moment clé comme une transition expliquée,
So that je comprenne la cause astrologique, le passage d’un état à un autre, et ce que cela implique pour la journée.

**Acceptance Criteria:**
- Chaque carte `Moment clé` affiche trois sections lisibles: `Pourquoi ça bascule`, `Ce qui change`, `Implication`.
- Le rendu explicite le passage `avant -> après` à partir des catégories dominantes, sans jargon technique brut.
- Le `primary_driver` astrologique est humanisé et affiché comme cause principale, avec un fallback sobre si aucun driver fort n’est disponible.
- Les impacts restent visibles sous forme de catégories/pictogrammes et restent cohérents avec l’agenda du jour.
- Le design mobile et desktop reste compact et ne réintroduit pas de bruit visuel excessif.

[Source: user request 2026-03-12 — “expliquer le changement : on avait ca => ca devient ca” ; frontend/src/components/prediction/TurningPointsList.tsx ; frontend/src/pages/TodayPage.tsx]

### Story 43.4: Verrouiller QA produit, cohérence multilingue et garde-fous d’explicabilité

As a QA engineer,
I want valider que les moments clés enrichis restent vrais, lisibles et localisés,
So that le produit ne surinterprète pas les bascules et conserve un wording cohérent en plusieurs langues.

**Acceptance Criteria:**
- Les tests couvrent au minimum un cas d’émergence, un cas de recomposition et un cas d’atténuation.
- Les suites frontend vérifient la production des textes FR/EN à partir de la même structure de données.
- Aucun wording ne dépend directement de chaînes backend non localisées pour les cartes de moments clés enrichis.
- Les cas sans driver, avec driver exact et avec plusieurs drivers restent stables et lisibles.
- Les régressions sur faux pivots de minuit et disparition complète des moments clés restent verrouillées.

[Source: user request 2026-03-12 ; frontend/src/tests/TodayPage.test.tsx ; frontend/src/utils/dailyAstrology.test.ts ; backend/app/tests/integration/test_daily_prediction_api.py]

## Epic 44: Quantifier les mouvements des moments clés du jour

Faire évoluer les `Moments clés du jour` pour qu'ils n'expliquent pas seulement `ce qui change`, mais aussi `de combien` et `dans quel sens`, avec des valeurs structurées, localisables et assez sobres pour rester compréhensibles sur mobile.

**FRs covered:** FR16, FR18, FR22, FR23, FR36

### Story 44.1: Étendre le contrat public des moments clés avec des indicateurs de mouvement

As a backend maintainer,
I want enrichir les turning points publics avec un bloc `movement` et des `category_deltas`,
So that le frontend puisse expliquer l'amplitude et la direction d'une bascule sans recalcul fragile côté client.

**Acceptance Criteria:**
- Le contrat public des moments clés expose de manière additive un bloc `movement` incluant au minimum `strength`, `previous_composite`, `next_composite`, `delta_composite` et `direction`.
- Le contrat public expose une liste `category_deltas` structurée, avec au minimum `code`, `direction`, `delta_score`, `delta_intensity` et `delta_rank` si disponible.
- Les nouveaux champs restent optionnels et backward compatibles pour les consommateurs qui ne les utilisent pas encore.
- Le schéma distingue explicitement un changement global (`movement.direction`) d'une variation locale par catégorie.
- Les types backend et frontend partagés restent cohérents et documentés.

[Source: user request 2026-03-12 — “enrichir ces moments clefs avec des valeurs qui justifie le mouvement ?” ; backend/app/prediction/schemas.py ; frontend/src/types/dailyPrediction.ts]

### Story 44.2: Calculer et projeter les deltas de mouvement des bascules

As a backend engineer,
I want calculer des deltas de mouvement fiables autour de chaque turning point,
So that les valeurs projetées justifient réellement le passage d'un état à l'autre sans surinterpréter le bruit.

**Acceptance Criteria:**
- Le backend calcule `previous_composite`, `next_composite` et `delta_composite` à partir de l'état juste avant et juste après la bascule.
- Le backend calcule `category_deltas` à partir des catégories dominantes avant/après, avec une règle explicite de tri et de limitation aux variations les plus utiles.
- Le backend classe le mouvement au minimum entre `rising`, `falling` et `recomposition`, de façon cohérente avec `change_type`.
- Des seuils empêchent d'exposer des micro-variations non significatives comme des mouvements forts.
- Les journées calmes ou bascules faibles restent rendues sans contradiction entre `change_type`, `transition` et valeurs de mouvement.

[Source: user request 2026-03-12 — “expliquer non seulement ce qui change, mais aussi à quel point” ; backend/app/prediction/public_projection.py ; backend/app/prediction/daily_prediction_evidence_builder.py]

### Story 44.3: Introduire un wording i18n des variations et de leur intensité

As a frontend architect,
I want traduire les variations de mouvement via i18n à partir des valeurs structurées,
So that les moments clés restent compréhensibles en plusieurs langues sans figer des phrases quantitatives dans le backend.

**Acceptance Criteria:**
- Le frontend introduit des clés i18n dédiées pour `direction`, `strength`, `delta` et les formulations de montée, recul, stabilité ou recomposition.
- Le wording sait produire une version qualitative sobre (`léger`, `net`, `marqué`) sans exposer de chiffres bruts dans la V1 des cartes.
- Les helpers i18n gèrent FR et EN à partir du même payload structuré.
- Si des valeurs numériques sont exposées plus tard, elles devront être formatées côté frontend selon la locale et jamais concaténées en dur.
- Les règles de formulation évitent les contradictions du type “ça change” alors que les catégories visibles restent identiques faute de contexte.

[Source: user request 2026-03-12 — “le wording doit etre gerer avec i18n” ; frontend/src/utils/predictionI18n.ts ; frontend/src/i18n/predictions.ts]

### Story 44.4: Refondre le rendu UI des moments clés avec mouvement et deltas

As a utilisateur consultant le daily,
I want voir pour chaque bascule quelles forces montent, reculent ou se redistribuent,
So that je comprenne visuellement pourquoi le moment mérite mon attention.

**Acceptance Criteria:**
- Chaque carte `Moment clé` peut afficher un bloc `Mouvement` ou `Évolution` basé sur `movement` et `category_deltas`.
- Le rendu met en avant au maximum les 2 ou 3 variations les plus utiles, avec une hiérarchie claire et sans surcharge mobile.
- Les catégories ajoutées, retirées ou stabilisées sont distinguées visuellement.
- Le composant conserve un fallback lisible quand les nouveaux champs ne sont pas présents.
- Le rendu reste cohérent avec les sections existantes `Pourquoi`, `Transition`, `Implication` et `Impacts`.

[Source: user request 2026-03-12 — “Travail monte nettement / Argent se retire / Santé reste dominante” ; frontend/src/components/prediction/TurningPointsList.tsx ; frontend/src/pages/TodayPage.tsx]

### Story 44.5: Verrouiller QA et garde-fous de bruit sur les valeurs de bascule

As a QA engineer,
I want vérifier que les valeurs de mouvement restent vraies, lisibles et non bruitées,
So that les moments clés enrichis ne sur-vendent pas des micro-variations et restent cohérents en plusieurs langues.

**Acceptance Criteria:**
- Les tests couvrent au minimum un cas d'augmentation nette, un cas d'atténuation, un cas de recomposition et un cas de mouvement sous seuil non affiché.
- Les suites backend vérifient les calculs de `movement` et `category_deltas` sur des bascules représentatives.
- Les suites frontend vérifient les rendus FR et EN du mouvement qualitatif et des variations locales.
- Les régressions connues restent couvertes: faux pivot de minuit, transition `avant -> après` incohérente, disparition complète des moments clés valides.
- Les garde-fous empêchent l'affichage de chiffres bruts instables, de décimales inutiles et de messages contradictoires entre `Implication` et `Mouvement`.

[Source: user request 2026-03-12 ; frontend/src/tests/TurningPointsEnriched.test.tsx ; frontend/src/tests/TodayPage.test.tsx ; backend/app/tests/integration/test_daily_prediction_api.py]

## Epic 45: Recomposer le parcours dashboard autour d'un résumé puis d'un détail horoscope

Faire évoluer le parcours dashboard pour que l'entrée `/dashboard` devienne une page d'atterrissage légère, centrée sur un résumé court de l'horoscope du jour et les autres activités disponibles, tandis que le détail complet de l'horoscope est déplacé vers une page dédiée accessible depuis ce résumé.

**FRs covered:** FR12, FR16, FR19, NFR2, NFR3, NFR13, NFR14

### Story 45.1: Refondre le routing dashboard et isoler la page horoscope détaillée

As a frontend architect,
I want séparer explicitement la landing `/dashboard` du détail horoscope `/dashboard/horoscope`,
so that le menu dashboard ouvre une page d'accueil légère sans perdre la continuité de navigation vers l'horoscope complet.

**Acceptance Criteria:**
- `/dashboard` n'affiche plus directement la page horoscope détaillée actuelle.
- Une route dédiée `/dashboard/horoscope` est introduite pour le détail complet du daily.
- Le bottom nav continue à considérer le parcours détaillé comme appartenant au dashboard.
- Le header shell n'introduit pas de double titre ou de conflit visuel sur les deux écrans du parcours dashboard.
- Les gardes d'authentification, redirections racine et deep links existants continuent de fonctionner.

[Source: user request 2026-03-12 ; frontend/src/app/routes.tsx ; frontend/src/components/layout/Header.tsx ; frontend/src/components/layout/BottomNav.tsx]

### Story 45.2: Créer la landing dashboard avec résumé 2 lignes et hub d'activités

As a utilisateur authentifié,
I want voir sur `/dashboard` uniquement un résumé très court de mon horoscope du jour puis mes autres activités,
so that j'accède immédiatement à l'essentiel avant de choisir d'aller plus loin ou d'ouvrir un autre parcours.

**Acceptance Criteria:**
- La landing dashboard affiche un cadre dédié à l'horoscope du jour avec un résumé visuellement limité à 2 lignes maximum.
- Le clic sur ce cadre ouvre `/dashboard/horoscope`.
- La section des activités (chat, tirage, etc.) est affichée sous le résumé et reste accessible sans scroller inutilement sur mobile.
- Les états `loading`, `error` et `empty` de l'horoscope restent gérés sans masquer la section activités.
- Le frontend réutilise les données du daily existantes, sans nouveau contrat backend.

[Source: user request 2026-03-12 ; frontend/src/components/ShortcutsSection.tsx ; frontend/src/pages/DashboardPage.tsx ; frontend/src/pages/TodayPage.tsx]

### Story 45.3: Restaurer une page horoscope détaillée avec retour explicite vers le dashboard

As a utilisateur consultant l'horoscope du jour,
I want ouvrir une page dédiée au daily complet avec un bouton retour clair vers le dashboard,
so that je retrouve tout le détail utile sans perdre mon point d'entrée principal.

**Acceptance Criteria:**
- `/dashboard/horoscope` affiche le contenu détaillé du daily déjà en place, avec au minimum le résumé, les moments clés du jour et l'agenda du jour.
- Un bouton de retour explicite permet de revenir vers `/dashboard`.
- La page détail n'affiche plus la section des autres activités qui appartient désormais à la landing dashboard.
- Les états `loading`, `error` et `empty` restent cohérents avec la page détail et ne cassent pas la navigation retour.
- L'ouverture du détail depuis la landing réutilise le cache React Query existant du daily quand les données sont déjà chargées.

[Source: user request 2026-03-12 ; frontend/src/pages/TodayPage.tsx ; frontend/src/api/useDailyPrediction.ts ; frontend/src/types/dailyPrediction.ts]

### Story 45.4: Verrouiller QA, accessibilité et cohérence i18n du nouveau parcours dashboard

As a QA engineer,
I want verrouiller le nouveau parcours dashboard par des tests de routing, d'états UI et de navigation,
so that la séparation landing/détail n'introduise ni régression fonctionnelle, ni incohérence visuelle, ni dette i18n supplémentaire.

**Acceptance Criteria:**
- Les tests couvrent la navigation `/dashboard` -> `/dashboard/horoscope` -> retour `/dashboard`.
- Les suites vérifient les états `loading`, `error` et `empty` sur la landing et sur la page détail.
- Le dashboard n'affiche plus les sections détaillées du daily, et la page détail n'affiche plus le hub d'activités.
- Le header et le bottom nav restent cohérents sur mobile et desktop sur les deux routes.
- Toute nouvelle chaîne introduite par l'epic 45 est centralisée et testable, sans ajout de hardcode gratuit.

[Source: user request 2026-03-12 ; frontend/src/tests/router.test.tsx ; frontend/src/tests/TodayPage.test.tsx ; frontend/src/tests/DashboardPage.test.tsx ; frontend/src/tests/layout/Header.test.tsx]

## Epic 46: Recentrer les consultations sur une guidance astrologique ciblée sans tirage

Faire évoluer `/consultations` pour supprimer toute notion de tirage de cartes ou de runes, tout en conservant des demandes ciblées de type amoureux, professionnel, événementiel ou libre, appuyées sur la guidance contextuelle astrologique existante.

**FRs covered:** FR17, FR19, FR20, FR21, FR23, NFR2, NFR3, NFR13, NFR14

### Story 46.1: Rebrancher les consultations ciblées sur la guidance contextuelle

As a frontend/backend integrator,
I want faire de la guidance contextuelle existante la source de vérité des consultations ciblées,
so that les parcours `dating`, `pro`, `event` et `free` restent utiles après la suppression des tirages sans retomber sur une interprétation natale hors sujet.

**Acceptance Criteria:**
- Le parcours consultations n'utilise plus `useExecuteModule()` ni `/v1/chat/modules/*` pour générer le résultat.
- Le frontend appelle `POST /v1/guidance/contextual` avec un payload cohérent fondé sur `situation`, `objective` et `time_horizon`.
- Le mapping des types `dating`, `pro`, `event`, `free` reste explicite et testable.
- La page résultat ne retombe plus sur l'interprétation natale comme fallback.
- Les routes `/consultations`, `/consultations/new` et `/consultations/result` restent stables.

[Source: user request 2026-03-13 ; frontend/src/pages/ConsultationResultPage.tsx ; backend/app/api/v1/routers/guidance.py ; backend/app/services/guidance_service.py]

### Story 46.2: Refondre le wizard et le modèle de données des consultations sans tirage

As a frontend architect,
I want retirer la notion de tirage du wizard, du modèle de données et de la page résultat,
so that `/consultations` devienne un vrai parcours de guidance astrologique ciblée, cohérent pour l'utilisateur et maintenable pour l'équipe.

**Acceptance Criteria:**
- Le wizard suit désormais un parcours `type -> astrologue -> demande`.
- `ConsultationDraft` et `ConsultationResult` ne portent plus `drawingOption` ni `drawing`.
- La page résultat n'affiche plus de cartes, runes ou section de tirage.
- Les constantes wizard et l'i18n consultations sont réalignées sans duplication.
- Les tests frontend couvrent le nouveau wizard et l'absence de rendu tirage.

[Source: user request 2026-03-13 ; frontend/src/types/consultation.ts ; frontend/src/state/consultationStore.tsx ; frontend/src/pages/ConsultationWizardPage.tsx ; frontend/src/pages/ConsultationResultPage.tsx]

### Story 46.3: Migrer l'historique local et préserver l'ouverture dans le chat

As a frontend maintainer,
I want migrer proprement l'historique local des consultations vers le nouveau schéma sans tirage,
so that les utilisateurs conservent leurs consultations passées et peuvent toujours ouvrir une guidance dans le chat sans régression.

**Acceptance Criteria:**
- Les anciennes entrées localStorage avec `drawingOption` et `drawing` restent lisibles via une migration de lecture.
- Les nouvelles écritures utilisent uniquement le schéma consultation sans tirage.
- L'historique et les deep links `?id=...` restent fonctionnels.
- `CHAT_PREFILL_KEY` continue d'ouvrir le chat avec un message utile basé sur la guidance contextuelle.
- Les tests couvrent migration legacy, nouveau schéma et ouverture chat.

[Source: user request 2026-03-13 ; frontend/src/state/consultationStore.tsx ; frontend/src/pages/ConsultationResultPage.tsx ; _bmad-output/implementation-artifacts/16-5-consultations-pages.md]

### Story 46.4: Revoir navigation, dashboard et wording i18n des consultations

As a product-facing frontend engineer,
I want remplacer partout la sémantique de tirage par celle de consultations astrologiques ciblées,
so that l'application ne présente plus de fonctionnalité hors périmètre tout en gardant un accès clair aux parcours `/consultations`.

**Acceptance Criteria:**
- L'entrée de navigation vers `/consultations` n'est plus libellée `Tirages`.
- Le dashboard ne promeut plus `Tirage du jour` ni ses variantes localisées.
- Les chaînes FR/EN/ES visibles ne mentionnent plus `tirage`, `cartes`, `runes`, `tarot` pour ce parcours.
- Les clés et handlers techniques les plus exposés (`onTirageClick`, `tirageTitle`, `--badge-tirage`) sont réalignés.
- La route `/consultations` reste inchangée.

[Source: user request 2026-03-13 ; frontend/src/ui/nav.ts ; frontend/src/components/ShortcutsSection.tsx ; frontend/src/i18n/dashboard.tsx ; frontend/src/i18n/consultations.ts]

### Story 46.5: Retirer le sous-système tarot/runes du backend et des contrats LLM

As a backend maintainer,
I want supprimer l'infrastructure tarot/runes devenue hors périmètre,
so that le backend et l'orchestration LLM ne portent plus de fonctionnalités mortes ou contradictoires avec la promesse astrologique du produit.

**Acceptance Criteria:**
- Les flags `tarot_enabled` et `runes_enabled` ainsi que les modules dédiés ne sont plus exposés.
- Les routes et clients `/v1/chat/modules/*` sont retirés du produit.
- Les contrats LLM ne référencent plus `tarot_reading`, `tarot_spread` ni `offer_tarot_reading`.
- La hard policy `astrology` ne mentionne plus le tarot.
- Les seeds, schémas et tests restent cohérents après suppression.

[Source: user request 2026-03-13 ; backend/app/services/feature_flag_service.py ; frontend/src/api/chat.ts ; backend/app/llm_orchestration/gateway.py ; backend/app/llm_orchestration/seeds/use_cases_seed.py]

### Story 46.6: Verrouiller QA, cohérence BMAD et non-régression de la refonte

As a QA and product consistency owner,
I want verrouiller la refonte consultations sans tirage par des tests, des gates et un réalignement documentaire BMAD,
so that le périmètre astrologique soit cohérent dans le produit, dans le code et dans les artefacts de référence.

**Acceptance Criteria:**
- Une matrice de non-régression couvre navigation, création des 4 types de consultation, historique et ouverture dans le chat.
- Les tests front/back reflètent le nouveau périmètre sans tirage.
- Une vérification ciblée confirme l'absence résiduelle de `tirage`, `tarot`, `runes`, `cartes` sur les surfaces critiques.
- Les artefacts BMAD 11.2, 16.5, 17.1, 17.5 et 45.2 sont réalignés.
- Un gate final liste validations manuelles, risques restants et limites.

[Source: user request 2026-03-13 ; _bmad-output/implementation-artifacts/11-2-modules-tarot-runes-derriere-feature-flags.md ; _bmad-output/implementation-artifacts/16-5-consultations-pages.md ; _bmad-output/implementation-artifacts/17-1-fondations-ui-tokens-typo-lucide.md ; _bmad-output/implementation-artifacts/17-5-raccourcis-shortcut-card.md ; _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]

## Epic 47: Faire évoluer `/consultations` vers une consultation complète pilotée par précheck, fallback et orchestration métier

Transformer le hub `/consultations` issu de l'epic 46 en une vraie consultation complète MVP, réutilisant les données natales existantes, exposant le niveau réel de précision, demandant uniquement les compléments nécessaires et s'appuyant sur un contrat backend consultation dédié.

**FRs covered:** FR11, FR16, FR17, FR19, FR20, FR21, FR23, NFR2, NFR3, NFR6, NFR13, NFR14, NFR16, NFR20, NFR22

### Story 47.1: Redéfinir le catalogue produit et la taxonomie des consultations complètes

As a product-facing frontend architect,
I want réaligner `/consultations` sur la taxonomie MVP de la consultation complète,
so that le parcours expose les bons types de consultation sans casser la route, l'historique existant ni les deep links hérités de l'epic 46.

**Acceptance Criteria:**
- Le catalogue visible de `/consultations` expose au minimum `period`, `work`, `orientation`, `relation`, `timing`.
- Les anciens types `dating`, `pro`, `event`, `free` restent lisibles en historique mais ne sont plus créables.
- Chaque type déclare promesse UX, besoins de données minimaux et mode nominal / dégradé attendu.
- Les routes `/consultations`, `/consultations/new`, `/consultations/result` restent stables.

[Source: docs/backlog_epics_consultation_complete.md ; frontend/src/types/consultation.ts ; frontend/src/pages/ConsultationsPage.tsx ; frontend/src/state/consultationStore.tsx]

### Story 47.2: Exposer le précheck de complétude et de précision des consultations

As a backend/frontend integrator,
I want introduire un précheck consultation dédié avant la génération,
so that `/consultations` sache réutiliser le profil natal existant, afficher le niveau réel de précision et annoncer proprement les modes disponibles avant d'engager l'utilisateur.

**Acceptance Criteria:**
- Un endpoint consultation dédié retourne `user_profile_quality`, `precision_level`, `missing_fields`, `available_modes` et les cas bloquants.
- Le calcul réutilise les services existants autour du birth profile et de l'astro profile.
- Le frontend consomme ce contrat via un client API centralisé sans dupliquer les règles métier.
- Les tests couvrent au minimum profil complet, sans heure, absent et bloquant.

[Source: docs/backlog_epics_consultation_complete.md ; backend/app/api/v1/routers/users.py ; backend/app/services/user_birth_profile_service.py ; backend/app/services/user_astro_profile_service.py]

### Story 47.3: Refondre le wizard consultations avec cadrage et collecte conditionnelle

As a consultations UX engineer,
I want transformer le wizard `/consultations/new` en parcours de cadrage et de collecte conditionnelle,
so that l'utilisateur ne saisisse que les informations nécessaires à la consultation choisie, avec une expérience cohérente avec le précheck et sans friction inutile.

**Acceptance Criteria:**
- Le wizard n'impose plus le choix d'astrologue comme étape métier bloquante.
- Le parcours demande uniquement les compléments requis par le type et le précheck.
- Le module "autre personne" n'apparaît que pour les parcours concernés.
- Les choix "heure inconnue" et "je ne sais pas" sont gérés proprement.

[Source: docs/backlog_epics_consultation_complete.md ; frontend/src/pages/ConsultationWizardPage.tsx ; frontend/src/state/consultationStore.tsx ; frontend/src/api/birthProfile.ts]

### Story 47.8: Etendre la collecte tiers aux consultations d'interaction ciblee

As a consultations product engineer,
I want permettre la saisie d'un tiers pour les consultations d'interaction ciblee au-dela du seul type `relation`,
so that les parcours `work` ou assimilés puissent embarquer un contexte bi-profil quand l'utilisateur prepare un entretien, un rendez-vous ou une interaction ciblee avec une personne identifiee.

**Acceptance Criteria:**
- Le wizard distingue `self_only` et `targeted_interaction` pour les types eligibles, au minimum `work`.
- Le module `OtherPersonForm` peut s'afficher pour un parcours `work` sans casser `relation`.
- Les payloads `precheck` et `generate` propagent `other_person` pour ces parcours.
- Les tests couvrent `work/self_only`, `work/targeted_interaction` et la non-regression `relation`.

[Source: docs/backlog_epics_consultation_complete.md ; frontend/src/features/consultations/components/DataCollectionStep.tsx ; frontend/src/features/consultations/components/OtherPersonForm.tsx ; frontend/src/pages/ConsultationWizardPage.tsx]

### Story 47.9: Persister et reutiliser les profils tiers de consultation

As a utilisateur des consultations,
I want pouvoir enregistrer un tiers avec un pseudonyme non identifiant et le reutiliser dans de futures consultations,
so that je n'aie pas a ressaisir ses donnees de naissance et que je puisse retrouver l'historique des consultations dans lesquelles ce tiers a ete utilise.

**Acceptance Criteria:**
- Le backend expose un stockage explicite des profils tiers rattaches a l'utilisateur, avec au minimum `nickname`, `birth_date`, `birth_time`, `birth_time_known`, `birth_place`, `birth_city`, `birth_country`, `place_resolved_id`, `birth_lat`, `birth_lon`.
- Le wizard consultation affiche, sur les parcours eligibles a un tiers, un acces a une liste de tiers deja enregistres et permet de pre-remplir le formulaire a partir d'une selection.
- Le formulaire tiers permet un enregistrement opt-in pendant la consultation via une action du type `Enregistrer dans mes contacts`, sans sauvegarde implicite.
- L'interface affiche un avertissement explicite demandant de ne pas utiliser un pseudonyme identifiant (nom, prenom, element reconnaissable).
- Chaque profil tiers expose la liste des consultations ou il a ete utilisee, sous forme de journal minimal consultation-centric, sans imposer une persistance complete de toutes les consultations.
- Les tests couvrent creation d'un tiers, reutilisation dans une consultation eligibile, affichage du warning de pseudonyme et journal minimal des usages.

[Source: docs/backlog_epics_consultation_complete.md#story-cc-03-04 ; docs/backlog_epics_consultation_complete.md#story-cc-03-05 ; frontend/src/features/consultations/components/OtherPersonForm.tsx ; frontend/src/pages/ConsultationWizardPage.tsx ; frontend/src/state/consultationStore.tsx]

### Story 47.4: Implémenter les modes dégradés et fallbacks des consultations

As a consultation domain engineer,
I want rendre explicites les modes dégradés et les sorties bloquantes du parcours consultations,
so that le produit reste honnête sur son niveau de précision et utile même quand les données disponibles sont incomplètes.

**Acceptance Criteria:**
- Le domaine consultation expose au minimum `user_no_birth_time`, `other_no_birth_time`, `relation_user_only`, `timing_degraded`, `blocking_missing_data`.
- Le backend distingue `nominal`, `degraded` et `blocked`.
- Le frontend affiche les limitations et actions de poursuite / retour adaptées.
- Les résultats et le prefill chat propagent `fallback_mode` et `precision_level`.

[Source: docs/backlog_epics_consultation_complete.md ; backend/app/services/guidance_service.py ; frontend/src/pages/ConsultationResultPage.tsx ; frontend/src/i18n/consultations.ts]

### Story 47.5: Construire le dossier de consultation et le routing LLM versionné

As a backend consultation architect,
I want introduire un `ConsultationDossier` et un routeur de génération consultation dédiés,
so that la feature `/consultations` cesse d'orchestrer sa logique métier côté frontend et dispose d'un contrat backend versionné, testable et compatible avec l'infrastructure LLM existante.

**Acceptance Criteria:**
- Le backend définit un `ConsultationDossier` v1 portant type, question, qualité, précision, fallback et métadonnées utiles.
- Un endpoint consultation dédié remplace le contrat produit final actuellement tiré de `guidance_contextual`.
- Le backend calcule un `route_key` déterministe et journalisé.
- Le routage réutilise la pile `GuidanceService` / `AIEngineAdapter` / `llm_orchestration`.

[Source: docs/backlog_epics_consultation_complete.md ; backend/app/api/v1/routers/guidance.py ; backend/app/services/guidance_service.py ; backend/app/services/ai_engine_adapter.py]

### Story 47.6: Refondre la génération et la restitution structurée des consultations

As a consultations frontend engineer,
I want consommer le contrat backend consultation complet et refaire la page résultat autour de la précision, des limitations et des sections structurées,
so that `/consultations/result` reflète réellement la nouvelle consultation complète tout en préservant l'historique local et l'ouverture dans le chat.

**Acceptance Criteria:**
- Le frontend appelle l'endpoint consultation dédié et non plus directement le payload produit brut de `guidance_contextual`.
- La page résultat affiche synthèse, sections, limitations, précision et fallback.
- Le localStorage reste backward-compatible avec les résultats 46.x et legacy.
- `open in chat` continue de fonctionner avec les nouvelles métadonnées.

[Source: docs/backlog_epics_consultation_complete.md ; frontend/src/pages/ConsultationResultPage.tsx ; frontend/src/state/consultationStore.tsx ; frontend/src/api/guidance.ts]

### Story 47.7: Verrouiller QA, observabilité et non-régression des consultations complètes

As a QA and product consistency owner,
I want verrouiller la nouvelle mouture des consultations complètes par des tests, du tracking et un gate documentaire final,
so that l'epic 47 puisse être implémenté sans régression sur les parcours existants et avec une visibilité claire sur précision, fallbacks et erreurs.

**Acceptance Criteria:**
- Une matrice QA couvre types MVP, nominal / degraded / blocked et legacy history.
- Les événements et logs consultation couvrent entrée, précheck, fallback, génération, résultat et ouverture chat.
- Les fixtures de test couvrent profils complets, incomplets et tiers partiels.
- Un gate final documente validations automatiques, validations manuelles et risques résiduels.

[Source: docs/backlog_epics_consultation_complete.md ; _bmad-output/implementation-artifacts/46-6-verrouiller-qa-coherence-bmad-et-non-regression-de-la-refonte.md ; frontend/src/tests/ConsultationsPage.test.tsx]

## Epic 48: Animer le résumé astrologique du dashboard avec un fond astrologique déterministe et maintenable

Faire évoluer la carte résumé de `/dashboard` pour lui donner un fond astrologique animé, doux et premium, déterministe selon le signe, l'utilisateur et la date, tout en restant accessible, performant et facilement modifiable.

**FRs covered:** FR16, NFR3, NFR13, NFR14

### Story 48.1: Créer le composant `AstroMoodBackground` paramétrable et maintenable

As a frontend UI architect,
I want encapsuler le fond astrologique animé dans un composant React réutilisable et facilement modifiable,
so that l'équipe puisse ajuster les motifs, palettes et micro-animations sans réécrire la carte résumé dashboard.

**Acceptance Criteria:**
- Un composant `frontend/src/components/astro/AstroMoodBackground.tsx` expose un contrat de props explicite au minimum `sign`, `userId`, `dateKey`, `dayScore`, `className`, `children`.
- Le rendu combine un fond stable en CSS et une surcouche Canvas 2D pour les étoiles, halos et constellation.
- La variation est déterministe pour une journée donnée à partir d'une seed issue de `userId + sign + dateKey`.
- Les 12 signes astrologiques sont pris en charge via une configuration extraite dans un module dédié plutôt que codés en dur dans la carte dashboard.
- Un variant `neutral` explicite couvre les cas sans signe exploitable.
- Le composant gère `prefers-reduced-motion`, nettoie `requestAnimationFrame` et `ResizeObserver`, et borne le `devicePixelRatio`.
- Des tests verrouillent le contrat du composant et les garde-fous critiques de seed, cleanup et accessibilité décorative.

[Source: docs/interfaces/integration_fond_astrologique_dashboard.md ; frontend/src/components/HeroHoroscopeCard.tsx ; frontend/src/components/HeroHoroscopeCard.css]

### Story 48.2: Intégrer le fond astrologique animé au résumé dashboard

As a product-facing frontend engineer,
I want brancher le composant `AstroMoodBackground` sur la carte résumé de `/dashboard`,
so that le résumé du jour gagne une présence premium sans changer le contrat backend ni casser les états existants de la landing.

**Acceptance Criteria:**
- La carte résumé dashboard utilise le nouveau fond animé lorsque la prédiction du jour est disponible, tout en restant cliquable et activable au clavier vers `/dashboard/horoscope`.
- Le mapping des paramètres visuels (`sign`, `userId`, `dateKey`, `dayScore`) est centralisé dans un module ou hook dédié et ne duplique pas de logique dans le JSX de page.
- `sign` vient de `astro_profile.sun_sign_code` via les données de naissance existantes, `dateKey` vient de `prediction.meta.date_local`, `userId` vient du token ou du profil auth, et `dayScore` est dérivé des catégories daily existantes selon une formule normative unique, sans nouveau backend.
- Les états `loading`, `error` et `empty` du dashboard restent cohérents et ne masquent jamais la section activités.
- Le résumé dashboard reste affichable sans attendre `birth-data`; un rendu `neutral` est utilisé tant que `sun_sign_code` n'est pas disponible.
- Le texte résumé reste lisible, la zone gauche reste respirante et aucune nouvelle chaîne inutile n'est hardcodée hors i18n.
- Les tests dashboard couvrent le nouveau rendu et les fallback visuels quand le signe ou la prédiction ne sont pas disponibles.

[Source: docs/interfaces/integration_fond_astrologique_dashboard.md ; frontend/src/pages/DashboardPage.tsx ; frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx ; frontend/src/api/useDailyPrediction.ts ; frontend/src/api/birthProfile.ts]

### Story 48.3: Verrouiller QA, accessibilité et performance du fond astrologique

As a QA and frontend quality owner,
I want verrouiller le fond astrologique animé par des tests et garde-fous ciblés,
so that l'évolution du résumé dashboard n'introduise ni régression de navigation, ni dette d'accessibilité, ni animation coûteuse ou instable.

**Acceptance Criteria:**
- Les tests couvrent les états `success`, `loading`, `error` et `empty` de `/dashboard` avec le nouveau résumé.
- Les garde-fous d'accessibilité sont vérifiés explicitement: `canvas` décoratif, `prefers-reduced-motion`, activation clavier de la carte, lisibilité des contenus.
- Les suites vérifient que l'animation nettoie bien ses ressources au démontage et au remount de type Strict Mode.
- Les assertions de non-régression confirment que `/dashboard` n'affiche toujours pas le détail daily complet et que `/dashboard/horoscope` reste inchangé.
- Les contraintes de performance minimales sont documentées et verrouillées dans les tests ou la revue de code ciblée: pas d'état React à chaque frame, DPR plafonné, pas de dépendance graphique supplémentaire.
- Les contrastes du texte nominal respectent WCAG AA sur le chemin nominal.
- Les fichiers BMAD de l'epic 48 reflètent explicitement ces garde-fous et les risques résiduels.

[Source: docs/interfaces/integration_fond_astrologique_dashboard.md ; _bmad-output/implementation-artifacts/45-4-verrouiller-qa-accessibilite-et-coherence-i18n-du-parcours-dashboard.md ; frontend/src/tests/DashboardPage.test.tsx ; frontend/src/tests/router.test.tsx]

## Epic 66: Refactoriser l'orchestration LLM pour remplacer les conventions implicites par des contrats d'exécution explicites

Faire évoluer l'architecture d'orchestration LLM d'un système fonctionnel mais basé sur des dictionnaires implicites et des fallbacks successifs, vers une plateforme à contrats explicites, typés, observables et gouvernés. L'objectif est de fiabiliser la plateforme interne sans changer le comportement produit visible.

**FRs covered:** FR66-1 à FR66-8, NFR66-1 à NFR66-5

**Document complet:** [epic-66-llm-orchestration-contrats-explicites.md](_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)

### Story 66.1: Introduire un `LLMExecutionRequest`

As a plateforme d'orchestration,
I want un modèle d'entrée explicite pour les appels LLM,
so that les conventions diffuses transportées dans `user_input` et `context` soient remplacées par un contrat typé.

### Story 66.2: Introduire un `ResolvedExecutionPlan`

As a moteur d'orchestration,
I want matérialiser la config finale réellement résolue avant exécution,
so that la vérité canonique de ce qui va être exécuté soit explicite et loggable.

### Story 66.3: Refactoriser `LLMGateway.execute()` en pipeline

As a développeur backend,
I want découper le gateway en étapes explicites et testables,
so that l'effet "god orchestrator" soit réduit et chaque étape soit indépendamment testable.

### Story 66.4: Séparer validation, normalisation et sanitization

As a plateforme LLM,
I want une chaîne explicite de traitement de sortie (parse → validate → normalize → sanitize),
so that les transformations réellement appliquées soient visibles et catégorisées.

### Story 66.5: Qualifier le common context

As a moteur de prompts,
I want connaître l'état exact du contexte commun injecté (`QualifiedContext`),
so que je puisse distinguer un contexte complet d'un contexte dégradé.

### Story 66.6: Clarifier le rôle de l'adapter

As a architecte backend,
I want séparer la normalisation métier de l'intégration technique côté `AIEngineAdapter`,
so that la dérive fonctionnelle de cette couche soit limitée.

### Story 66.7: Enrichir `GatewayMeta`

As a équipe produit / tech,
I want des métadonnées d'exécution exposant le chemin réel (nominal / repaired / fallback / degraded),
so that je puisse comprendre précisément le chemin suivi par chaque réponse.

### Story 66.8: Migrer le parcours natal vers les nouveaux contrats

As a domaine natal,
I want consommer les nouveaux contrats de plateforme sans perdre les spécificités métier,
so that la dette locale soit réduite tout en conservant le comportement utilisateur nominal.
