# Passe d’analyse (V3) vs Maquette Originale (Light) — Rapport enrichi + Correctifs (V5)

Référence utilisée : la maquette light originale jointe (écran “Horoscope” premium pastel).  
Implémentation analysée : capture V3 (light).

Objectif : obtenir un rendu **très proche** du visuel original : lisibilité “premium”, profondeur glass, cartes détachées du fond, constellation lumineuse mais intégrée, et mini-cards **très légèrement** teintées (pas des aplats saturés).

---

## 1) Constats mesurables (différences visuelles clés)

### 1.1 Fond global (page) — trop saturé et pas au bon endroit
Dans la maquette originale, le fond est **très clair en haut** (presque blanc rosé) puis descend vers une lavande douce, avec **grain/noise** subtil.

Échantillons (approx) :
- Original top ≈ **#FEF7F9** (254,247,249)  
- V3 top ≈ **#E8D6F9** (232,214,249) → trop violet trop tôt
- Original mid ≈ **#E3D8EC** (227,216,236)  
- V3 mid ≈ **#C2CDFC** (194,205,252) → trop “bleu froid”
- Original bottom ≈ **#C9B9F0** (201,185,240)  
- V3 bottom ≈ **#E4DFF7** (228,223,247) → trop clair en bas (inversion de sensation)

Conclusion : le gradient V3 est “déséquilibré” (haut trop violet, milieu trop bleu, bas trop clair). La maquette est plus homogène, douce, et texturée.

### 1.2 Typographie — problème racine (P0)
Dans la maquette originale :
- Le titre “Horoscope” et les textes sont en **dark ink** (muted violet/noir) → lisibilité + premium.

Échantillon titre :
- Original “Horoscope” ≈ **RGB(123,109,140)** (muted purple dark)
- V3 “Horoscope” ≈ **RGB(221,202,243)** (quasi blanc)

Conclusion : tant que la typo reste blanche en light, l’écran restera “washed out”.

### 1.3 Hero card — structure en 2 niveaux manquante + étoile/noise absent
Dans l’original :
- Hero card glass + **dégradé interne** (lavande) + **sparkle** léger
- Zone CTA posée sur un **sous-panel** (une seconde surface glass arrondie) → profondeur premium

Dans V3 :
- Constellation plus grande (✅) mais
- Texte blanc (❌)
- Manque le sous-panel CTA (❌)
- Manque l’effet sparkle/noise à l’intérieur de la card (souvent absent) (❌)

### 1.4 Raccourcis cards — contraste insuffisant
Échantillon fond carte raccourci :
- Original card ≈ **#F5EFF3** (245,239,243) très proche du blanc (mais détaché du fond)
- V3 card ≈ **#D0BFEA** (208,191,234) trop proche du fond → la carte “se fond”

Conclusion : en light, les cards doivent être **plus blanches** (alpha plus haut) + bordure plus nette + ombre douce.

### 1.5 Mini cards — trop “color block” vs original (P1)
Dans l’original :
- Mini cards sont majoritairement **neutres** (glass clair), avec un **léger** tint et surtout une icône/badge colorée.
Dans V3 :
- Mini cards sont très colorées (rose/bleu/jaune plein) → éloignement de la maquette.

Conclusion : garder l’idée “thématique” mais réduire la couleur à un **wash subtil** (10–18% max), pas un aplat.

### 1.6 Bottom nav — proche mais peut gagner en contraste
Dans l’original :
- Nav pill bien visible (glass), labels lisibles, actif subtil.
Dans V3 :
- OK global, mais avec texte blanc global, l’ensemble reste trop clair.

---

## 2) Correctifs CSS (V5) — précis et actionnables

### 2.1 P0 — Fix définitif de la typographie Light (interdiction du blanc)
1) Stopper toute classe `text-white` en light.
2) Forcer via tokens et classes.

```css
:root{
  --text-1: #1E1B2E;                 /* titres */
  --text-2: rgba(30,27,46,0.72);     /* secondaire */
  --text-3: rgba(30,27,46,0.55);     /* tertiaire */
}

.page{ color: var(--text-1); }
.kicker{ color: var(--text-2); }
.h1{ color: var(--text-1); }
.hero .headline{ color: var(--text-1); }
.section-title{ color: var(--text-1); }
.shortcut-title, .mini-card .card-title{ color: var(--text-1); }
.shortcut-sub, .mini-desc, .small-link{ color: var(--text-2); }
```

Option “match exact” pour le H1 (plus muted comme l’original) :
```css
.h1{ color: rgb(123,109,140); } /* proche original */
```

### 2.2 Fond global — revenir au gradient de l’original + texture
Remplacer les couleurs light par celles qui matchent la ref :

```css
:root{
  --bg-top: #FEF7F9;
  --bg-mid: #E3D8EC;
  --bg-bot: #C9B9F0;
}
```

Et background :
```css
.page.bg-light{
  background:
    radial-gradient(1200px 800px at 20% 10%, rgba(160,120,255,0.18), transparent 55%),
    radial-gradient(900px 700px at 80% 60%, rgba(120,190,255,0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-top) 0%, var(--bg-mid) 58%, var(--bg-bot) 100%);
}
```

Ajouter un noise **obligatoire** :
```css
.page::after{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: url("/noise.png");
  opacity: 0.08;
  mix-blend-mode: soft-light;
}
```

### 2.3 Hero card — recréer la profondeur originale (panel CTA + sparkle)
1) Hero glass :
```css
.hero{
  border-radius: 26px;
  padding: 18px;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.66);
  box-shadow: 0 18px 40px rgba(20,20,40,0.12);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  position: relative;
  overflow: hidden;
}
```

2) Dégradé interne (lavande) :
```css
.hero::before{
  content:"";
  position:absolute; inset:0;
  pointer-events:none;
  background:
    radial-gradient(700px 420px at 75% 40%, rgba(160,120,255,0.18), transparent 60%),
    radial-gradient(520px 380px at 25% 10%, rgba(120,190,255,0.10), transparent 62%);
}
```

3) Sparkle/stars **dans la card** (optionnel mais recommandé pour matcher l’original) :
```css
.hero::after{
  content:"";
  position:absolute; inset:0;
  pointer-events:none;
  background-image: url("/sparkles.png"); /* ou un starfield léger */
  opacity: 0.18;
  mix-blend-mode: overlay;
}
```

4) Sous-panel CTA (la maquette originale a 2 niveaux) :
```css
.hero .cta-panel{
  margin-top: 14px;
  padding: 14px;
  border-radius: 22px;
  background: rgba(255,255,255,0.34);
  border: 1px solid rgba(255,255,255,0.55);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
```

Puis mettre le bouton **à l’intérieur** de `.cta-panel`.

### 2.4 Constellation — taille et glow (mais ne pas écraser le texte)
Dans l’original, la constellation est visible mais pas agressive.

```css
.hero .constellation{
  position:absolute;
  right: -20px;
  top: 70px;
  width: 240px;
  opacity: 0.55; /* baisser si ça gêne le texte */
  filter: drop-shadow(0 10px 22px rgba(170,140,255,0.22));
  pointer-events:none;
}
```

### 2.5 Raccourcis cards — augmenter contraste (cards plus “blanches”)
```css
.shortcut-card{
  border-radius: 18px;
  padding: 14px;
  background: rgba(255,255,255,0.62);          /* plus blanc */
  border: 1px solid rgba(255,255,255,0.72);    /* plus net */
  box-shadow: 0 14px 28px rgba(20,20,40,0.12);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
```

Badges un peu plus “présents” mais pas énormes (original = moyen) :
```css
.badge{
  width: 40px; height: 40px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.60);
}
```

### 2.6 Mini cards — revenir au style original : glass neutre + wash subtil
1) Base neutre :
```css
.mini-card{
  border-radius: 18px;
  padding: 14px;
  background: rgba(255,255,255,0.40);
  border: 1px solid rgba(255,255,255,0.60);
  box-shadow: 0 14px 28px rgba(20,20,40,0.10);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  position: relative;
  overflow: hidden;
}
```

2) Wash subtil par thème (10–18% max) :
```css
.mini-card::before{
  content:"";
  position:absolute; inset:-40px;
  pointer-events:none;
  opacity: 0.16; /* <= clé pour ne pas faire “color block” */
}

.mini-card.love::before{ background: linear-gradient(180deg, #F3B5D6, #E69BC6); }
.mini-card.work::before{ background: linear-gradient(180deg, #B9C7FF, #9FB2F4); }
.mini-card.energy::before{ background: linear-gradient(180deg, #F9DEB2, #F0C98F); }
```

3) Badge icône coloré (dans l’original, c’est la “vraie” couleur) :
```css
.mini-badge{
  width: 36px; height: 36px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.55);
}
.mini-badge.love{ background: #EBA4C9; }
.mini-badge.work{ background: #AABEEF; }
.mini-badge.energy{ background: #F6D2A7; }
```

### 2.7 Bottom nav — lisibilité et actif subtil
```css
.bottom-nav{
  background: rgba(255,255,255,0.58);
  border: 1px solid rgba(255,255,255,0.70);
  box-shadow: 0 10px 30px rgba(20,20,40,0.18);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
.nav-item{ color: var(--text-2); }
.nav-item.active{
  color: var(--text-1);
  background: rgba(134,108,208,0.16);
}
```

---

## 3) Dark toggle (rappel P0)
Il faut pouvoir afficher la page dark pour valider la convergence globale (token `.dark` + stars background).  
Implémentation : toggle + persistence `localStorage` + classe `.dark` sur `<html>`.

---

## 4) DoD — Validation visuelle vs original
1) **H1 et headline lisibles** en light (dark ink, jamais blanc).  
2) Fond : haut quasi blanc rosé, bas lavande doux + noise.  
3) Hero : 2 niveaux (card + panel CTA) + sparkle interne léger.  
4) Raccourcis : cartes plus blanches que le fond (vraie séparation).  
5) Mini cards : plus neutres (wash subtil), badge coloré, pas d’aplats saturés.  
6) Bottom nav : labels lisibles + actif subtil.

---

## 5) Assets recommandés
- `/public/noise.png` (512×512, alpha faible)  
- `/public/sparkles.png` (optionnel, très subtil)  
- `/public/constellation.svg`

Fin.
