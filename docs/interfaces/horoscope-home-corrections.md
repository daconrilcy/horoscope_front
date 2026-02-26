# Corrections à appliquer — Home “Horoscope” (Light + Dark) vs maquettes de référence

Contexte : les deux écrans livrés par l’agent **ne matchent pas** les maquettes de référence (celles générées précédemment : light pastel premium + dark cosmic).  
Objectif : obtenir un rendu **visuellement quasi identique** (hiérarchie, contrastes, glassmorphism, gradients, icônes, spacing).

---

## 0) Résumé des écarts majeurs (à corriger en priorité)

### 0.1 Light mode — “cassé” (priorité P0)
- **Contraste texte incorrect** : titres et contenus sont **blancs / trop clairs** sur fond clair → le contenu devient illisible, “washed out”.  
  → Dans la maquette ref light, le texte est **dark ink** (#1E1B2E) avec secondaires en alpha.
- **Opacité globale** suspecte : on dirait qu’une opacité est appliquée au container (ou un overlay) qui “délave” tout.  
  → Interdit : `opacity` sur un wrapper parent. Corriger avec des couleurs/alphas ciblés.
- **Bottom nav** : labels + icônes trop pâles (presque gris clair), active state trop “tile” et peu premium.

### 0.2 Dark mode — ambiance cosmique non respectée (priorité P0)
- **Fond** : présence d’un “bokeh” (gros ronds) qui n’existe pas dans la ref. Il faut un **starfield + noise** discret, pas des bulles.
- **Glassmorphism** insuffisant : cartes trop “plates / opaques”, on ne voit pas l’univers cosmique à travers.  
  → Dans la ref dark, le fond étoilé est visible **dans** les cards via transparence + blur.
- **CTA** : bouton trop plat (couleur unie), manque le gradient + glow.

---

## 1) Corrections globales (P0) — thèmes, typos, règles de rendu

### 1.1 Stopper toute opacité globale
- Rechercher et supprimer : `opacity` appliquée sur le layout/page wrapper (ex: `opacity-50`, `style={{opacity:...}}`, overlay semi-transparent couvrant tout).
- À la place : gérer la “douceur” par des `rgba()` et par les variables `--text-2/--text-3`, `--glass`, etc.

### 1.2 Mettre en place un vrai système de tokens (obligatoire)
Implémenter des CSS variables identiques au spec, et vérifier qu’elles changent bien entre light et dark.

Requis minimum (doit être effectif dans le DOM) :
- `--text-1`, `--text-2`, `--text-3`
- `--bg-top`, `--bg-mid`, `--bg-bot`
- `--glass`, `--glass-2`, `--glass-border`
- `--cta-l`, `--cta-r`
- `--chip`
- `--nav-glass`, `--nav-border`
- `--shadow-card`, `--shadow-nav`

Critique : en light, `--text-1` doit être **#1E1B2E** (pas blanc).  
En dark, `--text-1` doit être **rgba(245,245,255,0.92)**.

### 1.3 Typographie : hiérarchie identique à la ref
- “Aujourd’hui” : 13px, weight 500, `color: var(--text-2)`
- “Horoscope” (H1) : 40px, weight ~650, tracking -0.5px, `color: var(--text-1)`
- Headline hero : 28px, weight ~650, `color: var(--text-1)`
- Section titles (“Raccourcis”, “Amour”) : 18px, weight ~650, `color: var(--text-1)`
- Labels nav : 12px, weight 500, `color: var(--text-2)` (active plus contrast)

Police :
`-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, system-ui, sans-serif`

### 1.4 Icônes : Lucide uniformisées
- `strokeWidth = 1.75` partout (premium).
- Tailles : 24 (nav), 20 (cards), 18 (CTA chevron), 16 (inline).
- Couleurs : monochrome (hérite du texte), couleur d’accent uniquement sur actif/CTA.

---

## 2) Background / texture (P0) — ce qui donne le “fancy”

### 2.1 Dark mode : remplacer “bokeh” par starfield
À supprimer :
- Tout overlay de ronds (“bubbles”, “bokeh”, cercles flous) sur l’écran.

À ajouter :
- Un layer “stars” (image PNG/SVG) en background global (sur la page entière), opacity 0.35–0.55.
- Un gradient cosmique (violet/bleu) sous les étoiles.

Important : le starfield doit rester visible **à travers les cards** (donc cards translucides + backdrop-blur).

### 2.2 Light mode : gradient pastel + noise (sans délavage)
À avoir :
- 2 radial gradients très doux + 1 linear gradient (rose->lavande).
- Un noise très subtil (opacité 0.06–0.10) pour éviter le rendu “plat”.

À éviter :
- Tout overlay gris/noir qui baisse le contraste global.

---

## 3) Header (P1) — alignements et éléments parasites

Écarts observés :
- Ajout d’un cercle en haut à gauche (type bouton retour placeholder) non présent dans la ref.
- Avatar “D” au lieu d’un avatar photo : ok en placeholder, mais doit être **discret** et cohérent.

Corrections :
1) Supprimer le bouton/cercle top-left sur la Home (pas de back sur l’onglet “Aujourd’hui”).  
2) Garder : “Aujourd’hui” centré + “Horoscope” centré.  
3) Avatar top-right : 40x40, border 1px translucide, fond léger.

---

## 4) Hero card (P0) — composant le plus important

### 4.1 Glass surface incorrecte
Écart :
- En dark, la hero card est trop opaque / trop “gris plein”.
- En light, la hero card est trop blanche ET le texte devient trop clair (donc double problème).

Corrections :
- Dark hero bg : `rgba(255,255,255,0.08)` + border `rgba(255,255,255,0.12)` + `backdrop-blur(14px)`
- Light hero bg : `rgba(255,255,255,0.55)` + border `rgba(255,255,255,0.65)` + `backdrop-blur(14px)`
- Shadow : dark `rgba(0,0,0,0.45)` / light `rgba(20,20,40,0.12)` (soft, large)

### 4.2 CTA bouton (trop plat actuellement)
Écart :
- Bouton violet uni, pas de gradient, pas de glow.

Corrections :
- Utiliser gradient : `linear-gradient(90deg, var(--cta-l), var(--cta-r))`
- Ajouter glow :
  - light : `0 14px 30px rgba(90,120,255,0.25)`
  - dark : `0 14px 30px rgba(0,0,0,0.35)` + léger outer glow violet possible
- Hauteur 48px, radius 9999.

### 4.3 Constellation (visuel)
Écart :
- Dans la ref, la constellation est un tracé “étoiles + lignes” glow, pas une “vague”.

Corrections :
- Remplacer l’illustration par un SVG constellation (points + segments) opacité ~0.55, placé à droite dans la hero card.
- Option : même SVG en light/dark, mais ajuster la couleur (blanc en light, léger violet en dark) + glow.

### 4.4 Chip (signe + date)
Écart :
- Ok globalement, mais doit être plus “pill” et harmonisé.

Corrections :
- Height 30–32px, padding 8px 12px, radius 999.
- Background : light `#C6B9E5` ; dark `#4F3F71`
- Texte : 13px, weight 500, **pas sousligné**.
- Ajouter le symbole ♒ (texte) ou un mini SVG, sinon une petite icône Lucide `Sparkles` en 16px.

---

## 5) Section “Raccourcis” + Shortcut cards (P1)

Écarts observés :
- Textes souslignés (probablement des `<a>` avec underline).
- Layout texte pas identique : dans la ref, c’est “propre” (titre + sous-titre), pas un style “link”.

Corrections :
1) **Supprimer underline** : `no-underline` / `text-decoration: none`.
2) Card background :
   - dark : `rgba(255,255,255,0.06)` + border `rgba(255,255,255,0.10)` + blur
   - light : `rgba(255,255,255,0.45)` + border `rgba(255,255,255,0.60)` + blur
3) Badge icône à gauche :
   - 36x36, radius 14, center
   - Chat badge bg :
     - light `#E1F0EA`
     - dark `#E4F2EC`
   - Tirage badge bg :
     - light `#F8CAA5`
     - dark `#D5946A`
4) Typo :
   - Titre : 14–15px semibold, `--text-1`
   - Sous-titre : 13px, `--text-2`
   - “En ligne” : 13px, color vert doux (pas fluo), **sans underline**

---

## 6) Section “Amour” + 3 mini cards (P1)

Écarts observés :
- Cards trop “plates” : on perd l’effet premium/glass.
- En light, texte trop clair donc illisible.

Corrections :
1) Card bg glass :
   - dark : `rgba(255,255,255,0.06)` + border `rgba(255,255,255,0.10)` + blur
   - light : `rgba(255,255,255,0.42)` + border `rgba(255,255,255,0.58)` + blur
2) Icon badge en haut :
   - 36x36, radius 14
   - Amour bg : light `#EBA4C9`, dark `#E779B4`
   - Travail bg : light `#AABEEF`, dark `#A8ACEF`
   - Énergie bg : light `#F6D2A7`, dark `#E5B270`
3) Typo :
   - Titre : 15px semibold, `--text-1`
   - Description : 13px, `--text-2`, max 2 lignes (ellipsis si besoin)

---

## 7) Bottom Navigation (P0)

Écarts observés :
- Light : icônes/labels trop pâles (doivent être plus dark).
- Active state : trop “bloc” (tile). Dans la ref c’est subtil et premium.

Corrections :
1) Container :
   - fixed bottom 16px, left/right 16px
   - radius 24, padding 10
   - blur 14px
   - bg `--nav-glass`
   - border `--nav-border`
   - shadow `--shadow-nav`
2) Items :
   - icon 24px stroke 1.75
   - label 12px
3) Active state :
   - fond actif : `rgba(134,108,208,0.18)` (light) / `rgba(150,110,255,0.18)` (dark)
   - icon+label : augmenter contraste (light => `--text-1`, dark => `--text-1`)
   - Éviter un carré/tile trop visible : radius 18 + padding 10/8 comme ref, mais avec opacité faible.

Navigation icons (Lucide) :
- Aujourd’hui `CalendarDays`
- Chat `MessageCircle`
- Thème `Star`
- Tirages `Layers`
- Profil `User`

---

## 8) Checklist “Definition of Done” (DoD) — validation visuelle

L’agent doit livrer :
1) 2 screenshots (light + dark) alignés sur la ref, même contenu, même hiérarchie.
2) Light mode : texte lisible (H1 et headline clairement dark), pas de “washed out”.
3) Dark mode : starfield visible derrière ET à travers les cards (transparence + blur).
4) Aucun “bokeh circles” / ronds flottants.
5) CTA : gradient + glow conforme.
6) Aucun texte sousligné dans les cards.
7) Icônes Lucide cohérentes (strokeWidth 1.75).

Procédure :
- Comparer côte à côte avec la ref à 50% zoom et 100% zoom.
- Vérifier particulièrement : contrastes light, glass dark, CTA, nav.

---

## 9) Si besoin d’assets (recommandé)
- `stars.png` (tileable, 1024x1024) + `noise.png` (512x512).
- `constellation.svg` (points+segments) en 1 couleur.

À intégrer via pseudo-elements :
- `::before` pour stars/noise
- `pointer-events: none;`

---

Fin.
