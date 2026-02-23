# Story 17.4: HeroHoroscopeCard — Glassmorphism

Status: done

## Story

As a utilisateur de l'application horoscope,
I want voir une carte hero visuelle et immersive au centre de la page "Aujourd'hui" avec mon signe astrologique, un insight du jour et un bouton d'action,
So that je sois immédiatement engagé par une information personnalisée et puisse accéder à mon horoscope complet en un tap.

## Contexte

La `HeroHoroscopeCard` est le composant clé de la page "Aujourd'hui" — celui qui donne toute l'identité visuelle premium. La spec §7.2 en détaille la structure complète :
1. Chip signe + date (♒ Verseau • 23 fév.)
2. Chevron top-right
3. Headline 28px ("Ta journée s'éclaircit après 14h.")
4. Constellation SVG en filigrane (droite)
5. CTA pill button ("Lire en 2 min" + chevron)
6. Lien "Version détaillée" centré

L'effet glassmorphism (`backdrop-filter: blur(14px)`, fond `--glass`, border `--glass-border`) est au cœur du rendu.

**Prérequis** : Stories 17.1 (tokens), 17.2 (fond visible pour que le glass soit rendu).

## Scope

### In-Scope
- Création de `frontend/src/components/HeroHoroscopeCard.tsx`
- Glassmorphism complet (backdrop-filter, glass bg, border, shadow)
- Chip sign (texte unicode + label date)
- Headline 28px configurable via props
- Constellation SVG filigrane (inline, opacité ~0.55)
- CTA pill button gradient avec shadow et chevron
- Lien "Version détaillée" (ou callback `onReadMore`)
- Props : `sign`, `date`, `headline`, `onReadFull`, `onReadDetailed`

### Out-of-Scope
- Connexion aux vraies données d'horoscope (données statiques pour cette story)
- Animation de la constellation
- Swipe pour changer de jour (epic ultérieur)

## Acceptance Criteria

### AC1: Card glassmorphism rendue correctement
**Given** le composant `HeroHoroscopeCard` est monté sur un fond gradient
**When** on l'observe visuellement
**Then** la carte affiche un effet de verre dépoli (`backdrop-filter: blur(14px)`)
**And** son background est `var(--glass)`, son border `1px solid var(--glass-border)`
**And** son radius est **26px**
**And** son ombre est `var(--shadow-card)`

### AC2: Chip signe + date rendu correctement
**Given** les props `sign="♒"` et `date="23 fév."` sont passées
**When** on observe le chip en haut à gauche
**Then** le chip affiche "♒ Verseau • 23 fév." (ou l'équivalent formaté)
**And** sa hauteur est 30–32px, son background est `var(--chip)`, son radius est 999
**And** sa typographie est 13px, `--text-1`

### AC3: Chevron top-right présent
**Given** le composant est rendu
**When** on observe l'angle haut-droite de la carte
**Then** une icône `ChevronRight` (Lucide, size 18, strokeWidth 1.75) est affichée en `--text-2`

### AC4: Headline 28px rendu correctement
**Given** la prop `headline="Ta journée s'éclaircit après 14h."` est passée
**When** on inspecte le texte headline
**Then** sa taille est 28px, son poids 650, son line-height 1.12, son letter-spacing -0.3px
**And** sa couleur est `--text-1`
**And** il est positionné sous le chip avec margin-top 12px

### AC5: Constellation SVG en filigrane
**Given** le composant est rendu
**When** on observe la partie droite de la carte (en overlay)
**Then** un SVG de constellation est positionné en absolu à droite (opacité ~0.55)
**And** il ne bloque pas les interactions (pointer-events: none)
**And** un glow léger est visible (filter: blur ou drop-shadow sur le SVG)

### AC6: CTA button pill gradient fonctionnel
**Given** le composant est rendu
**When** on observe le bouton "Lire en 2 min"
**Then** sa hauteur est 48px, son radius est 999 (pill), sa largeur est 100%
**And** son dégradé est `linear-gradient(90deg, var(--cta-l), var(--cta-r))`
**And** le texte est blanc, 16px, weight 650
**And** une icône `ChevronRight` est à droite du texte
**And** son ombre est `0 14px 30px rgba(90,120,255,0.25)` (light) / `rgba(0,0,0,0.35)` (dark)
**When** l'utilisateur clique dessus
**Then** le callback `onReadFull` est appelé

### AC7: Lien "Version détaillée" rendu
**Given** le composant est rendu
**When** on observe sous le CTA button
**Then** le texte "Version détaillée" est centré, 13px, `--text-2`
**And** il est cliquable et appelle `onReadDetailed` si fourni

### AC8: Thème dark rendu correctement
**Given** la classe `dark` est active sur `<html>`
**When** on observe la `HeroHoroscopeCard`
**Then** toutes les variables CSS basculent (glass plus sombre, chip plus foncé, CTA violet profond)
**And** le rendu correspond à la maquette dark cosmic

## Tasks

- [x] Task 1: Créer la constellation SVG inline (AC: #5)
  - [x] 1.1 Créer `frontend/src/components/ConstellationSVG.tsx`
  - [x] 1.2 SVG simple style "Verseau" : lignes fines + points, 120×120px environ
  - [x] 1.3 Couleur : `currentColor` ou blanc, `opacity: 0.55`, `filter: drop-shadow(0 0 6px rgba(200,180,255,0.4))`
  - [x] 1.4 `pointer-events: none`

- [x] Task 2: Créer `frontend/src/components/HeroHoroscopeCard.tsx` (AC: #1–#8)
  - [x] 2.1 Définir `HeroHoroscopeCardProps { sign: string; signName: string; date: string; headline: string; onReadFull?: () => void; onReadDetailed?: () => void }`
  - [x] 2.2 Container card : `border-radius: 26px`, `padding: 18px`, glassmorphism complet
  - [x] 2.3 Row top : chip à gauche + ChevronRight à droite (flex between)
  - [x] 2.4 Chip : `height: 32px`, `padding: 0 12px`, `border-radius: 999px`, `background: var(--chip)`
  - [x] 2.5 Headline : `font-size: 28px`, `font-weight: 650`, etc.
  - [x] 2.6 `<ConstellationSVG>` en `position: absolute`, `right: -20px`, `top: 60px`
  - [x] 2.7 CTA button : all styles (gradient, pill, shadow, text, chevron)
  - [x] 2.8 "Version détaillée" : lien centré `cursor: pointer`

- [x] Task 3: Styles CSS (AC: #1–#8)
  - [x] 3.1 Ajouter les classes dans `App.css` sous `/* === HeroHoroscopeCard === */`
  - [x] 3.2 Class `.hero-card` pour le container glassmorphism
  - [x] 3.3 Class `.hero-card__chip`, `.hero-card__headline`, `.hero-card__cta`, `.hero-card__link`
  - [x] 3.4 CTA shadow différente dark/light : utiliser `var(--cta-shadow)` ou media-query dark
  - [x] 3.5 Préfixe webkit pour backdrop-filter : `-webkit-backdrop-filter: blur(14px)`

- [x] Task 4: Test unitaire (AC: #1–#7)
  - [x] 4.1 Créer `frontend/src/tests/HeroHoroscopeCard.test.tsx`
  - [x] 4.2 Tester le rendu du chip avec les props sign + date
  - [x] 4.3 Tester le rendu du headline
  - [x] 4.4 Tester le clic sur le CTA → callback `onReadFull` appelé
  - [x] 4.5 Tester le clic sur "Version détaillée" → callback `onReadDetailed` appelé

## Dev Notes

### Structure JSX indicative (spec §11.2)

```tsx
<div className="hero-card" style={{ marginTop: '18px' }}>
  {/* Top row */}
  <div className="hero-card__top-row">
    <div className="hero-card__chip">
      <span>{sign}</span>
      <span>{signName} • {date}</span>
    </div>
    <ChevronRight size={18} strokeWidth={1.75} style={{ color: 'var(--text-2)' }} />
  </div>

  {/* Headline */}
  <h2 className="hero-card__headline">{headline}</h2>

  {/* Constellation overlay */}
  <div className="hero-card__constellation">
    <ConstellationSVG />
  </div>

  {/* CTA */}
  <button className="hero-card__cta" onClick={onReadFull}>
    Lire en 2 min <ChevronRight size={18} strokeWidth={1.75} />
  </button>

  {/* Link */}
  <div className="hero-card__link" onClick={onReadDetailed}>
    Version détaillée
  </div>
</div>
```

### Glassmorphism CSS

```css
.hero-card {
  border-radius: 26px;
  padding: 18px;
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  position: relative;
  overflow: hidden;
}
```

### Constellation SVG (exemple simple Verseau)

Le SVG doit évoquer la constellation du Verseau : deux lignes ondulées de points avec des lignes connectantes légères. Pas besoin d'exactitude astronomique — l'effet visuel prime.

```svg
<svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Points étoiles -->
  <circle cx="10" cy="30" r="2" fill="white"/>
  <circle cx="35" cy="20" r="1.5" fill="white"/>
  <!-- ... lignes connectantes ... -->
  <!-- Ligne onde supérieure -->
  <path d="M5 40 Q20 30 35 40 Q50 50 65 40 Q80 30 95 40"
        stroke="white" stroke-width="1" fill="none" opacity="0.6"/>
  <!-- Ligne onde inférieure -->
  <path d="M5 55 Q20 45 35 55 Q50 65 65 55 Q80 45 95 55"
        stroke="white" stroke-width="1" fill="none" opacity="0.6"/>
</svg>
```

### References

- [Source: docs/interfaces/horoscope-ui-spec.md §7.2, §11.2]
- [Maquettes: docs/interfaces/e5103e5d-d686-473f-8dfb-586b2e3918bb.png (light), docs/interfaces/ChatGPT Image 23 févr. 2026, 15_12_17.png (dark)]

## Dev Agent Record

### Implementation Notes

**Story 17.4 — Implémentée le 2026-02-23 (Revue et Corrigée - V2)**

**Approche :**
- `ConstellationSVG.tsx` : SVG optimisé (memoization, `preserveAspectRatio`). Opacités internes retirées pour contrôle CSS pur.
- `HeroHoroscopeCard.tsx` : Refactorisation sémantique complète (utilisation de `role="article"` et `<button>` au lieu de `div` pour l'accessibilité native). Support i18n pour les ARIA labels via props optionnelles. JSDoc ajoutée. Icônes décoratives masquées (aria-hidden).
- `App.css` : Styles de focus-visible, resets de boutons et classes BEM consolidées.
- `TodayHeader.tsx` : Documentation JSDoc ajoutée pour cohérence.

**Tests :** 17 tests unitaires couvrant AC1 à AC7, incluant les rôles sémantiques et les labels ARIA custom — tous passent (100%). Utilisation des meilleures pratiques RTL (queries via `screen`).

### File List

- `frontend/src/components/ConstellationSVG.tsx` (créé)
- `frontend/src/components/HeroHoroscopeCard.tsx` (créé)
- `frontend/src/tests/HeroHoroscopeCard.test.tsx` (créé)
- `frontend/src/components/TodayHeader.tsx` (modifié - JSDoc)
- `frontend/src/App.css` (modifié — styles HeroHoroscopeCard ajoutés)

## Change Log

| Date | Description |
|------|-------------|
| 2026-02-23 | Implémentation complète story 17.4 : ConstellationSVG, HeroHoroscopeCard, styles CSS glassmorphism, 21 tests unitaires — AC1–AC7 satisfaits, thème dark via CSS tokens (AC8) |
