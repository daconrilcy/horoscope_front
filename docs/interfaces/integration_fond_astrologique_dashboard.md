# Intégration d'un fond astrologique animé pour le dashboard

## 1. Objectif

Créer un fond premium, doux et vivant pour la page **Dashboard** de l'application, afin d'illustrer l'**humeur astrologique du jour**.

Le rendu recherché n'est pas un ciel profond réaliste, mais une **surface éditoriale lumineuse** inspirée du visuel fourni :

- fond clair nacré / lavande / mauve,
- large zone vide à gauche pour le texte,
- constellation lumineuse positionnée majoritairement à droite,
- micro-animation quasi imperceptible,
- variation quotidienne selon le signe astrologique, l'utilisateur et la date,
- légère variation colorimétrique en fonction du score global de la journée.

---

## 2. Direction visuelle retenue

À partir de l'image d'inspiration, la bonne direction est la suivante :

- **base très claire** : blanc rosé, lilas, lavande, violet doux,
- **constellation stylisée** : représentation graphique inspirée du signe, pas une carte astronomique scientifique,
- **mise en page asymétrique** : le visuel doit laisser l'espace texte respirer à gauche,
- **halo des étoiles** : glow doux, léger bloom, pas d'effet agressif,
- **animation lente** : scintillement, respiration, micro-dérive,
- **variation quotidienne contrôlée** : le fond ne doit jamais sembler totalement aléatoire ni totalement figé.

Le résultat attendu est un composant d'interface premium, cohérent avec une page de résumé astrologique haut de gamme.

---

## 3. Choix technique recommandé

### Pourquoi utiliser un `canvas` 2D

Le meilleur compromis pour cette V1 est :

- **fond principal en CSS** pour garder un dégradé net, facile à régler,
- **surcouche animée en Canvas 2D** pour dessiner :
  - les étoiles diffuses,
  - les halos,
  - la constellation,
  - les micro-animations.

### Pourquoi ce choix est pertinent

Cette architecture permet de :

- séparer le visuel stable du visuel vivant,
- limiter la charge CPU/GPU,
- garder un code lisible,
- piloter finement les variations du jour,
- intégrer facilement le composant dans React.

---

## 4. Principes de fonctionnement

Le composant repose sur 4 couches :

### 4.1 Fond de base

Un dégradé horizontal très clair :

- gauche : blanc rosé / ivoire,
- centre : lilas très doux,
- droite : lavande / mauve plus présent.

Le fond peut rester en CSS.

### 4.2 Brume lumineuse

De grands halos radiaux, très diffus, donnent une sensation de matière lumineuse.

### 4.3 Champ stellaire secondaire

Une multitude de petites étoiles discrètes, légèrement scintillantes, crée de la profondeur.

### 4.4 Constellation du signe

Quelques étoiles principales plus brillantes, reliées par des lignes fines, forment une signature propre au signe astrologique.

---

## 5. Variables métier à injecter

Le composant doit être piloté par les données suivantes :

### `sign`
Le signe astrologique principal de l'utilisateur.

Exemples :

- `aries`
- `taurus`
- `gemini`
- `cancer`
- `leo`
- `virgo`
- `libra`
- `scorpio`
- `sagittarius`
- `capricorn`
- `aquarius`
- `pisces`

### `userId`
Sert à personnaliser la graine de génération.

### `dateKey`
Date du jour, par exemple `2026-03-14`.

### `dayScore`
Score global de la journée, sur une échelle comme `1..20`.

Il sert à piloter la couleur des halos et la tonalité globale :

- `1..7` : journée plus tendue,
- `8..14` : journée équilibrée,
- `15..20` : journée fluide et favorable.

---

## 6. Logique de variation quotidienne

Le composant ne doit pas produire un rendu totalement aléatoire à chaque re-render.

Il faut un comportement **déterministe à la journée**.

### Principe

Créer une seed à partir de :

```txt
userId + sign + dateKey
```

Exemple :

```txt
user-123|taurus|2026-03-14
```

Cette seed sert à générer :

- la position fine des étoiles,
- l'écart léger autour du motif de base,
- la densité du champ secondaire,
- la taille des halos,
- la phase d'animation.

### Avantage

Avec ce modèle :

- le rendu reste stable toute la journée,
- il change d'un jour à l'autre,
- deux utilisateurs du même signe ne voient pas exactement le même fond,
- la variation reste contrôlée.

---

## 7. Logique de couleur selon l'humeur du jour

L'image doit rester élégante.

Il faut éviter de passer d'un blanc subtil à un rouge agressif.

### Recommandation

#### Journée difficile (`dayScore <= 7`)

- base : blanche / lilas froide,
- glow : rose froid / magenta feutré,
- ligne : un peu moins lumineuse.

#### Journée neutre (`8 <= dayScore <= 14`)

- palette équilibrée,
- halos blancs, lavande, bleu très doux.

#### Journée favorable (`dayScore >= 15`)

- fond plus lumineux,
- étoiles très blanches,
- halo bleu glacé / violet doux,
- impression plus claire et ouverte.

---

## 8. Répartition spatiale du visuel

Pour coller au visuel d'inspiration :

- la constellation doit vivre entre **60% et 100% de la largeur**,
- les petites étoiles peuvent exister partout, mais restent plus denses à droite,
- la zone gauche doit rester plus respirante pour le texte,
- le point visuel fort doit se trouver dans le tiers supérieur droit.

---

## 9. Animation recommandée

L'animation doit rester très douce.

### Effets à conserver

- scintillement lent,
- micro-dérive de quelques pixels,
- très légère pulsation des étoiles principales,
- respiration douce de la brume.

### Effets à éviter

- déplacement rapide,
- particules trop nombreuses,
- clignotement franc,
- rotation globale du fond,
- mouvement visible au premier coup d'oeil.

Le composant doit donner l'impression d'un visuel vivant, pas d'une animation décorative tapageuse.

---

## 10. Architecture React recommandée

### Structure

Le composant encapsule :

- un conteneur principal avec le dégradé CSS,
- un `<canvas>` absolu plein cadre,
- un conteneur `children` au-dessus.

### Hooks à utiliser

- `useRef` pour accéder au canvas DOM,
- `useEffect` pour initialiser l'animation et nettoyer les ressources,
- `ResizeObserver` pour recalculer la scène quand la taille du bloc change.

### Points d'attention

- gérer correctement le nettoyage au démontage,
- annuler le `requestAnimationFrame`,
- déconnecter le `ResizeObserver`,
- supporter `prefers-reduced-motion`.

---

## 11. Contrat de props recommandé

```ts
export type ZodiacSign =
  | "aries"
  | "taurus"
  | "gemini"
  | "cancer"
  | "leo"
  | "virgo"
  | "libra"
  | "scorpio"
  | "sagittarius"
  | "capricorn"
  | "aquarius"
  | "pisces";

export type AstroMoodBackgroundProps = {
  sign: ZodiacSign;
  userId: string;
  dateKey: string;  // ex: "2026-03-14"
  dayScore?: number; // ex: 1..20
  className?: string;
  children?: React.ReactNode;
};
```

---

## 12. Code proposé — composant complet React + TypeScript

```tsx
import React, { PropsWithChildren, useEffect, useRef } from "react";

type ZodiacSign =
  | "aries"
  | "taurus"
  | "gemini"
  | "cancer"
  | "leo"
  | "virgo"
  | "libra"
  | "scorpio"
  | "sagittarius"
  | "capricorn"
  | "aquarius"
  | "pisces";

type Props = PropsWithChildren<{
  sign: ZodiacSign;
  userId: string;
  dateKey: string; // ex: "2026-03-14"
  dayScore?: number; // 1..20
  className?: string;
}>;

type Point = { x: number; y: number };
type Star = {
  x: number;
  y: number;
  r: number;
  alpha: number;
  twinkleSpeed: number;
  twinkleOffset: number;
  driftX: number;
  driftY: number;
};
type MainStar = {
  x: number;
  y: number;
  r: number;
  pulseSpeed: number;
  pulseOffset: number;
  wobbleX: number;
  wobbleY: number;
};

const SIGN_PATTERNS: Record<ZodiacSign, { points: Point[]; links: [number, number][] }> = {
  aries: {
    points: [
      { x: 0.64, y: 0.34 },
      { x: 0.72, y: 0.27 },
      { x: 0.80, y: 0.31 },
      { x: 0.87, y: 0.24 },
      { x: 0.94, y: 0.18 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4]],
  },
  taurus: {
    points: [
      { x: 0.63, y: 0.33 },
      { x: 0.71, y: 0.25 },
      { x: 0.79, y: 0.27 },
      { x: 0.84, y: 0.39 },
      { x: 0.90, y: 0.28 },
      { x: 0.96, y: 0.20 },
    ],
    links: [[0, 1], [1, 2], [2, 4], [2, 3], [4, 5]],
  },
  gemini: {
    points: [
      { x: 0.68, y: 0.20 },
      { x: 0.68, y: 0.50 },
      { x: 0.78, y: 0.24 },
      { x: 0.78, y: 0.54 },
      { x: 0.89, y: 0.20 },
      { x: 0.89, y: 0.50 },
    ],
    links: [[0, 1], [2, 3], [4, 5], [0, 2], [2, 4], [1, 3], [3, 5]],
  },
  cancer: {
    points: [
      { x: 0.66, y: 0.29 },
      { x: 0.75, y: 0.22 },
      { x: 0.82, y: 0.31 },
      { x: 0.87, y: 0.19 },
      { x: 0.95, y: 0.27 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [2, 4]],
  },
  leo: {
    points: [
      { x: 0.63, y: 0.32 },
      { x: 0.71, y: 0.26 },
      { x: 0.79, y: 0.29 },
      { x: 0.85, y: 0.22 },
      { x: 0.90, y: 0.34 },
      { x: 0.97, y: 0.26 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5]],
  },
  virgo: {
    points: [
      { x: 0.65, y: 0.20 },
      { x: 0.69, y: 0.35 },
      { x: 0.75, y: 0.46 },
      { x: 0.81, y: 0.29 },
      { x: 0.89, y: 0.47 },
      { x: 0.96, y: 0.31 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
  },
  libra: {
    points: [
      { x: 0.64, y: 0.38 },
      { x: 0.73, y: 0.28 },
      { x: 0.82, y: 0.24 },
      { x: 0.90, y: 0.28 },
      { x: 0.98, y: 0.38 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4]],
  },
  scorpio: {
    points: [
      { x: 0.64, y: 0.24 },
      { x: 0.71, y: 0.35 },
      { x: 0.78, y: 0.25 },
      { x: 0.85, y: 0.39 },
      { x: 0.92, y: 0.29 },
      { x: 0.98, y: 0.18 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
  },
  sagittarius: {
    points: [
      { x: 0.63, y: 0.38 },
      { x: 0.74, y: 0.29 },
      { x: 0.84, y: 0.18 },
      { x: 0.87, y: 0.43 },
      { x: 0.95, y: 0.31 },
    ],
    links: [[0, 1], [1, 2], [1, 3], [3, 4]],
  },
  capricorn: {
    points: [
      { x: 0.64, y: 0.39 },
      { x: 0.73, y: 0.27 },
      { x: 0.81, y: 0.34 },
      { x: 0.89, y: 0.19 },
      { x: 0.97, y: 0.25 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4]],
  },
  aquarius: {
    points: [
      { x: 0.62, y: 0.27 },
      { x: 0.70, y: 0.33 },
      { x: 0.78, y: 0.27 },
      { x: 0.86, y: 0.35 },
      { x: 0.94, y: 0.29 },
      { x: 0.99, y: 0.38 },
    ],
    links: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
  },
  pisces: {
    points: [
      { x: 0.67, y: 0.20 },
      { x: 0.67, y: 0.49 },
      { x: 0.82, y: 0.34 },
      { x: 0.96, y: 0.20 },
      { x: 0.96, y: 0.49 },
    ],
    links: [[0, 1], [0, 2], [1, 2], [2, 3], [2, 4]],
  },
};

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function hashString(input: string): number {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(seed: number) {
  let t = seed >>> 0;
  return function next() {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function range(rand: () => number, min: number, max: number) {
  return min + (max - min) * rand();
}

function biasRight(rand: () => number) {
  return 1 - Math.pow(rand(), 1.85);
}

function getPalette(dayScore: number) {
  const score = clamp(dayScore, 1, 20);

  if (score <= 7) {
    return {
      left: "#fbf7f8",
      right: "#d9cafb",
      mist: "rgba(196, 173, 255, 0.22)",
      starCore: "rgba(255,255,255,0.98)",
      starGlow: "rgba(255, 190, 220, 0.26)",
      starGlow2: "rgba(171, 197, 255, 0.20)",
      line: "rgba(255,255,255,0.48)",
    };
  }

  if (score >= 15) {
    return {
      left: "#fffaf9",
      right: "#cdc1ff",
      mist: "rgba(189, 176, 255, 0.24)",
      starCore: "rgba(255,255,255,1)",
      starGlow: "rgba(196, 224, 255, 0.30)",
      starGlow2: "rgba(255, 220, 255, 0.24)",
      line: "rgba(255,255,255,0.56)",
    };
  }

  return {
    left: "#fcf8f9",
    right: "#d5c9fb",
    mist: "rgba(192, 178, 255, 0.23)",
    starCore: "rgba(255,255,255,0.99)",
    starGlow: "rgba(206, 225, 255, 0.24)",
    starGlow2: "rgba(255, 205, 235, 0.20)",
    line: "rgba(255,255,255,0.52)",
  };
}

export default function AstroMoodBackground({
  sign,
  userId,
  dateKey,
  dayScore = 12,
  className,
  children,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const seed = hashString(`${userId}|${sign}|${dateKey}`);
    const rand = mulberry32(seed);
    const palette = getPalette(dayScore);
    const pattern = SIGN_PATTERNS[sign];

    let width = 0;
    let height = 0;
    let dpr = 1;
    let animationId = 0;

    const fieldStars: Star[] = [];
    const mainStars: MainStar[] = [];
    const dustStars: Star[] = [];
    const mistBlobs: Array<{ x: number; y: number; radius: number; alpha: number }> = [];

    function rebuildScene() {
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = Math.max(1, Math.floor(rect.width * dpr));
      height = Math.max(1, Math.floor(rect.height * dpr));

      canvas.width = width;
      canvas.height = height;

      fieldStars.length = 0;
      mainStars.length = 0;
      dustStars.length = 0;
      mistBlobs.length = 0;

      const areaFactor = (width * height) / 320000;

      for (let i = 0; i < Math.round(70 * areaFactor); i++) {
        fieldStars.push({
          x: biasRight(rand) * 0.58 + 0.38,
          y: range(rand, 0.06, 0.94),
          r: range(rand, 0.7, 1.8) * dpr,
          alpha: range(rand, 0.24, 0.85),
          twinkleSpeed: range(rand, 0.35, 1.1),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -0.9, 0.9) * dpr,
          driftY: range(rand, -0.8, 0.8) * dpr,
        });
      }

      for (let i = 0; i < Math.round(120 * areaFactor); i++) {
        dustStars.push({
          x: range(rand, 0.10, 0.98),
          y: range(rand, 0.08, 0.92),
          r: range(rand, 0.3, 0.9) * dpr,
          alpha: range(rand, 0.08, 0.35),
          twinkleSpeed: range(rand, 0.25, 0.7),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -0.2, 0.2) * dpr,
          driftY: range(rand, -0.2, 0.2) * dpr,
        });
      }

      for (const p of pattern.points) {
        mainStars.push({
          x: p.x + range(rand, -0.018, 0.018),
          y: p.y + range(rand, -0.018, 0.018),
          r: range(rand, 2.4, 4.1) * dpr,
          pulseSpeed: range(rand, 0.45, 0.95),
          pulseOffset: range(rand, 0, Math.PI * 2),
          wobbleX: range(rand, -1.8, 1.8) * dpr,
          wobbleY: range(rand, -1.8, 1.8) * dpr,
        });
      }

      for (let i = 0; i < 3; i++) {
        mistBlobs.push({
          x: range(rand, 0.55, 0.95),
          y: range(rand, 0.10, 0.70),
          radius: range(rand, width * 0.11, width * 0.24),
          alpha: range(rand, 0.05, 0.11),
        });
      }
    }

    function drawBackground(time: number) {
      const linear = ctx.createLinearGradient(0, 0, width, 0);
      linear.addColorStop(0, palette.left);
      linear.addColorStop(0.45, "#efe6f7");
      linear.addColorStop(1, palette.right);

      ctx.fillStyle = linear;
      ctx.fillRect(0, 0, width, height);

      for (const mist of mistBlobs) {
        const breath = 1 + 0.04 * Math.sin(time * 0.00045 + mist.x * 10);
        const radial = ctx.createRadialGradient(
          mist.x * width,
          mist.y * height,
          0,
          mist.x * width,
          mist.y * height,
          mist.radius * breath
        );
        radial.addColorStop(0, `rgba(255,255,255,${mist.alpha})`);
        radial.addColorStop(0.5, palette.mist);
        radial.addColorStop(1, "rgba(255,255,255,0)");

        ctx.fillStyle = radial;
        ctx.beginPath();
        ctx.arc(mist.x * width, mist.y * height, mist.radius * breath, 0, Math.PI * 2);
        ctx.fill();
      }

      const rightGlow = ctx.createRadialGradient(
        width * 0.88,
        height * 0.32,
        0,
        width * 0.88,
        height * 0.32,
        width * 0.45
      );
      rightGlow.addColorStop(0, "rgba(255,255,255,0.22)");
      rightGlow.addColorStop(0.45, "rgba(224,210,255,0.18)");
      rightGlow.addColorStop(1, "rgba(255,255,255,0)");

      ctx.fillStyle = rightGlow;
      ctx.fillRect(0, 0, width, height);
    }

    function drawSoftStar(x: number, y: number, radius: number, alpha: number, glow: string) {
      const halo = ctx.createRadialGradient(x, y, 0, x, y, radius * 7);
      halo.addColorStop(0, glow);
      halo.addColorStop(0.28, glow);
      halo.addColorStop(1, "rgba(255,255,255,0)");

      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(x, y, radius * 7, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = `rgba(255,255,255,${alpha})`;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawCrossSpark(x: number, y: number, radius: number, alpha: number) {
      ctx.save();
      ctx.translate(x, y);
      ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
      ctx.lineWidth = Math.max(0.8 * dpr, radius * 0.22);
      ctx.lineCap = "round";

      ctx.beginPath();
      ctx.moveTo(-radius * 2.3, 0);
      ctx.lineTo(radius * 2.3, 0);
      ctx.moveTo(0, -radius * 2.3);
      ctx.lineTo(0, radius * 2.3);
      ctx.stroke();

      ctx.restore();
    }

    function drawField(time: number) {
      for (const s of dustStars) {
        const a = s.alpha * (0.82 + 0.18 * Math.sin(time * 0.001 * s.twinkleSpeed + s.twinkleOffset));
        const x = s.x * width + Math.sin(time * 0.00009 + s.twinkleOffset) * s.driftX;
        const y = s.y * height + Math.cos(time * 0.00008 + s.twinkleOffset) * s.driftY;

        ctx.fillStyle = `rgba(255,255,255,${a})`;
        ctx.beginPath();
        ctx.arc(x, y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }

      for (const s of fieldStars) {
        const a = s.alpha * (0.70 + 0.30 * Math.sin(time * 0.001 * s.twinkleSpeed + s.twinkleOffset));
        const x = s.x * width + Math.sin(time * 0.00012 + s.twinkleOffset) * s.driftX;
        const y = s.y * height + Math.cos(time * 0.00010 + s.twinkleOffset) * s.driftY;

        drawSoftStar(x, y, s.r, a, palette.starGlow2);
      }
    }

    function getAnimatedMainPoints(time: number) {
      return mainStars.map((s, index) => {
        const pulse = 1 + 0.10 * Math.sin(time * 0.001 * s.pulseSpeed + s.pulseOffset);
        const x = s.x * width + Math.sin(time * 0.00018 + index) * s.wobbleX;
        const y = s.y * height + Math.cos(time * 0.00016 + index) * s.wobbleY;

        return { x, y, r: s.r * pulse };
      });
    }

    function drawConstellation(time: number) {
      const points = getAnimatedMainPoints(time);

      ctx.save();
      ctx.strokeStyle = palette.line;
      ctx.lineWidth = Math.max(1.2 * dpr, width * 0.0016);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      ctx.beginPath();
      for (const [a, b] of pattern.links) {
        ctx.moveTo(points[a].x, points[a].y);
        ctx.lineTo(points[b].x, points[b].y);
      }
      ctx.stroke();
      ctx.restore();

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const alpha = 0.94 + 0.06 * Math.sin(time * 0.0012 + i);

        drawSoftStar(p.x, p.y, p.r, alpha, palette.starGlow);

        if (i % 2 === 0) {
          drawCrossSpark(p.x, p.y, p.r * 1.1, 0.55);
        }
      }

      const accent = points[Math.floor(points.length / 2)];
      drawCrossSpark(accent.x, accent.y, 5.2 * dpr, 0.8);
    }

    function render(time: number) {
      ctx.clearRect(0, 0, width, height);
      drawBackground(time);
      drawField(time);
      drawConstellation(reduceMotion ? 0 : time);
      animationId = window.requestAnimationFrame(render);
    }

    rebuildScene();

    const resizeObserver = new ResizeObserver(() => {
      rebuildScene();
    });

    resizeObserver.observe(canvas);
    animationId = window.requestAnimationFrame(render);

    return () => {
      window.cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
    };
  }, [sign, userId, dateKey, dayScore]);

  return (
    <div
      className={className}
      style={{
        position: "relative",
        overflow: "hidden",
        borderRadius: 28,
        minHeight: 300,
        background:
          "linear-gradient(90deg, #fcf8f9 0%, #f0e8f7 45%, #d5c9fb 100%)",
      }}
    >
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          display: "block",
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          minHeight: "inherit",
          padding: "32px 28px",
        }}
      >
        {children}
      </div>
    </div>
  );
}
```

---

## 13. Exemple d'usage dans le dashboard

```tsx
import AstroMoodBackground from "./AstroMoodBackground";

export default function TodayHero() {
  return (
    <AstroMoodBackground
      sign="taurus"
      userId="user-123"
      dateKey="2026-03-14"
      dayScore={16}
      className="w-full"
    >
      <div style={{ maxWidth: 360 }}>
        <h1
          style={{
            margin: 0,
            fontSize: "2.4rem",
            lineHeight: 1.08,
            letterSpacing: "-0.03em",
            color: "#1f1d2b",
            fontWeight: 500,
          }}
        >
          Ta journée s'éclaircit après 14h.
        </h1>
      </div>
    </AstroMoodBackground>
  );
}
```

---

## 14. Variante recommandée : extraire les motifs des signes dans un fichier dédié

Pour rendre le système plus maintenable, je recommande de déplacer la structure des constellations dans un fichier `zodiacPatterns.ts` ou dans un JSON typé.

### Exemple de structure

```ts
export const zodiacPatterns = {
  taurus: {
    points: [
      { x: 0.63, y: 0.33 },
      { x: 0.71, y: 0.25 },
      { x: 0.79, y: 0.27 },
      { x: 0.84, y: 0.39 },
      { x: 0.90, y: 0.28 },
      { x: 0.96, y: 0.20 },
    ],
    links: [[0, 1], [1, 2], [2, 4], [2, 3], [4, 5]],
  },
};
```

### Avantages

- meilleur découplage entre moteur et design,
- possibilité d'ajuster chaque signe sans toucher au moteur canvas,
- meilleure collaboration avec le design.

---

## 15. Intégration côté backend / front

### Backend

Le backend n'a pas besoin de générer l'image.

Il doit seulement renvoyer les données nécessaires au rendu :

```json
{
  "sign": "taurus",
  "dayScore": 16,
  "dateKey": "2026-03-14",
  "message": "Ta journée s'éclaircit après 14h."
}
```

### Frontend

Le front compose le visuel à partir de :

- `sign`,
- `dayScore`,
- `dateKey`,
- `userId`.

---

## 16. Notes d'intégration React importantes

### 16.1 Nettoyage des effets

Le composant crée des ressources externes à React :

- une boucle `requestAnimationFrame`,
- un `ResizeObserver`.

Ces ressources doivent impérativement être nettoyées dans le `return` du `useEffect`.

### 16.2 Strict Mode

En développement, React peut relancer les effets pour détecter les problèmes de cleanup.

Le composant doit donc être **idempotent** et bien nettoyer :

- annulation de l'animation,
- déconnexion de l'observer,
- reconstruction propre de la scène.

### 16.3 SSR / hydration

Le composant est bien adapté à un rendu React classique.

Si le projet utilise SSR ou App Router, le canvas doit être monté côté client, ce qui est compatible avec cette approche tant que le rendu effectif s'initialise dans `useEffect`.

---

## 17. Accessibilité

### Réduction des mouvements

Le composant doit tenir compte de `prefers-reduced-motion`.

Comportement recommandé :

- soit figer l'animation,
- soit conserver un rendu statique avec très peu de variations.

### Lisibilité du texte

Le texte doit rester lisible :

- zone gauche peu encombrée,
- contraste suffisant,
- pas de constellation derrière le bloc de lecture principal.

### Rôle du canvas

Le canvas étant purement décoratif, il doit être marqué comme non pertinent pour les technologies d'assistance :

```tsx
<canvas aria-hidden="true" />
```

---

## 18. Performance

### Bonnes pratiques

- limiter le `devicePixelRatio` à `2`,
- garder une animation légère,
- limiter le nombre d'étoiles,
- recalculer la scène uniquement au resize,
- ne pas recréer la scène à chaque frame,
- éviter tout state React pour l'animation elle-même.

### Pourquoi cette approche est saine

Le Canvas 2D convient bien à ce type de fond décoratif animé, surtout avec une animation discrète et un nombre maîtrisé d'objets à dessiner.

---

## 19. Plan d'intégration concret

### Étape 1
Créer le fichier composant :

```txt
frontend/src/components/astro/AstroMoodBackground.tsx
```

### Étape 2
Créer éventuellement :

```txt
frontend/src/components/astro/zodiacPatterns.ts
```

### Étape 3
Brancher le composant dans le hero de la page dashboard.

### Étape 4
Mapper les données métier :

- `sign` depuis le profil astro,
- `dateKey` depuis la date du jour,
- `dayScore` depuis le moteur horoscope,
- `userId` depuis la session utilisateur.

### Étape 5
Tester :

- desktop,
- mobile,
- navigateur avec réduction de mouvement,
- variations quotidiennes,
- plusieurs signes.

---

## 20. Critères d'acceptation recommandés

Le composant sera considéré comme validé si :

1. le fond reste fidèle à la direction du visuel d'inspiration,
2. le texte reste très lisible à gauche,
3. la constellation varie selon le signe,
4. l'image varie légèrement d'un jour à l'autre,
5. le rendu reste stable sur une journée donnée,
6. l'animation reste très subtile,
7. la réduction des mouvements est respectée,
8. le composant nettoie proprement ses ressources,
9. les performances restent bonnes sur desktop et mobile récents.

---

## 21. Recommandations pour une V2

Une V2 peut aller plus loin sans changer l'architecture générale.

### Améliorations possibles

- sortir totalement la configuration des signes,
- ajouter plusieurs variantes visuelles par signe,
- piloter plus finement la palette selon plusieurs sous-scores (énergie, émotion, travail, amour),
- introduire une légère variation de bruit lumineux,
- prévoir un mode `compact` et un mode `hero`,
- ajouter une transition douce lors du changement de journée.

### À éviter en V2

- effets trop spectaculaires,
- rendu spatial sombre de type fond d'écran,
- surcharge de particules,
- animation continue trop visible.

---

## 22. Résumé exécutif

La meilleure solution pour cette fonctionnalité est :

- **fond dégradé clair en CSS**,
- **surcouche animée en Canvas 2D**,
- **constellation stylisée selon le signe**,
- **variation quotidienne déterministe via seed**,
- **palette pilotée par le score du jour**,
- **intégration React propre avec `useRef`, `useEffect`, `ResizeObserver` et cleanup**.

C'est l'approche la plus cohérente pour obtenir un rendu premium, vivant, contrôlé et maintenable.

---

## 23. Références techniques utilisées pour guider cette proposition

- MDN — Canvas API
- MDN — `window.requestAnimationFrame()`
- MDN — `ResizeObserver`
- MDN — `CanvasRenderingContext2D.createLinearGradient()`
- MDN — `CanvasRenderingContext2D.createRadialGradient()`
- MDN — `prefers-reduced-motion`
- React documentation — `useRef`
- React documentation — `useEffect`
- React documentation — synchronisation avec les systèmes externes

