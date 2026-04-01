# Story 62.1 : Page de support et help center utilisateur

Status: done

---

## Story

En tant qu'utilisateur authentifié,
je veux accéder à une page de support qui m'explique le fonctionnement du site (tokens, abonnements, fonctionnalités), me permet de choisir une catégorie de demande parmi une liste maintenue en base de données, puis de soumettre un ticket horodaté tracé en base avec un statut `pending` / `solved` / `canceled`, une éventuelle réponse du support et un suivi visible côté utilisateur,
afin d'obtenir de l'aide de manière structurée et de pouvoir suivre l'avancement de mes demandes.

---

## Contexte

### Ce qui existe déjà (à réutiliser sans casser)

- `SupportIncidentModel` (`backend/app/infra/db/models/support_incident.py`) : table `support_incidents` avec `id`, `user_id`, `created_by_user_id`, `category` (String 32), `title`, `description`, `status` (String 16), `priority` (String 16), `support_response`, `resolved_at`, `created_at`, `updated_at`.
- `IncidentService` (`backend/app/services/incident_service.py`) : service complet CRUD incidents. Valide `VALID_INCIDENT_STATUS = {"open", "in_progress", "resolved", "closed"}` et `VALID_INCIDENT_CATEGORY = {"account", "subscription", "content"}`.
- `backend/app/api/v1/routers/support.py` : router `/v1/support/*` **réservé aux rôles `support`, `ops`, `admin`**. Ne pas toucher.
- `frontend/src/api/support.ts` : hooks TanStack Query pour l'usage ops. Ne pas modifier.
- Route `/support` dans `frontend/src/app/routes.tsx` : `RoleGuard roles={["support", "ops"]}`. Rester intact.
- `frontend/src/components/ui/UserMenu/UserMenu.tsx` + `frontend/src/components/layout/Header.tsx` : menu utilisateur déjà branché dans le header, avec navigation clavier, rôle `menu` / `menuitem`, fermeture `Escape` / click outside. Réutiliser ce point d'entrée pour exposer `/help`.
- Le frontend possède déjà des primitives et patterns à réutiliser : `PageLayout`, cartes settings (`settings-card`), `Skeleton`, `EmptyState`, `ErrorState`, composants UI du dossier `frontend/src/components/ui`, et la logique i18n/navigation existante.

### Ce qui manque (à créer)

1. Une table `support_ticket_categories` pour gérer les catégories en base.
2. Des endpoints accessibles aux utilisateurs authentifiés (`role=user`) sous `/v1/help/*`.
3. Une page frontend `/help` avec sections d'aide statiques + formulaire multi-étapes.
4. Un suivi des tickets propres à l'utilisateur connecté.

### Décisions de design

- **Route frontend** : `/help` (pas `/support`, déjà pris par le panneau ops).
- **Navigation utilisateur** : la page `/help` doit être accessible depuis le `user-menu` du header.
- **Statuts utilisateurs** : `pending` (ticket créé, en attente), `solved` (résolu), `canceled` (annulé / clôturé). Ces trois valeurs sont ajoutées aux statuts valides de l'`IncidentService` et à `ALLOWED_STATUS_TRANSITIONS`.
- **Priorité** : les tickets soumis par l'utilisateur ont toujours `priority="low"` (fixé côté API, non exposé à l'utilisateur).
- **Catégories** : `SupportIncidentModel.category` reste un `String(32)`. Le code de la catégorie (ex. `"billing_issue"`) y est stocké. Pas de FK hard en base — relation soft via le code.
- **Catégories validées en base** : le nouvel endpoint de création charge les codes actifs depuis `SupportTicketCategoryModel` pour valider la catégorie soumise. `VALID_INCIDENT_CATEGORY` dans `incident_service.py` continue de couvrir les catégories ops historiques.
- **Seed support catégories** : les catégories utilisateur sont auto-seedées au démarrage backend via `backend/scripts/seed_support_categories.py` si la table est vide.
- **Réponse support** : la réponse textuelle du support est persistée dans `SupportIncidentModel.support_response`, exposée dans `/v1/help/tickets` et visible dans la page `/help`.
- **Pas de Tailwind** : styles dans des fichiers `.css` dédiés, variables CSS du projet.
- **i18n** : nouveau fichier `frontend/src/i18n/support.ts` avec fr/en/es.
- **Standards UI support / help center** : la page `/help` doit s'aligner visuellement et structurellement avec le reste de l'application, en réutilisant au maximum les composants, layouts, tokens CSS et patterns déjà créés. Ne pas introduire un nouveau sous-système visuel si les primitives existantes couvrent le besoin.

---

## Acceptance Criteria

### AC1 — Table `support_ticket_categories` et seed initial

Une nouvelle table `support_ticket_categories` est créée via une migration Alembic dédiée :

```text
support_ticket_categories
  id              Integer PK autoincrement
  code            VARCHAR(64) NOT NULL UNIQUE
  label_fr        VARCHAR(160) NOT NULL
  label_en        VARCHAR(160) NOT NULL
  label_es        VARCHAR(160) NOT NULL
  description_fr  TEXT NULL
  display_order   Integer NOT NULL DEFAULT 0
  is_active       Boolean NOT NULL DEFAULT true
  created_at      DateTime(timezone=True) NOT NULL
```

Le seed initial (`backend/scripts/seed_support_categories.py`) insère ou met à jour (upsert sur `code`) les catégories suivantes :

| code | label_fr | label_en | display_order |
|------|----------|----------|---------------|
| `account_access` | Accès ou connexion au compte | Account access issue | 1 |
| `billing_issue` | Facturation ou paiement | Billing or payment issue | 2 |
| `subscription_problem` | Abonnement ou formule | Subscription or plan issue | 3 |
| `bug` | Bug ou problème technique | Bug or technical issue | 4 |
| `feature_question` | Question sur une fonctionnalité | Feature question | 5 |
| `data_privacy` | Données personnelles et confidentialité | Personal data and privacy | 6 |
| `other` | Autre | Other | 7 |

Le seed est idempotent (aucune erreur en cas de réexécution).

---

### AC2 — Endpoint `GET /v1/help/categories`

- Accessible à tout utilisateur authentifié (rôle `user`, `support`, `ops`, `admin`).
- Retourne uniquement les catégories `is_active=true`, triées par `display_order`.
- Format de réponse :

```json
{
  "data": {
    "categories": [
      {
        "code": "subscription_problem",
        "label": "Problème avec mon abonnement",
        "description": null
      }
    ]
  },
  "meta": { "request_id": "..." }
}
```

- Le champ `label` est la version dans la langue de la requête (`Accept-Language` ou `lang` query param, défaut `fr`).
- Rate limiting : 60 requêtes/min/utilisateur.
- Pas de cache Redis requis au MVP (lecture DB directe suffisante).

---

### AC3 — Endpoint `POST /v1/help/tickets`

- Accessible à tout utilisateur authentifié (rôle `user` au minimum).
- Crée un `SupportIncidentModel` avec `user_id = current_user.id`, `created_by_user_id = current_user.id`, `status = "pending"`, `priority = "low"`.
- Valide que `category_code` est un code actif en base (`SupportTicketCategoryModel`).
- Payload d'entrée :

```json
{
  "category_code": "bug",
  "subject": "Le chat ne répond plus depuis hier",
  "description": "Depuis hier soir, chaque message que j'envoie retourne une erreur..."
}
```

- `subject` → stocké dans `SupportIncidentModel.title` (max 160 caractères, non vide).
- `description` → stocké dans `SupportIncidentModel.description` (non vide).
- `category_code` → stocké dans `SupportIncidentModel.category`.
- Pour les catégories standards, le frontend remplit automatiquement `subject` avec le libellé de la catégorie.
- Pour la catégorie `other`, l'utilisateur doit saisir un objet dédié.
- Réponse 201 avec le ticket créé :

```json
{
  "data": {
    "ticket_id": 42,
    "category_code": "bug",
    "subject": "...",
    "description": "...",
    "status": "pending",
    "created_at": "2026-04-01T10:00:00Z",
    "resolved_at": null
  },
  "meta": { "request_id": "..." }
}
```

- Rate limiting : 5 tickets créés/heure/utilisateur (protège contre les spams).
- Erreur 422 si `category_code` inconnu ou inactif : `{ "error": { "code": "ticket_invalid_category", ... } }`.
- Erreur 422 si `subject` vide ou > 160 chars.
- Erreur 422 si `description` vide.

---

### AC4 — Endpoint `GET /v1/help/tickets`

- Accessible à l'utilisateur authentifié, retourne **ses propres tickets uniquement** (`user_id = current_user.id`).
- Triés par `created_at` DESC.
- Paramètre optionnel `?limit=20&offset=0`.
- Réponse :

```json
{
  "data": {
    "tickets": [
      {
        "ticket_id": 42,
        "category_code": "bug",
        "subject": "...",
        "description": "...",
        "status": "pending",
        "support_response": null,
        "created_at": "...",
        "updated_at": "...",
        "resolved_at": null
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "meta": { "request_id": "..." }
}
```

- Rate limiting : 30 requêtes/min/utilisateur.

---

### AC5 — Extension des statuts `IncidentService`

Dans `backend/app/services/incident_service.py`, les constantes sont étendues **sans supprimer les valeurs existantes** :

```python
VALID_INCIDENT_STATUS = {"open", "in_progress", "resolved", "closed", "pending", "canceled", "solved"}

ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress", "resolved", "closed"},
    "in_progress": {"resolved", "closed"},
    "resolved": {"closed"},
    "closed": set(),
    # Statuts utilisateurs
    "pending": {"solved", "canceled", "in_progress"},
    "solved": {"canceled"},
    "canceled": set(),
}
```

`resolved_at` est défini quand le statut devient `"resolved"`, `"solved"` ou `"canceled"`.
`resolved_at` est remis à `None` si le statut repasse à `"pending"` ou `"in_progress"`.

Aucune régression sur les tests existants des statuts ops.

---

### AC6 — Route frontend `/help` avec sections d'aide statiques

La page `/help` (`frontend/src/pages/HelpPage.tsx`) est accessible à tout utilisateur authentifié (pas de `RoleGuard`).

Elle comporte trois sections d'aide statiques (contenu i18n) :

**Section 1 : Comment fonctionne l'application**
- Présentation des rubriques : Dashboard / Horoscope du jour, Chat astrologue, Thème natal, Consultations.
- Chaque rubrique a une icône Lucide, un titre, une description courte.

**Section 2 : Les tokens — comment ça marche**
- Explication que les messages et consultations consomment des tokens LLM.
- Tableau lisible : plan Basic = X tokens/jour + Y/semaine + Z/mois ; Premium = ...
- Les limites sont **codées en dur dans les traductions** (pas récupérées via API) — valeurs à jour au moment de l'implémentation.

**Section 3 : Les abonnements disponibles**
- Plan Free (accès limité), Plan Basic, Plan Premium.
- Description des avantages de chaque plan.
- CTA "Gérer mon abonnement" → lien vers `/settings/subscription`.

Règles de style :
- Aucun style inline : tout dans `frontend/src/pages/HelpPage.css`.
- Utiliser les variables CSS du projet (`var(--text-1)`, `var(--glass)`, `var(--primary)`, etc.).
- Les sections sont visuellement séparées avec `var(--glass)` / `var(--glass-border)`.
- La page doit réutiliser le layout applicatif existant (`PageLayout` ou équivalent) et les patterns de sections déjà visibles dans `settings`, `dashboard` ou les pages de contenu proches.
- Réutiliser en priorité les composants existants pour les surfaces, boutons, états vides, erreurs et chargements (`Skeleton`, `EmptyState`, `ErrorState`, composants UI du dossier `components/ui`).
- Toute création d'un nouveau composant frontend doit être justifiée par un manque réel de primitive existante ; éviter la duplication de cartes, badges, CTA ou wrappers déjà disponibles.

---

### AC7 — Étape 1 : sélection de catégorie

En dessous des sections d'aide, un composant `SupportCategorySelect` (`frontend/src/pages/support/SupportCategorySelect.tsx`) affiche la liste des catégories récupérées depuis `GET /v1/help/categories`.

- Affichage en grille de cartes cliquables (une par catégorie).
- Chaque carte : icône Lucide associée au `code` (mapping statique), label traduit.
- Sélection d'une carte → passage automatique à l'étape 2 (formulaire).
- État loading : skeleton (réutiliser le composant `Skeleton` existant).
- État error : `ErrorState` existant avec bouton retry.

Mapping icônes suggéré (non bloquant) :

| code | icône Lucide |
|------|-------------|
| `subscription_problem` | `CreditCard` |
| `billing_issue` | `Receipt` |
| `bug` | `Bug` |
| `account_access` | `Lock` |
| `feature_question` | `HelpCircle` |
| `data_privacy` | `Shield` |
| `other` | `MessageSquare` |

---

### AC8 — Étape 2 : formulaire de demande de support

Le composant `SupportTicketForm` (`frontend/src/pages/support/SupportTicketForm.tsx`) s'affiche après sélection d'une catégorie.

- Affiche la catégorie sélectionnée avec un bouton "Modifier" (retour étape 1).
- Si la catégorie sélectionnée est `other`, afficher un champ **Objet** : `<input type="text">` — max 160 caractères, requis.
- Sinon, l'objet est prérempli côté frontend avec le label de la catégorie sélectionnée et n'est pas saisi par l'utilisateur.
- Champ **Description** : `<textarea>` — min 20 caractères, requis dans tous les cas.
- Bouton **Envoyer** : déclenche `POST /v1/help/tickets`.
- Validation via React Hook Form + Zod (aligné avec les patterns du projet).
- État d'envoi : bouton désactivé pendant la mutation, indicateur de chargement.
- Succès : affichage d'un message de confirmation + réinitialisation vers l'étape 1 + refresh de la liste des tickets.
- Erreur : message d'erreur traduit en fonction du `error.code` backend.
- Pas de style inline — styles dans `HelpPage.css`.

---

### AC9 — Suivi des tickets utilisateur

En bas de la page `/help`, un composant `SupportTicketList` (`frontend/src/pages/support/SupportTicketList.tsx`) affiche les tickets soumis par l'utilisateur connecté.

- Données depuis `GET /v1/help/tickets`.
- Si aucun ticket : `EmptyState` existant avec message traduit.
- Pour chaque ticket :
  - Catégorie (label traduit)
  - Objet (subject / title)
  - Description initiale
  - Réponse du support si présente
  - Date de création (format localisé)
  - Badge statut : `pending` (couleur neutre), `solved` (couleur succès `var(--success)`), `canceled` (couleur danger `var(--danger)`)
  - Date de résolution si disponible
- Liste triée par `created_at` DESC.
- Pagination simple : bouton "Voir plus" si `total > limit`.

---

### AC10 — Navigation et routing

Dans `frontend/src/app/routes.tsx`, ajouter :

```tsx
{
  path: "/help",
  element: <HelpPage />,
},
```

Sans `RoleGuard` — accessible à tout utilisateur authentifié.

Dans la sidebar / navigation existante (composant `AppShell` ou équivalent), ajouter une entrée "Aide & Support" pointant vers `/help`, visible pour le rôle `user`.
La clé i18n existante `nav.support` peut être réutilisée ou une nouvelle clé `nav.help` peut être créée — vérifier l'existant dans `navigation.ts` avant de créer.

> **Note** : `nav.support` existe déjà dans `frontend/src/i18n/navigation.ts` et son libellé est déjà "Support". Il peut être réutilisé si la sidebar dirige vers `/help` pour les utilisateurs normaux.

En plus de la sidebar, le `user-menu` du header doit exposer une entrée dédiée vers `/help` :

- visible pour les utilisateurs authentifiés ;
- libellé explicite ("Aide & Support" ou équivalent i18n) ;
- implémentée comme un vrai `menuitem` dans le composant `UserMenu` existant ;
- navigable clavier comme les autres entrées du menu ;
- sans régression sur les comportements existants (`Escape`, click outside, focus visible, fermeture après navigation).

---

### AC11 — Fichier i18n `frontend/src/i18n/support.ts`

Nouveau fichier couvrant toutes les chaînes de la page `/help` :
- Titres et descriptions des sections d'aide statiques
- Labels du formulaire (objet, description, boutons, messages d'erreur)
- Labels des statuts tickets (`pending`, `solved`, `canceled`)
- Messages vides / erreurs

Structure attendue :

```typescript
export interface SupportTranslation {
  help: {
    pageTitle: string
    sections: {
      howItWorks: { title: string; items: Record<string, { title: string; desc: string }> }
      tokens: { title: string; intro: string; plans: Record<string, string> }
      subscriptions: { title: string; cta: string }
    }
    categories: { title: string; loading: string; error: string }
    form: {
      title: string
      subject: { label: string; placeholder: string; errorRequired: string; errorMaxLen: string }
      description: { label: string; placeholder: string; errorRequired: string; errorMinLen: string }
      submit: string
      submitting: string
      success: string
      errorInvalidCategory: string
      errorGeneric: string
    }
    tickets: {
      title: string
      empty: string
      statuses: { pending: string; solved: string; canceled: string }
      resolvedAt: string
      loadMore: string
    }
  }
}
```

Langues : `fr`, `en`, `es`.

---

### AC12 — Tests

**Backend :**

- Unit : `SupportTicketCategoryModel` — seed idempotent.
- Unit : `IncidentService` — transitions `pending → solved`, `pending → canceled`, `pending → in_progress` autorisées ; `solved → pending` refusée.
- Integration : `GET /v1/help/categories` retourne les catégories actives triées.
- Integration : `POST /v1/help/tickets` crée un ticket `status=pending` avec `category_code` valide.
- Integration : `POST /v1/help/tickets` retourne 422 si `category_code` inconnu.
- Integration : `POST /v1/help/tickets` retourne 422 si `subject` vide.
- Integration : `GET /v1/help/tickets` retourne uniquement les tickets de l'utilisateur connecté.
- Integration : `GET /v1/help/tickets` remonte bien `support_response` et le statut mis à jour après traitement support.
- Non-régression : les tests ops existants sur `GET /v1/support/incidents` ne sont pas impactés.

**Frontend :**

- Test `SupportCategorySelect` : affiche les catégories, sélection d'une catégorie appelle le callback.
- Test `SupportTicketForm` : soumission valide appelle la mutation ; erreurs Zod affichées.
- Test `SupportTicketList` : affiche les tickets ; badge statut correct ; EmptyState si vide.
- Test `UserMenu` / navigation : l'entrée "Aide & Support" est visible, navigable et redirige vers `/help` sans régression sur les autres items du menu.

---

## Tasks / Subtasks

- [x] **T1 — Modèle `SupportTicketCategoryModel` + migration + seed** (AC: 1)
  - [x] Créer `backend/app/infra/db/models/support_ticket_category.py`
  - [x] Exporter dans `backend/app/infra/db/models/__init__.py`
  - [x] Créer la migration Alembic dédiée
  - [x] Créer `backend/scripts/seed_support_categories.py` (idempotent, 7 catégories)

- [x] **T2 — Extension des statuts `IncidentService`** (AC: 5)
  - [x] Ajouter `"pending"`, `"solved"`, `"canceled"` à `VALID_INCIDENT_STATUS`
  - [x] Mettre à jour `ALLOWED_STATUS_TRANSITIONS`
  - [x] Mettre à jour la logique `resolved_at` pour couvrir `"solved"` et `"canceled"`
  - [x] Vérifier que les tests existants passent toujours

- [x] **T3 — Router `/v1/help`** (AC: 2, 3, 4)
  - [x] Créer `backend/app/api/v1/routers/help.py`
  - [x] `GET /v1/help/categories` : lire `SupportTicketCategoryModel` actives
  - [x] `POST /v1/help/tickets` : valider `category_code` vs DB, créer `SupportIncidentModel` `status=pending`
  - [x] `GET /v1/help/tickets` : lister les tickets `user_id=current_user.id`
  - [x] Brancher le router dans `backend/app/main.py`

- [x] **T4 — Page `HelpPage.tsx` avec sections d'aide statiques** (AC: 6)
  - [x] Créer `frontend/src/pages/HelpPage.tsx`
  - [x] Créer `frontend/src/pages/HelpPage.css`
  - [x] Section 1 : fonctionnement de l'app (4 rubriques avec icônes Lucide)
  - [x] Section 2 : tokens / quotas (tableau plans)
  - [x] Section 3 : abonnements + CTA vers `/settings/subscription`
  - [x] Réutiliser `PageLayout` et les patterns visuels existants au lieu d'introduire de nouvelles surfaces ad hoc

- [x] **T5 — Composant `SupportCategorySelect`** (AC: 7)
  - [x] Créer `frontend/src/pages/support/SupportCategorySelect.tsx`
  - [x] Hook API `useHelpCategories` dans `frontend/src/api/help.ts`
  - [x] Loading skeleton, error state, grille de cartes cliquables

- [x] **T6 — Composant `SupportTicketForm`** (AC: 8)
  - [x] Créer `frontend/src/pages/support/SupportTicketForm.tsx`
  - [x] Hook mutation `useCreateHelpTicket` dans `frontend/src/api/help.ts`
  - [x] React Hook Form + Zod : validation conditionnelle subject (`other`) + description (requis, min 20)
  - [x] Gestion succès / erreur avec messages i18n

- [x] **T7 — Composant `SupportTicketList`** (AC: 9)
  - [x] Créer `frontend/src/pages/support/SupportTicketList.tsx`
  - [x] Hook query `useHelpTickets` dans `frontend/src/api/help.ts`
  - [x] Badges statut colorés, date, pagination "Voir plus"

- [x] **T8 — Routing, navigation, i18n** (AC: 10, 11)
  - [x] Ajouter `/help` dans `frontend/src/app/routes.tsx`
  - [x] Vérifier entrée navigation dans sidebar/AppShell vers `/help`
  - [x] Ajouter une entrée `/help` accessible depuis `frontend/src/components/ui/UserMenu/UserMenu.tsx`
  - [x] Créer `frontend/src/i18n/support.ts` (fr/en/es)
  - [x] Exporter depuis `frontend/src/i18n/index.ts`

- [x] **T9 — Tests** (AC: 12)
  - [x] Tests backend unit + integration (fichiers dédiés dans `test_help_api.py`, `test_incident_service_user_statuses.py`)
  - [x] Tests frontend (SupportCategorySelect, SupportTicketForm, SupportTicketList)

---

## Dev Notes

### Réutiliser sans modifier

- `SupportIncidentModel` : **ne pas modifier le schéma**. Le champ `category` (String 32) est assez large pour les codes de catégorie (max 64 — vérifier le sizing ou augmenter à String(64) dans la migration si nécessaire).
- `IncidentService` : étendre `VALID_INCIDENT_STATUS` et les transitions uniquement — ne pas modifier `VALID_INCIDENT_CATEGORY` (legacy ops).
- `SupportOpsPanel` + route `/support` : **inchangés**.
- `frontend/src/api/support.ts` : **inchangé**.
- `UserMenu` / `Header` : enrichir l'existant, ne pas créer un second menu utilisateur parallèle.

### Attention aux points critiques

1. **`category` String(32) vs codes de 64 chars** : le modèle actuel a `String(32)`. Les codes définis (`subscription_problem`, `account_access` = 18 chars max) tiennent dans 32. Vérifier avant d'écrire.

2. **Rate limiting utilisateurs** : sur `POST /v1/help/tickets`, appliquer un rate limit strict (5/heure) pour éviter le spam. Utiliser le pattern `check_rate_limit` existant dans `app.core.rate_limit`.

3. **Audit event** : optionnel au MVP pour la soumission de ticket utilisateur. Si ajouté, utiliser `AuditService.record_event` comme dans `support.py`.

4. **Styles CSS** : utiliser les variables existantes. Vérifier dans `frontend/src/index.css` et `frontend/src/styles/theme.css` avant de définir des nouvelles variables.

5. **React Hook Form + Zod** : déjà utilisés dans le projet (épics 50, 52). Importer depuis les chemins existants. Schémas Zod dans un fichier séparé si possible.

6. **TanStack Query** : les hooks doivent utiliser des query keys stables. Exemple :
   - `["help-categories"]`
   - `["help-tickets", userId]`

7. **Accessibilité navigation** : l'entrée `/help` du `user-menu` doit conserver les conventions d'accessibilité déjà présentes dans `UserMenu.tsx` (rôles ARIA, navigation bouton, focus visible, fermeture du menu après action).

8. **Réutilisation frontend** : avant de créer un style ou composant spécifique au help center, vérifier les éléments déjà disponibles dans `frontend/src/components/ui`, `layouts`, `pages/settings/*` et les patterns de cartes/états de chargement du produit.

9. **Support response** : toute réponse saisie via les flux support ops doit rester visible côté utilisateur dans `/v1/help/tickets`, avec `status` et `resolved_at` cohérents.

### Structure des fichiers à créer

```text
backend/
  app/
    api/v1/routers/help.py           (nouveau)
    infra/db/models/support_ticket_category.py  (nouveau)
  migrations/versions/xxxx_add_support_ticket_categories.py (nouveau)
  scripts/seed_support_categories.py (nouveau)
  tests/
    integration/test_help_api.py     (nouveau)
    unit/test_incident_service_user_statuses.py (nouveau)

frontend/src/
  api/help.ts                        (nouveau)
  i18n/support.ts                    (nouveau)
  pages/
    HelpPage.tsx                     (nouveau)
    HelpPage.css                     (nouveau)
    support/
      SupportCategorySelect.tsx      (nouveau)
      SupportTicketForm.tsx          (nouveau)
      SupportTicketList.tsx          (nouveau)
  tests/
    HelpPage.test.tsx                (nouveau)
```

### Fichiers existants à modifier

```text
backend/app/infra/db/models/__init__.py       (exporter SupportTicketCategoryModel)
backend/app/services/incident_service.py      (étendre VALID_INCIDENT_STATUS + transitions)
backend/app/main.py                           (brancher help router)
frontend/src/app/routes.tsx                   (ajouter route /help)
frontend/src/i18n/index.ts                    (exporter support translations)
```

### Patterns de référence

- Router FastAPI : `backend/app/api/v1/routers/billing.py` (format réponse, rate limit, auth, error handling).
- Modèle SQLAlchemy : `backend/app/infra/db/models/support_incident.py`.
- Hook API frontend : `frontend/src/api/support.ts` (pattern fetch + TanStack Query).
- Page settings : `frontend/src/pages/settings/SubscriptionSettings.tsx` (layout page avec sections).
- Page settings / usage : `frontend/src/pages/settings/UsageSettings.tsx` et `frontend/src/pages/settings/Settings.css` (surfaces, hiérarchie visuelle, feedback states).
- i18n : `frontend/src/i18n/billing.ts` (structure types + translations).
- Formulaire : `frontend/src/pages/ConsultationWizardPage.tsx` (React Hook Form + Zod + étapes).
- Menu utilisateur : `frontend/src/components/ui/UserMenu/UserMenu.tsx` + `frontend/src/components/layout/Header.tsx`.

### References

- Architecture : `_bmad-output/planning-artifacts/architecture.md` — sections Naming Patterns, API Patterns, Frontend Architecture.
- Modèle existant : `backend/app/infra/db/models/support_incident.py`.
- Service existant : `backend/app/services/incident_service.py`.
- Router ops existant : `backend/app/api/v1/routers/support.py`.
- API frontend ops : `frontend/src/api/support.ts`.
- Routes : `frontend/src/app/routes.tsx`.
- i18n navigation : `frontend/src/i18n/navigation.ts`.

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- **[Help API]** Ajout du router utilisateur `backend/app/api/v1/routers/help.py` avec `GET /v1/help/categories`, `POST /v1/help/tickets` et `GET /v1/help/tickets`, protégés par authentification et rate limiting.
- **[Support Categories]** Ajout du modèle `SupportTicketCategoryModel`, des migrations Alembic associées et du seed idempotent `backend/scripts/seed_support_categories.py`.
- **[Incident Statuses]** Extension de `IncidentService` pour supporter les statuts utilisateur `pending`, `solved` et `canceled`, avec transitions et gestion `resolved_at` adaptées.
- **[Help Page]** Création de la page `/help` avec sections d'aide statiques, CTA abonnement, sélection de catégorie, formulaire de ticket et historique des tickets.
- **[User Menu Access]** Ajout de l’entrée `Aide & Support` dans `UserMenu`, sans régression sur les autres entrées du menu utilisateur.
- **[Accessibility Fix]** Les cartes de catégories support sont désormais de vrais boutons focusables et activables au clavier; l’état erreur réutilise `ErrorState`.
- **[Frontend Reuse Fix]** Réalignement des composants support sur les primitives frontend existantes (`PageLayout`, `Button`, `Skeleton`, `EmptyState`, `ErrorState`) avec correction des props `Button`.
- **[Review Fix]** Suppression de la régression introduite dans la navigation globale: l’entrée `/help` n’est plus injectée comme item parasite dans `nav.ts`.
- **[Deprecation Fix]** Remplacement de `status.HTTP_422_UNPROCESSABLE_ENTITY` par `status.HTTP_422_UNPROCESSABLE_CONTENT` dans le router help pour supprimer le warning FastAPI.
- **[Validation]** Vérifications exécutées après implémentation et review: `ruff check` backend ciblé, `pytest` backend ciblé, `npm run lint`, `vitest` ciblé sur `HelpPage`, `UserMenu` et `ui-nav`.
- **[Support Categories Update]** Les catégories utilisateur finales ont été réalignées sur des demandes de support habituelles, avec ajout explicite de `other` et auto-seed au démarrage backend.
- **[Conditional Subject]** Le formulaire support n'affiche un champ objet que pour la catégorie `other`; sinon l'objet est dérivé du label de catégorie et la description reste toujours obligatoire.
- **[Support Response Persistence]** Les tickets utilisateur exposent désormais `support_response` et `updated_at`; le support peut enrichir un ticket et l'utilisateur voit la réponse et le statut mis à jour dans `/help`.
- **[Final Validation]** Vérifications finales exécutées: `pytest tests/integration/test_help_api.py app/tests/integration/test_support_api.py tests/unit/test_incident_service_user_statuses.py -q`, `npm test -- --run src/tests/HelpPage.test.tsx src/tests/UserMenu.test.tsx src/tests/ui-nav.test.ts`, `npm run lint`.

### File List

- `_bmad-output/implementation-artifacts/62-1-page-support-et-help-center-utilisateur.md`
- `backend/app/api/v1/routers/help.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/support_ticket_category.py`
- `backend/app/infra/db/models/support_incident.py`
- `backend/app/main.py`
- `backend/app/api/v1/routers/support.py`
- `backend/app/services/incident_service.py`
- `backend/migrations/versions/d5db148d2557_add_support_ticket_categories_table.py`
- `backend/migrations/versions/707ad78f51ac_add_description_en_and_description_es_.py`
- `backend/migrations/versions/20260401_0065_add_support_response_to_incidents.py`
- `backend/scripts/seed_support_categories.py`
- `backend/tests/integration/test_help_api.py`
- `backend/app/tests/integration/test_support_api.py`
- `backend/tests/unit/test_incident_service_user_statuses.py`
- `frontend/src/api/help.ts`
- `frontend/src/app/routes.tsx`
- `frontend/src/components/ui/UserMenu/UserMenu.tsx`
- `frontend/src/i18n/common.ts`
- `frontend/src/i18n/index.ts`
- `frontend/src/i18n/navigation.ts`
- `frontend/src/i18n/support.ts`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/HelpPage.tsx`
- `frontend/src/pages/support/SupportCategorySelect.tsx`
- `frontend/src/pages/support/SupportTicketForm.tsx`
- `frontend/src/pages/support/SupportTicketList.tsx`
- `frontend/src/tests/HelpPage.test.tsx`
- `frontend/src/tests/UserMenu.test.tsx`
- `frontend/src/tests/ui-nav.test.ts`
- `frontend/src/ui/icons.tsx`
- `frontend/src/ui/nav.ts`
