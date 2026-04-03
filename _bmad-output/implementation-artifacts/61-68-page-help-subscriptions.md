# Story 61.68 : Page `/help/subscriptions` — détail des abonnements depuis le catalogue canonique

Status: done

---

## Story

En tant qu'utilisateur authentifié,
je veux accéder à la page `/help/subscriptions` qui présente clairement le contenu de chaque abonnement (fonctionnalités incluses, quotas, prix),
afin de comprendre les différences entre les plans `free`, `basic` et `premium`, et de savoir vers quelle formule me diriger.

---

## Résultat de vérification

La story a été relue contre l'état actuel du projet et contre les stories parentes `61.66`, `61.67`, `62.1` et `62.2`.

Corrections et clarifications apportées dans cette version :

- le scope est confirmé : **nouvel endpoint backend + implémentation frontend** ;
- la dépendance réelle à la story `62.2` est précisée : la route existe déjà et `SubscriptionGuidePage.tsx` est bien un placeholder à remplacer ;
- la page source de vérité pour les quotas est explicitement le **catalogue canonique** (`plan_feature_bindings` + `plan_feature_quotas`), pas des chaînes i18n hardcodées ;
- le comportement des CTA est unifié : la page guide **redirige vers** `/settings/subscription`, elle ne lance pas directement Stripe ;
- les règles CSS sont alignées : les classes existantes peuvent être réutilisées telles quelles, mais **toute nouvelle classe** spécifique à cette page doit être préfixée `help-subscriptions-` ;
- les critères d'acceptation sont reformulés pour être plus testables et moins ambigus.

### Mise à jour post-implémentation

Les points ci-dessous décrivent l'état réellement livré après implémentation et ajustements produit. En cas de contradiction avec la rédaction initiale, **ces éléments prévalent**.

- la page `/help/subscriptions` est bien alimentée par `GET /v1/entitlements/plans` pour le catalogue ;
- la détection du plan courant repose sur `GET /v1/entitlements/me` avec fallback `useBillingSubscription()`, afin de couvrir correctement le plan `free` ;
- le plan `trial` n'est pas affiché à l'utilisateur final ;
- le bouton CTA héro de gestion a été supprimé pour éviter le doublon avec les CTA présents sur les cartes de plans ;
- la carte du plan courant n'affiche plus de bouton et rend un libellé statique `Votre plan actuel` ;
- le contenu éditorial de la page a été enrichi :
  - hero avec `kicker`, `title`, `lead`, `body`
  - panneau latéral `Repères rapides` avec plan courant / recommandé, prix d'entrée et points clés
  - descriptions longues par plan (`free`, `basic`, `premium`)
  - trois sections éditoriales de bas de page : `Comment choisir`, `Comment fonctionnent les tokens ?`, `Vous pouvez changer à tout moment` ;
- les badges de `processing_priority` sont affichés sur les cartes comme information de présentation ;
- les textes marketing affichés sur la page ont été réécrits pour exprimer la promesse produit sans casser l'alignement avec les droits réellement servis par l'API.
- le plan courant ou, à défaut, `basic`, est mis en avant visuellement comme carte vedette ;
- les cartes utilisent un rendu glassmorphism renforcé avec variations de matière selon le plan (`free`, `basic`, `premium`) ;
- le CTA `Comparer les offres` pointe vers `#subscription-plans` avec offset de scroll pour éviter le masquage sous le header fixe ;
- le bloc `Explorer les détails` est livré sous forme de `<details>` structuré en sections `Expérience` et `Fonctionnalités incluses` ;
- les CTA de cartes restent les seules actions de changement de plan ; aucun CTA héro ne duplique cette action ;
- les traductions `fr`, `en`, `es` couvrent les labels de hero, les plans, les quotas, les sections éditoriales et le panneau de détails ;
- les états de focus visibles ont été ajoutés pour les liens, CTA et résumés `<details>` ;
- le fond de page a été durci côté stacking (`isolation`, `z-index`, couches absolues) pour limiter les problèmes de rendu automatisé / capture headless ;
- les cartes éditoriales de bas de page sont alignées en grille, à hauteur homogène, avec neutralisation locale du `margin-top` hérité de `.settings-card + .settings-card`.

---

## Contexte

### Ce qui existe déjà

- La story `62.2` a ajouté la route frontend `/help/subscriptions` dans `frontend/src/app/routes.tsx`.
- La page `frontend/src/pages/SubscriptionGuidePage.tsx` existe déjà mais ne contient qu'un placeholder.
- La story `61.67` a basculé les quotas LLM vers un modèle canonique en tokens, persisté en base.
- La story `61.66` a supprimé les quotas hardcodés côté produit courant et a réaffirmé que les limites doivent venir du catalogue / des endpoints.
- La page `/help` contient déjà un CTA vers `/help/subscriptions`.

### Objectif de cette story

Transformer la page placeholder `/help/subscriptions` en une vraie page d'aide détaillant les plans B2C à partir d'un **catalogue backend dédié**, construit depuis les tables canoniques d'entitlements et les prix `billing_plans`.

Cette page n'est **pas** une page de checkout. C'est une page d'information et d'orientation. Toutes les actions commerciales renvoient vers `/settings/subscription`, qui reste le point d'entrée unique pour la gestion d'abonnement.

### Plans et features attendus (état cible du catalogue)

| Plan | Feature | access_mode | Quotas |
|------|---------|-------------|--------|
| free | natal_chart_short | unlimited | — |
| free | natal_chart_long | disabled | — |
| free | astrologer_chat | disabled | — |
| free | thematic_consultation | disabled | — |
| basic | natal_chart_short | unlimited | — |
| basic | natal_chart_long | quota | 1 interprétation (`lifetime`) |
| basic | astrologer_chat | quota | 1 667 tokens/jour · 12 500/semaine · 50 000/mois |
| basic | thematic_consultation | quota | 20 000 tokens/semaine |
| premium | natal_chart_short | unlimited | — |
| premium | natal_chart_long | quota | 5 interprétations (`lifetime`) |
| premium | astrologer_chat | quota | 50 000 tokens/jour · 375 000/semaine · 1 500 000/mois |
| premium | thematic_consultation | quota | 200 000 tokens/mois |

Prix attendus depuis `billing_plans` :

- `free` : `0`
- `basic` : `9 € / mois`
- `premium` : `29 € / mois`

Si les seeds ou les prix changent plus tard, **la page doit refléter la base**, pas des valeurs copiées dans le frontend.

---

## Acceptance Criteria

### AC1 — Endpoint `GET /v1/entitlements/plans`

Un endpoint authentifié `GET /v1/entitlements/plans` expose le catalogue des plans B2C utilisé par la page `/help/subscriptions`.

Contraintes :

- endpoint protégé par `require_authenticated_user` ;
- seuls les plans B2C actifs sont retournés ;
- ordre des plans imposé : `free`, `basic`, `premium` ;
- ordre des features imposé : `natal_chart_short`, `natal_chart_long`, `astrologer_chat`, `thematic_consultation` ;
- le prix vient de `billing_plans` via `plan_code` ;
- si aucun `billing_plan` n'existe pour un plan donné, alors `monthly_price_cents = 0` et `currency = "EUR"` par défaut.

Contrat attendu :

```json
{
  "data": [
    {
      "plan_code": "free",
      "plan_name": "Free",
      "monthly_price_cents": 0,
      "currency": "EUR",
      "is_active": true,
      "features": [
        {
          "feature_code": "natal_chart_short",
          "feature_name": "Thème natal",
          "is_enabled": true,
          "access_mode": "unlimited",
          "quotas": []
        },
        {
          "feature_code": "astrologer_chat",
          "feature_name": "Chat astrologue",
          "is_enabled": false,
          "access_mode": "disabled",
          "quotas": []
        }
      ]
    }
  ],
  "meta": { "request_id": "..." }
}
```

Le routeur est ajouté dans `backend/app/api/v1/routers/entitlements.py`.

### AC2 — Schémas Pydantic dédiés

Le fichier `backend/app/api/v1/schemas/entitlements.py` est étendu avec des schémas dédiés au catalogue de plans :

- `PlanFeatureQuotaData`
- `PlanFeatureData`
- `PlanCatalogData`
- `PlansCatalogResponse`

Champs attendus :

- `PlanFeatureQuotaData` : `quota_key`, `quota_limit`, `period_unit`, `period_value`, `reset_mode`
- `PlanFeatureData` : `feature_code`, `feature_name`, `is_enabled`, `access_mode`, `quotas`
- `PlanCatalogData` : `plan_code`, `plan_name`, `monthly_price_cents`, `currency`, `is_active`, `features`
- `PlansCatalogResponse` : `data`, `meta`

### AC3 — Hook frontend `useEntitlementsPlans`

Le frontend expose un hook `useEntitlementsPlans()` pour consommer `GET /v1/entitlements/plans`.

Implémentation attendue :

- dans `frontend/src/api/billing.ts` ou `frontend/src/api/entitlements.ts` si ce fichier existe déjà ;
- `useQuery` avec auth header standard du projet ;
- ajout des types TypeScript `PlanFeatureQuota`, `PlanFeature`, `PlanCatalog`.

Le hook ne doit pas dupliquer le pattern réseau existant de `billing.ts`.

### AC4 — La page `SubscriptionGuidePage.tsx` remplace le placeholder

Le contenu placeholder actuel de `frontend/src/pages/SubscriptionGuidePage.tsx` est remplacé par une vraie page.

Structure cible :

```tsx
<PageLayout className="is-settings-page">
  <div className="help-bg-halo" />
  <div className="help-noise" />

  <div className="help-page">
    <section className="help-section help-subscriptions-hero">
      <div className="help-subscriptions-hero-copy">
        <span className="help-subscriptions-hero-kicker">{t.subscriptions.hero.kicker}</span>
        <h1>{t.subscriptions.hero.title}</h1>
        <p className="help-subscriptions-hero-lead">{t.subscriptions.hero.lead}</p>
        <p>{t.subscriptions.hero.body}</p>
        <div className="help-subscriptions-hero-actions">...</div>
      </div>
      <div className="help-subscriptions-hero-panel">...</div>
    </section>

    <section id="subscription-plans" className="help-section help-subscriptions-grid">
      {plans.map((plan) => (
        <PlanCard key={plan.plan_code} plan={plan} isFeatured={...} />
      ))}
    </section>

    <section className="help-section help-subscriptions-editorial">
      <EditorialSection section={t.subscriptions.editorial.howToChoose} />
      <EditorialSection section={{ title: t.subscriptions.tokensExplainer.title, paragraphs: [...] }} />
      <EditorialSection section={t.subscriptions.editorial.flexibility} />
    </section>
  </div>
</PageLayout>
```

États obligatoires :

- chargement : `Skeleton` / `SkeletonGroup`
- erreur : `ErrorState`
- vide : `EmptyState`

La page ne doit contenir **aucun style inline**.

### AC5 — Composant `PlanCard`

Chaque plan est affiché dans une carte dédiée.

Le composant `PlanCard` peut être :

- local à `SubscriptionGuidePage.tsx`, ou
- extrait dans un sous-fichier si la taille de la page le justifie réellement.

Chaque carte affiche :

- le nom du plan ;
- une tagline et une description éditoriale du plan ;
- un éventuel badge `Le plus choisi` quand la carte est vedette mais n'est pas le plan courant ;
- un badge "plan actuel" si `plan.plan_code === userCurrentPlan` ;
- un badge de priorité si `processing_priority` est présent ;
- le prix formaté via `Intl.NumberFormat`, selon le même pattern que `SubscriptionSettings.tsx` ;
- une promesse courte et jusqu'à 3 highlights visibles immédiatement ;
- un bloc repliable `Explorer les détails` ;
- dans le bloc ouvert :
  - un intertitre `Inclus dans {plan}` ;
  - les sections `Expérience` et `Fonctionnalités incluses` ;
  - la liste ordonnée des features ;
- pour chaque feature :
  - état inclus / non inclus ;
  - mode d'accès (`unlimited`, `quota`, `disabled`) ;
  - quotas détaillés quand présents ;
- un CTA unique :
  - plan courant : **aucun bouton**, affichage du libellé `Votre plan actuel` ;
  - autre plan : lien vers `/settings/subscription` avec libellé d'upgrade ou de changement de formule.

Réutilisations obligatoires :

- `.subscription-plan-card`
- `.subscription-plan-card--active`
- `.subscription-plan-card--featured`
- `.subscription-plan-card__badge`
- `.settings-card`
- icônes `Check`, `X` de `lucide-react` pour les features
- `<Link>` de `react-router-dom` pour tous les CTA de navigation

Cette page **ne crée pas** de bouton lançant directement Checkout ou Customer Portal.

### AC6 — Détection du plan courant

La page consomme prioritairement `useEntitlementsSnapshot()` pour récupérer `plan_code` et marquer le plan courant, avec fallback `useBillingSubscription()`.

Contraintes :

- la détection doit fonctionner aussi pour le plan `free` ;
- si `entitlements.plan_code === "none"`, la page peut retomber sur `subscription.plan?.code` ;
- si aucune information d'abonnement n'est disponible, aucun badge "plan actuel" n'est affiché.

### AC7 — Style et CSS sans duplication

Règles CSS :

- pas de style inline ;
- réutiliser d'abord les classes existantes dans `Settings.css`, `HelpPage.css`, `frontend/src/index.css` et `frontend/src/styles/theme.css` ;
- les classes déjà existantes (`subscription-plan-card`, `settings-card`, `help-section`, `help-bg-halo`, `help-noise`, etc.) peuvent être utilisées telles quelles ;
- **toute nouvelle classe spécifique à cette page** doit être préfixée `help-subscriptions-` ;
- la grille de plans repose sur CSS Grid ;
- la section éditoriale de bas de page repose aussi sur CSS Grid avec alignement homogène des cartes ;
- hover limité et cohérent avec le reste de la page ;
- jamais de `transition: all`.

Variables CSS à privilégier :

- `var(--primary)`
- `var(--text-1)`
- `var(--text-2)`
- `var(--glass)`
- `var(--glass-border)`
- `var(--success)`
- `var(--danger)`
- `var(--settings-card-surface)`
- `var(--settings-card-border)`

### AC8 — i18n complète

Le fichier `frontend/src/i18n/support.ts` est étendu avec un namespace `subscriptions`.

Structure attendue :

```typescript
subscriptions: {
  hero: {
    kicker: string
    title: string
    lead: string
    body: string
    cta: string
    compareCta: string
    panelBadge: string
    currentPlanLabel: string
    recommendedPlanLabel: string
    startingFrom: string
    panelPoints: string[]
  },
  includedTitle: string,
  plans: {
    free: { name: string; tagline: string; positioning: string; description: string[] }
    basic: { name: string; tagline: string; positioning: string; description: string[] }
    premium: { name: string; tagline: string; positioning: string; description: string[] }
  },
  priority: {
    low: string
    medium: string
    high: string
  },
  planHighlights: {
    free: string[]
    basic: string[]
    premium: string[]
  },
  features: {
    natal_chart_short: string
    natal_chart_long: string
    astrologer_chat: string
    thematic_consultation: string
  },
  quota: {
    messages_per_week: string
    tokens_per_day: string
    tokens_per_week: string
    tokens_per_month: string
    consultations_per_week: string
    interpretations_lifetime: string
    unlimited: string
    disabled: string
  },
  detailTitles: {
    experience: string
    features: string
  },
  editorial: {
    howToChoose: { title: string; paragraphs: string[] }
    flexibility: { title: string; paragraphs: string[] }
  },
  perMonth: string
  currentPlan: string
  upgradeCta: string
  popularBadge: string
  viewDetails: string
}
```

Langues requises :

- `fr`
- `en`
- `es`

Important :

- les **libellés** sont traduits via i18n ;
- les **valeurs chiffrées** proviennent de l'API, pas des traductions.

### AC9 — Responsive

Rendu attendu :

- mobile : une colonne, CTA pleine largeur ;
- tablette / desktop à partir de `768px` : grille de 3 colonnes pour les plans ;
- les blocs éditoriaux de bas de page restent lisibles, correctement empilés sur mobile et alignés à hauteur homogène sur desktop ;
- les contenus restent lisibles sans overflow horizontal.

### AC10 — Tests frontend

Un fichier de test `frontend/src/tests/SubscriptionGuidePage.test.tsx` couvre au minimum :

- affichage des 3 cartes plans quand `useEntitlementsPlans()` retourne des données ;
- rendu du badge "plan actuel" sur le bon plan ;
- détection correcte du plan `free` comme plan courant ;
- rendu de `ErrorState` en cas d'erreur ;
- rendu de `EmptyState` si l'API retourne une liste vide ;
- affichage du contenu éditorial principal de la page ;
- ouverture du bloc `Explorer les détails` avant assertion du contenu replié ;
- CTA renvoyant vers `/settings/subscription`.

Les mocks réutilisent les patterns déjà présents dans `frontend/src/tests/`, en particulier ceux de `HelpPage.test.tsx`.

---

## Tasks / Subtasks

- [x] **T1 — Backend : schémas Pydantic** (AC: 2)
  - [x] Ajouter `PlanFeatureQuotaData`, `PlanFeatureData`, `PlanCatalogData`, `PlansCatalogResponse` dans `backend/app/api/v1/schemas/entitlements.py`

- [x] **T2 — Backend : endpoint `GET /v1/entitlements/plans`** (AC: 1)
  - [x] Ajouter le handler dans `backend/app/api/v1/routers/entitlements.py`
  - [x] Lire les plans B2C actifs
  - [x] Charger les bindings, features et quotas avec stratégie anti N+1
  - [x] Enrichir avec les prix `billing_plans`
  - [x] Garantir l'ordre stable plans + features

- [x] **T3 — Frontend : types et hook** (AC: 3)
  - [x] Ajouter `PlanFeatureQuota`, `PlanFeature`, `PlanCatalog`
  - [x] Ajouter `useEntitlementsPlans()`

- [x] **T4 — Frontend : i18n** (AC: 8)
  - [x] Étendre `frontend/src/i18n/support.ts` avec `subscriptions.*` en `fr`, `en`, `es`

- [x] **T5 — Frontend : styles** (AC: 7, 9)
  - [x] Vérifier les classes existantes avant toute création
  - [x] Ajouter uniquement les nouvelles règles nécessaires dans `HelpPage.css`
  - [x] Préfixer les nouvelles classes en `help-subscriptions-`

- [x] **T6 — Frontend : page `SubscriptionGuidePage.tsx`** (AC: 4, 5, 6)
  - [x] Remplacer le placeholder par la page réelle
  - [x] Ajouter le composant `PlanCard`
  - [x] Ajouter le panneau hero latéral et le CTA d'ancrage vers `#subscription-plans`
  - [x] Gérer chargement / erreur / vide
  - [x] Brancher le badge de plan courant via `useEntitlementsSnapshot()` avec fallback `useBillingSubscription()`
  - [x] Formater les prix et quotas
  - [x] Pointer tous les CTA vers `/settings/subscription`
  - [x] Retirer le CTA héro dupliqué
  - [x] Ajouter le contenu éditorial long des plans et des sections de bas de page
  - [x] Structurer `Explorer les détails` en sections
  - [x] Mettre en avant le plan courant ou `basic` par défaut

- [x] **T7 — Frontend : tests** (AC: 10)
  - [x] Créer `frontend/src/tests/SubscriptionGuidePage.test.tsx`
  - [x] Ouvrir les panneaux `<details>` dans les tests avant vérification du contenu masqué

---

## Dev Notes

### Fichiers à modifier

- `_bmad-output/implementation-artifacts/61-68-page-help-subscriptions.md`
- `backend/app/api/v1/schemas/entitlements.py`
- `backend/app/api/v1/routers/entitlements.py`
- `frontend/src/api/billing.ts` ou `frontend/src/api/entitlements.ts`
- `frontend/src/i18n/support.ts`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/tests/SubscriptionGuidePage.test.tsx`

### Fichiers à ne pas recréer inutilement

- `frontend/src/app/routes.tsx` : la route `/help/subscriptions` existe déjà
- `frontend/src/pages/SubscriptionGuidePage.tsx` : fichier déjà présent, à remplacer plutôt qu'à dupliquer
- `backend/scripts/seed_product_entitlements.py` : ne pas modifier dans cette story sauf découverte d'incohérence bloquante
- `backend/app/api/v1/routers/billing.py` : l'endpoint doit rester dans `entitlements.py`

### Anti-patterns à éviter

- créer un service backend `PlanCatalogService` uniquement pour encapsuler une lecture simple ;
- dupliquer les labels ou quotas dans le frontend ;
- créer un second point d'entrée commercial parallèle à `/settings/subscription` ;
- réinventer des styles déjà présents dans `Settings.css` ou `HelpPage.css`.

### Modèles DB impliqués

```text
PlanCatalogModel        -> plan_catalog
PlanFeatureBindingModel -> plan_feature_bindings
PlanFeatureCatalogModel -> feature_catalog
PlanFeatureQuotaModel   -> plan_feature_quotas
BillingPlanModel        -> billing_plans
```

### Stratégie backend recommandée

1. Charger les plans B2C actifs.
2. Charger les bindings avec `joinedload` / `selectinload` pour les features et quotas.
3. Construire un lookup de prix depuis `BillingPlanModel`.
4. Recomposer le DTO dans l'ordre imposé.

### Formatage des quotas côté frontend

Le formatage doit être piloté par les données API.

Exemple attendu :

```tsx
const formatQuota = (quota: PlanFeatureQuota, language: string) => {
  const amount = quota.quota_limit.toLocaleString(language === "fr" ? "fr-FR" : "en-US")

  if (quota.quota_key === "tokens" && quota.period_unit === "day") {
    return t.subscriptions.quota.tokens_per_day.replace("{{n}}", amount)
  }
  if (quota.quota_key === "tokens" && quota.period_unit === "week") {
    return t.subscriptions.quota.tokens_per_week.replace("{{n}}", amount)
  }
  if (quota.quota_key === "tokens" && quota.period_unit === "month") {
    return t.subscriptions.quota.tokens_per_month.replace("{{n}}", amount)
  }
  if (quota.period_unit === "lifetime") {
    return t.subscriptions.quota.interpretations_lifetime.replace("{{n}}", String(quota.quota_limit))
  }

  return amount
}
```

### Références utiles

- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/HelpPage.tsx`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/SubscriptionSettings.tsx`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/api/billing.ts`
- `frontend/src/i18n/support.ts`
- `backend/app/api/v1/routers/entitlements.py`
- `backend/app/api/v1/schemas/entitlements.py`
- `backend/scripts/seed_product_entitlements.py`

---

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Review Notes

- Verified backend implementation: updated `GET /v1/entitlements/plans` to always return 4 canonical features (exhaustivity AC1).
- Verified model relationships: added missing relationships in `product_entitlements.py`.
- Verified frontend: fixed price formatting to use i18n language and added translations for period.
- Verified frontend: current plan detection now relies on entitlements first so `free` is handled correctly.
- Verified frontend: hero CTA removed and editorial content expanded to match delivered product copy.
- Verified frontend: premium glass UI refinements, featured plan emphasis, hero side panel, details disclosure, focus states, and editorial cards alignment fixes.
- Verified tests: added comprehensive frontend tests.

### File List

- `backend/app/api/v1/schemas/entitlements.py`
- `backend/app/api/v1/routers/entitlements.py`
- `backend/app/infra/db/models/product_entitlements.py`
- `backend/app/tests/integration/test_entitlements_plans.py`
- `frontend/src/api/billing.ts`
- `frontend/src/i18n/support.ts`
- `frontend/src/pages/SubscriptionGuidePage.tsx`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/tests/SubscriptionGuidePage.test.tsx`
