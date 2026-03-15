import React, { useEffect, useRef } from 'react';
import type { PropsWithChildren } from 'react';
import { SIGN_PATTERNS } from './zodiacPatterns';
import type { ZodiacSign } from './zodiacPatterns';
import {
  biasRight,
  getPalette,
  hashString,
  mulberry32,
  range,
} from './astroMoodBackgroundUtils';
// useThemeSafe needed: Canvas WebGL rendering requires the theme to pick correct color palettes
import { useThemeSafe } from '../../state/ThemeProvider';
import './AstroMoodBackground.css';

export interface AstroMoodBackgroundProps extends PropsWithChildren {
  sign: ZodiacSign;
  userId: string;
  dateKey: string; // ex: "2026-03-14"
  dayScore?: number; // 1..20
  className?: string;
}

type Star = {
  x: number;
  y: number;
  r: number;
  alpha: number;
  twinkleSpeed: number;
  twinkleOffset: number;
  driftX: number;
  driftY: number;
  flareStrength: number;
  tint: string;
};

type MainStar = {
  x: number;
  y: number;
  r: number;
  pulseSpeed: number;
  pulseOffset: number;
  wobbleX: number;
  wobbleY: number;
  flareStrength: number;
};

type ShootingStar = {
  startX: number;
  startY: number;
  length: number;
  angle: number;
  width: number;
  alpha: number;
  speed: number;
  startTime: number;
  duration: number;
};

export const AstroMoodBackground: React.FC<AstroMoodBackgroundProps> = ({
  sign,
  userId,
  dateKey,
  dayScore = 12,
  className = '',
  children,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const themeContext = useThemeSafe();
  const theme = themeContext?.theme || 'light';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const seed = hashString(`${userId}|${sign}|${dateKey}`);
    const palette = getPalette(dayScore, theme === 'dark');
    const pattern = SIGN_PATTERNS[sign] || SIGN_PATTERNS['neutral'];

    let width = 0;
    let height = 0;
    let dpr = 1;
    let animationId = 0;

    const fieldStars: Star[] = [];
    const mainStars: MainStar[] = [];
    const dustStars: Star[] = [];
    const tertiaryStars: Star[] = [];
    const shootingStars: ShootingStar[] = [];
    const mistBlobs: Array<{
      x: number;
      y: number;
      radius: number;
      alpha: number;
    }> = [];
    const secondaryStarTints = [
      'rgba(170, 255, 196, 0.22)',
      'rgba(255, 184, 184, 0.2)',
      'rgba(176, 205, 255, 0.22)',
      'rgba(255, 255, 255, 0.2)',
      'rgba(255, 236, 170, 0.22)',
    ] as const;

    function rebuildScene() {
      if (!canvas) return;
      // Rebuild from the raw seed every time to keep the layout deterministic across resizes.
      const rand = mulberry32(seed);
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = Math.max(1, Math.floor(rect.width * dpr));
      height = Math.max(1, Math.floor(rect.height * dpr));

      canvas.width = width;
      canvas.height = height;

      fieldStars.length = 0;
      mainStars.length = 0;
      dustStars.length = 0;
      tertiaryStars.length = 0;
      shootingStars.length = 0;
      mistBlobs.length = 0;

      const areaFactor = (width * height) / 320000;

      // Medium stars, biased towards the right (AC 5)
      for (let i = 0; i < Math.round(96 * areaFactor); i++) {
        fieldStars.push({
          x: biasRight(rand) * 0.58 + 0.38,
          y: range(rand, 0.06, 0.94),
          r: range(rand, 0.8, 2.1) * dpr,
          alpha: range(rand, 0.32, 0.92),
          twinkleSpeed: range(rand, 0.45, 1.35),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -1.1, 1.1) * dpr,
          driftY: range(rand, -0.95, 0.95) * dpr,
          flareStrength: range(rand, 0.18, 0.5),
          tint: secondaryStarTints[Math.floor(rand() * secondaryStarTints.length)],
        });
      }

      // Small background stars, spread everywhere
      for (let i = 0; i < Math.round(168 * areaFactor); i++) {
        dustStars.push({
          x: range(rand, 0.1, 0.98),
          y: range(rand, 0.08, 0.92),
          r: range(rand, 0.35, 1.05) * dpr,
          alpha: range(rand, 0.12, 0.42),
          twinkleSpeed: range(rand, 0.35, 0.95),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -0.28, 0.28) * dpr,
          driftY: range(rand, -0.28, 0.28) * dpr,
          flareStrength: range(rand, 0.12, 0.28),
          tint: secondaryStarTints[Math.floor(rand() * secondaryStarTints.length)],
        });
      }

      // Tiny tertiary stars, almost imperceptible, used as a deep background texture
      for (let i = 0; i < Math.round(240 * areaFactor); i++) {
        tertiaryStars.push({
          x: range(rand, 0.02, 0.99),
          y: range(rand, 0.03, 0.97),
          r: range(rand, 0.12, 0.38) * dpr,
          alpha: range(rand, 0.03, 0.12),
          twinkleSpeed: range(rand, 0.18, 0.42),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -0.06, 0.06) * dpr,
          driftY: range(rand, -0.06, 0.06) * dpr,
          flareStrength: range(rand, 0.02, 0.08),
          tint: secondaryStarTints[Math.floor(rand() * secondaryStarTints.length)],
        });
      }

      // Constellation stars from pattern (AC 3, 4)
      const designAspect = 2.5; 
      const currentAspect = width / height;

      for (const p of pattern.points) {
        let adjX = p.x;
        let adjY = p.y;

        if (currentAspect > designAspect) {
          adjX = 0.8 + (p.x - 0.8) * (designAspect / currentAspect);
        } else {
          adjY = 0.5 + (p.y - 0.5) * (currentAspect / designAspect);
        }

        mainStars.push({
          x: adjX + range(rand, -0.015, 0.015),
          y: adjY + range(rand, -0.015, 0.015),
          r: range(rand, 2.4, 4.1) * dpr,
          pulseSpeed: range(rand, 0.45, 0.95),
          pulseOffset: range(rand, 0, Math.PI * 2),
          wobbleX: range(rand, -1.8, 1.8) * dpr,
          wobbleY: range(rand, -1.8, 1.8) * dpr,
          flareStrength: range(rand, 0.45, 0.9),
        });
      }

      // Mist blobs for depth
      for (let i = 0; i < 3; i++) {
        mistBlobs.push({
          x: range(rand, 0.55, 0.95),
          y: range(rand, 0.1, 0.7),
          radius: range(rand, width * 0.11, width * 0.24),
          alpha: range(rand, 0.05, 0.11),
        });
      }

      for (let i = 0; i < 4; i++) {
        shootingStars.push({
          startX: range(rand, width * 0.1, width * 0.82),
          startY: range(rand, height * 0.04, height * 0.4),
          length: range(rand, width * 0.12, width * 0.22),
          angle: range(rand, 0.58, 0.82),
          width: range(rand, 1.4, 3.6) * dpr,
          alpha: range(rand, 0.32, 0.58),
          speed: range(rand, 0.95, 1.4),
          startTime: range(rand, 400, 7600),
          duration: range(rand, 1000, 1500),
        });
      }
    }

    function drawBackground(time: number) {
      if (!ctx) return;
      const linear = ctx.createLinearGradient(0, 0, width, height);
      linear.addColorStop(0, palette.left);
      linear.addColorStop(0.35, palette.mid);
      linear.addColorStop(0.72, palette.right);
      linear.addColorStop(1, palette.deep);

      ctx.fillStyle = linear;
      ctx.fillRect(0, 0, width, height);

      const shadowVeil = ctx.createRadialGradient(
        width * 0.82,
        height * 0.78,
        width * 0.08,
        width * 0.82,
        height * 0.78,
        width * 0.62
      );
      shadowVeil.addColorStop(0, 'rgba(20, 14, 34, 0.24)');
      shadowVeil.addColorStop(0.55, 'rgba(30, 18, 56, 0.14)');
      shadowVeil.addColorStop(1, 'rgba(10, 8, 18, 0)');
      ctx.fillStyle = shadowVeil;
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
        radial.addColorStop(1, 'rgba(255,255,255,0)');

        ctx.fillStyle = radial;
        ctx.beginPath();
        ctx.arc(
          mist.x * width,
          mist.y * height,
          mist.radius * breath,
          0,
          Math.PI * 2
        );
        ctx.fill();
      }

      // Accent glow on the right
      const rightGlow = ctx.createRadialGradient(
        width * 0.88,
        height * 0.32,
        0,
        width * 0.88,
        height * 0.32,
        width * 0.45
      );
      rightGlow.addColorStop(0, 'rgba(255,255,255,0.22)');
      rightGlow.addColorStop(0.45, 'rgba(224,210,255,0.18)');
      rightGlow.addColorStop(1, 'rgba(255,255,255,0)');

      ctx.fillStyle = rightGlow;
      ctx.fillRect(0, 0, width, height);
    }

    function drawShootingStars(time: number) {
      if (!ctx || reduceMotion) return;

      for (const star of shootingStars) {
        const loopDuration = 11000;
        const loopTime = (time + star.startTime) % loopDuration;
        if (loopTime > star.duration) {
          continue;
        }

        const progress = loopTime / star.duration;
        const travel = width * 0.26 * star.speed;
        const x = star.startX + Math.cos(star.angle) * travel * progress;
        const y = star.startY + Math.sin(star.angle) * travel * progress;
        const tailX = x - Math.cos(star.angle) * star.length;
        const tailY = y - Math.sin(star.angle) * star.length;
        const fade = Math.sin(progress * Math.PI);
        const streakWidth = star.width * (0.72 + fade * 0.95);

        const gradient = ctx.createLinearGradient(x, y, tailX, tailY);
        gradient.addColorStop(0, `rgba(255,255,255,${star.alpha * fade})`);
        gradient.addColorStop(0.35, `rgba(220,210,255,${star.alpha * 0.7 * fade})`);
        gradient.addColorStop(1, 'rgba(255,255,255,0)');

        ctx.save();
        ctx.strokeStyle = gradient;
        ctx.lineWidth = streakWidth;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(tailX, tailY);
        ctx.stroke();

        const headGlow = ctx.createRadialGradient(x, y, 0, x, y, streakWidth * 5.5);
        headGlow.addColorStop(0, `rgba(255,255,255,${star.alpha * 0.85 * fade})`);
        headGlow.addColorStop(0.45, `rgba(218,210,255,${star.alpha * 0.42 * fade})`);
        headGlow.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = headGlow;
        ctx.beginPath();
        ctx.arc(x, y, streakWidth * 5.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    function drawSoftStar(
      x: number,
      y: number,
      radius: number,
      alpha: number,
      glow: string,
      haloScale: number = 1,
      tint?: string
    ) {
      if (!ctx) return;
      const isDarkTheme = theme === 'dark';
      const haloInner = isDarkTheme
        ? glow.replace(/[\d.]+\)$/u, `${Math.max(0.04, alpha * 0.1)})`)
        : glow;
      const haloMid = isDarkTheme
        ? glow.replace(/[\d.]+\)$/u, `${Math.max(0.025, alpha * 0.06)})`)
        : glow.replace(/[\d.]+\)$/u, `${Math.max(0.04, alpha * 0.12)})`);
      const haloRadius = radius * 7 * haloScale;
      const halo = ctx.createRadialGradient(x, y, 0, x, y, haloRadius);
      halo.addColorStop(0, haloInner);
      halo.addColorStop(0.08, haloInner);
      halo.addColorStop(0.24, haloMid);
      halo.addColorStop(0.52, isDarkTheme ? 'rgba(255,255,255,0.015)' : 'rgba(255,255,255,0.022)');
      halo.addColorStop(0.78, 'rgba(255,255,255,0.006)');
      halo.addColorStop(1, 'rgba(255,255,255,0)');

      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(x, y, haloRadius, 0, Math.PI * 2);
      ctx.fill();

      if (tint) {
        const diffraction = ctx.createRadialGradient(x, y, 0, x, y, haloRadius * 0.82);
        diffraction.addColorStop(0, tint);
        diffraction.addColorStop(0.42, tint.replace(/[\d.]+\)$/u, '0.08)'));
        diffraction.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = diffraction;
        ctx.beginPath();
        ctx.arc(x, y, haloRadius * 0.82, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.fillStyle = `rgba(255,255,255,${alpha})`;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    function drawCrossSpark(x: number, y: number, radius: number, alpha: number) {
      if (!ctx) return;
      ctx.save();
      ctx.translate(x, y);
      ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
      ctx.lineWidth = Math.max(0.8 * dpr, radius * 0.22);
      ctx.lineCap = 'round';

      ctx.beginPath();
      ctx.moveTo(-radius * 2.3, 0);
      ctx.lineTo(radius * 2.3, 0);
      ctx.moveTo(0, -radius * 2.3);
      ctx.lineTo(0, radius * 2.3);
      ctx.stroke();

      ctx.restore();
    }

    function drawField(time: number) {
      if (!ctx) return;
      for (const s of tertiaryStars) {
        const twinkle = 0.55 + 0.28 * Math.sin(time * 0.0007 * s.twinkleSpeed + s.twinkleOffset);
        const a = s.alpha * twinkle;
        const x = s.x * width + Math.sin(time * 0.00003 + s.twinkleOffset) * s.driftX;
        const y = s.y * height + Math.cos(time * 0.00003 + s.twinkleOffset) * s.driftY;

        ctx.fillStyle = `rgba(255,255,255,${a})`;
        ctx.beginPath();
        ctx.arc(x, y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }

      for (const s of dustStars) {
        const twinkleBase = Math.sin(time * 0.0016 * s.twinkleSpeed + s.twinkleOffset);
        const twinkle = 0.38 + 0.72 * twinkleBase;
        const a =
          s.alpha *
          twinkle;
        const x =
          s.x * width + Math.sin(time * 0.00009 + s.twinkleOffset) * s.driftX;
        const y =
          s.y * height + Math.cos(time * 0.00008 + s.twinkleOffset) * s.driftY;
        const haloScale = 0.78 + Math.max(0, twinkle) * s.flareStrength;

        if (a > 0.035) {
          ctx.fillStyle = `rgba(255,255,255,${a})`;
          ctx.beginPath();
          ctx.arc(x, y, s.r, 0, Math.PI * 2);
          ctx.fill();
        }

        if (a > 0.14) {
          drawSoftStar(x, y, s.r * 0.7, a * 0.85, palette.starGlow2, haloScale, s.tint);
        }
      }

      for (const s of fieldStars) {
        const twinkleBase = Math.sin(time * 0.0021 * s.twinkleSpeed + s.twinkleOffset);
        const appearPhase = Math.sin(time * 0.00022 + s.twinkleOffset * 1.7);
        const twinkle = 0.24 + 0.84 * twinkleBase;
        const appearance = Math.max(0, appearPhase);
        const a =
          s.alpha *
          twinkle *
          (0.3 + appearance);
        const x =
          s.x * width + Math.sin(time * 0.00012 + s.twinkleOffset) * s.driftX;
        const y =
          s.y * height + Math.cos(time * 0.0001 + s.twinkleOffset) * s.driftY;
        const haloScale = 0.82 + Math.max(0, twinkle) * s.flareStrength;

        if (a > 0.045) {
          drawSoftStar(x, y, s.r, a, palette.starGlow2, haloScale, s.tint);
        }

        if (a > 0.72) {
          drawCrossSpark(x, y, s.r * 0.95, 0.22 + s.flareStrength * 0.35);
        }
      }
    }

    function getAnimatedMainPoints(time: number) {
      return mainStars.map((s, index) => {
        const pulse =
          1 + 0.22 * Math.sin(time * 0.0022 * s.pulseSpeed + s.pulseOffset);
        const x = s.x * width + Math.sin(time * 0.00018 + index) * s.wobbleX;
        const y = s.y * height + Math.cos(time * 0.00016 + index) * s.wobbleY;

        return { x, y, r: s.r * pulse, flareStrength: s.flareStrength };
      });
    }

    function drawConstellation(time: number) {
      if (!ctx) return;
      const points = getAnimatedMainPoints(time);

      ctx.save();
      ctx.strokeStyle = palette.line;
      ctx.lineWidth = Math.max(1.2 * dpr, width * 0.0016);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.beginPath();
      for (const [a, b] of pattern.links) {
        if (points[a] && points[b]) {
          ctx.moveTo(points[a].x, points[a].y);
          ctx.lineTo(points[b].x, points[b].y);
        }
      }
      ctx.stroke();
      ctx.restore();

      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const shimmer = 0.78 + 0.32 * Math.sin(time * 0.0024 + i * 0.9);
        const alpha = Math.min(1, 0.82 + shimmer * 0.24);
        const haloScale = 1 + shimmer * p.flareStrength;

        drawSoftStar(p.x, p.y, p.r, alpha, palette.starGlow, haloScale);

        drawCrossSpark(
          p.x,
          p.y,
          p.r * (1.1 + shimmer * 0.18),
          0.42 + shimmer * 0.34
        );
      }

      if (points.length > 0) {
        const accent = points[Math.floor(points.length / 2)];
        drawCrossSpark(accent.x, accent.y, 5.8 * dpr, 0.9);
      }
    }

    function render(time: number) {
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      drawBackground(time);
      drawField(time);
      drawConstellation(reduceMotion ? 0 : time);
      drawShootingStars(time);
      if (!reduceMotion) {
        animationId = window.requestAnimationFrame(render);
      }
    }

    rebuildScene();

    const resizeObserver = new ResizeObserver(() => {
      rebuildScene();
      if (reduceMotion) {
        render(0);
      }
    });

    resizeObserver.observe(canvas);

    if (reduceMotion) {
      render(0);
    } else {
      animationId = window.requestAnimationFrame(render);
    }

    return () => {
      window.cancelAnimationFrame(animationId);
      resizeObserver.disconnect();
    };
  }, [sign, userId, dateKey, dayScore, theme]);

  return (
    <div className={`astro-mood-background ${className}`}>
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="astro-mood-background__canvas"
      />
      <div className="astro-mood-background__content astro-context">{children}</div>
    </div>
  );
};

export default AstroMoodBackground;
