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
---

# Product Requirements Document - horoscope_front

**Author:** Cyril
**Date:** 2026-02-17T19:44:31+01:00

## Executive Summary

Le produit est une application web centrée sur un moteur backend Python de calcul astrologique, exposé pour un frontend React et des usages conversationnels. Il vise des utilisateurs recherchant un accompagnement astrologique personnalisé, disponible à tout moment, pour des décisions personnelles ou des moments de vie sensibles.

La proposition de valeur combine trois exigences rarement réunies: rigueur des calculs, personnalisation contextuelle continue, et accessibilité tarifaire. Le système doit produire des résultats cohérents à partir de données utilisateur structurées (profil natal, contexte, historique d’interaction) et permettre une consultation 24/7 via des astrologues virtuels capables de maintenir le contexte sans requalification répétée.

Le positionnement repose sur la confiance: méthodes de calcul explicites, qualité perçue stable, et confidentialité forte des données personnelles. L’objectif est de créer une relation durable par la précision, la continuité de service et la sécurité des informations intimes partagées par l’utilisateur.

### What Makes This Special

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

- FR38: Enterprise clients can create and manage API credentials for their account.
- FR39: Enterprise clients can consume astrology content through authenticated API access.
- FR40: Enterprise clients can manage plan limits and view consumption metrics.
- FR41: Enterprise clients can request content style adjustments aligned with editorial needs.
- FR42: The business can bill enterprise clients using fixed subscription and usage-based components.
## Non-Functional Requirements

### Performance

- NFR1: Le système doit permettre la génération d’un premier thème astral en <= 2 min 30 après soumission complète des données de naissance.
- NFR2: Le parcours inscription -> première réponse utile doit être réalisable en < 5 min pour un utilisateur standard.
- NFR3: Les actions d’interface critiques (navigation interne SPA, envoi message, ouverture historique) doivent fournir un feedback utilisateur immédiat et éviter les blocages perçus.
- NFR4: Le service conversationnel doit supporter des réponses progressives (streaming ou équivalent) pour réduire la latence perçue.

### Security & Privacy

- NFR5: Les données sensibles doivent être chiffrées en transit et au repos selon standards reconnus.
- NFR6: Les échanges envoyés aux LLM doivent exclure les identifiants personnels directs.
- NFR7: Le système doit fournir des mécanismes opérationnels d’export et suppression des données utilisateur.
- NFR8: Les actions sensibles (suppression données, régénération clés, changements d’offre) doivent être journalisées de manière traçable.
- NFR9: Les secrets d’intégration (clés API, credentials) doivent être gérés via un mécanisme dédié de gestion des secrets.

### Scalability

- NFR10: Le système doit pouvoir absorber une croissance progressive vers l’objectif de ~2 000 utilisateurs payants sans dégradation majeure de l’expérience perçue.
- NFR11: Les composants critiques doivent permettre une montée en charge incrémentale (scale out ou équivalent) sans refonte fonctionnelle.
- NFR12: Le système doit permettre la mise en place de limites d’usage (quotas/messages) afin de maîtriser la charge et les coûts LLM.

### Accessibility

- NFR13: Les parcours critiques doivent viser la conformité WCAG 2.1 AA.
- NFR14: Les interactions principales doivent être utilisables au clavier et compréhensibles par lecteur d’écran.
- NFR15: Les contrastes et libellés des composants critiques doivent respecter les bonnes pratiques d’accessibilité.

### Integration

- NFR16: Le système doit intégrer de manière fiable les APIs LLM avec gestion d’erreurs, retries contrôlés et fallback défini.
- NFR17: Le système doit exposer des interfaces d’intégration versionnables pour les usages B2B (post-MVP).
- NFR18: Les intégrations externes doivent être observables via métriques minimales (disponibilité, erreurs, latence).

### Reliability & Operational Quality

- NFR19: Le système doit maintenir une disponibilité compatible avec un service utilisateur 24/7.
- NFR20: Le système doit détecter, tracer et remonter les réponses hors-scope afin de soutenir l’amélioration continue.
- NFR21: Le système doit disposer d’un mécanisme de rollback de configuration pour restaurer rapidement la qualité de service.
- NFR22: Le système doit conserver une traçabilité entre résultats astrologiques et version du moteur logique utilisée.

