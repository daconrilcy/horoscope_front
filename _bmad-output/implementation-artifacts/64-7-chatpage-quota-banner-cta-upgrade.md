# Story 64.7 — ChatPage : encart quota dynamique + CTA upgrade

Status: done

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

- [x] T1 — Créer `ChatQuotaBanner` (AC1, AC2, AC3, AC4, AC5)
  - [x] T1.1 Créer `frontend/src/features/chat/components/ChatQuotaBanner.tsx`
  - [x] T1.2 Pas de props — lit `useChatEntitlementUsage()` + `useAstrologyLabels()` directement
  - [x] T1.3 Logique : null si data absent, banner info si remaining>0, banner alerte+CTA si épuisé
  - [x] T1.4 Formatage date via `formatDateTime` depuis `utils/formatDate`
  - [x] T1.5 Créer `ChatQuotaBanner.css` avec variables CSS projet

- [x] T2 — Intégrer `ChatQuotaBanner` dans `ChatPage.tsx` (AC1, AC6)
  - [x] T2.1-T2.4 Inséré après `ChatPageHeader`, avant `SectionErrorBoundary`

- [x] T3 — Clés i18n pour le banner (AC4)
  - [x] T3.1-T3.2 `ChatQuotaMessages` + `getChatQuotaMessages()` ajoutés dans `billing.ts` (fr/en/es)

- [x] T4 — Tests (AC7)
  - [x] T4.1 3 tests ajoutés dans `ChatComponents.test.tsx` : null sans data, info avec quota, alerte épuisé+CTA
  - [x] Fix `ChatPage.test.tsx` : ajout mock `hooks/useEntitlementSnapshot` (regression due à UpgradeCTA)

- [x] T5 — Validation finale
  - [x] T5.1 N/A (test manuel)
  - [x] T5.2 55/55 tests dans ChatComponents.test.tsx ; suite complète : 3 échecs pré-existants uniquement

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

## Dev Agent Record

### File List

- `frontend/src/features/chat/components/ChatQuotaBanner.tsx` — created
- `frontend/src/features/chat/components/ChatQuotaBanner.css` — created
- `frontend/src/pages/ChatPage.tsx` — modified (import + `<ChatQuotaBanner />`)
- `frontend/src/i18n/billing.ts` — modified (`ChatQuotaMessages`, `getChatQuotaMessages`)
- `frontend/src/tests/chat/ChatComponents.test.tsx` — modified (3 tests + mocks)
- `frontend/src/tests/ChatPage.test.tsx` — modified (mock `useEntitlementSnapshot`)

### Implementation Notes

- `ChatQuotaBanner` : composant sans props, lit `useChatEntitlementUsage()` pour les données quota et `useAstrologyLabels()` pour la langue. Retourne `null` si `data` absent (plan unlimited ou loading). Deux états : `.chat-quota-banner--info` (quota restant) et `.chat-quota-banner--exhausted` (quota épuisé, avec `role="alert"` + `UpgradeCTA`).
- La vérification d'épuisement utilise `data.blocked || data.remaining === 0` pour couvrir tous les cas.
- `ChatPage.tsx` : `<ChatQuotaBanner />` inséré entre le `ChatPageHeader` et `SectionErrorBoundary`, position non-fixed pour ne pas obstruer le scroll.
- `billing.ts` : ajout de `ChatQuotaMessages` et `getChatQuotaMessages(lang)` avec traductions fr/en/es sous forme de fonctions interpolées (pas de template strings avec placeholders).
- Fix `ChatPage.test.tsx` : ajout mock `../hooks/useEntitlementSnapshot` car `UpgradeCTA` (dans `ChatQuotaBanner`) appelle `useUpgradeHint` → `fetchEntitlementsSnapshot` non fourni dans le mock billing partiel existant.

### Post-Completion Hardening

- Correction backend du débit `tokens` pour `astrologer_chat` :
  - un premier message Basic dont le coût réel LLM dépasse le quota journalier n'est plus rejeté après génération ;
  - le compteur canonique est maintenant saturé à la limite disponible au lieu de rollbacker toute la transaction ;
  - le message utilisateur et la réponse assistant sont donc bien persistés, puis le message suivant est bloqué normalement avec `chat_quota_exceeded`.
- Correction backend du débit `messages` pour le plan Free :
  - le gate canonique contrôlait bien l'accès avant appel LLM, mais aucun compteur `messages` n'était consommé après un tour réussi ;
  - `ChatGuidanceService` consomme désormais aussi les quotas non-token dans la même transaction que l'enregistrement du message utilisateur et de la réponse assistant ;
  - le comportement attendu est restauré : premier message free autorisé, état weekly à `1/1`, second envoi bloqué avec `quota_key=messages`.
- Correction du paradoxe produit `0 utilisé` + `quota dépassé` :
  - auparavant le quota était vérifié avant appel LLM puis débité après coup, ce qui pouvait annuler toute la transaction ;
  - désormais l'état affiché dans `/chat` reste cohérent avec la réalité du dernier échange.
- Séparation explicite des usages LLM :
  - les interprétations natales journalisent leurs tokens par utilisateur pour l'observabilité ;
  - ces tokens ne consomment plus le quota `astrologer_chat`, réservé aux échanges de chat.

- Hardening backend complémentaire documenté :
  - `backend/app/services/chat_guidance_service.py` prend désormais en charge la consommation transactionnelle des quotas non-token de `astrologer_chat` ;
  - `backend/app/tests/integration/test_chat_api.py` vérifie explicitement le contrat free `messages=1` : premier message accepté, second message refusé en `429`.

### Désactivation de la saisie au quota épuisé

Vérifier dans `ChatWindow.tsx` si une prop existe pour désactiver l'input. Si `quota_remaining === 0`, le backend retournera déjà une erreur 429 à l'envoi — s'assurer que le message d'erreur est géré proprement. Le CTA upgrade est affiché en amont pour éviter cette friction.

### Position dans le layout

L'encart doit être positionné entre le `ChatPageHeader` et la liste de conversations / `ChatWindow`. Il ne doit pas être `position: fixed` pour ne pas bloquer le scroll. Utiliser `position: sticky; top: 0; z-index: ...` si un effet d'accroche est souhaité.
