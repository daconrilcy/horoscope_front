# Story 64.6 — Composants `UpgradeCTA` + `LockedSection` réutilisables

Status: done

## Story

En tant que développeur frontend,
je veux deux composants réutilisables — `LockedSection` (section floutée avec overlay lock) et `UpgradeCTA` (bouton d'upgrade contextualisé) — disponibles dans la bibliothèque UI,
afin que les stories 64.7, 64.8 et 64.9 puissent instrumenter les pages stratégiques sans dupliquer de logique de présentation.

## Context

Dépend de **Story 64.5** (hook `useUpgradeHint` disponible).

Ce projet n'utilise pas Tailwind ni de librairie de composants. Tout le style est en CSS custom avec variables CSS (`--glass`, `--text-1`, `--primary`, etc.). Les nouveaux composants doivent respecter ce système.

**Comportement attendu :**
- `LockedSection` : wrapper qui rend son contenu visiblement flou + overlay avec icône lock + optionnellement un `UpgradeCTA` en bas
- `UpgradeCTA` : bouton/lien de CTA d'upgrade qui lit le hint via `useUpgradeHint` ou reçoit les props directement, avec le label traduit depuis `benefit_key`

**UX cibles (UX64-1, UX64-2, UX64-6) :**
- Blur CSS non intrusif (le contenu reste lisible en silhouette)
- CTA visible mais non agressif
- Sur mobile, le CTA ne doit pas obstruer la navigation

## Acceptance Criteria

**AC1 — LockedSection flou + overlay**
**Given** un composant `<LockedSection>` wrappant du contenu  
**When** il est rendu dans le navigateur  
**Then** le contenu est visuellement flou (CSS `filter: blur(...)` ou équivalent)  
**And** un overlay semi-transparent est visible avec une icône lock  
**And** le contenu reste présent dans le DOM (non supprimé)

**AC2 — UpgradeCTA avec label issu du benefit_key**
**Given** `<UpgradeCTA featureCode="horoscope_daily" />` dans un composant  
**When** le composant est rendu  
**Then** le label du bouton est traduit depuis la clé `benefit_key` de l'upgrade hint  
**And** le lien pointe vers la page d'abonnement (`/subscription-guide` ou équivalent)

**AC3 — LockedSection accepte UpgradeCTA en slot optionnel**
**Given** `<LockedSection cta={<UpgradeCTA featureCode="horoscope_daily" />}>`  
**When** il est rendu  
**Then** le CTA est affiché dans l'overlay ou en bas de section  
**And** si `cta` n'est pas fourni, aucun CTA n'est rendu (section lockée sans appel à l'action)

**AC4 — UpgradeCTA silencieux si hint absent**
**Given** `<UpgradeCTA featureCode="some_feature" />` et aucun hint pour cette feature  
**When** le composant est rendu  
**Then** rien n'est rendu (retour `null`) — pas d'erreur, pas de CTA vide

**AC5 — Style sans classes Tailwind, avec variables CSS**
**Given** le fichier CSS du composant  
**When** il est inspecté  
**Then** aucune classe Tailwind n'est utilisée  
**And** le blur, l'overlay et les couleurs utilisent les variables CSS du projet (`--glass`, `--text-1`, `--primary`, etc.)

**AC6 — Responsive mobile**
**Given** `LockedSection` et `UpgradeCTA` en viewport mobile  
**When** la page est rendue  
**Then** le CTA est visible sans obstruer la navigation du bas (`BottomNav`)  
**And** le blur ne cause pas de débordement horizontal

**AC7 — Tests de rendu**
**Given** `frontend/src/components/ui/LockedSection/LockedSection.test.tsx` et `UpgradeCTA.test.tsx`  
**When** les tests sont exécutés  
**Then** : rendu correct avec et sans CTA, rendu null si hint absent, pas d'erreur console

## Tasks / Subtasks

- [x] T1 — Créer le composant `LockedSection` (AC1, AC3, AC5, AC6)
  - [x] T1.1 Créer `frontend/src/components/ui/LockedSection/LockedSection.tsx`
  - [x] T1.2 Interface avec `children`, `cta?`, `label?`
  - [x] T1.3 Implémenter le markup avec `aria-hidden="true"` sur le contenu
  - [x] T1.4 Créer `frontend/src/components/ui/LockedSection/LockedSection.css` avec variables CSS projet

- [x] T2 — Créer le composant `UpgradeCTA` (AC2, AC4, AC5)
  - [x] T2.1 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.tsx`
  - [x] T2.2 Interface avec `featureCode`, `variant?: 'button' | 'link'`
  - [x] T2.3 Utilise `useUpgradeHint` + `useAstrologyLabels` + `getUpgradeBenefitLabel` (i18n projet)
  - [x] T2.4 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
  - [x] T2.5 Ajouter clés `benefit_key` dans `frontend/src/i18n/billing.ts`

- [x] T3 — Exporter depuis l'index UI
  - [x] T3.1 Créé `frontend/src/components/ui/LockedSection/index.ts`
  - [x] T3.2 Créé `frontend/src/components/ui/UpgradeCTA/index.ts`
  - [x] T3.3 Ajouté exports dans `frontend/src/components/ui/index.ts`

- [x] T4 — Tests de rendu (AC7)
  - [x] T4.1 Créer `frontend/src/components/ui/LockedSection/LockedSection.test.tsx` (6 tests)
  - [x] T4.2 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` (5 tests)
  - [x] T4.3 Tests : rendu avec CTA, sans CTA, UpgradeCTA null si hint absent
  - [x] T4.4 `npx vitest run` → 0 erreur sur les 11 tests nouveaux

## Dev Notes

### Icône lock

Utiliser `lucide-react` (déjà utilisé dans le projet, ex: `ChevronLeft`, `RefreshCw`). L'icône appropriée est `Lock` ou `LockKeyhole`.

### Variables CSS existantes à utiliser

Vérifier dans `frontend/src/index.css` et `frontend/src/styles/theme.css` les variables disponibles. Ne pas créer de nouvelles variables sans d'abord vérifier leur existence :
- `--glass` ou `--glass-2` pour l'overlay
- `--primary` pour le bouton CTA
- `--radius-md` ou équivalent pour les bordures arrondies
- `--space-sm`, `--space-md` pour les espacements

### Traduction du benefit_key

Le `benefit_key` est une clé de message i18n (ex: `"upgrade.horoscope_daily.full_access"`). Utiliser le système de traduction existant dans le projet. Regarder comment `tAstrologers`, `tSettings`, etc. sont implémentés dans `frontend/src/i18n/` pour suivre le même pattern.

### UX : blur non agressif

Le `filter: blur(6px)` est une valeur de départ. Tester sur mobile — si trop agressif, réduire à 4px. L'objectif est que le contenu soit reconnaissable en silhouette (donne envie) mais pas lisible.

## Dev Agent Record

### File List

- `frontend/src/components/ui/LockedSection/LockedSection.tsx` — created
- `frontend/src/components/ui/LockedSection/LockedSection.css` — created
- `frontend/src/components/ui/LockedSection/index.ts` — created
- `frontend/src/components/ui/LockedSection/LockedSection.test.tsx` — created
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.tsx` — created
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css` — created
- `frontend/src/components/ui/UpgradeCTA/index.ts` — created
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx` — created
- `frontend/src/components/ui/index.ts` — modified (exports ajoutés)
- `frontend/src/i18n/billing.ts` — modified (UPGRADE_BENEFIT_LABELS + getUpgradeBenefitLabel)

### Implementation Notes

- `LockedSection.tsx` : markup avec `aria-hidden="true"` sur `.locked-section__content` pour accessibilité. Icône `Lock` de `lucide-react`. Slot `cta` rendu dans `.locked-section__cta-container`.
- `UpgradeCTA.tsx` : utilise `useUpgradeHint(featureCode)` depuis Story 64.5, `useAstrologyLabels()` pour la langue courante, et `getUpgradeBenefitLabel(key, lang)` ajouté dans `frontend/src/i18n/billing.ts`. Lien vers `/subscription-guide`. Retourne `null` si hint absent.
- Extension ultérieure validée :
  - `UpgradeCTA` accepte désormais une prop optionnelle `label` pour surcharger ponctuellement le message issu du `benefit_key` quand une page produit a besoin d'un wording de conversion plus précis ;
  - ce mode est utilisé sur `/dashboard/horoscope` et `/consultations` pour orienter explicitement l'utilisateur free vers l'abonnement Basic sans dupliquer un second composant CTA.
- i18n : trois clés ajoutées dans `billing.ts` — `upgrade.horoscope_daily.full_access`, `upgrade.natal_chart_long.full_interpretation`, `upgrade.astrologer_chat.unlimited_messages` — avec traductions fr/en/es.
- CSS : variables du projet utilisées (`--glass`, `--primary`, `--text-1`, `--radius-md`, `--space-sm`, `--space-md`). Aucune classe Tailwind.
- Exports ajoutés dans `frontend/src/components/ui/index.ts`.

### Tests

- 6 tests LockedSection : rendu contenu aria-hidden, overlay, label conditionnel, CTA slot, container vide sans CTA
- 5 tests UpgradeCTA : null sans hint, lien traduit, href vers /subscription-guide, variant button par défaut, variant link

### Deviations from Story

Aucune déviation fonctionnelle. Note : `react-i18next` absent du projet — remplacé par le système i18n custom (`useAstrologyLabels` + `getUpgradeBenefitLabel`) conformément aux patterns existants.
