---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
status: 'ready-for-development'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
workflowType: 'epic'
epicNumber: 65
createdAt: '2026-04-04'
owner: Cyril
lastEdited: '2026-04-04'
editHistory:
  - date: '2026-04-04'
    changes: 'Ajout FR65-13 à FR65-18 + clarifications FR65-3/4/5/7 suite retour Cyril — v2'
  - date: '2026-04-04'
    changes: 'Clarifications finales FR65-6/9/10 + NFR3 suite validation Cyril — v3, prêt step-02'
  - date: '2026-04-04'
    changes: 'Stories 65-1 à 65-21 générées (6 groupes, 21 stories) — step-03 complété'
  - date: '2026-04-04'
    changes: 'Corrections finales v4 : status dédupliqué, story 65-18b ajoutée (FR65-6d), frontière 65-4/65-21 clarifiée — gel définitif'
---

# Epic 65 — Espace Admin : Pilotage Produit, Observabilité et Gouvernance

**Status:** draft  
**Créé le:** 2026-04-04  
**Owner:** Cyril  

---

## Requirements Inventory

### Exigences Fonctionnelles issues du PRD (FR existants liés à l'admin)

FR13: Les agents support peuvent accéder au contexte du compte utilisateur nécessaire pour résoudre les demandes.  
FR23: Les équipes produit/opérations peuvent configurer les limites de comportement des personas d'astrologues virtuels.  
FR28: L'entreprise peut définir et gérer les plans tarifaires et les politiques d'usage associées.  
FR33: Le système fournit une visibilité d'audit sur les actions sensibles liées aux comptes et aux droits des données.  
FR34: Les utilisateurs support peuvent gérer les incidents liés au compte, à l'abonnement et aux contenus.  
FR35: Les utilisateurs opérations peuvent surveiller les indicateurs de qualité produit liés à la pertinence conversationnelle.  
FR36: Les utilisateurs opérations peuvent appliquer et annuler des changements de configuration affectant le comportement de qualité des réponses.  
FR37: Les utilisateurs opérations peuvent surveiller les indicateurs d'usage nécessaires aux décisions produit et business.  

### Nouvelles Exigences Fonctionnelles (FR65)

**FR65-1** *(Dashboard business — KPIs filtrés par période et par plan)* :  
L'admin peut accéder à un tableau de bord affichant les KPIs clés avec filtres temporels (7j / 30j / 12 mois), granularité journalière pour les tendances, et segmentation par plan (free / basic / premium) : inscrits totaux, utilisateurs actifs, taux de conversion free→basic→premium, churn estimé, MRR/ARR, essais en cours, upgrades/downgrades, échecs de paiement, revenu par plan, usage moyen par fonctionnalité. Les données sont quasi temps réel (rafraîchissement ≤ 5 min) ou agrégées quotidiennement selon la nature du KPI. *(Clarifié point 5 — source et temporalité des KPI.)*

**FR65-2** *(Fiche utilisateur — consultation)* :  
L'admin peut rechercher un utilisateur (email, id) et consulter sa fiche complète : profil (nom, email, date de création), plan actif, statut Stripe (abonnement, méthode de paiement, dernière facture), quotas consommés vs autorisés, historique des 20 dernières générations (use case, date, statut, coût token), derniers tickets support ouverts, 10 derniers événements d'audit le concernant.

**FR65-3** *(Actions sur compte utilisateur — périmètre applicatif + effets externes explicites)* :  
L'admin peut déclencher des actions manuelles sur un compte utilisateur. Chaque action a un périmètre précis et documenté :
- **Suspendre / réactiver** : flag applicatif uniquement (bloque l'accès JWT) — aucun effet Stripe.
- **Réinitialiser un quota** : remise à zéro du compteur applicatif pour la période courante — aucune création de crédit Stripe.
- **Forcer un refresh d'abonnement** : resynchronisation depuis Stripe en lecture+écriture (le statut et le plan en DB sont mis à jour depuis Stripe) — aucun changement de facturation côté Stripe.
- **Débloquer un compte verrouillé** : levée du verrou applicatif (trop de tentatives, flag de suspension).
- **Attribuer un plan manuellement** : mise à jour directe du plan en DB sans passer par Stripe, uniquement pour des plans internes ou des périodes d'essai prolongées — génère un audit log avec motif obligatoire.
- **Enregistrer un geste commercial** : flag interne `commercial_gesture` sur l'abonnement (ex : +N jours, +N messages) sans création d'avoir ni remboursement Stripe. *(Clarifié point 1 — périmètre des actions et effets externes.)*

**FR65-4a** *(Matrice entitlements — consultation)* :  
L'admin peut consulter une matrice de lecture des droits d'accès par plan (free / basic / premium) : types de contenus visibles, contenus générables, profondeur de génération LLM, quotas (valeur actuelle en DB), contenus teaser verrouillés, CTA d'upgrade attendus, priorités de rendu, règles trial et lifetime. La matrice est une vue canonique cross-couches : elle aligne en un seul écran la DB (`plan_catalog`, `product_entitlements`), les règles backend et le comportement attendu frontend.

**FR65-4b** *(Matrice entitlements — édition)* :  
L'admin peut modifier les valeurs de quotas et les flags de features par plan directement depuis la matrice : modification d'une cellule, confirmation double, audit log automatique avec valeur avant/après. **Les règles de génération LLM (variants de prompt) ne sont pas éditables depuis l'admin dans cet epic** — elles restent dans la config éditorial (FR65-6). *(Clarifié point 2 — consultation vs édition séparées.)*

**FR65-5** *(Supervision IA — performance et pilotage métier)* :  
L'admin peut superviser les performances des use cases LLM dans une perspective **métier** : volume par use case (natal_interpretation_short, horoscope_daily_variant_narration, chat, etc.), coût tokens estimé, temps de réponse moyen (p50/p95), taux d'échec par use case, taux de retry, persona et prompt version utilisés par période. Visualisation sous forme de graphes et tableaux. **Ce panneau ne couvre pas les incidents techniques** (→ FR65-7). *(Clarifié point 3 — distinction métier vs technique.)*

**FR65-6** *(Configuration éditoriale et métier — à découper en sous-domaines au story mapping)* :  
L'admin peut consulter et modifier la configuration éditoriale et métier du produit. Ce FR regroupe intentionnellement plusieurs sous-domaines qui seront découpés en stories distinctes lors du step 3 : **(a) Prompts LLM** (version active, historique, diff, rollback) ; **(b) Personas d'astrologues** (paramètres actifs, activation/désactivation) ; **(c) Contenus et paywalls** (textes des paywalls, wording marketing in-app, messages transactionnels) ; **(d) Règles métier** (templates éditoriaux, scoring/calibration) ; **(e) Feature flags** (activation/désactivation par feature). Toute modification est versionnée et génère un audit log via FR65-14. Le rollback vers une version précédente est disponible en ≤ 15 min (NFR21).

**FR65-7** *(Observabilité technique — incidents, erreurs, anomalies)* :  
L'admin dispose d'un cockpit **technique** distinct de FR65-5 : erreurs applicatives (HTTP 5xx, tracebacks), jobs en échec, événements Stripe incohérents (webhook non traité, statut inconnu), logs de génération LLM filtrables (par use case, statut, période), alertes sur quotas proches du seuil, réponses LLM invalides (hors-scope, format incorrect, score bas), replay des cas problématiques (re-exécution d'un appel LLM depuis un log). **Ce panneau est technique** — distinct du pilotage métier de FR65-5. *(Clarifié point 3.)*

**FR65-8** *(Support et modération)* :  
L'admin peut consulter les tickets support ouverts, les historiques de messages utilisateurs liés à un ticket, les demandes de remboursement, les contenus générés signalés comme problématiques. L'historique des actions admin sur chaque dossier est visible (qui a fait quoi, quand, avec quel motif).

**FR65-9** *(Sécurité et gouvernance — audit, exports, préparation RBAC)* :  
L'admin peut consulter les journaux d'audit globaux (filtrables par acteur, cible, type d'action, période) et exporter des données sensibles (utilisateurs, générations, billing) en format CSV/JSON avec double confirmation. Les clés/configs sensibles sont masquées par défaut (révélation explicite loguée). Les actions irréversibles requièrent une double confirmation modale. **Périmètre "gestion des accès" dans cet epic :** lecture seule de la configuration d'accès courante (qui a le rôle admin, historique des connexions admin) et mise en place de l'infrastructure de permissions (contexte auth front, dépendance backend) conformément à FR65-13. **Une UI complète d'administration RBAC (création/modification de rôles, attribution de profils fins) n'est pas dans le scope de cet epic** — c'est la direction d'architecture posée par FR65-13 pour un epic futur.

**FR65-10** *(Seed dev — utilisateur admin par défaut)* :  
En mode dev (`APP_ENV=dev` ou `SEED_ADMIN=true`), un utilisateur admin est semé automatiquement au démarrage de l'application si aucun utilisateur avec le rôle `admin` n'existe déjà : email `admin@test.com`, mot de passe `admin123`, rôle `admin`. Le seed est idempotent. **Ce seed ne doit jamais s'exécuter hors environnement de développement ou de test local** : le code de seed doit impérativement vérifier `APP_ENV in {"dev", "test"}` (ou la variable `SEED_ADMIN=true` explicitement positionnée) et refuser son exécution silencieusement en production ou staging. Cette vérification est une condition bloquante de la story, pas optionnelle.

**FR65-11** *(Guard admin — frontend et backend)* :  
Les routes `/admin/*` sont protégées côté frontend (redirection `/login` si non authentifié, `/` si rôle insuffisant) et côté backend via une dépendance FastAPI centralisée `require_admin_user` dans `auth.py`. Cette dépendance remplace les checks inline `if user.role not in {...}` dispersés dans les routers admin existants. Les endpoints non-admin qui acceptent aussi le rôle `admin` conservent leur comportement actuel.

**FR65-12** *(Navigation admin — 10 sections)* :  
Le menu admin expose 10 sections ordonnées : Tableau de bord, Utilisateurs, Abonnements & Droits, Générations IA, Prompts & Personas, Contenus & Paywalls, Billing, Logs & Incidents, Support, Paramètres. Les 4 sections existantes (Pricing, Monitoring, Personas, Reconciliation) sont intégrées dans cette nouvelle structure sans casser les URLs actuelles.

**FR65-13** *(Permissions fines par domaine admin — direction d'architecture)* :  
L'espace admin doit être conçu pour supporter des permissions granulaires par domaine fonctionnel, même si l'implémentation initiale utilise le rôle unique `admin`. L'architecture doit distinguer 4 profils cibles (à implémenter progressivement) : `admin_business` (dashboard, billing, users lecture), `admin_support` (fiche user, tickets, actions limitées), `admin_ops` (config éditoriale, prompts, feature flags, monitoring IA), `super_admin` (tout + gouvernance + exports). Dans cet epic, tous les accès sont accordés au rôle `admin`, mais les écrans et composants doivent accepter un système de permissions injecté (prop ou contexte) pour permettre la restriction future sans refonte.

**FR65-14** *(Audit trail détaillé des mutations manuelles)* :  
Toute action manuelle admin sur une entité métier (utilisateur, quota, plan, config, remboursement, feature flag, contenu) génère un événement d'audit dans `audit_events` avec les champs : `actor_user_id`, `actor_role`, `action` (code normalisé), `target_type`, `target_id`, `status`, et dans `details` (JSON) : `before` (état avant), `after` (état après), `reason` (motif saisi par l'admin si applicable). Les événements sont requêtables depuis l'espace admin via FR65-9 et affichés sur la fiche utilisateur via FR65-2. *(Mécanisme `AuditEventModel` existant et réutilisable — les champs `before`/`after`/`reason` passent dans `details` JSON.)*

**FR65-15** *(Consultation vs édition — distinction explicite pour plans/quotas/entitlements)* :  
La consultation de la matrice des droits (FR65-4a) et l'édition des valeurs (FR65-4b) sont deux modes distincts de l'écran "Abonnements & Droits". Le mode consultation est accessible à tous les profils admin. Le mode édition est restreint (`admin_ops` ou `super_admin` dans la direction d'architecture, `admin` dans l'implémentation initiale) et requiert une confirmation explicite. Toute modification de quota ou de feature flag génère un audit log via FR65-14.

**FR65-16** *(Comportement des actions admin à effets externes — contrat explicite)* :  
Chaque action admin susceptible de déclencher un effet hors du périmètre applicatif doit afficher dans l'UI une indication explicite de son périmètre (applicatif seulement / synchronisation Stripe en lecture / synchronisation Stripe en écriture). Les actions sans effet externe sont marquées "applicatif uniquement". Les actions avec resynchronisation Stripe (ex : forcer un refresh d'abonnement) affichent un avertissement et requièrent une confirmation. Aucune action admin ne crée de charge ou avoir dans Stripe directement dans cet epic.

**FR65-17** *(Filtres et granularité des KPI dashboard)* :  
Le tableau de bord business (FR65-1) expose obligatoirement les filtres suivants : période (7 derniers jours / 30 derniers jours / 12 derniers mois / personnalisé), segmentation par plan (tous / free / basic / premium), et pour les tendances, granularité journalière. Les KPIs instantanés (ex : inscrits totaux, MRR actuel) s'affichent sans filtre de période. Les KPIs de flux (ex : upgrades, churn) s'affichent avec filtre de période. La source de données est la DB applicative (pas Stripe directement) pour éviter les dépendances temps réel.

**FR65-18** *(Visibilité conditionnelle des sections du menu selon permissions)* :  
Les sections du menu admin sont conditionnellement visibles selon les permissions du profil connecté. Dans l'implémentation initiale (rôle unique `admin`), toutes les sections sont visibles. L'architecture du composant menu accepte une configuration de sections filtrée côté frontend (liste de sections autorisées injectée depuis le contexte auth) pour permettre la restriction future sans refonte de la navigation.

---

### Exigences Non-Fonctionnelles applicables

NFR3: Le **feedback d'initiation d'action** (déclenchement de l'état de chargement, spinner, désactivation du bouton) doit être visible en ≤ 200ms après l'interaction utilisateur — il ne s'agit pas de la complétion de l'action backend, mais de la réponse UI locale signalant que l'action a été prise en compte.  
NFR5: Chiffrement en transit et au repos pour toutes les données sensibles exposées dans l'admin.  
NFR8: Toutes les actions sensibles admin (suspension, mutation plan, suppression, reset quota, geste commercial, export) doivent être journalisées avec horodatage, acteur, type d'action, identifiant de ressource, et valeurs avant/après dans `details`.  
NFR20: Le système détecte et trace les réponses hors-scope ; un rapport de suivi est accessible dans l'espace admin (Logs & Incidents).  
NFR21: Le mécanisme de rollback de configuration doit être exécutable depuis l'admin en ≤ 15 minutes.  

---

### Exigences Techniques (Architecture) — État au 2026-04-04

**Mécanismes existants réutilisables :**  
- `AuditEventModel` (`audit_events`) : opérationnel, champs `actor_user_id`, `actor_role`, `action`, `target_type`, `target_id`, `status`, `details` (JSON). Les champs `before`/`after`/`reason` seront stockés dans `details`. ✅ Réutilisable sans migration pour FR65-14.  
- `AuditService` : service fonctionnel, appelable depuis tous les routers admin. ✅  
- Rôle `admin` dans `rbac.py` : déjà défini et valide. ✅  
- Seeds LLM (`llm_orchestration/seeds/`) : pattern réutilisable pour FR65-10. ✅  

**Angle mort 1 — Guards admin dispersés :**  
Les routers admin existants implémentent des checks inline `if user.role not in {...}` — pattern incohérent et non centralisé. `admin_llm.py` possède un helper local `_ensure_admin_role()` non réutilisé. → Story FR65-11 crée `require_admin_user` comme dépendance FastAPI centralisée dans `auth.py`, puis migre les routers admin existants vers ce guard.

**Angle mort 2 — Navigation admin non structurée pour la granularité future :**  
Le menu actuel (`AdminPage.tsx`) est une liste statique de 4 sections sans système de permissions. → FR65-13 et FR65-18 imposent dès maintenant une architecture de menu paramétrable (sections filtrables via contexte auth).

**Contraintes frontend :**  
- React 19 + TypeScript, CSS variables uniquement (pas de Tailwind, pas de lib de composants).  
- i18n via `frontend/src/i18n/`, clé de namespace `admin` déjà présente.  
- Aucun style inline : tout le CSS dans les fichiers `.css`/`.scss` appropriés.  
- Routes existantes `/admin/pricing`, `/admin/monitoring`, `/admin/personas`, `/admin/reconciliation` à intégrer sans casser les URLs.  

**Contraintes backend :**  
- Nouvelles routes admin sous `/api/v1/admin/` avec guard centralisé `require_admin_user`.  
- Backend port 8001, `pyproject.toml` comme source unique des dépendances.  

---

### Exigences UX applicables

- Philosophie structurante : **voir → comprendre → corriger → tracer** (4 verbes, ordre intentionnel).  
- Affichage matriciel pour les entitlements (tableau plans × features avec indicateurs visuels).  
- Feedback immédiat sur toutes les actions admin (toast de confirmation, spinner, état d'erreur).  
- Actions irréversibles avec double confirmation modale (message d'avertissement + saisie de confirmation ou bouton explicite).  
- Indicateur visible du périmètre de chaque action (applicatif / Stripe lecture / Stripe écriture) — FR65-16.  
- Menu conditionnel dès l'implémentation initiale — FR65-18.  
- Accessibilité WCAG 2.1 AA sur les écrans MVP admin.  

---

## Epic List

L'Epic 65 est organisé en **6 groupes de stories** (sous-epics), structurés par valeur fonctionnelle et non par couche technique. Chaque groupe est livrable de façon autonome une fois le groupe A posé.

### Groupe 65.A — Fondation Admin *(prerequisite)*
Valeur : accès sécurisé à l'espace admin, navigation structurée prête pour les permissions futures.  
**FRs couverts :** FR65-10, FR65-11, FR65-12, FR65-13, FR65-18

### Groupe 65.B — Dashboard & Analytics *(priorité stratégique #3a)*
Valeur : l'admin comprend en 30 secondes la santé du produit — croissance, conversion, billing.  
**FRs couverts :** FR65-1, FR65-17, FR37  
⚠️ *KPIs distingués au story mapping : calculables immédiatement depuis DB vs nécessitant agrégation dédiée.*

### Groupe 65.C — Utilisateurs & Actions Support *(priorité stratégique #2)*
Valeur : l'admin retrouve un utilisateur, comprend son état complet et peut agir — suspension, quota, plan, geste commercial.  
**FRs couverts :** FR65-2, FR65-3, FR65-8, FR65-14 *(usage transverse)*, FR65-16, FR13, FR34

### Groupe 65.D — Abonnements & Entitlements *(priorité stratégique #1)*
Valeur : source de vérité visuelle des droits par plan — l'admin voit, comprend et peut ajuster les règles sans ambiguïté DB/backend/frontend.  
**FRs couverts :** FR65-4a, FR65-4b, FR65-15, FR28

### Groupe 65.E — LLM Ops & Configuration *(dual : métier + technique)*
Valeur : l'admin détecte les dérives LLM (métier) et diagnostique les incidents techniques (ops), et peut ajuster la configuration éditoriale sans déploiement.  
**FRs couverts :** FR65-5, FR65-6 *(5 sous-stories)*, FR65-7, FR23, FR35, FR36

### Groupe 65.F — Gouvernance & Audit
Valeur : toute action admin est traçable, les exports sensibles sont sécurisés, et l'infrastructure de permissions est prête pour les profils fins futurs.  
**FRs couverts :** FR65-9, FR65-13 *(direction d'archi)*, FR65-14 *(usage transverse)*, FR33

---

### FR Coverage Map

FR13: Groupe 65.C — fiche utilisateur, contexte support  
FR23: Groupe 65.E — configuration personas d'astrologues  
FR28: Groupe 65.D — plans tarifaires et politiques d'usage  
FR33: Groupe 65.F — visibilité audit actions sensibles  
FR34: Groupe 65.C — gestion incidents support  
FR35: Groupe 65.E — monitoring qualité conversationnelle  
FR36: Groupe 65.E — rollback configuration  
FR37: Groupe 65.B — indicateurs d'usage business  
FR65-1: Groupe 65.B — dashboard KPIs  
FR65-2: Groupe 65.C — fiche utilisateur consultation  
FR65-3: Groupe 65.C — actions sur compte utilisateur  
FR65-4a: Groupe 65.D — matrice entitlements consultation  
FR65-4b: Groupe 65.D — matrice entitlements édition  
FR65-5: Groupe 65.E — supervision IA métier  
FR65-6 (a-e): Groupe 65.E — config éditoriale 5 sous-domaines  
FR65-7: Groupe 65.E — observabilité technique  
FR65-8: Groupe 65.C — support et modération  
FR65-9: Groupe 65.F — gouvernance et exports  
FR65-10: Groupe 65.A — seed dev admin  
FR65-11: Groupe 65.A — guard admin frontend + backend  
FR65-12: Groupe 65.A — navigation 10 sections  
FR65-13: Groupe 65.A + 65.F — direction architecture permissions  
FR65-14: Transverse 65.C, 65.D, 65.E, 65.F — audit trail mutations  
FR65-15: Groupe 65.D — consultation vs édition entitlements  
FR65-16: Groupe 65.C — périmètre des actions à effets externes  
FR65-17: Groupe 65.B — filtres et granularité dashboard  
FR65-18: Groupe 65.A — menu conditionnel selon permissions  

**Couverture totale : 26/26 FRs mappés. ✅**

---

## Stories

---

## Groupe 65.A — Fondation Admin

*Prerequisite de tous les autres groupes. Livrable en 1 sprint avant d'ouvrir le reste.*

---

### Story 65-1 : Seed dev — utilisateur admin par défaut

En tant qu'**équipe de développement**,  
je veux qu'un utilisateur admin soit créé automatiquement au démarrage en mode dev,  
afin de pouvoir tester l'espace admin immédiatement sans manipulation manuelle de base de données.

**Acceptance Criteria :**

**Given** l'application démarre avec `APP_ENV=dev` ou `SEED_ADMIN=true`  
**When** aucun utilisateur avec le rôle `admin` n'existe en base  
**Then** un utilisateur est créé avec email `admin@test.com`, password hashé correspondant à `admin123`, rôle `admin`  
**And** le seed est idempotent : si l'utilisateur existe déjà, aucune action n'est effectuée, aucune erreur levée

**Given** l'application démarre avec `APP_ENV=production` ou `APP_ENV=staging`  
**When** le seed est évalué  
**Then** il ne s'exécute pas — la vérification `APP_ENV in {"dev", "test"}` est bloquante  
**And** aucun log d'erreur n'est émis (refus silencieux)

**Given** le seed s'exécute en dev  
**When** l'admin créé tente de se connecter via `POST /api/v1/auth/login`  
**Then** la connexion réussit et retourne un token JWT avec `role: "admin"`

*Notes techniques :* Suivre le pattern `llm_orchestration/seeds/`. Créer `backend/app/startup/dev_seed.py`. Appeler depuis `main.py` dans le lifespan uniquement si `settings.app_env in {"dev", "test"} or settings.seed_admin`. Ajouter `SEED_ADMIN=false` dans `.env.example`.

---

### Story 65-2 : Guard admin backend — dépendance FastAPI centralisée

En tant que **développeur backend**,  
je veux une dépendance FastAPI `require_admin_user` centralisée,  
afin que tous les endpoints admin partagent une logique de contrôle d'accès cohérente et maintenable.

**Acceptance Criteria :**

**Given** un endpoint admin utilise `Depends(require_admin_user)`  
**When** la requête arrive avec un token JWT valide et `role: "admin"`  
**Then** l'endpoint s'exécute normalement et retourne `AuthenticatedUser` avec le rôle admin

**Given** un endpoint admin utilise `Depends(require_admin_user)`  
**When** la requête arrive sans token ou avec un token invalide  
**Then** l'endpoint retourne HTTP 401 avec le code `missing_access_token` ou `invalid_token`

**Given** un endpoint admin utilise `Depends(require_admin_user)`  
**When** la requête arrive avec un token valide mais un rôle autre que `admin` (ex : `ops`, `user`, `support`)  
**Then** l'endpoint retourne HTTP 403 avec le code `insufficient_role` et `details: {"required_role": "admin", "actual_role": "..."}`

**Given** les routers admin existants (`admin_llm.py`, `admin_pdf_templates.py`, `ops_monitoring.py`, `ops_persona.py`)  
**When** la migration vers `require_admin_user` est effectuée  
**Then** les checks inline `if user.role not in {...}` et le helper local `_ensure_admin_role()` sont supprimés  
**And** le comportement fonctionnel des endpoints existants est inchangé (tests de non-régression passent)

*Notes techniques :* Ajouter `require_admin_user` dans `backend/app/api/dependencies/auth.py`. Cette fonction utilise `require_authenticated_user` en dépendance puis vérifie `user.role == "admin"`. Les endpoints non-admin qui acceptent aussi le rôle `admin` (ex : `chat.py`) conservent leurs propres guards existants.

---

### Story 65-3 : Guard admin frontend — protection des routes /admin/*

En tant qu'**utilisateur non-admin**,  
je veux être redirigé hors de l'espace admin si je n'ai pas les permissions,  
afin que l'espace admin soit inaccessible à toute personne non autorisée.

**Acceptance Criteria :**

**Given** un utilisateur non authentifié tente d'accéder à `/admin` ou `/admin/*`  
**When** la route est évaluée  
**Then** il est redirigé vers `/login` avec le paramètre `redirect=/admin` (ou équivalent) pour revenir après connexion

**Given** un utilisateur authentifié avec rôle `user`, `support`, `ops` ou `enterprise_admin` tente d'accéder à `/admin/*`  
**When** la route est évaluée  
**Then** il est redirigé vers `/` (dashboard utilisateur) sans message d'erreur affiché

**Given** un utilisateur authentifié avec rôle `admin` accède à `/admin`  
**When** la route est évaluée  
**Then** la page admin se charge normalement

**Given** le composant de guard admin est rendu  
**When** le rôle de l'utilisateur est en cours de chargement (état async)  
**Then** un spinner de chargement est affiché — aucune redirection n'est déclenchée prématurément

*Notes techniques :* Créer un composant `AdminGuard` (ou `RequireAdmin`) dans `frontend/src/components/` ou `frontend/src/layouts/`. Utiliser le contexte d'authentification existant. Envelopper toutes les routes `/admin/*` dans le routeur React.

---

### Story 65-4 : Navigation admin — menu 10 sections avec architecture de permissions conditionnelle

En tant qu'**admin**,  
je veux un menu de navigation structuré en 10 sections avec l'infrastructure pour des permissions futures,  
afin de piloter tous les domaines du produit depuis une interface cohérente et évolutive.

**Acceptance Criteria :**

**Given** l'admin est connecté et accède à `/admin`  
**When** le layout admin est rendu  
**Then** le menu latéral affiche les 10 sections dans l'ordre : Tableau de bord (`/admin/dashboard`), Utilisateurs (`/admin/users`), Abonnements & Droits (`/admin/entitlements`), Générations IA (`/admin/ai-generations`), Prompts & Personas (`/admin/prompts`), Contenus & Paywalls (`/admin/content`), Billing (`/admin/billing`), Logs & Incidents (`/admin/logs`), Support (`/admin/support`), Paramètres (`/admin/settings`)

**Given** les 4 sections existantes (`/admin/pricing`, `/admin/monitoring`, `/admin/personas`, `/admin/reconciliation`)  
**When** l'admin y accède via leur ancienne URL  
**Then** elles continuent de fonctionner (pas de 404) — soit via redirect vers leur nouvelle URL dans la structure, soit en conservant l'URL  
**And** elles apparaissent dans le menu unifié de la nouvelle navigation

**Given** le composant menu admin  
**When** il est rendu  
**Then** il accepte une prop `allowedSections: string[]` ou un contexte de permissions injecté  
**And** dans l'implémentation initiale, `allowedSections` contient toutes les 10 sections pour le rôle `admin`  
**And** le composant filtre les sections affichées selon cette liste (prêt pour restriction future sans refonte)

**Given** l'admin navigue entre sections  
**When** une section est active  
**Then** l'entrée de menu correspondante a un style actif visible (`aria-current="page"`)

*Notes techniques :* Modifier `AdminPage.tsx` et `AdminLayout`. **Frontière avec Story 65-21 :** cette story crée le contexte `AdminPermissionsContext` avec sa structure (`allowedSections`, `canEdit`, `canExport`) et l'instancie pour le menu. La story 65-21 définit le contrat complet du contexte et vérifie que TOUS les composants admin l'utilisent correctement — la logique de filtrage des sections est ici, l'architecture réutilisable cross-composants est dans 65-21. Pas de duplication : 65-4 instancie, 65-21 contractualise. Toutes les sections ont leur route de fallback (`/admin/*` non reconnue → redirect vers `/admin/dashboard`). CSS dans `frontend/src/pages/AdminPage.css` ou `frontend/src/layouts/AdminLayout.css`. Clés i18n dans `frontend/src/i18n/` namespace `admin`.

---

## Groupe 65.B — Dashboard & Analytics

*Prerequisite : Groupe 65.A livré. Données depuis DB applicative uniquement.*

---

### Story 65-5 : Dashboard — KPIs instantanés (inscrits, actifs, MRR)

En tant qu'**admin business**,  
je veux voir les métriques de santé instantanées du produit sur le tableau de bord,  
afin de comprendre en quelques secondes la taille de la base, l'activité et le revenu courant.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/dashboard`  
**When** la page charge  
**Then** les KPIs instantanés suivants sont affichés sans filtre de période :
  - Inscrits totaux (count `users`)
  - Utilisateurs actifs 7j (users avec au moins 1 génération ou message dans les 7 derniers jours)
  - Utilisateurs actifs 30j
  - Abonnements actifs par plan (free / basic / premium) — count + %
  - MRR estimé (sum `monthly_price_cents` des abonnements `status = active`)
  - ARR estimé (MRR × 12)
  - Essais en cours (abonnements `status = trial`)

**Given** les KPIs sont calculés  
**When** la page est affichée  
**Then** chaque KPI affiche une valeur numérique avec son label et son unité  
**And** les données sont issues de la DB applicative (pas d'appel Stripe direct)  
**And** un indicateur de date/heure de dernière mise à jour est visible

**Given** les données sont en cours de chargement  
**When** la requête API est pendante  
**Then** chaque carte KPI affiche un état de chargement (skeleton ou spinner)

*Notes techniques :* Créer `GET /api/v1/admin/dashboard/kpis-snapshot` (guard `require_admin_user`). Requêtes SQL directes sur `users`, `user_subscriptions`, `billing_plans`. Composant `AdminDashboardPage.tsx`. CSS dans `AdminDashboardPage.css`.

---

### Story 65-6 : Dashboard — KPIs de flux avec filtres temporels (conversion, churn, upgrades)

En tant qu'**admin business**,  
je veux voir les métriques de flux filtrées par période sur le tableau de bord,  
afin de détecter si la croissance accélère, ralentit ou si une friction apparaît dans le funnel.

**Acceptance Criteria :**

**Given** l'admin est sur `/admin/dashboard`  
**When** il sélectionne une période (7j / 30j / 12 mois)  
**Then** les KPIs de flux suivants se recalculent pour la période choisie :
  - Nouveaux inscrits
  - Upgrades (free→basic, free→premium, basic→premium) — count par transition
  - Downgrades (premium→basic, etc.)
  - Churn estimé (abonnements passés de `active` à `cancelled` ou `expired`)
  - Échecs de paiement (abonnements avec `failure_reason` non null)
  - Revenu par plan sur la période

**Given** l'admin sélectionne "12 mois"  
**When** la visualisation de tendance est affichée  
**Then** un graphe en courbes montre l'évolution journalière ou hebdomadaire des inscrits et upgrades  
**And** la granularité est cohérente avec la période (7j → journalier, 30j → journalier, 12m → hebdomadaire)

**Given** l'admin applique un filtre de plan (tous / free / basic / premium)  
**When** le filtre est actif  
**Then** tous les KPIs de flux se recalculent pour le segment de plan sélectionné

*Notes techniques :* Endpoint `GET /api/v1/admin/dashboard/kpis-flux?period=7d&plan=all`. Les transitions de plan sont dérivées des `audit_events` (`action: "plan_changed"`) ou de la table `user_subscriptions` avec horodatage. Distinguer clairement ce qui est calculable directement vs ce qui nécessite une agrégation plus complexe (churn notamment — MVP = count `status = cancelled/expired`, not cohort-based).

---

### Story 65-7 : Dashboard — KPIs billing (échecs de paiement, revenu, Stripe summary)

En tant qu'**admin billing**,  
je veux voir les indicateurs de santé du billing sur le tableau de bord,  
afin de détecter immédiatement une friction de paiement ou un écart de revenu.

**Acceptance Criteria :**

**Given** l'admin est sur `/admin/dashboard`  
**When** la section billing est affichée  
**Then** les indicateurs suivants sont visibles :
  - Nombre d'abonnements en échec de paiement (count par période)
  - Revenu total facturé sur la période (somme calculée depuis `user_subscriptions` actifs × prix plan)
  - Répartition revenu par plan (graphe ou tableau)

**Given** un indicateur d'échec de paiement est non nul  
**When** l'admin clique sur le compteur  
**Then** il est redirigé vers la section Users filtrée sur les comptes avec `failure_reason` non null

**Given** la section billing est affichée  
**When** le filtre de période est changé  
**Then** les KPIs billing recalculent avec la même période que les KPIs de flux (cohérence du contexte de filtre)

*Notes techniques :* Source de données = DB applicative (`user_subscriptions`, `billing_plans`) — pas d'appel direct à l'API Stripe dans cet endpoint MVP. Ajouter un lien vers la section Billing `/admin/billing` pour le détail complet.

---

## Groupe 65.C — Utilisateurs & Actions Support

*Prerequisite : Groupe 65.A livré.*

---

### Story 65-8 : Fiche utilisateur — recherche et consultation complète

En tant qu'**admin support**,  
je veux retrouver un utilisateur et consulter sa fiche complète,  
afin de comprendre son état exact et répondre efficacement à toute demande.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/users`  
**When** il saisit un email ou un ID numérique dans la barre de recherche et valide  
**Then** la liste des utilisateurs correspondants s'affiche (nom/email, plan, statut, date d'inscription)  
**And** la recherche par email partiel fonctionne (ILIKE sur PostgreSQL)

**Given** l'admin clique sur un utilisateur dans les résultats  
**When** la fiche s'ouvre  
**Then** les sections suivantes sont visibles :
  - Profil : email, rôle, date de création, statut (actif / suspendu / verrouillé)
  - Plan actif : code plan, statut abonnement, date de début
  - Stripe : ID client Stripe (masqué partiellement), statut abonnement Stripe, méthode de paiement (type + 4 derniers chiffres), dernière facture (date + montant)
  - Quotas : consommés vs autorisés pour la période courante (par feature)
  - Générations récentes : 20 dernières (use case, date, statut succès/échec, tokens utilisés)
  - Tickets support : 5 derniers ouverts (titre, statut, date)
  - Audit : 10 derniers événements d'audit le concernant (action, acteur, date)

**Given** l'admin consulte la fiche  
**When** les données Stripe sont affichées  
**Then** l'ID Stripe est masqué (`cus_xxx...xxx` — seuls les 4 premiers et 4 derniers caractères visibles)  
**And** la révélation complète nécessite un clic explicite qui génère un audit log `action: "sensitive_data_revealed"`

*Notes techniques :* Endpoint `GET /api/v1/admin/users/{user_id}` (guard admin). Agrège les données depuis `users`, `user_subscriptions`, `billing_plans`, `stripe_billing`, `token_usage_log`, `audit_events`, tables support. Composant `AdminUserDetailPage.tsx`. Gestion du masquage côté backend (ne jamais retourner les IDs Stripe complets par défaut).

---

### Story 65-9 : Actions applicatives sur compte (suspension, reset quota, déblocage)

En tant qu'**admin support**,  
je veux pouvoir suspendre, réactiver, réinitialiser un quota ou débloquer un compte,  
afin de résoudre des incidents utilisateur sans passer par la base de données directement.

**Acceptance Criteria :**

**Given** l'admin est sur la fiche d'un utilisateur actif  
**When** il clique "Suspendre le compte" et confirme dans la modale  
**Then** un flag de suspension est posé sur le compte (champ `suspended: true` ou équivalent)  
**And** les prochains refresh de token JWT pour cet utilisateur échouent avec `account_suspended`  
**And** un audit log est généré : `action: "account_suspended"`, `target_type: "user"`, `target_id: user_id`, `before: {suspended: false}`, `after: {suspended: true}`  
**And** le badge de statut sur la fiche passe à "Suspendu"

**Given** l'admin est sur la fiche d'un utilisateur suspendu  
**When** il clique "Réactiver le compte" et confirme  
**Then** le flag de suspension est levé, audit log généré avec `action: "account_reactivated"`

**Given** l'admin clique "Réinitialiser le quota [feature]" pour une feature spécifique  
**When** il confirme dans la modale (aucun champ de motif requis pour cette action)  
**Then** le compteur de quota pour la période courante est remis à zéro  
**And** un audit log est généré : `action: "quota_reset"`, `details: {feature_code, before: N, after: 0}`  
**And** l'indicateur de quota sur la fiche se met à jour

**Given** un compte est verrouillé (trop de tentatives)  
**When** l'admin clique "Débloquer le compte" et confirme  
**Then** le verrou est levé, audit log généré : `action: "account_unlocked"`

**Given** l'admin initie une action  
**When** le bouton est cliqué  
**Then** le feedback d'initiation (spinner, désactivation bouton) est visible en ≤ 200ms

*Notes techniques :* **Migration DB requise en premier :** ajouter les colonnes `is_suspended: bool = False` et `is_locked: bool = False` sur la table `users` via Alembic avant d'implémenter les endpoints. Endpoints `POST /api/v1/admin/users/{user_id}/suspend`, `/unsuspend`, `/reset-quota`, `/unlock`. Chaque endpoint appelle `AuditService.create_event()`. La suspension doit bloquer côté `require_authenticated_user` ou dans un middleware de vérification du statut utilisateur.

---

### Story 65-10 : Actions avec effets Stripe — refresh abonnement, plan manuel, geste commercial

En tant qu'**admin billing/support**,  
je veux pouvoir resynchroniser un abonnement depuis Stripe, attribuer un plan manuellement ou enregistrer un geste commercial,  
afin de corriger des incohérences ou accorder des exceptions sans toucher à la facturation.

**Acceptance Criteria :**

**Given** l'admin clique "Forcer un refresh d'abonnement" sur une fiche utilisateur  
**When** la modale s'affiche  
**Then** un avertissement explicite est visible : "Cette action resynchronise le statut et le plan depuis Stripe en lecture+écriture. Aucun changement de facturation ne sera effectué côté Stripe."  
**And** après confirmation, l'abonnement DB est mis à jour depuis Stripe (statut, plan_id)  
**And** un audit log est généré : `action: "subscription_refresh_forced"`, `details: {before: {...}, after: {...}}`

**Given** l'admin attribue un plan manuellement  
**When** la modale s'ouvre  
**Then** un sélecteur de plan est disponible + un champ de motif obligatoire  
**And** le badge "Applicatif uniquement — sans effet Stripe" est visible  
**And** après confirmation avec motif saisi, le plan en DB est mis à jour  
**And** un audit log est généré : `action: "plan_manually_assigned"`, `details: {before: plan_code_avant, after: plan_code_après, reason: "..."}`

**Given** l'admin enregistre un geste commercial  
**When** la modale s'ouvre  
**Then** les champs disponibles sont : type de geste (jours supplémentaires / messages supplémentaires), valeur numérique, motif (optionnel)  
**And** le badge "Applicatif uniquement — aucun crédit Stripe" est visible  
**And** après confirmation, un flag `commercial_gesture` est appliqué sur l'abonnement  
**And** un audit log est généré : `action: "commercial_gesture_recorded"`, `details: {gesture_type, value, reason, before, after}`

*Notes techniques :* Endpoints `POST /api/v1/admin/users/{user_id}/refresh-subscription`, `/assign-plan`, `/commercial-gesture`. La resynchronisation Stripe utilise le SDK Stripe en lecture (retrieve subscription). Le motif obligatoire pour `assign-plan` est validé côté backend (champ non vide).

---

### Story 65-11 : Support — consultation tickets et contenus signalés

En tant qu'**admin support**,  
je veux consulter les tickets ouverts et les contenus signalés depuis l'espace admin,  
afin de traiter les demandes utilisateurs et modérer le contenu problématique.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/support`  
**When** la page charge  
**Then** la liste des tickets support ouverts est affichée (titre, auteur, statut, date, catégorie)  
**And** un filtre par statut (ouvert / en cours / résolu) et par catégorie est disponible

**Given** l'admin clique sur un ticket  
**When** le détail s'ouvre  
**Then** le contexte complet est visible : description initiale, historique des échanges, actions admin déjà effectuées sur ce dossier (audit trail du ticket)  
**And** un lien direct vers la fiche utilisateur correspondante est présent

**Given** l'admin accède à la section "Contenus signalés"  
**When** la liste s'affiche  
**Then** chaque entrée montre : type de contenu (génération / chat), extrait, utilisateur, date du signalement  
**And** les actions disponibles sont : marquer comme traité, accéder à la fiche utilisateur

**Given** l'admin effectue une action sur un ticket ou un contenu signalé  
**When** l'action est complétée  
**Then** un audit log est généré avec `action: "support_ticket_action"` ou `"flagged_content_reviewed"`, acteur, cible, date

*Notes techniques :* Utiliser les tables `support_incident` et `support_ticket_category` existantes. Endpoint `GET /api/v1/admin/support/tickets` et `GET /api/v1/admin/support/flagged-content`. Composant `AdminSupportPage.tsx`.

---

## Groupe 65.D — Abonnements & Entitlements

*Prerequisite : Groupe 65.A livré. Source de vérité : `plan_catalog`, `product_entitlements`.*

---

### Story 65-12 : Matrice entitlements — vue canonique consultation (plans × features)

En tant qu'**admin ops ou business**,  
je veux consulter une matrice visuelle des droits par plan,  
afin d'avoir en un seul écran la source de vérité sur ce que chaque plan permet, sans ambiguïté entre DB, backend et frontend.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/entitlements`  
**When** la page charge  
**Then** une matrice est affichée avec :
  - Colonnes : plans (free / basic / premium + tout plan actif en DB)
  - Lignes : chaque feature/use case (horoscope_daily, natal_interpretation, chat, etc.)
  - Cellules : pour chaque plan × feature : mode d'accès (disabled / quota / unlimited), valeur du quota, période de reset, règles trial/lifetime, variant de génération LLM attendu, indicateur teaser (oui/non)

**Given** la matrice est affichée  
**When** l'admin survole une cellule  
**Then** un tooltip affiche les détails complets de l'entitlement correspondant (valeurs exactes depuis DB)

**Given** les données sont issues de la DB (`plan_catalog` + `product_entitlements`)  
**When** la matrice est construite  
**Then** toutes les valeurs reflètent exactement ce qui est en base — pas de valeurs hardcodées frontend  
**And** une section "Règles backend / comportement frontend attendu" est visible en bas de page pour chaque feature (annotation éditoriale, non éditée via cette vue)

**Given** un plan a une valeur incohérente (ex : quota à 0 avec mode `quota`)  
**When** la cellule est affichée  
**Then** un indicateur visuel d'alerte est présent sur la cellule

*Notes techniques :* Endpoint `GET /api/v1/admin/entitlements/matrix`. Requête cross-table `plan_catalog` × `product_entitlements`. Composant `AdminEntitlementsPage.tsx`. Vue lecture seule distincte du mode édition (story suivante). CSS avec variables `--line`, `--glass`, `--text-1`.

---

### Story 65-13 : Matrice entitlements — édition quotas et feature flags avec audit

En tant qu'**admin ops**,  
je veux pouvoir modifier les valeurs de quotas et les flags de features directement depuis la matrice,  
afin d'ajuster les droits d'accès sans déploiement et avec traçabilité complète.

**Acceptance Criteria :**

**Given** l'admin est sur la vue matrice  
**When** il active le mode édition (bouton "Modifier" explicite)  
**Then** les cellules éditables (quotas, mode d'accès, flags teaser) deviennent interactives  
**And** un bandeau "Mode édition — toute modification génère un audit log" est visible

**Given** l'admin modifie la valeur d'un quota dans une cellule  
**When** il valide la cellule  
**Then** une modale de confirmation s'ouvre affichant : plan, feature, valeur avant, valeur après  
**And** l'admin doit confirmer explicitement (bouton "Confirmer la modification")

**Given** la modification est confirmée  
**When** la requête est envoyée  
**Then** la valeur en DB est mise à jour  
**And** un audit log est généré : `action: "entitlement_quota_updated"`, `target_type: "plan_entitlement"`, `details: {plan_code, feature_code, before: {quota: N}, after: {quota: M}}`  
**And** la matrice se rafraîchit avec la nouvelle valeur

**Given** l'admin tente de modifier un variant de prompt LLM depuis la matrice  
**When** il inspecte la cellule correspondante  
**Then** le champ est en lecture seule avec la mention "Configurable dans Prompts & Personas"

*Notes techniques :* Endpoint `PATCH /api/v1/admin/entitlements/{plan_code}/{feature_code}`. Validation backend stricte : seuls `quota_value`, `access_mode`, `is_teaser` sont éditables via cet endpoint. Journalisation via `AuditService`.

---

## Groupe 65.E — LLM Ops & Configuration

*Prerequisite : Groupe 65.A livré. Certaines stories utilisent les tables LLM existantes.*

---

### Story 65-14 : Supervision IA — tableau de bord métier des use cases LLM

En tant qu'**admin ops ou product**,  
je veux voir les performances métier des use cases LLM (volume, coût, latence, taux d'échec),  
afin de détecter rapidement une dérive ou une surconsommation avant qu'elle impacte les coûts ou l'expérience.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/ai-generations`  
**When** la page charge  
**Then** un tableau de bord affiche pour chaque use case actif (sur la période sélectionnée) :
  - Volume total d'appels
  - Coût tokens estimé (prompt + completion tokens × prix unitaire configuré)
  - Temps de réponse moyen (p50 et p95)
  - Taux d'échec (calls avec status `error` / total)
  - Taux de retry (calls avec `retry_count > 0` / total)
  - Persona et prompt version les plus utilisés

**Given** l'admin applique un filtre de période (7j / 30j)  
**When** le filtre change  
**Then** tous les métriques recalculent pour la période choisie

**Given** un use case a un taux d'échec > seuil (ex : 5%)  
**When** il apparaît dans le tableau  
**Then** sa ligne est surlignée avec `var(--danger)` ou un indicateur visuel d'alerte

**Given** l'admin clique sur un use case  
**When** le détail s'ouvre  
**Then** un graphe de tendance temporelle du volume et du taux d'échec est affiché  
**And** les 10 derniers appels en échec sont listés avec leurs métadonnées (timestamp, error_code, user_id masqué)

*Notes techniques :* Source : table `llm_observability` (LlmCallLogModel) et `token_usage_log`. Endpoint `GET /api/v1/admin/ai/metrics?period=7d`. Ce panneau est distinct de FR65-7 (observabilité technique) — il est métier, pas incidents. Composant `AdminAiGenerationsPage.tsx`.

---

### Story 65-15 : Observabilité technique — incidents, erreurs applicatives, logs LLM, replay

En tant qu'**admin technique (ops)**,  
je veux un cockpit technique centralisant erreurs applicatives, incidents Stripe et logs LLM,  
afin de diagnostiquer et rejouer les cas problématiques sans accès direct aux serveurs.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/logs`  
**When** la page charge  
**Then** trois onglets sont disponibles : "Erreurs applicatives", "Logs LLM", "Événements Stripe"

**Given** l'onglet "Logs LLM" est actif  
**When** l'admin applique des filtres (use case, statut succès/échec, période)  
**Then** la liste filtrée des appels LLM s'affiche (timestamp, use case, statut, durée, tokens, error_code si échec)

**Given** l'admin sélectionne un log LLM en échec  
**When** il clique "Rejouer cet appel"  
**Then** une modale de confirmation s'affiche avec le contexte de l'appel (use case, persona, prompt version)  
**And** après confirmation, le service de replay est appelé et le résultat est affiché (succès/échec, nouvelle réponse)  
**And** un audit log est généré : `action: "llm_call_replayed"`, `details: {original_log_id, replay_result}`

**Given** l'onglet "Événements Stripe" est actif  
**When** la liste s'affiche  
**Then** les webhooks Stripe non traités ou en erreur sont mis en évidence avec leur type d'événement et le motif d'échec

**Given** l'admin consulte les alertes sur quotas  
**When** un utilisateur est à > 90% de son quota  
**Then** il apparaît dans une section "Alertes quotas" avec son email (masqué partiellement), son plan et son taux de consommation

*Notes techniques :* Utilise `LlmCallLogModel` (existant), `ObservabilityService`, `ReplayService` (déjà implémenté dans `admin_llm.py`). Centraliser l'accès dans le nouveau composant `AdminLogsPage.tsx`. Endpoints `GET /api/v1/admin/logs/llm`, `/logs/stripe`, `/logs/errors`, `POST /api/v1/admin/logs/llm/{log_id}/replay`.

---

### Story 65-16 : Config prompts LLM — consultation, diff et rollback

En tant qu'**admin ops**,  
je veux consulter les prompts LLM actifs, voir leur historique et revenir à une version précédente,  
afin d'ajuster la qualité des réponses sans déploiement et de rollback en < 15 min si nécessaire.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/prompts`  
**When** la page charge  
**Then** la liste des use cases est affichée avec pour chacun : version de prompt active, date d'activation, persona associée, statut (`active` / `draft` / `deprecated`)

**Given** l'admin clique sur un use case  
**When** le détail s'ouvre  
**Then** le prompt actif est affiché avec son contenu complet  
**And** l'historique des versions précédentes est listé (version, date, auteur de l'activation)

**Given** l'admin compare deux versions  
**When** il sélectionne "Comparer avec la version précédente"  
**Then** un diff côte à côte est affiché (ajouts en vert `var(--success)`, suppressions en rouge `var(--danger)`)

**Given** l'admin décide de revenir à une version précédente  
**When** il clique "Rollback vers cette version" et confirme dans la modale (≤ 15 min requis par NFR21)  
**Then** la version sélectionnée devient active  
**And** un audit log est généré : `action: "prompt_rollback"`, `details: {use_case, from_version, to_version}`  
**And** la page se met à jour avec la nouvelle version active

*Notes techniques :* Utilise les tables `llm_prompt` (`LlmPromptVersionModel`, `LlmUseCaseConfigModel`) existantes et `PromptRegistryV2`. Endpoints déjà partiellement existants dans `admin_llm.py` — wrapper dans la nouvelle structure de navigation. Composant `AdminPromptsPage.tsx`.

---

### Story 65-17 : Config personas — consultation et activation/désactivation

En tant qu'**admin ops**,  
je veux consulter et activer/désactiver les personas d'astrologues,  
afin d'ajuster le comportement conversationnel sans déploiement.

**Acceptance Criteria :**

**Given** l'admin accède à l'onglet "Personas" dans `/admin/prompts` (ou sous-section dédiée)  
**When** la page charge  
**Then** la liste des personas est affichée avec : nom, statut (active/inactive), description, date de dernière modification

**Given** l'admin clique sur une persona  
**When** le détail s'ouvre  
**Then** les paramètres complets sont visibles (nom, description, contraintes de comportement, use cases associés)

**Given** l'admin désactive une persona active  
**When** il confirme dans la modale  
**Then** la persona passe en statut `inactive`  
**And** un audit log est généré : `action: "persona_deactivated"`, `details: {persona_id, persona_name}`  
**And** si la persona est assignée à des utilisateurs actifs, un avertissement est affiché avant confirmation

*Notes techniques :* Utilise `LlmPersonaModel` et les endpoints existants dans `admin_llm.py`. Intégrer dans la nouvelle navigation plutôt que créer des endpoints redondants. Composant `AdminPersonasPage.tsx` (existant à migrer/adapter).

---

### Story 65-18 : Config contenus & paywalls — textes et feature flags

En tant qu'**admin ops ou product**,  
je veux modifier les textes des paywalls, le wording marketing in-app et activer/désactiver des feature flags,  
afin d'ajuster l'expérience produit sans déploiement.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/content`  
**When** la page charge  
**Then** trois sections sont visibles : "Textes paywalls", "Messages transactionnels", "Feature flags"

**Given** l'admin édite un texte de paywall  
**When** il modifie le contenu et sauvegarde  
**Then** la modification est persistée en DB  
**And** un audit log est généré : `action: "content_text_updated"`, `details: {content_key, before, after}`  
**And** un indicateur de version (timestamp de dernière modification) est affiché

**Given** l'admin accède à la section "Feature flags"  
**When** la liste s'affiche  
**Then** chaque flag est présenté avec : code, description, état courant (activé/désactivé), scope (tous plans / plan spécifique)

**Given** l'admin bascule un feature flag  
**When** il confirme dans la modale  
**Then** l'état du flag change en DB  
**And** un audit log est généré : `action: "feature_flag_toggled"`, `details: {flag_code, before: false, after: true}`

*Notes techniques :* **Nouveau modèle DB requis :** créer `ConfigTextModel` (table `config_texts` : `key`, `value`, `category`, `updated_at`, `updated_by_user_id`) via Alembic avant les endpoints de modification. Utilise `ops_feature_flags.py` router existant pour les feature flags. Composant `AdminContentPage.tsx`. **Périmètre de cette story :** textes paywalls + messages transactionnels + feature flags uniquement. Les templates éditoriaux et règles de scoring/calibration (FR65-6d) sont traités dans la story suivante (65-18b).

---

### Story 65-18b : Config règles métier — templates éditoriaux et scoring/calibration

En tant qu'**admin ops**,  
je veux consulter et modifier les templates éditoriaux et les règles de scoring/calibration,  
afin d'ajuster la structure et la qualité des contenus générés sans déploiement.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/content` section "Règles métier"  
**When** la page charge  
**Then** deux sous-sections sont visibles : "Templates éditoriaux" et "Règles de calibration"

**Given** l'admin consulte un template éditorial  
**When** le détail s'ouvre  
**Then** la structure du template est visible (sections, balises attendues, exemple de rendu)  
**And** le template actif est identifié avec sa version et sa date d'activation

**Given** l'admin modifie un template éditorial  
**When** il sauvegarde après modification  
**Then** la nouvelle version est enregistrée en DB (versionnée, pas d'écrasement)  
**And** un audit log est généré : `action: "editorial_template_updated"`, `details: {template_code, before_version, after_version}`  
**And** le rollback vers la version précédente est disponible

**Given** l'admin consulte les règles de calibration  
**When** la liste s'affiche  
**Then** chaque règle est présentée avec : code, valeur courante, type (numérique / booléen / enum), description de l'effet

**Given** l'admin modifie une règle de calibration  
**When** il confirme dans la modale  
**Then** la valeur est mise à jour en DB  
**And** un audit log est généré : `action: "calibration_rule_updated"`, `details: {rule_code, before, after}`

*Notes techniques :* Les templates éditoriaux utilisent probablement `consultation_template` ou un modèle équivalent existant — vérifier avant de créer une nouvelle table. Les règles de calibration peuvent s'appuyer sur `calibration.py` dans les modèles DB. Si aucune table existante n'est adaptée, créer `EditorialTemplateVersionModel` suivant le même pattern de versioning que `LlmPromptVersionModel`. Composant dans `AdminContentPage.tsx` (sous-section "Règles métier").

---

## Groupe 65.F — Gouvernance & Audit

*Prerequisite : Groupe 65.A livré. Utilise `AuditEventModel` existant.*

---

### Story 65-19 : Journal d'audit global — consultation filtrée

En tant qu'**admin (super-admin futur)**,  
je veux consulter le journal d'audit global de toutes les actions admin,  
afin d'avoir une traçabilité complète de qui a fait quoi et quand sur le système.

**Acceptance Criteria :**

**Given** l'admin accède à `/admin/settings` (section "Journal d'audit")  
**When** la page charge  
**Then** la liste des événements d'audit récents est affichée (50 par page, paginée) avec : timestamp, acteur (email masqué partiellement), action, cible (type + id masqué), statut

**Given** l'admin applique des filtres  
**When** il filtre par acteur, type d'action (ex : `account_suspended`, `prompt_rollback`) ou période  
**Then** la liste se met à jour avec les événements correspondants

**Given** l'admin clique sur un événement d'audit  
**When** le détail s'ouvre  
**Then** le contenu complet de `details` est visible : `before`, `after`, `reason` si présents  
**And** un lien vers la fiche utilisateur cible est présent si `target_type = "user"`

**Given** l'admin exporte le journal filtré  
**When** il clique "Exporter" et confirme (double confirmation)  
**Then** un fichier CSV est généré et téléchargé  
**And** un audit log est généré : `action: "audit_log_exported"`, `details: {filters_applied, record_count}`

*Notes techniques :* Utilise `AuditService` et `AuditEventModel` existants. Endpoint `GET /api/v1/admin/audit?actor=&action=&period=` (guard admin). Pagination cursor-based ou offset. Composant `AdminAuditLogPage.tsx` (dans `/admin/settings`).

---

### Story 65-20 : Exports sécurisés — utilisateurs, générations, billing

En tant qu'**admin (super-admin futur)**,  
je veux exporter des données sensibles en format structuré avec double confirmation,  
afin de produire des rapports ou de transférer des données en respectant les processus de sécurité.

**Acceptance Criteria :**

**Given** l'admin accède à la section "Exports" dans `/admin/settings`  
**When** la page charge  
**Then** les exports disponibles sont listés : "Liste utilisateurs (CSV)", "Historique générations (CSV/JSON)", "Données billing (CSV)"

**Given** l'admin clique sur un export  
**When** la modale s'ouvre  
**Then** un avertissement explicite est visible : "Cet export contient des données sensibles. Il sera journalisé."  
**And** un champ de filtre de période est disponible  
**And** une double confirmation est requise (cocher une case + cliquer "Confirmer l'export")

**Given** l'export est confirmé  
**When** le fichier est généré  
**Then** le download démarre  
**And** un audit log est généré : `action: "sensitive_data_exported"`, `details: {export_type, filters, record_count, actor_user_id}`

**Given** les données exportées contiennent des identifiants Stripe ou des données personnelles  
**When** le fichier est généré  
**Then** les IDs Stripe sont présents mais les données bancaires ne le sont pas (numéros de carte jamais exportés)

*Notes techniques :* Endpoints `POST /api/v1/admin/exports/{type}` (guard admin). Génération CSV côté backend avec `csv` stdlib Python. Les exports volumineux (> 10 000 lignes) retournent un job asynchrone avec polling ou webhook — gérer le cas MVP synchrone avec une limite de 5 000 lignes.

---

### Story 65-21 : Infrastructure permissions — contexte auth frontend + préparation RBAC

En tant que **développeur frontend et architect**,  
je veux que l'infrastructure de permissions admin soit en place pour les profils fins futurs,  
afin que l'ajout de profils `admin_business`, `admin_support`, `admin_ops` ne nécessite pas de refonte.

**Acceptance Criteria :**

**Given** l'utilisateur admin est connecté  
**When** le contexte auth est initialisé  
**Then** un `AdminPermissionsContext` React expose : `allowedSections: string[]`, `canEdit: (domain: string) => boolean`, `canExport: boolean`

**Given** l'implémentation initiale (rôle unique `admin`)  
**When** le contexte est initialisé pour un utilisateur `admin`  
**Then** `allowedSections` contient toutes les 10 sections  
**And** `canEdit("entitlements")`, `canEdit("prompts")`, `canExport` retournent tous `true`

**Given** un composant admin reçoit `canEdit("entitlements") = false` (simulation future)  
**When** le composant est rendu  
**Then** le bouton "Modifier" n'est pas affiché (ou est désactivé avec indication visuelle)  
**And** le mode consultation reste pleinement accessible

**Given** le backend reçoit une requête admin  
**When** le guard `require_admin_user` valide le token  
**Then** l'objet `AuthenticatedUser` retourné inclut `permissions: list[str]` (liste vide pour MVP initial, extensible sans breaking change)

*Notes techniques :* **Frontière avec Story 65-4 :** la story 65-4 crée le contexte et l'instancie pour le menu de navigation. Cette story (65-21) contractualise l'interface complète du contexte (`allowedSections`, `canEdit`, `canExport`), vérifie que tous les composants admin (matrice entitlements, prompts, exports) le consomment correctement, et ajoute le champ `permissions` côté backend. Ordre d'implémentation : 65-4 d'abord, 65-21 en dernier sprint (groupe F). Créer `frontend/src/context/AdminPermissionsContext.tsx`. Backend : ajouter le champ `permissions: list[str] = []` à `AuthenticatedUser` dans `auth.py` (valeur vide pour tous les admins dans cet epic). Pas de table de permissions à créer dans cet epic — c'est de la direction d'architecture.
