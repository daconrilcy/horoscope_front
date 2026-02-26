# Horoscope Home — Guidelines V3 (Design + CSS)  
**Scope**: Page d’accueil “Aujourd’hui / Horoscope” en **Light** + **Dark**.  
**But**: retrouver le rendu **premium** de la maquette initiale (fond saturé + sparkle/stars, hero card très “cosmic”, mini cards colorées par thème, raccourcis contrastés, bottom nav glass pill).

---

## 0) Différences constatées (V2 actuelle) vs cible (maquette initiale)
1) **Fond de page**  
- Actuel: lavande très pâle, quasi blanc  
- Cible: **gradient violet/lavande riche** + **texture sparkle/étoilée** visible sur toute la page.

2) **Hero card (constellation)**  
- Actuel: petite constellation discrète  
- Cible: **grande constellation lumineuse** occupant la carte, points “glowing”, lignes claires, et **fond dégradé violet profond dans la carte**.

3) **Mini cards Amour/Travail/Énergie**  
- Actuel: cartes blanches plates  
- Cible: cartes glass **avec gradient coloré individuel** (Amour=rose, Travail=bleu, Énergie=jaune/or).

4) **Raccourcis cards**  
- Actuel: peu de contraste + petits badges  
- Cible: cartes plus “présentes” (glass + shadow), **badges plus grands**.

5) **Avatar** (non prioritaire)  
- Actuel: initiale  
- Cible: photo utilisateur.

---

## 1) P0 — Bloquants à corriger immédiatement
### 1.1 Dark toggle (obligatoire)
- Ajout d’un toggle dans Header ou Profil.  
- Persisté dans `localStorage`.  
- Applique `.dark` sur `<html>`.

### 1.2 Contraste typographique Light (interdiction du blanc)
En light, **H1**, **headline**, **titres**, **labels** doivent utiliser `--text-1/2/3` (encre foncée).  
Interdit : `color: white` ou `opacity` globale sur wrapper.

### 1.3 Interdiction d’opacité globale
Ne jamais faire `opacity: <1` sur un conteneur parent (cela “délave” tout).  
Si besoin d’un voile, utiliser un pseudo-élément `::before` avec `rgba()`.

---

## 2) Design tokens — CSS variables (obligatoire)
Créer `src/styles/theme.css`. Les tokens ci-dessous sont calibrés pour être **plus saturés** (fond global) et pour permettre les **gradients intra-cards**.

### 2.1 Light Premium Pastel (plus riche/saturé)
```css
:root{
  --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, system-ui, sans-serif;

  /* Text: dark ink (CRITIQUE) */
  --text-1: #1E1B2E;
  --text-2: rgba(30,27,46,0.72);
  --text-3: rgba(30,27,46,0.55);

  /* Global background (more saturated than V2) */
  --bg-top: #F6E9F8;
  --bg-mid: #D2BCE8;
  --bg-bot: #BEB0F0;

  /* Glass */
  --glass: rgba(255,255,255,0.52);
  --glass-2: rgba(255,255,255,0.40);
  --glass-border: rgba(255,255,255,0.66);

  /* CTA */
  --cta-l: #866CD0;
  --cta-r: #A190ED;

  /* Chip */
  --chip: #C6B9E5;

  /* Nav */
  --nav-glass: rgba(255,255,255,0.55);
  --nav-border: rgba(255,255,255,0.66);

  /* Shadows */
  --shadow-hero: 0 18px 40px rgba(20,20,40,0.14);
  --shadow-card: 0 14px 28px rgba(20,20,40,0.12);
  --shadow-nav:  0 10px 30px rgba(20,20,40,0.18);

  /* Accent badges (raccourcis) */
  --badge-chat: #E1F0EA;
  --badge-draw: #F8CAA5;

  /* Status */
  --status-online: #1F9D7A;

  /* Mini-card gradients (KEY: per-card color) */
  --love-g1: #F3B5D6;
  --love-g2: #E69BC6;

  --work-g1: #B9C7FF;
  --work-g2: #9FB2F4;

  --energy-g1: #F9DEB2;
  --energy-g2: #F0C98F;

  /* Hero-card gradient background (within card) */
  --hero-g1: rgba(172,132,255,0.28);
  --hero-g2: rgba(110,170,255,0.18);
}
```

### 2.2 Dark Cosmic
```css
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

  --shadow-hero: 0 18px 40px rgba(0,0,0,0.45);
  --shadow-card: 0 14px 28px rgba(0,0,0,0.40);
  --shadow-nav:  0 10px 30px rgba(0,0,0,0.55);

  --badge-chat: #E4F2EC;
  --badge-draw: #D5946A;

  --status-online: #2AD1A3;

  /* Mini-card gradients (richer in dark) */
  --love-g1: rgba(231,121,180,0.28);
  --love-g2: rgba(160,70,130,0.18);

  --work-g1: rgba(168,172,239,0.26);
  --work-g2: rgba(90,110,220,0.16);

  --energy-g1: rgba(229,178,112,0.26);
  --energy-g2: rgba(170,110,40,0.16);

  --hero-g1: rgba(160,120,255,0.22);
  --hero-g2: rgba(90,170,255,0.14);
}
```

---

## 3) Fond global (page) — plus “rich” + sparkle/stars
Créer `src/styles/home-bg.css`.

### 3.1 Base layout
```css
.page{
  font-family: var(--font-sans);
  min-height: 100dvh;
  padding: 22px 18px 110px; /* réserve bottom nav */
  color: var(--text-1);
}
```

### 3.2 Background gradients (light & dark)
```css
.page.bg-light{
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.22), transparent 55%),
    radial-gradient(900px 700px at 80% 60%, rgba(120,190,255,0.12), transparent 60%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 55%, var(--bg-bot) 100%);
}

.page.bg-dark{
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.24), transparent 55%),
    radial-gradient(900px 700px at 80% 60%, rgba(90,170,255,0.16), transparent 60%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 55%, var(--bg-bot) 100%);
}
```

### 3.3 Texture overlay (RECOMMANDÉ)
- Light: `noise.png` + micro sparkles (optionnel `sparkles.png`)  
- Dark: `stars.png` + `noise.png`

```css
/* Noise (both) */
.page::after{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: url("/noise.png");
  opacity: 0.08;
  mix-blend-mode: soft-light;
}

/* Stars in dark (critical for cosmic) */
.dark .page::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: url("/stars.png"); /* tileable */
  background-size: 700px 700px;
  opacity: 0.45;
}
```

⚠️ Interdit: “bokeh bubbles” (gros ronds flottants).

---

## 4) Typographie — tailles/poids exacts
```css
.kicker{ font-size:13px; font-weight:500; letter-spacing:.2px; color:var(--text-2); text-align:center; }

.h1{
  font-size:40px; font-weight:650; line-height:1.05; letter-spacing:-.5px;
  color:var(--text-1); text-align:center;
}

.section-title{ margin-top:18px; font-size:18px; font-weight:650; color:var(--text-1); }

.card-title{ font-size:15px; font-weight:650; color:var(--text-1); }

.card-subtitle{ font-size:13px; font-weight:500; color:var(--text-2); }

.small-link{ font-size:13px; font-weight:500; color:var(--text-2); text-decoration:none; text-align:center; }
```

---

## 5) Glassmorphism — recette exacte (à appliquer partout)
Règle: une card “glass premium” = **background translucide + border + shadow + blur**.

```css
.glass{
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.glass-soft{
  background: var(--glass-2);
  border: 1px solid rgba(255,255,255,0.45); /* light */
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
.dark .glass-soft{
  border: 1px solid rgba(255,255,255,0.10);
}
```

---

## 6) Hero card — fond violet + grande constellation lumineuse (P0)
Le hero est la “pièce” principale: il doit être plus profond, plus cosmique.

Créer `src/styles/hero.css`.

```css
.hero{
  margin-top:18px;
  border-radius:26px;
  padding:18px;
  position:relative;
  overflow:hidden;

  /* glass base */
  background: var(--glass);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-hero);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

/* Hero internal gradient wash (gives rich violet depth) */
.hero::before{
  content:"";
  position:absolute;
  inset:0;
  pointer-events:none;
  background:
    radial-gradient(700px 420px at 75% 40%, var(--hero-g1), transparent 60%),
    radial-gradient(520px 380px at 25% 10%, var(--hero-g2), transparent 62%);
  opacity: 1;
}

/* Chip row */
.hero .toprow{ display:flex; align-items:center; justify-content:space-between; position:relative; z-index:2; }

.hero .chip{
  height:32px;
  padding:0 12px;
  border-radius:999px;
  background: var(--chip);
  display:inline-flex;
  align-items:center;
  gap:8px;
  font-size:13px;
  font-weight:500;
  color: var(--text-1);
}

/* Headline */
.hero .headline{
  position:relative; z-index:2;
  margin-top:12px;
  font-size:28px;
  font-weight:650;
  line-height:1.12;
  letter-spacing:-.3px;
  color: var(--text-1);
}

/* Constellation overlay: MUST be LARGE + glowing */
.hero .constellation{
  position:absolute;
  right:-40px;
  top:35px;
  width: 220px;         /* bigger than current */
  height: 160px;
  opacity:0.68;
  pointer-events:none;
  z-index:1;

  /* glow */
  filter:
    drop-shadow(0 10px 22px rgba(170,140,255,0.35))
    drop-shadow(0 6px 14px rgba(255,255,255,0.25));
  mix-blend-mode: screen; /* gives luminous feel on dark & light */
}

/* CTA */
.hero .cta{
  position:relative; z-index:2;
  margin-top:16px;
  width:100%;
  height:48px;
  border:0;
  border-radius:999px;
  background: linear-gradient(90deg, var(--cta-l), var(--cta-r));
  color: rgba(255,255,255,0.95);
  font-size:16px;
  font-weight:650;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  box-shadow: 0 14px 30px rgba(90,120,255,0.25);
}
.dark .hero .cta{ box-shadow: 0 14px 30px rgba(0,0,0,0.35); }

.hero .detail{
  position:relative; z-index:2;
  margin-top:10px;
  font-size:13px;
  font-weight:500;
  color: var(--text-2);
  text-align:center;
  text-decoration:none;
}
```

Constellation asset: `constellation.svg` (points + lines).  
Recommandation SVG: traits blancs 1.2–1.5px, points avec blur/glow léger.

---

## 7) Raccourcis cards — plus de contraste + badges plus grands
Créer `src/styles/shortcuts.css`.

```css
.shortcuts-grid{
  margin-top:10px;
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
}

.shortcut-card{
  border-radius:18px;
  padding:14px;
  background: var(--glass-2);
  border: 1px solid rgba(255,255,255,0.58);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
.dark .shortcut-card{
  border: 1px solid rgba(255,255,255,0.10);
}

.shortcut-row{ display:flex; gap:12px; align-items:center; }

.badge{
  width:44px;           /* bigger than current */
  height:44px;
  border-radius:16px;
  display:grid;
  place-items:center;
  border: 1px solid rgba(255,255,255,0.55);
  box-shadow: 0 10px 18px rgba(20,20,40,0.10);
}

.badge.chat{ background: var(--badge-chat); }
.badge.draw{ background: var(--badge-draw); }

.shortcut-title{
  font-size:15px;
  font-weight:650;
  color: var(--text-1);
  text-decoration:none;
}
.shortcut-sub{
  font-size:13px;
  font-weight:500;
  color: var(--text-2);
  text-decoration:none;
}
.shortcut-sub.online{ color: var(--status-online); }
```

---

## 8) Mini cards — glass + gradient thématique (P0)
Créer `src/styles/mini-cards.css`.

```css
.mini-grid{
  margin-top:10px;
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:12px;
}

.mini-card{
  border-radius:18px;
  padding:14px;
  position:relative;
  overflow:hidden;

  /* glass base */
  background: var(--glass-2);
  border: 1px solid rgba(255,255,255,0.58);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
.dark .mini-card{ border: 1px solid rgba(255,255,255,0.10); }

/* Color gradient wash INSIDE the card (this is the key difference vs flat white) */
.mini-card::before{
  content:"";
  position:absolute;
  inset:-30px; /* let gradient bleed */
  pointer-events:none;
  opacity:0.95;
  filter: blur(0px);
}

/* Per-type gradients */
.mini-card.love::before{
  background: radial-gradient(220px 180px at 30% 10%, rgba(255,255,255,0.25), transparent 60%),
              linear-gradient(180deg, var(--love-g1), var(--love-g2));
}
.mini-card.work::before{
  background: radial-gradient(220px 180px at 30% 10%, rgba(255,255,255,0.22), transparent 60%),
              linear-gradient(180deg, var(--work-g1), var(--work-g2));
}
.mini-card.energy::before{
  background: radial-gradient(220px 180px at 30% 10%, rgba(255,255,255,0.18), transparent 60%),
              linear-gradient(180deg, var(--energy-g1), var(--energy-g2));
}

/* Content above gradient */
.mini-content{ position:relative; z-index:2; }

.mini-badge{
  width:36px;
  height:36px;
  border-radius:14px;
  display:grid;
  place-items:center;
  background: rgba(255,255,255,0.26); /* neutral glass badge */
  border: 1px solid rgba(255,255,255,0.55);
  margin-bottom:10px;
}

.mini-desc{
  font-size:13px;
  font-weight:500;
  color: var(--text-2);
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
}
```

Remarque: on peut garder des badges “neutres” (translucides) ou colorés; le plus important est **le gradient de fond de la card**.

---

## 9) Bottom nav — glass pill + active state subtil
Créer `src/styles/bottom-nav.css`.

```css
.bottom-nav{
  position:fixed;
  left:16px;
  right:16px;
  bottom:16px;
  padding:10px;
  border-radius:24px;
  background: var(--nav-glass);
  border: 1px solid var(--nav-border);
  box-shadow: var(--shadow-nav);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.bottom-nav .row{
  display:flex;
  gap:6px;
  justify-content:space-between;
}

.nav-item{
  flex:1;
  border:0;
  background:transparent;
  border-radius:18px;
  padding:10px 8px;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:6px;
  color: var(--text-2);
}

.nav-item span{
  font-size:12px;
  font-weight:500;
  letter-spacing:.2px;
}

.nav-item.active{
  background: rgba(134,108,208,0.18);
  color: var(--text-1);
}
.dark .nav-item.active{
  background: rgba(150,110,255,0.18);
  color: var(--text-1);
}
```

---

## 10) Icônes (Lucide) — règles & mapping
Installer:
```bash
npm i lucide-react
```

Règles:
- `strokeWidth = 1.75`
- size: 24 (nav), 20 (badges/cards), 18 (CTA chevron)

Mapping:
- Aujourd’hui `CalendarDays`
- Chat `MessageCircle`
- Thème `Star`
- Tirages `Layers`
- Profil `User`
- Chevron `ChevronRight`
- Mini cards: `Heart`, `Briefcase`, `Zap`

---

## 11) Dark toggle — implémentation TypeScript (à copier-coller)
```ts
export function setTheme(theme: "light" | "dark") {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else root.classList.remove("dark");
  localStorage.setItem("theme", theme);
}

export function initTheme() {
  const saved = localStorage.getItem("theme") as "light" | "dark" | null;
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  setTheme(saved ?? (prefersDark ? "dark" : "light"));
}
```

---

## 12) Checklist DoD (validation finale)
- Light: **texte lisible** (H1/headline dark ink, pas blanc).  
- Fond: gradient plus riche + noise; dark: stars visibles (pas bokeh).  
- Hero: fond violet riche + **constellation grande & glowing**.  
- Raccourcis: contraste OK + badges **44px** + aucun underline.  
- Mini cards: gradients par thème visibles + profondeur (shadow + border + blur).  
- CTA: gradient + glow.  
- Bottom nav: glass pill + active state subtil.  
- Toggle Dark fonctionne et affiche le thème dark.

---

## 13) Assets recommandés
- `/public/noise.png` (512x512, alpha faible)  
- `/public/stars.png` (tileable, 1024x1024)  
- `/public/constellation.svg` (points + lignes, 1 couleur)

Fin.
