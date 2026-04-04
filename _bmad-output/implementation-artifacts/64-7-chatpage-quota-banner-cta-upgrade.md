# Story 64.7 — ChatPage : encart quota dynamique + CTA upgrade

Status: todo

## Story

En tant qu'utilisateur free sur la page `/chat`,
je veux voir un encart discret indiquant mes messages restants, le quota total et la date de rechargement,
afin de savoir où j'en suis dans ma consommation et d'être guidé naturellement vers l'upgrade quand je touche ma limite.

## Context

Dépend de **Story 64.5** (hook `useEntitlementSnapshot` disponible).

`ChatPage.tsx` importe déjà `useChatEntitlementUsage` depuis `billing.ts` — ce hook retourne les données de quota chat en temps réel. Cette story crée un composant `ChatQuotaBanner` qui consomme ce hook existant **et** le hint d'upgrade depuis `useUpgradeHint("astrologer_chat")`.

**Règles UX (UX64-3, UX64-4) :**
- Encart discret tant que quota non épuisé (info, pas alerte)
- Quota épuisé → message clair + CTA upgrade immédiatement visible
- Sur mobile, ne pas obstruer la navigation

## Acceptance Criteria

**AC1 — ChatQuotaBanner affiché pour les utilisateurs free avec quota**
**Given** un utilisateur free avec un quota chat restant  
**When** la page `/chat` est rendue  
**Then** un encart affiche : messages restants, quota total, date/heure de rechargement  
**And** l'encart est discret (style informatif, pas alarmiste)

**AC2 — ChatQuotaBanner masqué pour les plans sans quota (unlimited)**
**Given** un utilisateur basic ou premium avec accès illimité  
**When** la page `/chat` est rendue  
**Then** aucun encart quota n'est affiché

**AC3 — État quota épuisé : message clair + CTA upgrade visible**
**Given** un utilisateur free dont le quota est épuisé (`quota_remaining === 0`)  
**When** la page `/chat` est rendue  
**Then** l'encart affiche un message clair indiquant que le quota est atteint  
**And** `<UpgradeCTA featureCode="astrologer_chat" />` est visible et cliquable  
**And** la saisie de message est désactivée ou un indicateur bloquant est visible

**AC4 — Données dynamiques (pas hardcodées)**
**Given** ChatQuotaBanner  
**When** le composant consomme les données  
**Then** `quota_remaining`, `quota_limit`, `window_end` proviennent du hook `useChatEntitlementUsage`  
**And** aucune valeur de quota n'est hardcodée dans le composant

**AC5 — Style CSS conforme au projet**
**Given** le CSS de `ChatQuotaBanner`  
**When** inspecté  
**Then** aucune classe Tailwind n'est utilisée  
**And** les variables CSS du projet sont utilisées (`--text-2`, `--glass-border`, etc.)

**AC6 — Mobile : pas d'obstruction de la navigation**
**Given** viewport mobile  
**When** la page `/chat` est rendue avec `ChatQuotaBanner`  
**Then** l'encart ne recouvre pas `BottomNav`  
**And** la zone de saisie du chat reste accessible

**AC7 — Tests de rendu**
**Given** `frontend/src/tests/chat/ChatComponents.test.tsx` (existant) et un nouveau test  
**When** les tests sont exécutés  
**Then** : rendu avec quota, rendu quota épuisé (CTA visible), rendu masqué pour premium

## Tasks / Subtasks

- [ ] T1 — Créer `ChatQuotaBanner` (AC1, AC2, AC3, AC4, AC5)
  - [ ] T1.1 Créer `frontend/src/features/chat/components/ChatQuotaBanner.tsx`
  - [ ] T1.2 Interface :
    ```tsx
    // ChatQuotaBanner lit directement les hooks — pas de props
    export function ChatQuotaBanner() {
      const { data: entitlementData } = useChatEntitlementUsage()
      const upgradeCTA = <UpgradeCTA featureCode="astrologer_chat" variant="button" />
      // ...
    }
    ```
  - [ ] T1.3 Logique de rendu :
    - Si `entitlementData` est absent ou `access_mode === "unlimited"` → `return null`
    - Si `quota_remaining > 0` → encart informatif discret
    - Si `quota_remaining === 0` → encart alerte + CTA upgrade
  - [ ] T1.4 Formater la date de rechargement depuis `window_end` (utiliser `formatDateTime` depuis `utils/formatDate`)
  - [ ] T1.5 Créer `ChatQuotaBanner.css` avec les styles appropriés

- [ ] T2 — Intégrer `ChatQuotaBanner` dans `ChatPage.tsx` (AC1, AC6)
  - [ ] T2.1 Lire entièrement `frontend/src/pages/ChatPage.tsx`
  - [ ] T2.2 Identifier l'emplacement approprié (en dessous du header, au-dessus du chat window)
  - [ ] T2.3 Importer et insérer `<ChatQuotaBanner />` dans le layout existant
  - [ ] T2.4 Vérifier que le layout mobile n'est pas cassé

- [ ] T3 — Clés i18n pour le banner (AC4)
  - [ ] T3.1 Lire `frontend/src/i18n/billing.ts`
  - [ ] T3.2 Ajouter les clés de traduction :
    - `chatQuota.remaining` → fr: `"{remaining} message(s) restant(s) ce {period}"`, en: `"{remaining} message(s) left this {period}"`
    - `chatQuota.exhausted` → fr: `"Quota atteint — rechargement le {date}"`, en: `"Quota reached — resets on {date}"`
    - `chatQuota.resetDate` → fr: `"Rechargement le {date}"`, en: `"Resets on {date}"`

- [ ] T4 — Tests (AC7)
  - [ ] T4.1 Ajouter dans `frontend/src/tests/chat/ChatComponents.test.tsx` :
    - Test : rendu avec `remaining=3, limit=5` → encart visible et informatif
    - Test : rendu avec `remaining=0` → message alerte + CTA visible
    - Test : rendu avec `access_mode="unlimited"` → `null` (rien rendu)

- [ ] T5 — Validation finale
  - [ ] T5.1 Tester manuellement en mode free (compte de test)
  - [ ] T5.2 `npx vitest run` → 0 erreur

## Dev Notes

### Données disponibles depuis useChatEntitlementUsage

```ts
// Type ChatEntitlementFeatureStatus (billing.ts)
{
  feature_code: "astrologer_chat",
  granted: boolean,
  reason_code: string,
  access_mode: "quota" | "unlimited" | null,
  quota_limit: number | null,
  quota_remaining: number | null,
  usage_states: [{ remaining, exhausted, window_end, ... }]
}
```

Le `access_mode === "quota"` indique que le plan a un quota — afficher le banner. `access_mode === "unlimited"` → masquer.

### Désactivation de la saisie au quota épuisé

Vérifier dans `ChatWindow.tsx` si une prop existe pour désactiver l'input. Si `quota_remaining === 0`, le backend retournera déjà une erreur 429 à l'envoi — s'assurer que le message d'erreur est géré proprement. Le CTA upgrade est affiché en amont pour éviter cette friction.

### Position dans le layout

L'encart doit être positionné entre le `ChatPageHeader` et la liste de conversations / `ChatWindow`. Il ne doit pas être `position: fixed` pour ne pas bloquer le scroll. Utiliser `position: sticky; top: 0; z-index: ...` si un effet d'accroche est souhaité.
