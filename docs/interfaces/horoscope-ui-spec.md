# Horoscope App — UI Spec “Premium” (Light + Dark Cosmic)

Objectif : implémenter **la page d’accueil (Aujourd’hui/Horoscope)** en **mode clair** et en **mode dark cosmic** pour qu’elle ressemble **au plus proche** aux deux maquettes fournies (visuel, hiérarchie, spacing, glassmorphism, icônes, etc.).  
Stack ciblée : **React + TypeScript + Vite** (ou équivalent) avec **TailwindCSS**. Les tokens sont aussi fournis en CSS variables pour rester agnostique.

---

## 1) Hypothèses & contraintes

- Écran cible : iPhone “classique” (largeur logique ~390px).  
- Layout **mobile-first** avec un conteneur centré (max-width 420px) en web.
- Thèmes :
  - **Light Pastel Premium**
  - **Dark Cosmic**
- Police : on vise le rendu “iOS premium”.
  - Web : `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, system-ui, sans-serif`
- Icônes : **Lucide** (via `lucide-react`).
- Les fonds (dégradés + étoiles/noise) sont essentiels au rendu “fancy”.
- Pixel-perfect : on privilégie des valeurs fixes (padding, radius, tailles) plutôt que du “responsive freestyle”.

---

## 2) Palette & tokens (extraits des maquettes)

### 2.1. Couleurs principales (LIGHT)
Ces valeurs viennent de points d’échantillonnage sur la maquette light (donc “visuellement cohérentes”).

- Background top : `#FDF5F8`
- Background mid (lavender haze) : `#D9CBE1`
- Background bottom : `#D8D0EE`

- Hero card “glass” (base) : `rgba(255,255,255,0.55)`
- Hero card border : `rgba(255,255,255,0.65)`
- Hero card shadow : `0 18px 40px rgba(20, 20, 40, 0.12)`

- Chip (signe + date) bg : `#C6B9E5`
- CTA button gradient :
  - left `#866CD0`
  - right `#A190ED`

- Bottom nav glass bg (base) : `rgba(255,255,255,0.55)`  
  (dans la maquette, le rendu “nav_bg” observé est proche `#CAC2E3` une fois mélangé au fond)
- Bottom nav border : `rgba(255,255,255,0.65)`

- Texte primary (dark ink) recommandé : `#1E1B2E`
- Texte secondary : `rgba(30,27,46,0.72)`
- Texte tertiary : `rgba(30,27,46,0.55)`

Accents (badges) observés :
- Chat badge bg : `#E1F0EA`
- Tirage badge bg : `#F8CAA5`
- Amour badge bg : `#EBA4C9`
- Travail badge bg : `#AABEEF`
- Énergie badge bg : `#F6D2A7`

### 2.2. Couleurs principales (DARK COSMIC)
- Background top : `#181626`
- Background mid : `#0F0E18`
- Background bottom : `#2A2436`

- Hero card “glass” (base) : `rgba(255,255,255,0.08)`
- Hero card border : `rgba(255,255,255,0.12)`
- Hero card shadow : `0 18px 40px rgba(0,0,0,0.45)`

- Chip bg : `#4F3F71`
- CTA button gradient :
  - left `#37226E`
  - right `#5839B8`

- Bottom nav glass bg : `rgba(255,255,255,0.08)`  
  (visuellement proche d’un mélange autour de `#211C2B`)
- Bottom nav border : `rgba(255,255,255,0.12)`

- Texte primary : `rgba(245,245,255,0.92)`
- Texte secondary : `rgba(235,235,245,0.72)`
- Texte tertiary : `rgba(235,235,245,0.55)`

Accents (badges) observés :
- Chat badge bg : `#E4F2EC`
- Tirage badge bg : `#D5946A`
- Amour badge bg : `#E779B4`
- Travail badge bg : `#A8ACEF`
- Énergie badge bg : `#E5B270`

---

## 3) Tokens CSS (recommandé)

Créer un fichier `src/styles/theme.css` et appliquer les variables sur `:root` + `.dark`.

```css
:root{
  /* Text */
  --text-1: #1E1B2E;
  --text-2: rgba(30,27,46,0.72);
  --text-3: rgba(30,27,46,0.55);

  /* Background */
  --bg-top: #FDF5F8;
  --bg-mid: #D9CBE1;
  --bg-bot: #D8D0EE;

  /* Glass surfaces */
  --glass: rgba(255,255,255,0.55);
  --glass-2: rgba(255,255,255,0.38);
  --glass-border: rgba(255,255,255,0.65);

  /* Accent / CTA */
  --cta-l: #866CD0;
  --cta-r: #A190ED;

  /* Chips */
  --chip: #C6B9E5;

  /* Nav */
  --nav-glass: rgba(255,255,255,0.55);
  --nav-border: rgba(255,255,255,0.65);

  /* Shadows */
  --shadow-card: 0 18px 40px rgba(20,20,40,0.12);
  --shadow-nav:  0 10px 30px rgba(20,20,40,0.18);
}

.dark{
  --text-1: rgba(245,245,255,0.92);
  --text-2: rgba(235,235,245,0.72);
  --text-3: rgba(235,235,245,0.55);

  --bg-top: #181626;
  --bg-mid: #0F0E18;
  --bg-bot: #2A2436;

  --glass: rgba(255,255,255,0.08);
  --glass-2: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.12);

  --cta-l: #37226E;
  --cta-r: #5839B8;

  --chip: #4F3F71;

  --nav-glass: rgba(255,255,255,0.08);
  --nav-border: rgba(255,255,255,0.12);

  --shadow-card: 0 18px 40px rgba(0,0,0,0.45);
  --shadow-nav:  0 10px 30px rgba(0,0,0,0.55);
}
```

---

## 4) Typographie (rendu proche maquette)

### 4.1 Échelle
- **Overline / kicker** (“Aujourd’hui”)  
  - size: **13px**, weight **500**, letter-spacing **0.2px**, opacity via `--text-2`
- **H1 page title** (“Horoscope”)  
  - size: **40px**, weight **650**, line-height **1.05**, letter-spacing **-0.5px**
- **Hero headline** (“Ta journée s’éclaircit…”)  
  - size: **28px**, weight **650**, line-height **1.12**, letter-spacing **-0.3px**
- **Section title** (“Raccourcis”, “Amour”)  
  - size: **18px**, weight **650**, opacity `--text-1`
- **Card title**  
  - size: **15px**, weight **650**
- **Card subtitle / description**  
  - size: **13px**, weight **500**, opacity `--text-2` ou `--text-3`
- **Bottom nav label**  
  - size: **12px**, weight **500**, opacity `--text-2`

### 4.2 Police
CSS recommandé :

```css
html, body{
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, system-ui, sans-serif;
}
```

---

## 5) Layout (spacing, grid, radius)

### 5.1 Grille et marges
- Padding page horizontal : **18px**
- Padding page top : **22px** + safe-area (si iOS PWA)
- Espace entre header et hero card : **18px**
- Sections : **18px** au-dessus de chaque titre de section
- Grille “Raccourcis” : 2 colonnes, gap **12px**
- Grille “Mini cards” (Amour/Travail/Énergie) : 3 colonnes, gap **12px**

### 5.2 Radius
- Surfaces principales (hero + nav) : **24–26px**
- Cards secondaires : **18px**
- Badges icônes : **14px**
- CTA button : **999px** (pill), hauteur **48px**

### 5.3 Ombres
- Hero card : `var(--shadow-card)`
- Bottom nav : `var(--shadow-nav)`
- Ombres ultra-douces, pas de shadow “dure”.

### 5.4 Effet “glass”
- `backdrop-filter: blur(14px)` (+ webkit)
- BG translucide (variables `--glass` / `--nav-glass`)
- Border 1px translucide

---

## 6) Fond & textures (critique pour le rendu)

### 6.1 Light
- Fond = 2 radial gradients + 1 linear gradient + un **noise** très subtil.
- Sans noise, le rendu devient “plat / cheap”.

Pseudo CSS :

```css
.bg-light{
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.18), transparent 55%),
    radial-gradient(900px 700px at 80% 60%, rgba(120,190,255,0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 55%, var(--bg-bot) 100%);
}
```

Noise (option A) : PNG semi-transparent `noise.png` en overlay avec `mix-blend-mode: soft-light` et opacité 0.08.  
Noise (option B) : SVG noise / filter (plus “pur web”).

### 6.2 Dark cosmic
- Même logique, mais avec un **starfield** (image) ou un pattern d’étoiles SVG.
- Astuce : starfield en background + `radial-gradient` violet/bleu très doux.

```css
.bg-dark{
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.22), transparent 55%),
    radial-gradient(900px 700px at 80% 60%, rgba(90,170,255,0.14), transparent 60%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 55%, var(--bg-bot) 100%);
}
```

Puis ajouter un layer `stars.png` (opacité 0.35–0.55) ou un SVG répétable.

---

## 7) Composants (spec pixel-orientée)

La page d’accueil est composée de 4 blocs + bottom nav.

### 7.1 Header (top)
Contenu :
- Kicker centré : “Aujourd’hui”
- H1 centré : “Horoscope”
- Avatar rond en haut à droite

Spéc :
- Container header : padding-top **6px**
- Kicker : 13px, `--text-2`
- H1 : 40px, `--text-1`
- Avatar : 40x40, radius 999, border 1px translucide

### 7.2 Hero Horoscope Card (le bloc majeur)
C’est le composant clé du rendu.

Structure interne :
1) **Chip** en haut à gauche : “♒ Verseau • 23 fév.”
2) **Chevron** en haut à droite (icône)
3) **Headline** (28px)
4) **Constellation** (illustration en filigrane à droite)
5) **CTA button** (“Lire en 2 min” + chevron)
6) **Link** “Version détaillée” centré

Spéc (dimensions visuelles) :
- Card padding : **18px**
- Card radius : **26px**
- Card background : `var(--glass)`
- Card border : 1px `var(--glass-border)`
- Card shadow : `var(--shadow-card)`
- Constellation : opacité ~0.55, glow léger

Chip :
- Height : 30–32px
- Padding : 8px 12px
- Radius : 999
- Background : `var(--chip)`
- Texte : 13px, `--text-1` (en dark), `--text-1` (en light)
- Icône de signe : Lucide `Waves` n’existe pas ; utiliser un petit SVG signe Verseau (ou texte “♒”) + `Sparkles` si besoin.

CTA button :
- Height : **48px**
- Radius : 999
- Width : 100%
- Gradient : `linear-gradient(90deg, var(--cta-l), var(--cta-r))`
- Texte : 16px, weight 650, blanc en dark/light
- Shadow : `0 14px 30px rgba(90,120,255,0.25)` (light) / `rgba(0,0,0,0.35)` (dark)
- Icône : `ChevronRight` (Lucide)

Link “Version détaillée” :
- 13px, `--text-2` / `--text-3`
- Align center

### 7.3 Section “Raccourcis” + 2 Shortcut cards
- Titre “Raccourcis” (18px)
- 2 cards en grid 2 colonnes

Shortcut card structure :
- Badge icon à gauche (36–40px)
- Texte : titre 14–15px, sous-titre 13px (couleur status pour “En ligne”)
- Card background : `--glass-2` + border `--glass-border` plus léger

Badges :
- Chat badge bg : light `#E1F0EA`, dark `#E4F2EC`
- Tirage badge bg : light `#F8CAA5`, dark `#D5946A`
Badge radius : 14px

### 7.4 Section “Amour” + chevron + 3 mini cards
Header de section :
- “Amour” à gauche
- `ChevronRight` à droite
- spacing : margin-top 18px

Mini cards (3)
Structure :
- Icône en haut (centrée ou légèrement alignée au centre haut)
- Title
- Description 2 lignes max

Spéc :
- Card radius : 18px
- Padding : 14px
- Background : `--glass-2`
- Border : `--glass-border` (opacité plus faible)
- Badge icône : optionnel (si tu veux coller au rendu, l’icône peut être “posée” sans badge, mais la maquette montre une présence colorée).  
  Recommandation : badge 36x36 radius 14 avec bg :
  - Amour : light `#EBA4C9`, dark `#E779B4`
  - Travail : light `#AABEEF`, dark `#A8ACEF`
  - Énergie : light `#F6D2A7`, dark `#E5B270`

---

## 8) Bottom Navigation (glass pill)

- Position : fixed, bottom 16px, left/right 16px
- Container :
  - radius 24
  - padding 10
  - `backdrop-filter: blur(14px)`
  - background `var(--nav-glass)`
  - border 1px `var(--nav-border)`
  - shadow `var(--shadow-nav)`

Items (5) :
- Layout : `flex: 1`, align center
- Icon : 24px, `strokeWidth 1.75`
- Label : 12px
- Active state :
  - background `rgba(150,110,255,0.18)` (dark) / `rgba(134,108,208,0.18)` (light)
  - text/icon plus contrast

---

## 9) Icônes — Lucide (MVP pack)

Installer :
```bash
npm i lucide-react
```

Règles :
- Size : 24 (nav), 20 (cards), 16 (inline)
- `strokeWidth` : **1.75** (premium)
- Couleur : monochrome par défaut, accent uniquement sur l’état actif / CTA

### 9.1 Mapping navigation
- Aujourd’hui : `CalendarDays`
- Chat : `MessageCircle`
- Thème : `Star`
- Tirages : `Layers`
- Profil : `User`

### 9.2 Hero card / sections
- CTA chevron : `ChevronRight`
- Version détaillée : `FileText` (si tu ajoutes une icône, optionnel)
- Constellation : image/SVG custom (pas une icône Lucide)

### 9.3 Raccourcis + mini cards
- Chat astrologue : `MessageCircle`
- Tirage du jour : `Layers` (ou `LayoutGrid` si tu veux différencier)
- Amour : `Heart`
- Travail : `Briefcase`
- Énergie : `Zap`

### 9.4 Système
- Paramètres : `Settings`
- Notifications : `Bell`
- Confidentialité : `Shield`
- Dark mode : `Moon`
- Logout : `LogOut`
- Loader : `Loader2`

---

## 10) Architecture React recommandée

### 10.1 Arborescence
```
src/
  components/
    AppShell.tsx
    Header.tsx
    HeroHoroscopeCard.tsx
    ShortcutCard.tsx
    MiniInsightCard.tsx
    BottomNav.tsx
  pages/
    TodayPage.tsx
  styles/
    theme.css
    globals.css
  ui/
    icons.tsx
    nav.ts
```

### 10.2 AppShell (fond + container)
- Applique `.dark` sur `<html>` ou `<body>` selon le thème.
- Ajoute un layer `noise` (optionnel mais recommandé).
- Container max-width : 420px, center.

Pseudo:
- `<div className="min-h-dvh px-[18px] pt-[22px] pb-[110px] ...">`

### 10.3 TodayPage composition
Ordre :
1) `<Header />`
2) `<HeroHoroscopeCard />`
3) `<Section title="Raccourcis">` + 2 `<ShortcutCard/>`
4) `<SectionHeader title="Amour" rightIcon ChevronRight />`
5) `<MiniInsightRow/>` (3 cards)
6) `<BottomNav active="today" />`

---

## 11) Tailwind “ready” (si vous l’utilisez)

### 11.1 Classes utilitaires clés
- Glass surface :
  - `backdrop-blur-[14px]`
  - `bg-[var(--glass)]`
  - `border border-[var(--glass-border)]`
  - `shadow-[var(--shadow-card)]`

- CTA gradient :
  - `bg-[linear-gradient(90deg,var(--cta-l),var(--cta-r))]`

### 11.2 Exemple de HeroCard (structure)
*(code indicatif — l’agent devra ajuster pour matcher le pixel-perfect)*

```tsx
<div className="mt-[18px] rounded-[26px] p-[18px] bg-[var(--glass)] border border-[var(--glass-border)] shadow-[var(--shadow-card)] backdrop-blur-[14px] relative overflow-hidden">
  <div className="flex items-center justify-between">
    <div className="h-[32px] px-[12px] rounded-full bg-[var(--chip)] flex items-center gap-2">
      <span className="text-[13px] font-medium text-[var(--text-1)]">♒</span>
      <span className="text-[13px] font-medium text-[var(--text-1)]">Verseau • 23 fév.</span>
    </div>
    <ChevronRight size={18} strokeWidth={1.75} className="text-[var(--text-2)]" />
  </div>

  <h2 className="mt-[12px] text-[28px] leading-[1.12] font-[650] tracking-[-0.3px] text-[var(--text-1)]">
    Ta journée s’éclaircit<br/>après 14h.
  </h2>

  {/* Constellation overlay (SVG) */}
  <div className="pointer-events-none absolute right-[-20px] top-[60px] opacity-60">
    {/* TODO: SVG constellation */}
  </div>

  <button className="mt-[16px] w-full h-[48px] rounded-full text-white font-[650] text-[16px]
    bg-[linear-gradient(90deg,var(--cta-l),var(--cta-r))]
    shadow-[0_14px_30px_rgba(90,120,255,0.25)]
    flex items-center justify-center gap-2">
    Lire en 2 min <ChevronRight size={18} strokeWidth={1.75} />
  </button>

  <div className="mt-[10px] text-center text-[13px] text-[var(--text-2)]">Version détaillée</div>
</div>
```

---

## 12) Checklist pixel-perfect (à faire valider)

1) **Fond** : le rendu “premium” dépend du mix *gradient + noise + (stars en dark)*  
2) **Radius** : hero/nav très arrondis, cards secondaires plus petites  
3) **CTA** : pill button, gradient doux, pas de bord dur  
4) **Opacity** : textes secondaires toujours via `--text-2/--text-3`  
5) **Nav** : glass pill avec blur, active state très subtil  
6) **Badges couleurs** : uniquement sur quelques points (chat/tirage + 3 mini cards)  
7) **Icons** : Lucide, strokeWidth 1.75, tailles cohérentes

---

## 13) Données statiques (pour coller à la maquette)

Home (exemple) :
- Signe : Verseau
- Date : 23 fév.
- Insight : “Ta journée s’éclaircit après 14h.”
- Raccourcis :
  - Chat astrologue — “En ligne”
  - Tirage du jour — “3 cartes”
- Mini cards :
  - Amour — “Balance dans ta relation”
  - Travail — “Nouvelle opportunité à saisir”
  - Énergie — “Énergie haute, humeur positive”

---

Fin.
