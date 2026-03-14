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
    const rand = mulberry32(seed);
    const palette = getPalette(dayScore, theme);
    const pattern = SIGN_PATTERNS[sign] || SIGN_PATTERNS['neutral'];

    let width = 0;
    let height = 0;
    let dpr = 1;
    let animationId = 0;

    const fieldStars: Star[] = [];
    const mainStars: MainStar[] = [];
    const dustStars: Star[] = [];
    const mistBlobs: Array<{
      x: number;
      y: number;
      radius: number;
      alpha: number;
    }> = [];

    function rebuildScene() {
      if (!canvas) return;
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

      // Medium stars, biased towards the right (AC 5)
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

      // Small background stars, spread everywhere
      for (let i = 0; i < Math.round(120 * areaFactor); i++) {
        dustStars.push({
          x: range(rand, 0.1, 0.98),
          y: range(rand, 0.08, 0.92),
          r: range(rand, 0.3, 0.9) * dpr,
          alpha: range(rand, 0.08, 0.35),
          twinkleSpeed: range(rand, 0.25, 0.7),
          twinkleOffset: range(rand, 0, Math.PI * 2),
          driftX: range(rand, -0.2, 0.2) * dpr,
          driftY: range(rand, -0.2, 0.2) * dpr,
        });
      }

      // Constellation stars from pattern (AC 3, 4)
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

      // Mist blobs for depth
      for (let i = 0; i < 3; i++) {
        mistBlobs.push({
          x: range(rand, 0.55, 0.95),
          y: range(rand, 0.1, 0.7),
          radius: range(rand, width * 0.11, width * 0.24),
          alpha: range(rand, 0.05, 0.11),
        });
      }
    }

    function drawBackground(time: number) {
      if (!ctx) return;
      const linear = ctx.createLinearGradient(0, 0, width, 0);
      linear.addColorStop(0, palette.left);
      linear.addColorStop(0.45, palette.mid);
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

    function drawSoftStar(
      x: number,
      y: number,
      radius: number,
      alpha: number,
      glow: string
    ) {
      if (!ctx) return;
      const halo = ctx.createRadialGradient(x, y, 0, x, y, radius * 7);
      halo.addColorStop(0, glow);
      halo.addColorStop(0.28, glow);
      halo.addColorStop(1, 'rgba(255,255,255,0)');

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
      for (const s of dustStars) {
        const a =
          s.alpha *
          (0.82 + 0.18 * Math.sin(time * 0.001 * s.twinkleSpeed + s.twinkleOffset));
        const x =
          s.x * width + Math.sin(time * 0.00009 + s.twinkleOffset) * s.driftX;
        const y =
          s.y * height + Math.cos(time * 0.00008 + s.twinkleOffset) * s.driftY;

        ctx.fillStyle = `rgba(255,255,255,${a})`;
        ctx.beginPath();
        ctx.arc(x, y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }

      for (const s of fieldStars) {
        const a =
          s.alpha *
          (0.7 + 0.3 * Math.sin(time * 0.001 * s.twinkleSpeed + s.twinkleOffset));
        const x =
          s.x * width + Math.sin(time * 0.00012 + s.twinkleOffset) * s.driftX;
        const y =
          s.y * height + Math.cos(time * 0.0001 + s.twinkleOffset) * s.driftY;

        drawSoftStar(x, y, s.r, a, palette.starGlow2);
      }
    }

    function getAnimatedMainPoints(time: number) {
      return mainStars.map((s, index) => {
        const pulse =
          1 + 0.1 * Math.sin(time * 0.001 * s.pulseSpeed + s.pulseOffset);
        const x = s.x * width + Math.sin(time * 0.00018 + index) * s.wobbleX;
        const y = s.y * height + Math.cos(time * 0.00016 + index) * s.wobbleY;

        return { x, y, r: s.r * pulse };
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
        const alpha = 0.94 + 0.06 * Math.sin(time * 0.0012 + i);

        drawSoftStar(p.x, p.y, p.r, alpha, palette.starGlow);

        if (i % 2 === 0) {
          drawCrossSpark(p.x, p.y, p.r * 1.1, 0.55);
        }
      }

      if (points.length > 0) {
        const accent = points[Math.floor(points.length / 2)];
        drawCrossSpark(accent.x, accent.y, 5.2 * dpr, 0.8);
      }
    }

    function render(time: number) {
      if (!ctx) return;
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
  }, [sign, userId, dateKey, dayScore, theme]);

  return (
    <div className={`astro-mood-background ${className}`}>
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="astro-mood-background__canvas"
      />
      <div className="astro-mood-background__content">{children}</div>
    </div>
  );
};

export default AstroMoodBackground;
