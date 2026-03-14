import type { Theme } from '../../state/ThemeProvider';

export function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

export function hashString(input: string): number {
  let h = 2166136261;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

export function mulberry32(seed: number) {
  let t = seed >>> 0;
  return function next() {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

export function range(rand: () => number, min: number, max: number) {
  return min + (max - min) * rand();
}

export function biasRight(rand: () => number) {
  return 1 - Math.pow(rand(), 1.85);
}

export function getPalette(dayScore: number, theme: Theme = 'light') {
  const score = clamp(dayScore, 1, 20);

  if (theme === 'dark') {
    if (score <= 7) {
      return {
        left: '#181626',
        mid: '#21193a',
        right: '#2A2436',
        mist: 'rgba(120, 100, 200, 0.15)',
        starCore: 'rgba(235, 235, 255, 0.95)',
        starGlow: 'rgba(150, 120, 255, 0.22)',
        starGlow2: 'rgba(100, 150, 255, 0.18)',
        line: 'rgba(255, 255, 255, 0.35)',
      };
    }
    if (score >= 15) {
      return {
        left: '#1e1b2e',
        mid: '#2a1f4a',
        right: '#37226E',
        mist: 'rgba(170, 140, 255, 0.22)',
        starCore: 'rgba(255, 255, 255, 1)',
        starGlow: 'rgba(180, 200, 255, 0.35)',
        starGlow2: 'rgba(220, 180, 255, 0.28)',
        line: 'rgba(255, 255, 255, 0.55)',
      };
    }
    return {
      left: '#181626',
      mid: '#13111f',
      right: '#0F0E18',
      mist: 'rgba(140, 120, 230, 0.18)',
      starCore: 'rgba(245, 245, 255, 0.98)',
      starGlow: 'rgba(160, 150, 255, 0.28)',
      starGlow2: 'rgba(150, 180, 255, 0.24)',
      line: 'rgba(255, 255, 255, 0.45)',
    };
  }

  // Light theme (original)
  if (score <= 7) {
    return {
      left: '#fbf7f8',
      mid: '#efe6f7',
      right: '#d9cafb',
      mist: 'rgba(196, 173, 255, 0.22)',
      starCore: 'rgba(255, 255, 255, 0.98)',
      starGlow: 'rgba(255, 190, 220, 0.26)',
      starGlow2: 'rgba(171, 197, 255, 0.20)',
      line: 'rgba(255, 255, 255, 0.48)',
    };
  }

  if (score >= 15) {
    return {
      left: '#fffaf9',
      mid: '#ede4ff',
      right: '#cdc1ff',
      mist: 'rgba(189, 176, 255, 0.24)',
      starCore: 'rgba(255, 255, 255, 1)',
      starGlow: 'rgba(196, 224, 255, 0.30)',
      starGlow2: 'rgba(255, 220, 255, 0.24)',
      line: 'rgba(255, 255, 255, 0.56)',
    };
  }

  return {
    left: '#fcf8f9',
    mid: '#ede5fb',
    right: '#d5c9fb',
    mist: 'rgba(192, 178, 255, 0.23)',
    starCore: 'rgba(255, 255, 255, 0.99)',
    starGlow: 'rgba(206, 225, 255, 0.24)',
    starGlow2: 'rgba(255, 205, 235, 0.20)',
    line: 'rgba(255, 255, 255, 0.52)',
  };
}
