---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
inputDocuments: []
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 0
classification:
  projectType: web_app
  domain: general
  complexity: medium
  projectContext: greenfield
workflowType: 'prd'
lastEdited: '2026-02-21T14:35:34+01:00'
editHistory:
  - date: '2026-02-21T14:35:34+01:00'
    changes: 'PRD coherence pass: harmonisation FR + precision NFR11'
  - date: '2026-02-21T14:34:26+01:00'
    changes: 'NFR SMART pass #3: formalisation accessibilite et integration (NFR13/14/15/17/18)'
  - date: '2026-02-21T14:33:00+01:00'
    changes: 'NFR SMART pass #2: formalisation des NFR6/7/8/11/12/16/20/21/22'
  - date: '2026-02-21T14:28:51+01:00'
    changes: 'NFR SMART pass: clarifications measurability/security/scalability/reliability'
---

# Product Requirements Document - horoscope_front

**Author:** Cyril
**Date:** 2026-02-17T19:44:31+01:00

## Executive Summary

Le produit est une application web centrée sur un moteur backend Python de calcul astrologique, exposé pour un frontend React et des usages conversationnels. Il vise des utilisateurs recherchant un accompagnement astrologique personnalisé, disponible à tout moment, pour des décisions personnelles ou des moments de vie sensibles.

La proposition de valeur combine trois exigences rarement réunies: rigueur des calculs, personnalisation contextuelle continue, et accessibilité tarifaire. Le système doit produire des résultats cohérents à partir de données utilisateur structurées (profil natal, contexte, historique d’interaction) et permettre une consultation 24/7 via des astrologues virtuels capables de maintenir le contexte sans requalification répétée.

Le positionnement repose sur la confiance: méthodes de calcul explicites, qualité perçue stable, et confidentialité forte des données personnelles. L’objectif est de créer une relation durable par la précision, la continuité de service et la sécurité des informations intimes partagées par l’utilisateur.

### Ce Qui Rend Le Produit Unique

Le différenciateur principal est l’intégration d’un socle de calcul astrologique robuste avec une interface conversationnelle personnalisée en continu. Contrairement aux horoscopes génériques, l’expérience cible des recommandations contextualisées par utilisateur, exploitables dans des situations concrètes.

Le produit se distingue par:
- une disponibilité permanente d’un astrologue virtuel context-aware;
- une personnalisation profonde fondée sur les données utilisateur et l’historique;
- un cadrage de confiance basé sur la rigueur calculatoire et la traçabilité logique des sorties;
- une approche confidentialité-first sur des données à forte sensibilité personnelle;
- une stratégie de prix accessible pour favoriser l’adoption récurrente.

## Project Classification

- **Project Type:** `web_app`
- **Domain:** `general` (astrologie/ésotérisme)
- **Complexity:** `medium`
- **Project Context:** `greenfield`
## Success Criteria

### User Success

- L’utilisateur obtient une première valeur perçue forte via un rapport astrologique journalier/hebdomadaire jugé pertinent ("effet waouh").
- L’utilisateur peut compléter son onboarding (date/heure/lieu de naissance) et recevoir un premier thème astral exploitable en moins de 5 minutes.
- Objectif de performance produit sur le flux initial: génération du thème astral en 2 min 30 max après soumission complète des données.
- Rétention cible: au moins 50% des utilisateurs reviennent après leur premier thème astral (fenêtre opérationnelle à confirmer).

### Business Success

- Objectif financier principal: dépasser 100 000 EUR de revenu annuel (ARR) à 12 mois.
- Hypothèse de base: 2 000 utilisateurs à 5 EUR/mois = 10 000 EUR/mois, soit 120 000 EUR/an.
- Monétisation multi-niveaux:
  - Basic à 5 EUR/mois: 5 messages/jour.
  - Premium à 20 EUR/mois: échanges illimités.
- Ventes additionnelles à la demande:
  - tirages spécifiques (moments critiques),
  - extensions ponctuelles de quota messages.

### Technical Success

- Expérience conversationnelle proche des standards d’un assistant LLM moderne (fluidité et clarté des réponses).
- Latence maîtrisée sur le cœur de calcul astrologique pour ne pas dégrader l’expérience chat.
- Qualité des réponses encadrée: garde-fous pour limiter les réponses hors-scope, incohérentes ou non pertinentes.
- Confidentialité et sécurité by design:
  - accès utilisateur à ses données,
  - suppression simple et effective des données,
  - anonymisation des échanges transmis aux LLM (pas d’identifiants directs),
  - chiffrement des données au repos et en transit via standards reconnus.

### Measurable Outcomes

- Temps max première réponse utile: < 5 min.
- Temps max production thème astral initial: <= 2 min 30.
- Rétention post-premier thème: >= 50% (fenêtre à confirmer).
- ARR à 12 mois: >= 100 000 EUR.
- Utilisateurs actifs payants à 12 mois: ~2 000 (minimum).
- KPI monétisation: part Basic vs Premium, taux de passage Basic -> Premium, taux d’achat d’options à la demande.
- KPI qualité IA: taux de réponses hors-scope sous seuil défini (seuil à fixer).

## Product Scope

### MVP - Minimum Viable Product

- Génération d’un thème astral complet et lisible à partir de date/heure/lieu de naissance.
- Restitution documentée, claire, bien structurée.
- Chat avec astrologue virtuel pour interaction en messages.
- Déploiement d’un profil astrologue unique pour le lancement MVP.

### Growth Features (Post-MVP)

- Renforcement de la personnalisation conversationnelle selon contexte et historique utilisateur.
- Amélioration de la différenciation conversationnelle (qualité, ton, profondeur des réponses).
- Optimisations produit pour rendre le chat un avantage concurrentiel net.

### Vision (Future)

- Extension vers cartomancie et pratiques associées: tarot, runes, etc.
- Multiplication des profils d’accompagnants (astrologues spécialisés, styles variés).
- Plateforme holistique d’accompagnement astro/cartomancie personnalisée.
## User Journeys

### 1) Primary User - Success Path (B2C)

**Persona:** Emma, 31 ans, consultante, utilise l’astrologie pour préparer des décisions personnelles importantes.
**Opening Scene:** Elle veut une guidance personnalisée, pas un horoscope générique. Elle s’inscrit avec date/heure/lieu de naissance.
**Rising Action:** En moins de 5 minutes, elle reçoit son thème astral initial, clair et structuré. Elle ouvre ensuite le chat avec un astrologue virtuel qui conserve son contexte.
**Climax:** Lors d’un moment de doute, elle pose une question sensible et obtient une réponse précise, contextualisée et perçue comme crédible.
**Resolution:** Elle adopte un usage récurrent (check hebdo + questions ponctuelles), passe à une offre adaptée à son intensité d’usage.

### 2) Primary User - Edge Case (Confiance / confidentialité / qualité)

**Persona:** Lucas, 27 ans, utilisateur prudent sur la vie privée.
**Opening Scene:** Il veut tester le service mais craint l’usage de ses données personnelles.
**Rising Action:** Il vérifie les paramètres de confidentialité, les mécanismes d’accès/suppression des données, et démarre une session.
**Climax:** Il reçoit une réponse qu’il juge trop générique ou hors-scope; il signale le problème.
**Resolution:** Le produit fournit une reformulation/retry encadrée, et Lucas garde le contrôle de ses données (suppression/export). La confiance est restaurée par transparence + contrôle utilisateur.

### 3) Admin Produit / Operations

**Persona:** Nadia, Product Ops.
**Opening Scene:** Elle gère les offres (5 EUR / 20 EUR), quotas, profils astrologues et configuration des garde-fous.
**Rising Action:** Elle ajuste les limites messages, active un nouveau profil d’astrologue, surveille les KPI (conversion, rétention, hors-scope, latence).
**Climax:** Un pic de réponses hors-scope est détecté après un changement de prompt/policy.
**Resolution:** Rollback contrôlé + ajustement de configuration; les KPI reviennent au niveau cible sans interruption majeure.

### 4) Support Client / RGPD

**Persona:** Karim, support niveau 1/2.
**Opening Scene:** Il reçoit une demande combinée: “je veux supprimer mes données et comprendre une facturation d’option.”
**Rising Action:** Depuis le back-office, il retrouve le compte, l’historique d’achats add-on, et déclenche le workflow RGPD (export/suppression).
**Climax:** Le client demande confirmation explicite que ses données ne sont pas envoyées identifiantes au LLM.
**Resolution:** Support fournit preuve de process (anonymisation, chiffrement, logs de conformité) et clôture la demande dans les SLA internes.

### 5) API/Integration - Client B2B Média

**Persona:** Sophie, responsable produit d’un média digital.
**Opening Scene:** Son journal veut publier une rubrique astrologie hebdomadaire personnalisée par signe, avec ton éditorial maison.
**Rising Action:** Elle souscrit une offre B2B, crée/régénère des clés API depuis son espace compte, configure style éditorial et volumes attendus.
**Climax:** L’équipe intègre l’API dans leur CMS, consomme les prédictions hebdo, et demande des ajustements de style.
**Resolution:** Le média publie régulièrement du contenu aligné à sa ligne éditoriale; le suivi KPI (usage API, qualité, volume, disponibilité) pilote l’extension de contrat (fixe + variable au volume).

### 6) B2B Account Admin - Expansion & Billing

**Persona:** Thomas, manager partenariats B2B.
**Opening Scene:** Le client média veut augmenter la fréquence de publication et ajouter des segments.
**Rising Action:** Il compare usage réel vs forfait, propose upgrade et options volume, active extension de plan.
**Climax:** Le client demande flexibilité tarifaire selon pics saisonniers.
**Resolution:** Modèle hybride (abonnement fixe + tranche volume) appliqué, avec visibilité claire sur consommation et prévision budgétaire.

### Journey Requirements Summary

Ces parcours révèlent les capacités indispensables suivantes:
- Onboarding natal rapide (date/heure/lieu) + génération de thème en délai cible.
- Chat contextuel persistant avec profils astrologues.
- Contrôles qualité IA (hors-scope, retry, garde-fous).
- Confidentialité by design (anonymisation LLM, chiffrement, export/suppression).
- Back-office interne (offres, quotas, profils, monitoring KPI, rollback config).
- Support outillé (tickets, facturation, RGPD, traçabilité conformité).
- Espace compte B2B (clés API, style éditorial, gestion offre, suivi consommation).
- API de contenu astrologique versionnée, gouvernée par quotas/plan et métriques d’usage.
- Billing hybride (fixe + volume) avec mécanismes d’upgrade.
## Domain-Specific Requirements

### Compliance & Regulatory
- RGPD by design: droit d’accès, export, suppression complète des données utilisateur.
- Journalisation des actions sensibles (suppression/export, changements de plan, régénération de clés API).
- Politique de conservation des données explicite (durée, purge, justification métier).

### Technical Constraints
- Chiffrement en transit (TLS) et au repos (standards reconnus).
- Anonymisation/pseudonymisation avant envoi vers LLM (pas d’identifiants directs).
- Garde-fous IA: filtrage hors-scope, validation de format de réponse, mécanisme de retry contrôlé.
- Performance cible alignée UX: onboarding + génération thème dans les délais définis, chat fluide.

### Integration Requirements
- API B2B sécurisée avec clés régénérables, quotas et limites par plan.
- Back-office client B2B: gestion offre, style éditorial, suivi consommation, demandes de modification.
- Modèle de facturation hybride: abonnement fixe + composante volume.

### Risk Mitigations
- Risque fuite données: chiffrement fort + séparation des secrets + rotation des clés.
- Risque réponse IA incorrecte/hors-scope: règles de cadrage, fallback, monitoring qualité.
- Risque dérive coûts API LLM: quotas, alerting, plafonds de consommation.
- Risque réputation B2B (contenu inadéquat): workflow de validation éditoriale et paramètres de style contrôlés.
## Innovation & Novel Patterns

### Detected Innovation Areas

- Fusion de trois couches rarement intégrées proprement dans ce marché:
  - moteur de calcul astrologique structuré et traçable,
  - assistant conversationnel contextuel disponible 24/7,
  - distribution B2B via API avec personnalisation éditoriale.
- Passage d’un contenu astro “broadcast” (générique) à un service “context-aware” individuel + entreprise.
- Packaging business hybride B2C/B2B sur un même socle technique (abonnements, quotas, volume).

### Market Context & Competitive Landscape

- Côté B2C, l’offre existante est souvent fragmentée: soit horoscope générique, soit consultation humaine coûteuse, soit chatbot peu spécialisé.
- Côté B2B média, la valeur vient de la capacité à produire un contenu astro régulier, éditorialisable, piloté par API et KPI.
- Différenciation visée:
  - crédibilité calculatoire,
  - continuité conversationnelle,
  - confidentialité forte,
  - capacité de custom éditorial B2B.

### Validation Approach

- Pilote B2C:
  - mesurer “wow moment” après premier thème,
  - mesurer rétention post-premier usage,
  - mesurer taux de réponses jugées pertinentes.
- Pilote B2B:
  - signer 1–3 premiers clients média,
  - valider intégration API + paramétrage style,
  - suivre usage, qualité perçue, renouvellement/upsell.
- Expérimentations:
  - A/B sur styles de restitution,
  - tests de profondeur contextuelle du chat,
  - tests de limites quotas/pricing.

### Risk Mitigation

- Risque “innovation theater” (promesse > preuve):
  - priorité aux KPI de confiance/qualité avant expansion fonctionnelle.
- Risque qualité IA variable:
  - garde-fous, templates de réponse, monitoring hors-scope, boucle d’amélioration.
- Risque B2B de non-alignement éditorial:
  - paramètres de style explicites + workflow de feedback.
- Risque de complexité produit trop tôt:
  - phasage strict MVP -> Growth -> Vision.
## Web App Specific Requirements

### Project-Type Overview

Le produit est conçu comme une Single Page Application (SPA) avec frontend React, orientée interaction conversationnelle continue. Le choix SPA est motivé par l’exigence de fluidité sur le chat, la navigation rapide entre vues, et la persistance de contexte utilisateur pendant les sessions astrologiques.

Le SEO n’est pas un objectif prioritaire à ce stade: le produit cible principalement une expérience applicative authentifiée et récurrente plutôt qu’une stratégie d’acquisition organique par indexation de pages publiques.

### Technical Architecture Considerations

- Application Model: SPA React avec routing client-side.
- Browser Support: support officiel Chrome et Edge (versions stables actuelles).
- Real-Time Interaction: support natif des échanges temps réel pour le chat astrologique (streaming/réponses progressives et gestion d’état conversationnel).
- Accessibility Baseline: conformité cible WCAG 2.1 AA pour garantir une accessibilité standard de niveau professionnel.
- Performance Baseline: alignement sur des standards e-commerce usuels (temps de chargement perçu court, interaction fluide, stabilité visuelle, réactivité interface).

### Browser Matrix

- Navigateurs officiellement pris en charge:
  - Google Chrome (desktop)
  - Microsoft Edge (desktop)
- Politique de compatibilité:
  - prise en charge des versions stables majeures;
  - comportement dégradé acceptable hors périmètre officiel.

### Responsive Design

- Expérience utilisable desktop + mobile.
- Priorité aux parcours critiques:
  - onboarding natal,
  - lecture de thème,
  - chat astrologue,
  - gestion abonnement.

### Performance Targets

- Objectif général: performance perçue site marchand (rapide, stable, réactive).
- Cibles qualitatives:
  - chargement initial optimisé,
  - transitions rapides entre écrans,
  - latence UI faible dans le chat,
  - absence de blocages visibles lors des appels backend/LLM.

### SEO Strategy

- SEO non prioritaire pour le MVP.
- Implémentation minimale:
  - métadonnées de base,
  - pages légales accessibles,
  - architecture évolutive si SEO devient stratégique plus tard.

### Accessibility Level

- Référence: WCAG 2.1 AA.
- Exigences minimales:
  - navigation clavier sur parcours critiques,
  - contrastes lisibles,
  - libellés explicites des champs/formulaires,
  - compatibilité lecteur d’écran sur composants clés.

### Implementation Considerations

- Le frontend doit refléter les contraintes métier du backend de calcul (temps de réponse, disponibilité, garde-fous).
- Les états loading/error/empty doivent être explicites sur les vues critiques (thème, chat, abonnement).
- Le design de l’expérience temps réel doit éviter toute ambiguïté sur:
  - statut de génération de réponse,
  - limites de quota/messages,
  - consommation liée au plan utilisateur.
## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving + Revenue MVP.
Objectif: prouver rapidement la valeur utilisateur (thème + chat) et la viabilité commerciale avec un socle monétisable simple.

**Resource Requirements:**
- 1 backend Python (moteur astro + API)
- 1 frontend React (SPA + chat + compte)
- 1 fullstack/ops (auth, billing simple, infra, sécurité)
- support ponctuel produit/contenu pour validation qualité astrologique

### Phase 0 - Foundation (Avant MVP)

- Construction du moteur de logique astrologique dédié.
- Structuration de la base de référence (planètes, signes, maisons, aspects, caractéristiques).
- Versionning des règles de calcul et des données de référence.
- Mise en place de la traçabilité entre résultats produits et versions de règles/données.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- B2C uniquement au lancement: onboarding natal -> thème astral initial -> chat astrologue.
- Edge case critique: accès/suppression des données utilisateur.
- Pas de parcours B2B en MVP initial.

**Must-Have Capabilities:**
- Génération thème astral (date/heure/lieu) dans les délais cibles.
- Chat astrologue avec un seul profil au lancement.
- Un seul plan payant initial (Basic 5 EUR) pour limiter la complexité billing.
- Confidentialité/sécurité essentielles:
  - chiffrement transit/repos,
  - anonymisation des données envoyées au LLM,
  - export/suppression des données.
- Dashboard minimal utilisateur:
  - quota/jour,
  - historique basique,
  - gestion compte.

### Post-MVP Features

**Phase 2 (Post-MVP):**
- Premium illimité.
- Multi-profils astrologues.
- B2B API + espace entreprise.
- Add-ons à la demande (tirages spécifiques, extensions messages).
- Personnalisation conversationnelle avancée.

**Phase 3 (Expansion):**
- Extension ésotérique complète: tarot, runes, cartomancie élargie.
- Expériences premium avancées.
- Déploiement B2B multi-clients et partenariats élargis.

### Risk Mitigation Strategy

**Technical Risks:**
- Risque principal: qualité/pertinence des réponses IA et cohérence métier astro.
- Mitigation: garde-fous stricts, monitoring hors-scope, rollback de configuration.

**Market Risks:**
- Risque principal: faible valeur perçue après premier thème.
- Mitigation: optimisation du wow moment et suivi de la rétention post-premier usage.

**Resource Risks:**
- Risque principal: dispersion B2C/B2B trop tôt.
- Mitigation: séquencement strict, B2B reporté post-MVP.
## Functional Requirements

### Astrology Logic Engine (Foundation Prerequisite)

- FR1: Product and engineering teams can establish the Astrology Logic Engine as a prerequisite foundation before MVP application features.
- FR2: The system can provide a dedicated astrology logic engine as an independent core capability.
- FR3: The astrology logic engine can compute astrological results from user birth inputs.
- FR4: The astrology logic engine can use and maintain a reference database of celestial entities (planets, signs, houses, aspects).
- FR5: The astrology logic engine can store and expose astrological characteristics linked to reference entities.
- FR6: The astrology logic engine can version its computation rules and reference data.
- FR7: Product and operations users can manage updates to astrological reference data and rule definitions.
- FR8: The system can trace which rule and data version produced a given astrological output.

### Account & Identity Management

- FR9: Users can create an account and authenticate to access personalized features.
- FR10: Users can manage their profile data required for personalized astrology services.
- FR11: Users can provide and update birth data (date, time, place) used for astrological outputs.
- FR12: Users can access account settings and subscription status.
- FR13: Support agents can access user account context needed to resolve user requests.

### Astrology Core Experience

- FR14: Users can request generation of a natal chart from their birth data.
- FR15: Users can view a structured natal chart interpretation.
- FR16: Users can request daily or weekly astrological guidance derived from their profile.
- FR17: Users can request contextualized guidance tied to their current situation.
- FR18: The system can produce astrology outputs using a consistent ruleset across sessions.

### Conversational Astrologer Experience

- FR19: Users can interact with a virtual astrologer through conversational messaging.
- FR20: The system can preserve conversation context to avoid repeated user re-explanation.
- FR21: Users can continue prior conversations and retrieve relevant conversation history.
- FR22: The system can provide guided recovery when a response is flagged as irrelevant or off-scope.
- FR23: Product operations can configure astrologer persona behavior boundaries.

### Subscription, Quotas & Monetization

- FR24: Users can subscribe to an entry paid plan.
- FR25: The system can enforce daily message quotas according to the user’s active plan.
- FR26: Users can view remaining quota and usage for the current period.
- FR27: Users can upgrade or modify subscription plans when additional tiers are enabled.
- FR28: The business can define and manage pricing plans and associated usage policies.

### Privacy, Data Rights & Trust

- FR29: Users can request export of their personal data.
- FR30: Users can request deletion of their personal data and account data.
- FR31: The system can process user data for LLM interactions without exposing direct personal identifiers.
- FR32: Support and operations can track completion of privacy-related requests.
- FR33: The system can provide audit visibility for sensitive account and data-rights actions.

### Support & Operations Management

- FR34: Support users can manage incidents related to account, subscription, and content issues.
- FR35: Operations users can monitor product quality indicators related to conversational relevance.
- FR36: Operations users can apply and revert configuration changes affecting response quality behavior.
- FR37: Operations users can monitor usage indicators needed for product and business decisions.

### B2B API & Enterprise Self-Service (Post-MVP Scope)

- FR38: Les clients entreprise peuvent créer et gérer des identifiants API pour leur compte.
- FR39: Les clients entreprise peuvent consommer du contenu astrologique via un accès API authentifié.
- FR40: Les clients entreprise peuvent gérer les limites de leur plan et consulter leurs métriques de consommation.
- FR41: Les clients entreprise peuvent demander des ajustements de style de contenu alignés avec leurs besoins éditoriaux.
- FR42: L’entreprise peut facturer les clients entreprise via un modèle combinant abonnement fixe et composante variable à l’usage.
## Non-Functional Requirements

### Performance

- NFR1: Le système doit permettre la génération d’un premier thème astral en <= 2 min 30 après soumission complète des données de naissance.
- NFR2: Le parcours inscription -> première réponse utile doit être réalisable en < 5 min pour un utilisateur standard.
- NFR3: Les actions d’interface critiques (navigation interne SPA, envoi message, ouverture historique) doivent afficher un feedback visuel en <= 200 ms dans 95% des cas et ne jamais bloquer l’interface utilisateur plus de 1 s sans indicateur de chargement.
- NFR4: Le service conversationnel doit fournir une première unité de réponse en <= 3 s (p95) et terminer la réponse complète en <= 15 s (p95) pour une requête standard.

### Security & Privacy

- NFR5: Les données sensibles doivent être chiffrées en transit (TLS 1.2+) et au repos (AES-256 ou équivalent), avec vérification trimestrielle documentée de la configuration.
- NFR6: 100% des requêtes envoyées aux LLM doivent être pseudonymisées pour exclure les identifiants personnels directs (email, téléphone, nom complet, adresse postale), avec contrôle automatique en pré-envoi.
- NFR7: Le système doit permettre l’export des données utilisateur en format structuré (JSON ou CSV) sous <= 72 h après demande validée, et la suppression complète sous <= 30 jours calendaires avec confirmation d’exécution.
- NFR8: Les actions sensibles (suppression données, régénération clés, changements d’offre) doivent être journalisées avec horodatage, acteur, type d’action et identifiant de ressource, avec conservation des journaux pendant au moins 12 mois.
- NFR9: Les secrets d’intégration (clés API, credentials) doivent être stockés dans un gestionnaire de secrets dédié, jamais en clair dans le code ou les logs, et tournés au minimum tous les 90 jours.

### Scalability

- NFR10: Le système doit supporter au moins 2 000 utilisateurs payants actifs/mois en maintenant une latence API p95 <= 2 s sur les endpoints critiques et un taux d’erreur serveur mensuel < 1%.
- NFR11: Les composants critiques doivent permettre une montée en charge horizontale d’au moins x2 du trafic moyen observé sur les 30 derniers jours, sans refonte fonctionnelle et sans régression des SLO définis (latence p95 et taux d’erreur).
- NFR12: Le système doit appliquer des quotas configurables par plan (messages/jour et appels API/jour) avec blocage automatique au dépassement et remise à zéro périodique documentée.

### Accessibility

- NFR13: Les parcours critiques doivent atteindre la conformité WCAG 2.1 niveau AA sur 100% des écrans MVP audités avant mise en production.
- NFR14: 100% des interactions principales doivent être utilisables au clavier (navigation tabulation + activation Entrée/Espace) et compatibles lecteur d’écran sur Chrome et Edge.
- NFR15: Les composants critiques doivent respecter un contraste minimum de 4.5:1 pour le texte normal et 3:1 pour les éléments UI non textuels.

### Integration

- NFR16: Le système doit intégrer les APIs LLM avec timeout <= 20 s par appel, au maximum 2 retries exponentiels sur erreurs transitoires, et fallback explicite vers une réponse dégradée en cas d’échec final.
- NFR17: Le système doit exposer des interfaces d’intégration B2B versionnées (ex. `/v1`, `/v2`) avec politique de compatibilité rétroactive d’au moins 6 mois après annonce de dépréciation.
- NFR18: Les intégrations externes doivent publier au minimum les métriques disponibilité, taux d’erreur et latence p95, avec une fenêtre d’observation continue et un tableau de bord opérationnel mis à jour en temps réel.

### Reliability & Operational Quality

- NFR19: Le système doit maintenir une disponibilité mensuelle >= 99.5% sur les services critiques orientés utilisateur.
- NFR20: Le système doit détecter et tracer les réponses hors-scope avec un taux de classification automatique >= 90% sur jeu de validation interne, et produire un rapport hebdomadaire de suivi.
- NFR21: Le mécanisme de rollback de configuration doit permettre un retour à la dernière configuration stable en <= 15 minutes après déclenchement.
- NFR22: Chaque résultat astrologique doit inclure un identifiant de version du moteur logique et des règles utilisées, afin de garantir une traçabilité de 100% des calculs restitués.

