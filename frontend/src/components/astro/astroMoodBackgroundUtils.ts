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

export function getPalette(dayScore: number, isDark: boolean = false) {
  const score = clamp(dayScore, 1, 20);

  if (isDark) {
    if (score <= 7) {
      return {
        left: '#1c1630',
        mid: '#312056',
        right: '#422b63',
        deep: '#120f20',
        mist: 'rgba(146, 110, 230, 0.22)',
        starCore: 'rgba(235, 235, 255, 0.95)',
        starGlow: 'rgba(176, 132, 255, 0.28)',
        starGlow2: 'rgba(140, 120, 255, 0.22)',
        line: 'rgba(255, 255, 255, 0.35)',
      };
    }
    if (score >= 15) {
      return {
        left: '#241b3a',
        mid: '#44217a',
        right: '#6b2fd0',
        deep: '#171127',
        mist: 'rgba(192, 150, 255, 0.3)',
        starCore: 'rgba(255, 255, 255, 1)',
        starGlow: 'rgba(210, 190, 255, 0.4)',
        starGlow2: 'rgba(226, 166, 255, 0.34)',
        line: 'rgba(255, 255, 255, 0.55)',
      };
    }
    return {
      left: '#1d1730',
      mid: '#2c1a4f',
      right: '#3e2765',
      deep: '#110e1d',
      mist: 'rgba(152, 122, 230, 0.24)',
      starCore: 'rgba(245, 245, 255, 0.98)',
      starGlow: 'rgba(182, 160, 255, 0.34)',
      starGlow2: 'rgba(185, 145, 255, 0.28)',
      line: 'rgba(255, 255, 255, 0.45)',
    };
  }

  // Light theme (original)
  if (score <= 7) {
    return {
      left: '#faf5fb',
      mid: '#ead9ff',
      right: '#ceb4ff',
      deep: '#d8cbf3',
      mist: 'rgba(188, 136, 255, 0.28)',
      starCore: 'rgba(255, 255, 255, 0.98)',
      starGlow: 'rgba(224, 170, 255, 0.24)',
      starGlow2: 'rgba(176, 158, 255, 0.24)',
      line: 'rgba(255, 255, 255, 0.48)',
    };
  }

  if (score >= 15) {
    return {
      left: '#fff8fc',
      mid: '#ead8ff',
      right: '#be9dff',
      deep: '#c4b0f2',
      mist: 'rgba(190, 140, 255, 0.3)',
      starCore: 'rgba(255, 255, 255, 1)',
      starGlow: 'rgba(214, 188, 255, 0.34)',
      starGlow2: 'rgba(236, 188, 255, 0.28)',
      line: 'rgba(255, 255, 255, 0.56)',
    };
  }

  return {
    left: '#fcf6fb',
    mid: '#eadcff',
    right: '#c7adff',
    deep: '#cdb8f3',
    mist: 'rgba(188, 146, 255, 0.28)',
    starCore: 'rgba(255, 255, 255, 0.99)',
    starGlow: 'rgba(214, 190, 255, 0.3)',
    starGlow2: 'rgba(230, 180, 255, 0.24)',
    line: 'rgba(255, 255, 255, 0.52)',
  };
}
