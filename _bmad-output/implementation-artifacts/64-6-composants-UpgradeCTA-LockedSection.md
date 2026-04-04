# Story 64.6 — Composants `UpgradeCTA` + `LockedSection` réutilisables

Status: todo

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

- [ ] T1 — Créer le composant `LockedSection` (AC1, AC3, AC5, AC6)
  - [ ] T1.1 Créer `frontend/src/components/ui/LockedSection/LockedSection.tsx`
  - [ ] T1.2 Interface :
    ```tsx
    interface LockedSectionProps {
      children: React.ReactNode
      cta?: React.ReactNode
      label?: string  // texte dans l'overlay (ex: "Disponible avec Basic")
    }
    ```
  - [ ] T1.3 Implémenter le markup :
    ```tsx
    <div className="locked-section">
      <div className="locked-section__content">{children}</div>
      <div className="locked-section__overlay">
        <LockIcon />
        {label && <span className="locked-section__label">{label}</span>}
        {cta}
      </div>
    </div>
    ```
  - [ ] T1.4 Créer `frontend/src/components/ui/LockedSection/LockedSection.css`
    ```css
    .locked-section {
      position: relative;
      overflow: hidden;
    }
    .locked-section__content {
      filter: blur(6px);
      pointer-events: none;
      user-select: none;
    }
    .locked-section__overlay {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--space-sm, 0.5rem);
      background: var(--glass, rgba(0,0,0,0.3));
    }
    ```

- [ ] T2 — Créer le composant `UpgradeCTA` (AC2, AC4, AC5)
  - [ ] T2.1 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.tsx`
  - [ ] T2.2 Interface :
    ```tsx
    interface UpgradeCTAProps {
      featureCode: string
      variant?: 'button' | 'link'  // défaut: 'button'
    }
    ```
  - [ ] T2.3 Implémenter :
    ```tsx
    export function UpgradeCTA({ featureCode, variant = 'button' }: UpgradeCTAProps) {
      const hint = useUpgradeHint(featureCode)
      if (!hint) return null

      const label = t(hint.benefit_key) // résolution i18n
      return (
        <Link to="/subscription-guide" className={`upgrade-cta upgrade-cta--${variant}`}>
          {label}
        </Link>
      )
    }
    ```
  - [ ] T2.4 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
    ```css
    .upgrade-cta {
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 1rem;
      background: var(--primary);
      color: var(--text-on-primary, #fff);
      border-radius: var(--radius-md, 6px);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.875rem;
      transition: opacity 0.15s ease;
    }
    .upgrade-cta:hover { opacity: 0.85; }
    ```
  - [ ] T2.5 Ajouter les clés `benefit_key` dans `frontend/src/i18n/billing.ts` :
    - `"upgrade.horoscope_daily.full_access"` → fr: "Accéder à l'horoscope complet", en: "Get full horoscope"
    - `"upgrade.natal_chart_long.full_interpretation"` → fr: "Débloquer l'interprétation complète", en: "Unlock full interpretation"
    - `"upgrade.astrologer_chat.unlimited_messages"` → fr: "Échanger sans limite", en: "Chat without limits"

- [ ] T3 — Exporter depuis l'index UI (si applicable)
  - [ ] T3.1 Vérifier s'il existe un `frontend/src/components/ui/index.ts` ou `@ui` alias
  - [ ] T3.2 Exporter `LockedSection` et `UpgradeCTA` depuis cet index

- [ ] T4 — Tests de rendu (AC7)
  - [ ] T4.1 Créer `frontend/src/components/ui/LockedSection/LockedSection.test.tsx`
  - [ ] T4.2 Créer `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.test.tsx`
  - [ ] T4.3 Tests : rendu avec CTA, sans CTA, UpgradeCTA null si hint absent
  - [ ] T4.4 `npx vitest run` → 0 erreur

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
