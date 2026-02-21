---
stepsCompleted:
  - step-01-document-discovery
documentsIncluded:
  prd: prd.md
  prd_validation: prd-validation-report.md
  architecture: architecture.md
  epics: epics.md
  ux_design: ux-design-specification.md
  - step-02-prd-analysis
  - step-03-epic-coverage-validation
  - step-04-ux-alignment
  - step-05-epic-quality-review
  - step-06-final-assessment
---

# Implementation Readiness Assessment Report

**Date:** 2026-02-18
**Project:** horoscope_front

## 1. Inventaire des Documents

| Type | Fichier | Statut |
|------|---------|--------|
| PRD | prd.md | ✅ Trouvé |
| PRD Validation | prd-validation-report.md | ✅ Trouvé |
| Architecture | architecture.md | ✅ Trouvé |
| Epics & Stories | epics.md | ✅ Trouvé |
| UX Design | ux-design-specification.md | ✅ Trouvé |

**Doublons :** Aucun
**Documents manquants :** Aucun

## 2. Analyse du PRD

### Exigences Fonctionnelles (FRs)

**Astrology Logic Engine (Foundation Prerequisite)**
- FR1: Product and engineering teams can establish the Astrology Logic Engine as a prerequisite foundation before MVP application features.
- FR2: The system can provide a dedicated astrology logic engine as an independent core capability.
- FR3: The astrology logic engine can compute astrological results from user birth inputs.
- FR4: The astrology logic engine can use and maintain a reference database of celestial entities (planets, signs, houses, aspects).
- FR5: The astrology logic engine can store and expose astrological characteristics linked to reference entities.
- FR6: The astrology logic engine can version its computation rules and reference data.
- FR7: Product and operations users can manage updates to astrological reference data and rule definitions.
- FR8: The system can trace which rule and data version produced a given astrological output.

**Account & Identity Management**
- FR9: Users can create an account and authenticate to access personalized features.
- FR10: Users can manage their profile data required for personalized astrology services.
- FR11: Users can provide and update birth data (date, time, place) used for astrological outputs.
- FR12: Users can access account settings and subscription status.
- FR13: Support agents can access user account context needed to resolve user requests.

**Astrology Core Experience**
- FR14: Users can request generation of a natal chart from their birth data.
- FR15: Users can view a structured natal chart interpretation.
- FR16: Users can request daily or weekly astrological guidance derived from their profile.
- FR17: Users can request contextualized guidance tied to their current situation.
- FR18: The system can produce astrology outputs using a consistent ruleset across sessions.

**Conversational Astrologer Experience**
- FR19: Users can interact with a virtual astrologer through conversational messaging.
- FR20: The system can preserve conversation context to avoid repeated user re-explanation.
- FR21: Users can continue prior conversations and retrieve relevant conversation history.
- FR22: The system can provide guided recovery when a response is flagged as irrelevant or off-scope.
- FR23: Product operations can configure astrologer persona behavior boundaries.

**Subscription, Quotas & Monetization**
- FR24: Users can subscribe to an entry paid plan.
- FR25: The system can enforce daily message quotas according to the user's active plan.
- FR26: Users can view remaining quota and usage for the current period.
- FR27: Users can upgrade or modify subscription plans when additional tiers are enabled.
- FR28: The business can define and manage pricing plans and associated usage policies.

**Privacy, Data Rights & Trust**
- FR29: Users can request export of their personal data.
- FR30: Users can request deletion of their personal data and account data.
- FR31: The system can process user data for LLM interactions without exposing direct personal identifiers.
- FR32: Support and operations can track completion of privacy-related requests.
- FR33: The system can provide audit visibility for sensitive account and data-rights actions.

**Support & Operations Management**
- FR34: Support users can manage incidents related to account, subscription, and content issues.
- FR35: Operations users can monitor product quality indicators related to conversational relevance.
- FR36: Operations users can apply and revert configuration changes affecting response quality behavior.
- FR37: Operations users can monitor usage indicators needed for product and business decisions.

**B2B API & Enterprise Self-Service (Post-MVP Scope)**
- FR38: Enterprise clients can create and manage API credentials for their account.
- FR39: Enterprise clients can consume astrology content through authenticated API access.
- FR40: Enterprise clients can manage plan limits and view consumption metrics.
- FR41: Enterprise clients can request content style adjustments aligned with editorial needs.
- FR42: The business can bill enterprise clients using fixed subscription and usage-based components.

**Total FRs: 42**

### Exigences Non-Fonctionnelles (NFRs)

**Performance**
- NFR1: Génération d'un premier thème astral en <= 2 min 30 après soumission complète des données.
- NFR2: Parcours inscription -> première réponse utile en < 5 min.
- NFR3: Feedback immédiat sur actions d'interface critiques, pas de blocages perçus.
- NFR4: Réponses progressives (streaming) pour réduire la latence perçue.

**Sécurité & Vie privée**
- NFR5: Chiffrement en transit et au repos selon standards reconnus.
- NFR6: Exclusion des identifiants personnels directs dans les échanges LLM.
- NFR7: Mécanismes d'export et suppression des données utilisateur.
- NFR8: Journalisation traçable des actions sensibles.
- NFR9: Gestion des secrets via mécanisme dédié.

**Scalabilité**
- NFR10: Croissance progressive vers ~2 000 utilisateurs payants sans dégradation.
- NFR11: Montée en charge incrémentale sans refonte fonctionnelle.
- NFR12: Limites d'usage (quotas/messages) pour maîtriser charge et coûts LLM.

**Accessibilité**
- NFR13: Conformité WCAG 2.1 AA sur parcours critiques.
- NFR14: Utilisable au clavier et lecteur d'écran.
- NFR15: Contrastes et libellés conformes aux bonnes pratiques.

**Intégration**
- NFR16: Intégration fiable des APIs LLM avec gestion d'erreurs, retries et fallback.
- NFR17: Interfaces d'intégration versionnables pour B2B (post-MVP).
- NFR18: Observabilité des intégrations externes (disponibilité, erreurs, latence).

**Fiabilité & Qualité opérationnelle**
- NFR19: Disponibilité compatible service 24/7.
- NFR20: Détection et traçabilité des réponses hors-scope.
- NFR21: Mécanisme de rollback de configuration.
- NFR22: Traçabilité résultats astrologiques / version moteur logique.

**Total NFRs: 22**

### Exigences Additionnelles

**Contraintes techniques**
- SPA React avec routing client-side
- Support navigateurs: Chrome et Edge (versions stables)
- SEO non prioritaire pour MVP
- Responsive desktop + mobile

**Contraintes business**
- MVP B2C uniquement, B2B reporté post-MVP
- Un seul plan payant initial (Basic 5 EUR/mois)
- Un seul profil astrologue au lancement
- Phasage strict: Phase 0 (Foundation) -> Phase 1 (MVP) -> Phase 2 (Post-MVP) -> Phase 3 (Expansion)

**Conformité & Réglementaire**
- RGPD by design: droit d'accès, export, suppression
- Politique de conservation des données explicite
- Journalisation des actions sensibles

### Évaluation de Complétude du PRD

- ✅ 42 exigences fonctionnelles clairement numérotées et catégorisées
- ✅ 22 exigences non-fonctionnelles couvrant performance, sécurité, scalabilité, accessibilité, intégration et fiabilité
- ✅ Séparation claire MVP vs Post-MVP (FR38-FR42 identifiées Post-MVP)
- ✅ Parcours utilisateurs détaillés (6 journeys)
- ✅ Critères de succès mesurables définis
- ✅ Stratégie de phasage documentée

## 3. Validation de la Couverture des Epics

### Matrice de Couverture FR

| FR | Exigence PRD | Couverture Epic | Statut |
|----|-------------|-----------------|--------|
| FR1 | Establish Astrology Logic Engine as prerequisite | Epic 1 - Story 1.1 | ✅ Couvert |
| FR2 | Dedicated astrology logic engine | Epic 1 - Story 1.4 | ✅ Couvert |
| FR3 | Compute astrological results from birth inputs | Epic 1 - Story 1.2, 1.4 | ✅ Couvert |
| FR4 | Reference database of celestial entities | Epic 1 - Story 1.3 | ✅ Couvert |
| FR5 | Astrological characteristics linked to reference | Epic 1 - Story 1.3 | ✅ Couvert |
| FR6 | Version computation rules and reference data | Epic 1 - Story 1.3, 1.5 | ✅ Couvert |
| FR7 | Manage updates to reference data and rules | Epic 1 - Story 1.3 | ✅ Couvert |
| FR8 | Trace rule/data version per output | Epic 1 - Story 1.5 | ✅ Couvert |
| FR9 | Create account and authenticate | Epic 2 - Story 2.1 | ✅ Couvert |
| FR10 | Manage profile data | Epic 2 - Story 2.2 | ✅ Couvert |
| FR11 | Provide/update birth data | Epic 2 - Story 2.2 | ✅ Couvert |
| FR12 | Access account settings and subscription status | Epic 2 - Story 2.4 | ✅ Couvert |
| FR13 | Support agents access user account context | Epic 4 - Story 4.6 | ✅ Couvert |
| FR14 | Request generation of natal chart | Epic 2 - Story 2.3 | ✅ Couvert |
| FR15 | View structured natal chart interpretation | Epic 2 - Story 2.4 | ✅ Couvert |
| FR16 | Request daily/weekly astrological guidance | Epic 3 - Story 3.4 | ✅ Couvert |
| FR17 | Request contextualized guidance | Epic 3 - Story 3.4 | ✅ Couvert |
| FR18 | Consistent ruleset across sessions | Epic 2 - Story 2.5 | ✅ Couvert |
| FR19 | Interact with virtual astrologer via messaging | Epic 3 - Story 3.1 | ✅ Couvert |
| FR20 | Preserve conversation context | Epic 3 - Story 3.2 | ✅ Couvert |
| FR21 | Continue prior conversations / retrieve history | Epic 3 - Story 3.3 | ✅ Couvert |
| FR22 | Guided recovery for off-scope responses | Epic 3 - Story 3.5 | ✅ Couvert |
| FR23 | Configure astrologer persona boundaries | Epic 3 - Story 3.6 | ✅ Couvert |
| FR24 | Subscribe to entry paid plan | Epic 4 - Story 4.1 | ✅ Couvert |
| FR25 | Enforce daily message quotas | Epic 4 - Story 4.2 | ✅ Couvert |
| FR26 | View remaining quota and usage | Epic 4 - Story 4.2 | ✅ Couvert |
| FR27 | Upgrade/modify subscription plans | Epic 4 - Story 4.3 | ✅ Couvert |
| FR28 | Define/manage pricing plans and policies | Epic 4 - Story 4.1, 4.3 | ✅ Couvert |
| FR29 | Request export of personal data | Epic 4 - Story 4.4 | ✅ Couvert |
| FR30 | Request deletion of personal data/account | Epic 4 - Story 4.4 | ✅ Couvert |
| FR31 | Process user data for LLM without identifiers | Epic 4 - Story 4.5 | ✅ Couvert |
| FR32 | Track privacy request completion | Epic 4 - Story 4.6 | ✅ Couvert |
| FR33 | Audit visibility for sensitive actions | Epic 4 - Story 4.5 | ✅ Couvert |
| FR34 | Manage support incidents | Epic 4 - Story 4.6 | ✅ Couvert |
| FR35 | Monitor conversational quality indicators | Epic 4 - Story 4.7 | ✅ Couvert |
| FR36 | Apply/revert quality config changes | Epic 4 - Story 4.7 | ✅ Couvert |
| FR37 | Monitor usage indicators | Epic 4 - Story 4.7 | ✅ Couvert |
| FR38 | Create/manage API credentials (B2B) | Epic 5 - Story 5.1 | ✅ Couvert |
| FR39 | Consume astrology content via API (B2B) | Epic 5 - Story 5.2 | ✅ Couvert |
| FR40 | Manage plan limits / consumption metrics (B2B) | Epic 5 - Story 5.3 | ✅ Couvert |
| FR41 | Request content style adjustments (B2B) | Epic 5 - Story 5.4 | ✅ Couvert |
| FR42 | Bill enterprise clients fixed + usage (B2B) | Epic 5 - Story 5.5 | ✅ Couvert |

### Exigences Manquantes

Aucune FR manquante identifiée.

### Statistiques de Couverture

- Total FRs dans le PRD : 42
- FRs couvertes dans les epics : 42
- Pourcentage de couverture : **100%**

## 4. Évaluation de l'Alignement UX

### Statut du Document UX

✅ **Trouvé** : `ux-design-specification.md` — document complet (14 étapes réalisées)

### Alignement UX ↔ PRD

| Aspect | PRD | UX Design | Alignement |
|--------|-----|-----------|------------|
| Onboarding natal (date/heure/lieu) | FR11, FR14 | Journey 1 - collecte + calcul thème | ✅ Aligné |
| Génération thème astral | FR14, FR15 | AstralThemeInsightCard + Journey 1 | ✅ Aligné |
| Chat astrologue virtuel | FR19, FR20, FR21 | AstroChatThread (composant central) | ✅ Aligné |
| Guidance quotidienne/hebdo | FR16, FR17 | WeeklyGuidanceRitualCard | ✅ Aligné |
| Détection hors-scope + recovery | FR22 | DistressSafetyGuard + Story 3.5 | ✅ Aligné |
| Persona astrologue configurable | FR23 | Journey 3 - changement astrologue | ✅ Aligné |
| Quotas et consommation | FR25, FR26 | Paywall après valeur (Journey 1) | ✅ Aligné |
| Export/suppression données | FR29, FR30 | Non détaillé visuellement dans UX | ⚠️ Partiel |
| Conformité WCAG 2.1 AA | NFR13-NFR15 | Section Responsive & Accessibility | ✅ Aligné |
| Responsive mobile-first | PRD scope | Stratégie mobile-first documentée | ✅ Aligné |
| Support navigateurs Chrome/Edge | PRD scope | Non mentionné dans UX (implicite) | ✅ OK |
| B2B API (Post-MVP) | FR38-FR42 | Non adressé (cohérent - Post-MVP) | ✅ N/A MVP |

### Alignement UX ↔ Architecture

| Aspect | UX Design | Architecture | Alignement |
|--------|-----------|-------------|------------|
| Design System (Tailwind + shadcn/ui) | Choix documenté | Architecture mentionne "UI kit custom léger" | ⚠️ Écart mineur |
| Chat streaming/progressif | AstroChatThread - état "generating/partial-stream" | NFR4 streaming supporté | ✅ Aligné |
| États loading/error/empty | Documentés pour tous composants custom | Pattern obligatoire dans architecture | ✅ Aligné |
| Navigation mobile-first | Bottom nav (chat, guidance, consultations, profil) | Structure pages frontend alignée | ✅ Aligné |
| Mode offline (lecture seule) | Documenté dans UX patterns | Non explicitement adressé dans architecture | ⚠️ Écart |
| ConsultationHubPanel (cartes, runes, etc.) | Composant documenté | Non présent dans structure frontend architecture | ⚠️ Écart |
| DistressSafetyGuard | Composant transversal documenté | Non explicitement adressé dans architecture | ⚠️ Écart |
| ContextTransferConsentModal | Composant documenté | Non explicitement adressé dans architecture | ⚠️ Écart |

### Problèmes d'Alignement Identifiés

**⚠️ Écart 1 : Design System**
- UX spécifie Tailwind CSS + shadcn/ui (primitives Radix)
- Architecture mentionne "UI kit custom léger" sans nommer ces technologies
- **Impact** : Faible — l'intention est alignée, la précision technique manque côté architecture

**⚠️ Écart 2 : Mode Offline**
- UX prévoit consultation offline en lecture seule des derniers échanges
- Architecture ne mentionne pas de stratégie de cache offline/service worker
- **Impact** : Moyen — nécessitera une décision technique pour l'implémentation

**⚠️ Écart 3 : Composants UX spécialisés non reflétés dans la structure frontend**
- ConsultationHubPanel, DistressSafetyGuard, ContextTransferConsentModal, WeeklyGuidanceRitualCard ne sont pas dans l'arborescence frontend de l'architecture
- **Impact** : Faible — l'architecture donne une structure de base extensible, ces composants s'y intègreront naturellement

**⚠️ Écart 4 : Fonctionnalités UX étendues vs scope MVP PRD**
- UX mentionne consultations spécialisées (tirage cartes, runes, compatibilité amoureuse, thème d'une autre personne)
- PRD MVP ne les inclut pas explicitement — classées Growth/Vision
- **Impact** : Faible si le phasage est respecté, mais le document UX devrait clarifier ce qui est MVP vs post-MVP

**⚠️ Écart 5 : Export/suppression données (UX incomplet)**
- PRD exige export (FR29) et suppression (FR30) des données
- UX ne détaille pas les écrans/flux visuels correspondants
- **Impact** : Moyen — les parcours utilisateur RGPD devraient être spécifiés visuellement

### Avertissements

- Le document UX est riche et bien structuré mais contient des fonctionnalités qui dépassent le scope MVP du PRD (consultations spécialisées, multi-profils astrologues). Un phasage clair dans le document UX lui-même éviterait toute confusion lors de l'implémentation.
- Les flux RGPD (export/suppression) méritent une spécification UX dédiée pour garantir la cohérence avec les exigences PRD.

## 5. Revue Qualité des Epics & Stories

### A. Validation de la Valeur Utilisateur par Epic

| Epic | Titre | Orienté utilisateur ? | Verdict |
|------|-------|-----------------------|---------|
| Epic 1 | Moteur Astrologique Fiable et Versionné | ⚠️ Borderline technique | 🟠 Accepté sous conditions |
| Epic 2 | Compte Utilisateur et Première Valeur (Thème Natal) | ✅ Oui | ✅ Conforme |
| Epic 3 | Guidance Astrologique Conversationnelle Contextuelle | ✅ Oui | ✅ Conforme |
| Epic 4 | Monétisation B2C, Quotas, Privacy et Operations | ⚠️ Mixte | 🟠 Trop large |
| Epic 5 | Offre B2B API et Self-Service Entreprise | ✅ Oui (pour clients entreprise) | ✅ Conforme |

### B. Validation de l'Indépendance des Epics

| Relation | Dépendance | Verdict |
|----------|-----------|---------|
| Epic 1 → standalone | Aucune dépendance | ✅ Indépendant |
| Epic 2 → Epic 1 | Utilise le moteur astrologique | ✅ Forward-only |
| Epic 3 → Epic 1 + 2 | Utilise moteur + compte/profil | ✅ Forward-only |
| Epic 4 → Epic 2 + 3 | Quotas messages dépend du chat (E3) | ✅ Forward-only |
| Epic 5 → Epic 1 + 4 | API B2B post-MVP | ✅ Forward-only |

Pas de dépendances circulaires. Séquence respectée.

### C. Revue Story par Story

#### Epic 1 — Findings

| Story | Valeur utilisateur | Dépendances | AC BDD | Verdict |
|-------|-------------------|-------------|--------|---------|
| 1.1 Setup projet starter | Technique (ingénieur) | Aucune | Given/When/Then ✅ | ✅ Conforme (starter requis par archi) |
| 1.2 Données natales + conversions | Utilisateur (fiabilité calculs) | 1.1 | Given/When/Then ✅ | ✅ Conforme |
| 1.3 Référentiel astrologique versionné | Ops user (gestion référentiel) | 1.1 | Given/When/Then ✅ | ✅ Conforme |
| 1.4 Calcul natal de base | Utilisateur (résultat astro) | 1.2, 1.3 | Given/When/Then ✅ | ✅ Conforme |
| 1.5 Traçabilité règle/donnée → résultat | Support/Ops (audit) | 1.4 | Given/When/Then ✅ | ✅ Conforme |

**Dépendances intra-epic** : Forward-only ✅

#### Epic 2 — Findings

| Story | Valeur utilisateur | Dépendances | AC BDD | Verdict |
|-------|-------------------|-------------|--------|---------|
| 2.1 Inscription + auth JWT | Utilisateur (accès) | E1 complété | Given/When/Then ✅ | ✅ Conforme |
| 2.2 Saisie données natales | Utilisateur (personnalisation) | 2.1 | Given/When/Then ✅ | ✅ Conforme |
| 2.3 Génération thème natal | Utilisateur (première valeur) | 2.2 + E1 | Given/When/Then ✅ | ✅ Conforme |
| 2.4 Restitution lisible thème | Utilisateur (compréhension) | 2.3 | Given/When/Then ✅ | ✅ Conforme |
| 2.5 Cohérence inter-sessions | Support (confiance) | 2.3 + E1 | Given/When/Then ✅ | ✅ Conforme |

**Dépendances intra-epic** : Forward-only ✅

#### Epic 3 — Findings

| Story | Valeur utilisateur | Dépendances | AC BDD | Verdict |
|-------|-------------------|-------------|--------|---------|
| 3.1 Chat envoi/réception messages | Utilisateur (interaction) | E2 (auth) | Given/When/Then ✅ | ✅ Conforme |
| 3.2 Persistance contexte | Utilisateur (continuité) | 3.1 | Given/When/Then ✅ | ✅ Conforme |
| 3.3 Historique + reprise | Utilisateur (retrouver échanges) | 3.2 | Given/When/Then ✅ | ✅ Conforme |
| 3.4 Guidance quotidienne/hebdo | Utilisateur (accompagnement) | E1 + E2 | Given/When/Then ✅ | ✅ Conforme |
| 3.5 Détection hors-scope + recovery | Utilisateur (fiabilité) | 3.1 | Given/When/Then ✅ | ✅ Conforme |
| 3.6 Paramétrage persona | Ops (contrôle qualité) | 3.1 | Given/When/Then ✅ | ✅ Conforme |

**Dépendances intra-epic** : Forward-only ✅

#### Epic 4 — Findings

| Story | Valeur utilisateur | Dépendances | AC BDD | Verdict |
|-------|-------------------|-------------|--------|---------|
| 4.1 Souscription plan payant | Utilisateur (accès service) | E2 (auth) | Given/When/Then ✅ | ✅ Conforme |
| 4.2 Quotas journaliers | Utilisateur (transparence usage) | 4.1 + E3 (chat) | Given/When/Then ✅ | ✅ Conforme |
| 4.3 Upgrade plan | Utilisateur (flexibilité) | 4.1 | Given/When/Then ✅ | ✅ Conforme |
| 4.4 Export/suppression données | Utilisateur (contrôle données) | E2 (auth) | Given/When/Then ✅ | ✅ Conforme |
| 4.5 Anonymisation LLM + audit | Ops (conformité) | E3 (LLM) | Given/When/Then ✅ | ✅ Conforme |
| 4.6 Outillage support | Support (résolution incidents) | E2 (comptes) | Given/When/Then ✅ | ✅ Conforme |
| 4.7 Monitoring qualité + ops | Ops (pilotage) | E3 (chat qualité) | Given/When/Then ✅ | ✅ Conforme |

**Dépendances intra-epic** : Forward-only ✅

#### Epic 5 — Findings

| Story | Valeur utilisateur | Dépendances | AC BDD | Verdict |
|-------|-------------------|-------------|--------|---------|
| 5.1 Espace compte B2B + credentials | Client entreprise (accès) | E2 (auth) | Given/When/Then ✅ | ✅ Conforme |
| 5.2 Consommation API authentifiée | Client entreprise (intégration) | 5.1 + E1 | Given/When/Then ✅ | ✅ Conforme |
| 5.3 Gestion limites/consommation | Client entreprise (pilotage) | 5.1 | Given/When/Then ✅ | ✅ Conforme |
| 5.4 Personnalisation éditoriale | Client entreprise (identité marque) | 5.2 | Given/When/Then ✅ | ✅ Conforme |
| 5.5 Facturation hybride | Business (monétisation B2B) | 5.1 | Given/When/Then ✅ | ✅ Conforme |

**Dépendances intra-epic** : Forward-only ✅

### D. Création Tables DB — Vérification

- Story 1.1 : setup projet (pas de tables) ✅
- Story 1.3 : crée les tables référentiel astro (quand nécessaire) ✅
- Story 2.1 : crée la table users (quand nécessaire) ✅
- Story 4.1 : crée les tables abonnement (quand nécessaire) ✅
- Pas de "create all tables upfront" détecté ✅

### E. Starter Template — Vérification

- Architecture spécifie : Split Starter (FastAPI backend + Vite React frontend) ✅
- Epic 1 Story 1.1 : "Set up initial project from starter template" ✅
- Inclut clonage, dépendances, structure cible ✅

### F. Checklist Bonnes Pratiques par Epic

| Critère | E1 | E2 | E3 | E4 | E5 |
|---------|----|----|----|----|-----|
| Valeur utilisateur | 🟠 | ✅ | ✅ | 🟠 | ✅ |
| Indépendance | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dimensionnement stories | ✅ | ✅ | ✅ | 🟠 | ✅ |
| Pas de dépendances en avant | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tables créées au besoin | ✅ | ✅ | ✅ | ✅ | ✅ |
| AC clairs (Given/When/Then) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Traçabilité FR maintenue | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### Violations et Recommandations

#### 🟠 Issue Majeure 1 : Epic 1 est un jalon technique fondation

**Constat :** L'Epic 1 "Moteur Astrologique Fiable et Versionné" est essentiellement un composant backend technique sans interface utilisateur directe. Les personas des stories sont "product engineer", "operations user" et "support user" — pas l'utilisateur final.

**Atténuation :** Le PRD classifie explicitement le moteur astrologique comme "Foundation Prerequisite (Phase 0)" avant le MVP. L'architecture le confirme. C'est un choix produit délibéré.

**Recommandation :** Acceptable dans ce contexte car le PRD l'impose comme prérequis. Reformuler le titre pour inclure l'objectif utilisateur final : ex. "Fondation pour des calculs astrologiques fiables et traçables".

#### 🟠 Issue Majeure 2 : Epic 4 est trop large et mélange des préoccupations

**Constat :** L'Epic 4 couvre 7 stories avec 4 préoccupations distinctes :
1. Monétisation (4.1, 4.2, 4.3) — valeur utilisateur
2. Privacy/RGPD (4.4) — valeur utilisateur
3. Sécurité LLM + audit (4.5) — préoccupation ops/technique
4. Support + monitoring (4.6, 4.7) — préoccupation ops

Cela représente 15 FRs dans un seul epic, le plus large du projet.

**Recommandation :** Envisager de scinder en 2-3 epics :
- Epic 4a : Abonnement et quotas (FR24-FR28)
- Epic 4b : Privacy et droits données (FR29-FR33)
- Epic 4c : Outillage support et monitoring ops (FR34-FR37)

#### 🟡 Concern Mineur 1 : AC pourraient inclure plus de cas d'erreur

**Constat :** La plupart des AC couvrent le happy path et un cas d'erreur générique ("erreurs explicites", "feedback clair"). Certaines stories bénéficieraient de cas d'erreur plus spécifiques.

**Exemples :**
- Story 2.3 (génération thème) : Quel comportement si le moteur est temporairement indisponible ?
- Story 3.1 (chat) : Quel comportement si le LLM ne répond pas dans les délais NFR ?
- Story 4.1 (souscription) : Quel comportement si le paiement échoue ?

**Recommandation :** Enrichir les AC des stories critiques avec les scénarios d'erreur spécifiques liés aux NFR (timeout, indisponibilité, échec paiement).

#### 🟡 Concern Mineur 2 : Story 3.4 couvre deux FR distinctes (FR16 + FR17)

**Constat :** La Story 3.4 "Guidance quotidienne/hebdomadaire et contextualisée" combine guidance périodique (FR16) et guidance contextuelle (FR17) dans une seule story.

**Recommandation :** Acceptable si le scope reste maîtrisable. Sinon, scinder en 2 stories distinctes.

## 6. Résumé et Recommandations

### Statut Global de Readiness

## READY — Prêt pour l'implémentation avec recommandations

Les artefacts de planification sont complets, cohérents et alignés. Aucune lacune critique bloquante n'a été identifiée. Le projet peut démarrer l'implémentation en tenant compte des recommandations ci-dessous.

### Tableau de Synthèse

| Dimension | Résultat | Détail |
|-----------|----------|--------|
| Documents complets | ✅ | 5/5 documents trouvés, aucun doublon |
| Couverture FR | ✅ | 42/42 FRs couvertes (100%) |
| Couverture NFR | ✅ | 22/22 NFRs documentées |
| Alignement UX ↔ PRD | ✅ avec 2 écarts moyens | Export/suppression données non détaillé visuellement ; scope UX > scope MVP |
| Alignement UX ↔ Architecture | ✅ avec 3 écarts mineurs | Mode offline, composants spécialisés, design system non nommé |
| Qualité des Epics | ✅ avec 2 issues majeures | Epic 1 technique (justifié), Epic 4 trop large |
| Qualité des Stories | ✅ avec 2 concerns mineurs | AC manquent certains cas d'erreur, Story 3.4 couvre 2 FRs |
| Indépendance / Dépendances | ✅ | Pas de dépendances circulaires, toutes forward-only |
| Traçabilité | ✅ | FR Coverage Map complète et cohérente |

### Issues Requérant une Action

#### Priorité Haute (à traiter avant ou pendant l'implémentation)

1. **Scinder l'Epic 4** en 2-3 epics distincts pour améliorer la lisibilité et l'indépendance des préoccupations (monétisation / privacy / ops). Cela facilitera le travail d'implémentation et la priorisation.

2. **Compléter les spécifications UX pour les flux RGPD** (export et suppression de données). Ces parcours utilisateur sont exigés par le PRD (FR29, FR30) mais n'ont pas de maquettes/flux visuels dans le document UX.

#### Priorité Moyenne (recommandé mais non bloquant)

3. **Clarifier le phasage MVP vs post-MVP dans le document UX**. Les consultations spécialisées (cartes, runes, compatibilité) et le multi-profils astrologues sont documentés dans l'UX mais pas dans le scope MVP du PRD.

4. **Enrichir les critères d'acceptation** des stories critiques (2.3, 3.1, 4.1) avec les scénarios d'erreur spécifiques (timeout moteur, indisponibilité LLM, échec paiement).

5. **Documenter la stratégie offline** dans l'architecture si le mode lecture seule des derniers échanges (mentionné dans l'UX) est attendu en MVP.

#### Priorité Basse (amélioration continue)

6. **Reformuler le titre de l'Epic 1** pour inclure l'objectif utilisateur final plutôt qu'une description technique.

7. **Aligner la terminologie design system** entre architecture ("UI kit custom léger") et UX (Tailwind CSS + shadcn/ui + Radix).

8. **Considérer scinder la Story 3.4** si le scope guidance périodique + contextuelle s'avère trop large.

### Prochaines Étapes Recommandées

1. Appliquer les recommandations priorité haute (scission Epic 4, flux UX RGPD)
2. Démarrer l'implémentation par Epic 1 Story 1.1 (setup starter template)
3. Mettre en place les conventions de patterns d'architecture dès le premier commit
4. Traiter les recommandations priorité moyenne au fil de l'implémentation

### Note Finale

Cette évaluation a identifié **7 points d'amélioration** répartis sur 3 niveaux de priorité, dont **aucun n'est bloquant**. La couverture fonctionnelle est exhaustive (100%), les documents sont bien structurés et alignés entre eux. Le projet horoscope_front est **prêt pour l'implémentation**.

---

**Évaluation réalisée le :** 2026-02-18
**Évaluateur :** Expert Product Manager & Scrum Master (workflow BMAD)
**Documents analysés :** prd.md, architecture.md, epics.md, ux-design-specification.md, prd-validation-report.md

---

## Addendum - Actions de remédiation appliquées

**Date:** 2026-02-18  
**Statut global:** Toutes les corrections prévues sont traitées.

### Suivi des recommandations

| # | Recommandation | Priorité | Statut | Implémentation |
|---|----------------|----------|--------|----------------|
| 1 | Scinder l'Epic 4 | Haute | ✅ Traité | `epics.md` restructuré en Epic 4 (B2C quotas), Epic 5 (Privacy/RGPD), Epic 6 (Support/Ops), B2B renuméroté Epic 7 |
| 2 | Compléter les flux UX RGPD | Haute | ✅ Traité | `ux-design-specification.md` enrichi avec `Journey 4 - Droits donnees (RGPD)` + composant `DataRightsCenter` |
| 3 | Clarifier phasage MVP vs Post-MVP | Moyenne | ✅ Traité | `ux-design-specification.md` enrichi avec section `MVP vs Post-MVP Scope Clarification` |
| 4 | Enrichir AC stories critiques avec cas d'erreur | Moyenne | ✅ Traité | `epics.md`: AC renforcés sur stories `2.3`, `3.1`, `4.1` (timeout moteur, timeout LLM/fallback, échec paiement) |
| 5 | Documenter stratégie offline en architecture | Moyenne | ✅ Traité | `architecture.md` enrichi avec section `Offline Strategy` (MVP read-only + trajectoire post-MVP outbox) |
| 6 | Reformuler le titre de l'Epic 1 | Basse | ✅ Traité | `epics.md`: titre ajusté en "Fondation pour des calculs astrologiques fiables et tracables" |
| 7 | Aligner terminologie design system | Basse | ✅ Traité | `architecture.md` aligné explicitement sur Tailwind CSS + shadcn/ui + primitives Radix |
| 8 | Scinder la Story 3.4 (guidance) | Basse | ✅ Traité | `epics.md` mis à jour: 3.4 (guidance périodique) + 3.5 (guidance contextuelle), avec renumérotation 3.6/3.7 |

### Impact sur la readiness

- Couverture FR: inchangée à **100%**.
- Cohérence PRD/UX/Architecture/Epics: améliorée.
- Risques résiduels: aucun point de correction planifié restant ouvert.
