# Story 60.24 : Refactorisation des pages `/settings` — suppression liens sidebar, choix astrologue par défaut, refonte subscription/usage/style premium

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

En tant qu'utilisateur authentifié naviguant dans les paramètres de l'application,
Je veux des pages `/settings` épurées, cohérentes visuellement avec le reste de l'app premium,
Afin de pouvoir gérer facilement mon astrologue par défaut, consulter mes plans disponibles et suivre ma consommation.

## Acceptance Criteria

### AC1 — Nettoyage de la sidebar

1. Les entrées `profile` (vers `/settings`) et `privacy` (vers `/privacy`) sont **retirées** de la liste `navItems` dans `frontend/src/ui/nav.ts`.
2. La sidebar en mode `expanded` ne propose plus de lien vers `/settings/account` ni vers `/privacy`.
3. L'accès aux paramètres reste possible via d'autres entrées de navigation (bouton profil dans la topbar, ou lien dans le footer si existant).
4. Les pages `/settings/*` et `/privacy` restent accessibles par URL directe (pas de suppression de routes).

### AC2 — Remplacement du sélecteur de style par un astrologue par défaut

5. La section « Style d'astrologue » dans `AccountSettings.tsx` est **remplacée** par une section « Astrologue par défaut ».
6. La nouvelle section affiche la liste des astrologues réels (issus de `useAstrologers()`), avec leur avatar, nom et style.
7. L'utilisateur peut sélectionner un astrologue comme défaut en cliquant sur sa card (pas de radio button visible — la card entière est cliquable).
8. La sélection est persistée via `PATCH /v1/users/me/settings` avec le champ `default_astrologer_id` (string UUID ou `null`).
9. Le backend expose et persiste le champ `default_astrologer_id` dans `UserSettings` :
   - Ajout du champ dans le modèle Pydantic `UserSettings`
   - Migration DB : ajout de la colonne `default_astrologer_id` (nullable) dans la table `user_settings`
   - L'endpoint `GET /v1/users/me/settings` retourne ce champ
   - L'endpoint `PATCH /v1/users/me/settings` accepte ce champ
10. L'option « Automatique » (sélection aléatoire, `null`) est disponible comme première card de la grille.
11. La card sélectionnée est visuellement mise en évidence (bordure colorée, fond teinté, check mark ou badge « Sélectionné »).
12. Le feedback de sauvegarde (enregistrement… / sauvegardé ✓ / erreur) est affiché sous la grille.

### AC3 — Indicateur « Astrologue par défaut » sur les pages astrologues

13. Sur la page liste `/astrologers`, l'astrologue marqué comme défaut affiche un badge « Votre défaut » visible sur sa card.
14. Sur la page profil `/astrologers/:id`, si cet astrologue est le défaut de l'utilisateur, un badge distinct s'affiche dans la zone `profile-badge-row` (à côté du badge provider type existant).
15. Sur la page profil `/astrologers/:id`, un bouton « Définir par défaut » (ou « Retirer comme défaut » s'il l'est déjà) est présent dans la section `profile-final-cta`, en dessous des CTAs principaux.
16. Ce bouton appelle `PATCH /v1/users/me/settings` avec `{ default_astrologer_id: "<id>" }` (ou `null` pour retirer).
17. L'état de ce bouton est synchronisé via React Query (invalidation du cache `["user-settings"]` après mutation réussie).

### AC4 — Refonte de la page `/settings/subscription`

18. La page `/settings/subscription` affiche tous les plans disponibles (pas seulement le plan actif).
19. Le plan actuellement actif de l'utilisateur est mis en évidence visuellement (badge « Actif », bordure dorée/violette accentuée).
20. Une section « Acheter des crédits » est présente avec bouton désactivé (backend non encore implémenté) et texte explicatif.
21. Les plans affichés correspondent au minimum aux plans existants (`basic-entry`, `premium-unlimited`) avec labels lisibles, description courte, et limite de messages.
22. La page ne repose plus sur le composant `BillingPanel` brut : une UI dédiée et premium est créée dans `SubscriptionSettings.tsx`.
23. Tout le style est dans `Settings.css` (aucun style inline).

### AC5 — Vérification et stabilisation de `/settings/usage`

24. La page `/settings/usage` affiche correctement les crédits consommés, la limite, les crédits restants et la date de réinitialisation.
25. L'API `GET /v1/billing/quota` est appelée correctement et les données s'affichent sans erreur avec backend actif.
26. En cas d'erreur (réseau, 401, 5xx), le message d'erreur traduit s'affiche correctement.
27. La barre de progression utilise le pattern CSS `--usage-progress` (custom property) déjà en place, avec `transition` fluide.

### AC6 — Alignement visuel premium de toutes les pages `/settings`

28. Les pages settings héritent exactement du système visuel de `AstrologerProfilePage.css` :
    - Fond fixe avec halos radiaux + bruit SVG (même technique que `.profile-bg-halo` / `.profile-noise`)
    - CSS local variables sur le container : card surface, card border, card shadow, text heading/body/muted
    - Cards en glass-morphism : `backdrop-filter: blur(16px)`, `border-radius: 26px`, surface `rgba(255,255,255,0.62–0.76)`, `border: 1px solid rgba(205,217,240,0.72)`
    - Titres de section en Cormorant Garamond avec underline pseudo-élément (barre de 3px, 46px de large, gradient violet/doré)
    - Badges/pills en border-radius 999px, fond glass, bordure douce
29. Le fichier `frontend/src/pages/settings/Settings.css` centralise tout le CSS des trois pages settings.
30. **Aucun style inline** dans les composants React settings — tout dans `.css`.
31. Les onglets `SettingsTabs` sont stylisés avec le même traitement pill/glass que les boutons de navigation du profil astrologue.

---

## Tasks / Subtasks
- [ ] [ ] Task: 1. Sidebar — Retrait des liens (AC1)

  - [ ] **Fichier :** `frontend/src/ui/nav.ts`
  - [ ] Supprimer les entrées à clé `profile` et `privacy` du tableau `navItems`

  - [ ] [ ] Task: 2. Backend — Extension UserSettings (AC2)

  - [ ] **Fichiers backend :**
  - [ ] Modèle ORM et schéma Pydantic : ajouter `default_astrologer_id: str | None = None`
  - [ ] Migration Alembic : `ADD COLUMN default_astrologer_id VARCHAR(64) NULL`
  - [ ] Endpoint `GET /v1/users/me/settings` : exposer le champ
  - [ ] Endpoint `PATCH /v1/users/me/settings` : accepter et persister le champ

**Types frontend :**
  - [ ] `frontend/src/types/user.ts` : `UserSettings { astrologer_profile: string; default_astrologer_id: string | null }`

  - [ ] [ ] Task: 3. Nouveau hook useUserSettings (AC2, AC3)

  - [ ] **Fichier :** `frontend/src/api/userSettings.ts`
```ts
export function useUserSettings() {
  return useQuery({ queryKey: ["user-settings"], queryFn: fetchUserSettings })
}
export function useUpdateUserSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: patchUserSettings,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["user-settings"] }),
  })
}
```

  - [ ] [ ] Task: 4. AccountSettings — Sélecteur d'astrologue par défaut (AC2)

  - [ ] **Fichier :** `frontend/src/pages/settings/AccountSettings.tsx`
  - [ ] Supprimer `ASTROLOGER_STYLES`, `astrologer-style-section`, tous les styles inline
  - [ ] Ajouter `useAstrologers()` + `useUserSettings()` + `useUpdateUserSettings()`
  - [ ] Rendre une grille `.default-astrologer-grid` avec :
  - Une card « Automatique » (id null)
  - Une card par astrologue (avatar, nom, style)
  - [ ] La card active porte la classe `.default-astrologer-option--selected`
  - [ ] Au clic → `updateSettings.mutate({ default_astrologer_id: id })`
  - [ ] Feedback via `updateSettings.isPending / isSuccess / isError`

  - [ ] [ ] Task: 5. Pages astrologues — Badge et bouton défaut (AC3)

  - [ ] **Fichier :** `frontend/src/pages/AstrologersPage.tsx`
  - [ ] Ajouter `useUserSettings()` pour lire `default_astrologer_id`
  - [ ] Passer la prop `isDefault={astrologer.id === settings?.default_astrologer_id}` à chaque card dans `AstrologerGrid`
  - [ ] La card affiche le badge `.astrologer-default-badge` si `isDefault`

  - [ ] **Fichier :** `frontend/src/pages/AstrologerProfilePage.tsx`
  - [ ] Ajouter `useUserSettings()` + `useUpdateUserSettings()`
  - [ ] Dans `profile-badge-row` : badge `.profile-default-badge` si c'est le défaut
  - [ ] Dans `profile-final-cta` : bouton secondaire « Définir par défaut » / « Retirer comme défaut »

  - [ ] [ ] Task: 6. SubscriptionSettings — Refonte premium (AC4)

  - [ ] **Fichier :** `frontend/src/pages/settings/SubscriptionSettings.tsx`
  - [ ] Supprimer `<BillingPanel />`
  - [ ] Ajouter `useBillingSubscription()` pour connaître le plan actif
  - [ ] Définir les plans en dur (en attendant un endpoint `/v1/billing/plans`) :
  ```ts
  const PLANS = [
    { code: null,                label: "Gratuit",        limit: "5 msg/jour",   price: "0 €" },
    { code: "basic-entry",       label: "Basic",          limit: "50 msg/jour",  price: "9 €/mois" },
    { code: "premium-unlimited", label: "Premium",        limit: "1000 msg/jour",price: "29 €/mois" },
  ]
  ```
  - [ ] Rendre une grille `.subscription-plans-grid` avec 3 cards `.subscription-plan-card`
  - [ ] La card active porte `.subscription-plan-card--active`
  - [ ] Section `.subscription-credits-section` avec bouton désactivé

  - [ ] [ ] Task: 7. Settings.css — Style premium (AC6)

  - [ ] **Fichier à créer :** `frontend/src/pages/settings/Settings.css`

---

## Dev Notes
### Contexte Technique
### Architecture actuelle

**Sidebar** (`frontend/src/ui/nav.ts`) :
- `navItems` contient les items `profile` (vers `/settings`) et `privacy` (vers `/privacy`)
- Ces deux entrées sont visibles dans `app-sidebar app-sidebar--expanded`

**Paramètres compte** (`frontend/src/pages/settings/AccountSettings.tsx`) :
- Section `astrologer-style-section` avec labels radio sur 5 styles hardcodés (standard, védique, humaniste, karmique, psychologique)
- Sauvegarde via `PATCH /v1/users/me/settings` → champ `astrologer_profile`
- Nombreux styles inline dans le JSX → à migrer vers CSS
- Types dans `frontend/src/types/user.ts` → `UserSettings { astrologer_profile: string }`

**API settings** :
- `GET /v1/users/me/settings` → `{ data: { astrologer_profile: string }, meta: { request_id } }`
- `PATCH /v1/users/me/settings` → body `{ astrologer_profile?: string }`

**Astrologues** :
- `useAstrologers()` dans `frontend/src/api/astrologers.ts` → liste `Astrologer[]`
- Type `Astrologer` : `{ id, name, first_name, last_name, provider_type, avatar_url?, specialties, style, bio_short }`

**Subscription** (`frontend/src/pages/settings/SubscriptionSettings.tsx`) :
- Délègue tout à `BillingPanel` (composant admin/dev non premium)
- `BillingPanel` : utilise `useTranslation("admin").b2b.billing_v2`, UI de debug

**Usage** (`frontend/src/pages/settings/UsageSettings.tsx`) :
- `useBillingQuota()` → `{ consumed, limit, remaining, reset_at? }`
- Fonctionnel mais style non aligné

**Référence visuelle principale** : `AstrologerProfilePage.css`
- Variables locales CSS sur `.astrologer-profile-container`
- Background : `.profile-bg-halo` (fixed, z-index:-1) + `.profile-noise`
- Cards : `.profile-metrics-bar`, `.profile-mission-card`, `.specialties-card`
- Titres : `.profile-section-title` + `.profile-section-title--underlined`
- Page layout override : `.is-astrologer-profile-page`

---

### Spécification CSS Détaillée
— Settings.css

L'objectif est une cohérence pixel-perfect avec `AstrologerProfilePage.css`. Toutes les valeurs ci-dessous sont directement issues ou dérivées de ce fichier de référence.

### 7.1 — Variables locales CSS (sur le container)

Scoper les variables sur `.settings-container` (même principe que `.astrologer-profile-container`) :

```css
.settings-container {
  /* Palette — miroir du profil astrologue, accent violet au lieu du bleu */
  --settings-purple:        #866cd0;          /* = var(--primary) de l'app */
  --settings-purple-soft:   rgba(134, 108, 208, 0.12);
  --settings-purple-border: rgba(134, 108, 208, 0.28);
  --settings-gold:          #d59a39;          /* = --profile-gold */
  --settings-gold-soft:     rgba(213, 154, 57, 0.16);
  --settings-gold-border:   rgba(213, 154, 57, 0.28);

  /* Cards — copié de AstrologerProfilePage.css */
  --settings-card-surface:        rgba(255, 255, 255, 0.62);
  --settings-card-surface-strong: rgba(255, 255, 255, 0.76);
  --settings-card-border:         rgba(205, 217, 240, 0.72);
  --settings-card-shadow:         0 22px 60px rgba(132, 150, 190, 0.16);
  --settings-card-shadow-soft:    0 16px 42px rgba(132, 150, 190, 0.12);

  /* Texte — copié de AstrologerProfilePage.css */
  --settings-text-heading: #24334d;
  --settings-text-body:    #4f5f78;
  --settings-text-muted:   #7f8da4;

  /* Layout */
  position: relative;
  max-width: 860px;
  margin: 0 auto;
  padding: 24px 24px 96px;
  box-sizing: border-box;
}
```

### 7.2 — Override page layout (même pattern que .is-astrologer-profile-page)

```css
.is-settings-page {
  width: 100% !important;
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
}

.is-settings-page .page-layout__main {
  padding: 0 !important;
}
```

> **Note d'implémentation** : Pour appliquer cette classe, `SettingsPage.tsx` doit passer `className="is-settings-page"` à `<PageLayout>` (ou `<SettingsLayout>` doit l'accepter et le propager). Vérifier la chaîne de props avant d'appliquer.

### 7.3 — Fond (background halos + bruit)

Même technique que `.profile-bg-halo` / `.profile-noise` dans `AstrologerProfilePage.css` — le fond est `position: fixed` donc il couvre toute la page sans affecter le scroll. Adapter les couleurs vers violet/lavande (thème settings) plutôt que bleu ciel (thème profil astrologue) :

```css
.settings-bg-halo,
.settings-noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
}

.settings-bg-halo {
  background:
    radial-gradient(circle at 10% 16%, rgba(171, 148, 255, 0.34) 0%, transparent 28%),
    radial-gradient(circle at 80% 12%, rgba(190, 170, 255, 0.22) 0%, transparent 26%),
    radial-gradient(circle at 55% 80%, rgba(241, 218, 168, 0.20) 0%, transparent 30%),
    linear-gradient(180deg, #fdfcff 0%, #f7f4ff 48%, #f0f5ff 100%);
}

.settings-noise {
  opacity: 0.028;                /* = même opacité que profile-noise */
  mix-blend-mode: soft-light;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.58' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}
```

Ces deux éléments sont rendus dans `SettingsPage.tsx` juste après l'ouverture du JSX principal (avant `<SettingsLayout>`), comme `.profile-bg-halo` dans `AstrologerProfilePage`.

### 7.4 — Cards en glass-morphism

Classe de base `.settings-card` — reprend exactement `.profile-metrics-bar` / `.specialties-card` :

```css
.settings-card {
  background: var(--settings-card-surface-strong);
  border: 1px solid var(--settings-card-border);
  border-radius: 26px;                           /* = profile cards */
  box-shadow: var(--settings-card-shadow);
  backdrop-filter: blur(16px);                   /* = profile blur */
  padding: 28px 32px;
  position: relative;
  z-index: 1;
}

.settings-card + .settings-card {
  margin-top: 20px;
}
```

Variante plus légère pour les sous-sections internes :

```css
.settings-card--soft {
  background: var(--settings-card-surface);
  box-shadow: var(--settings-card-shadow-soft);
  border-radius: 22px;
  padding: 22px 26px;
}
```

Variante accentuée pour les cards "mission / info importantes" — reprend `.profile-mission-card` :

```css
.settings-card--accent {
  background: linear-gradient(180deg, rgba(229, 224, 255, 0.86) 0%, rgba(218, 210, 255, 0.72) 100%);
  border: 1px solid var(--settings-purple-border);
  border-radius: 22px;
  box-shadow: var(--settings-card-shadow-soft);
}
```

### 7.5 — Titres de section

Même traitement que `.profile-section-title` + `.profile-section-title--underlined` :

```css
.settings-section-title {
  margin: 0 0 18px;
  color: var(--settings-text-heading);
  font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif;
  font-size: clamp(1.6rem, 2.2vw, 2rem);         /* légèrement plus petit que profil */
  line-height: 1.05;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Variante avec barre décorative (= --underlined dans profil) */
.settings-section-title--decorated {
  position: relative;
  padding-bottom: 14px;
}

.settings-section-title--decorated::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  width: 46px;                                   /* = profile-section-title--underlined */
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--settings-purple) 0%, rgba(134, 108, 208, 0.4) 100%);
  /* La barre est violette (settings) au lieu de dorée (profil astrologue) */
}
```

### 7.6 — Onglets SettingsTabs

Remplacer le style actuel par le même traitement pill/glass que `.profile-back-btn` dans `AstrologerProfilePage.css` :

```css
.settings-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.settings-tab {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 0 20px;
  border-radius: 999px;                          /* = profile-back-btn */
  border: 1px solid rgba(197, 211, 233, 0.86);   /* = profile-back-btn */
  background: rgba(255, 255, 255, 0.68);         /* = profile-back-btn */
  box-shadow: 0 10px 24px rgba(132, 150, 190, 0.10); /* = profile */
  color: var(--settings-text-body);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition:
    color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    background 0.18s ease;
}

.settings-tab:hover {
  color: var(--settings-purple);
  border-color: rgba(163, 143, 220, 0.88);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 14px 28px rgba(132, 150, 190, 0.14);
}

.settings-tab--active {
  background: var(--settings-purple);
  border-color: var(--settings-purple);
  color: #fff;
  box-shadow: 0 10px 28px rgba(134, 108, 208, 0.28);
}

.settings-tab--active:hover {
  background: #7460bb;
  border-color: #7460bb;
  color: #fff;
}
```

### 7.7 — Séparateurs de section

Même traitement que les bordures internes du profil :

```css
.settings-divider {
  height: 1px;
  background: rgba(195, 206, 225, 0.72);         /* = metric-card separator */
  margin: 24px 0;
  border: none;
}
```

### 7.8 — Sélecteur d'astrologue par défaut (AccountSettings)

```css
.default-astrologer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

/* Card sélectionnable — reprend le style .profile-meta-pill étendu en bloc */
.default-astrologer-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 18px 16px;
  border-radius: 18px;
  border: 1px solid var(--settings-card-border);
  background: var(--settings-card-surface);
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition:
    border-color 0.18s ease,
    background 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.14s ease;
  text-align: center;
}

.default-astrologer-option:hover {
  border-color: rgba(163, 143, 220, 0.64);
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 12px 32px rgba(134, 108, 208, 0.10);
  transform: translateY(-1px);
}

/* État sélectionné — accentuation violette identique aux cards actives du site */
.default-astrologer-option--selected {
  border: 2px solid var(--settings-purple);
  background: var(--settings-purple-soft);
  box-shadow: 0 14px 38px rgba(134, 108, 208, 0.16);
}

/* Avatar circulaire — même style que .profile-hero-avatar en petit */
.default-astrologer-option__avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  object-position: center 28%;
  border: 1px solid var(--settings-card-border);
  box-shadow: 0 6px 18px rgba(111, 135, 166, 0.16);
  flex-shrink: 0;
}

.default-astrologer-option__avatar--placeholder {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(241, 237, 255, 0.96) 0%, rgba(221, 212, 250, 0.94) 100%);
  border: 1px solid var(--settings-purple-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--settings-purple);
  font-size: 22px;
}

.default-astrologer-option__name {
  color: var(--settings-text-heading);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
}

.default-astrologer-option__style {
  color: var(--settings-text-muted);
  font-size: 12px;
  line-height: 1.3;
}

/* Badge "Sélectionné" sur la card active */
.default-astrologer-option__check {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--settings-purple);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

/* Badge "Par défaut" affiché sur les cards dans /astrologers — style = profile-provider-badge */
.astrologer-default-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid var(--settings-purple-border);
  color: var(--settings-purple);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

/* Badge "Par défaut" dans profile-badge-row de AstrologerProfilePage */
.profile-default-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid var(--settings-purple-border, rgba(134, 108, 208, 0.28));
  color: var(--settings-purple, #866cd0);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  box-shadow: 0 8px 20px rgba(134, 108, 208, 0.10);
  white-space: nowrap;
}
```

### 7.9 — Plans d'abonnement (SubscriptionSettings)

```css
.subscription-plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

/* Card plan — même base que .settings-card */
.subscription-plan-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 24px 22px;
  border-radius: 22px;
  border: 1px solid var(--settings-card-border);
  background: var(--settings-card-surface);
  backdrop-filter: blur(16px);
  box-shadow: var(--settings-card-shadow-soft);
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

/* Plan actif — reprend le traitement bordure accentuée des cards actives dans l'app */
.subscription-plan-card--active {
  border: 2px solid var(--settings-gold);
  background: linear-gradient(180deg, rgba(255, 250, 243, 0.92) 0%, rgba(255, 247, 233, 0.82) 100%);
  box-shadow:
    var(--settings-card-shadow),
    0 0 0 1px rgba(213, 154, 57, 0.16);
}

.subscription-plan-card__name {
  color: var(--settings-text-heading);
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.subscription-plan-card__limit {
  color: var(--settings-text-muted);
  font-size: 13px;
}

.subscription-plan-card__price {
  color: var(--settings-text-heading);
  font-size: 22px;
  font-weight: 700;
}

/* Badge "Actif" — style = .step-number (cercle numéroté du profil), adapté en pill */
.subscription-plan-card__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 999px;
  background: linear-gradient(180deg, #f6d28a 0%, #ebb25a 100%);
  box-shadow: 0 8px 22px rgba(214, 154, 57, 0.18);
  color: #79521a;
  font-size: 12px;
  font-weight: 700;
  align-self: flex-start;
}

/* Section crédits */
.subscription-credits-section {
  margin-top: 28px;
  padding: 24px 26px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(229, 224, 255, 0.70) 0%, rgba(218, 210, 255, 0.55) 100%);
  border: 1px solid var(--settings-purple-border);
  box-shadow: var(--settings-card-shadow-soft);
}

.subscription-credits-section__title {
  margin: 0 0 8px;
  color: var(--settings-text-heading);
  font-size: 16px;
  font-weight: 700;
}

.subscription-credits-section__desc {
  margin: 0 0 16px;
  color: var(--settings-text-muted);
  font-size: 14px;
  line-height: 1.6;
}
```

### 7.10 — Usage stats (UsageSettings)

```css
/* Grille des stats — reprend .profile-metrics-bar sans les séparateurs verticaux */
.usage-stats-premium {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0;
  background: var(--settings-card-surface-strong);
  border: 1px solid var(--settings-card-border);
  border-radius: 22px;
  box-shadow: var(--settings-card-shadow);
  backdrop-filter: blur(16px);
  overflow: hidden;
  margin-bottom: 20px;
}

.usage-stat-item {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 22px 24px;
}

/* Séparateur vertical interne — = .metric-card + .metric-card::before */
.usage-stat-item + .usage-stat-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 20px;
  bottom: 20px;
  width: 1px;
  background: rgba(195, 206, 225, 0.9);
}

.usage-stat-label {
  color: var(--settings-text-muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.usage-stat-value {
  color: var(--settings-text-heading);
  font-size: 24px;                               /* = .metric-value */
  font-weight: 700;
  line-height: 1;
}

/* Barre de progression — même variable custom property que l'existant, meilleur style */
.usage-progress-bar {
  height: 8px;
  border-radius: 999px;
  background: rgba(195, 206, 225, 0.5);
  overflow: hidden;
  position: relative;
}

.usage-progress-fill {
  height: 100%;
  width: calc(var(--usage-progress, 0) * 1%);
  border-radius: 999px;
  background: linear-gradient(90deg, var(--settings-purple) 0%, rgba(134, 108, 208, 0.7) 100%);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 7.11 — Feedback de sauvegarde

```css
/* Texte de feedback inline (saving / saved / error) */
.settings-save-feedback {
  min-height: 20px;
  font-size: 13px;
  margin-top: 10px;
}

.settings-save-feedback--saving {
  color: var(--settings-text-muted);
}

.settings-save-feedback--success {
  color: #3a8f5e;                              /* vert succès cohérent avec var(--success) */
}

.settings-save-feedback--error {
  color: #c0392b;                              /* rouge erreur cohérent avec var(--danger) */
}
```

### 7.12 — Responsive mobile (max-width: 640px)

```css
@media (max-width: 640px) {
  .settings-container {
    padding: 16px 16px 80px;
  }

  .default-astrologer-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .subscription-plans-grid {
    grid-template-columns: 1fr;
  }

  .usage-stats-premium {
    grid-template-columns: repeat(2, 1fr);
  }

  .usage-stat-item + .usage-stat-item::before {
    display: none;
  }

  .settings-tabs {
    gap: 8px;
  }

  .settings-tab {
    font-size: 13px;
    padding: 0 14px;
    min-height: 38px;
  }
}
```

---

### Tests & Quality
- [ ] `AccountSettings` : sélection d'un astrologue → appel PATCH avec `default_astrologer_id`
- [ ] `AccountSettings` : sélection « Automatique » → appel PATCH avec `default_astrologer_id: null`
- [ ] `AstrologerProfilePage` : bouton « Définir par défaut » → appel PATCH + invalide cache `["user-settings"]`
- [ ] `SubscriptionSettings` : plan actif affiché avec classe `--active`
- [ ] Backend : `PATCH /v1/users/me/settings` accepte et persiste `default_astrologer_id`
- [ ] Backend : `GET /v1/users/me/settings` retourne `default_astrologer_id`

---

### Developer Guardrails & Learnings
- **From Story 60-23**: Align style strictly with AstrologerProfilePage.css and use the .wizard-astrologer-card / .astrologer-default-badge design patterns to stay DRY.
- **Rétrocompatibilité** : Le champ `astrologer_profile` reste dans la DB et l'API (non supprimé). Il peut servir de fallback dans le moteur IA si `default_astrologer_id` est null. Aucune migration de données existantes nécessaire.
- **CSS inline → CSS classes** : `AccountSettings.tsx` contient de nombreux styles inline à migrer vers les nouvelles classes. Ce nettoyage est **obligatoire** dans cette story (cf. règle projet CLAUDE.md).
- **Plans hardcodés** : Les données des plans disponibles sont définies en constante frontend pour cette story. Laisser un `// TODO: replace with GET /v1/billing/plans` dans le code.
- **Crédits** : Le bouton d'achat de crédits est rendu `disabled` avec `title="Bientôt disponible"`.
- **Sidebar** : La suppression des items de la sidebar ne supprime pas les routes React Router.
- **Font Cormorant Garamond** : Vérifier que la font est bien chargée dans `index.html` ou `index.css` avant de l'utiliser dans les titres settings (elle est déjà utilisée dans `AstrologerProfilePage.css`).

### Project Structure Notes
#### Fichiers Modifiés ou Créés
| Fichier | Action |
|---------|--------|
| `frontend/src/ui/nav.ts` | Modifier — supprimer items `profile` et `privacy` |
| `frontend/src/types/user.ts` | Modifier — ajouter `default_astrologer_id: string \| null` |
| `frontend/src/api/userSettings.ts` | Créer — hooks `useUserSettings`, `useUpdateUserSettings` |
| `frontend/src/pages/settings/AccountSettings.tsx` | Modifier — remplacer section style par sélecteur astrologue, supprimer tous les styles inline |
| `frontend/src/pages/settings/SubscriptionSettings.tsx` | Modifier — UI premium, remplacer BillingPanel |
| `frontend/src/pages/settings/UsageSettings.tsx` | Modifier — alignement visuel premium, supprimer styles inline |
| `frontend/src/pages/settings/Settings.css` | Créer — toute la spécification CSS ci-dessus |
| `frontend/src/layouts/SettingsLayout.tsx` | Modifier — rendre les halos de fond + accepter className is-settings-page |
| `frontend/src/components/settings/SettingsTabs.tsx` | Modifier — utiliser les nouvelles classes `.settings-tab` |
| `frontend/src/pages/AstrologersPage.tsx` | Modifier — badge « Par défaut » sur la card |
| `frontend/src/pages/AstrologerProfilePage.tsx` | Modifier — badge + bouton « Définir par défaut » |
| `frontend/src/i18n/settings.ts` | Modifier — nouveaux libellés (astrologue défaut, plans, crédits) |
| Backend modèle + schéma | Modifier — ajouter `default_astrologer_id` |
| Migration Alembic | Créer — `ADD COLUMN default_astrologer_id` |

---

### References
- Story 60.22 (done) : `AstrologerProfilePage.css` — source du style de référence (valeurs exactes réutilisées)
- Story 60.23 (done) : patterns API consultations comme référence d'architecture hooks
- Backend `useAstrologers()` + `useBillingSubscription()` + `useBillingQuota()` : déjà implémentés

---

## Dev Agent Record

### Agent Model Used
Antigravity (Gemini 2.5 Pro)

### Debug Log References
- Reviewed and aligned via mad-create-story workflow. Mapped custom headings to standard template.

### Completion Notes List
- Ensured strict CSS isolation without inline styling.
- Mapped existing AccountSettings implementation instructions to tasks.

### File List
- _bmad-output/implementation-artifacts/60-24-refactorisation-settings-astrologue-defaut-abonnements.md
- ackend/app/infra/db/models/user_settings.py
- rontend/src/api/userSettings.ts
- rontend/src/pages/settings/Settings.css
