import React from 'react';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { render, cleanup } from '@testing-library/react';
import AstroMoodBackground from '../components/astro/AstroMoodBackground';
import {
  hashString,
  mulberry32,
  range,
  getPalette,
} from '../components/astro/astroMoodBackgroundUtils';
import * as ThemeProvider from '../state/ThemeProvider';

// Mock ResizeObserver
class ResizeObserverMock {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}

vi.stubGlobal('ResizeObserver', ResizeObserverMock);

// Mock Canvas getContext
const mockCtx = {
  clearRect: vi.fn(),
  beginPath: vi.fn(),
  arc: vi.fn(),
  fill: vi.fn(),
  stroke: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  translate: vi.fn(),
  createLinearGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
  createRadialGradient: vi.fn(() => ({ addColorStop: vi.fn() })),
  fillRect: vi.fn(),
};

// @ts-ignore
HTMLCanvasElement.prototype.getContext = vi.fn(() => mockCtx);

// Mock matchMedia
vi.stubGlobal('matchMedia', vi.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(), // deprecated
  removeListener: vi.fn(), // deprecated
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
})));

describe('AstroMoodBackground', () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    vi.spyOn(ThemeProvider, 'useThemeSafe').mockReturnValue({ theme: 'light', toggleTheme: vi.fn() });
    
    const { container } = render(
      <AstroMoodBackground
        sign="aries"
        userId="user-1"
        dateKey="2026-03-14"
      >
        <div>Content</div>
      </AstroMoodBackground>
    );

    expect(container.querySelector('.astro-mood-background')).toBeInTheDocument();
    expect(container.querySelector('canvas')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('handles theme changes', () => {
    const useThemeSpy = vi.spyOn(ThemeProvider, 'useThemeSafe');
    useThemeSpy.mockReturnValue({ theme: 'light', toggleTheme: vi.fn() });
    
    const { rerender } = render(
      <AstroMoodBackground
        sign="aries"
        userId="user-1"
        dateKey="2026-03-14"
      />
    );

    useThemeSpy.mockReturnValue({ theme: 'dark', toggleTheme: vi.fn() });
    rerender(
      <AstroMoodBackground
        sign="aries"
        userId="user-1"
        dateKey="2026-03-14"
      />
    );
    
    // getPalette should have been called with 'dark'
    // We can verify this if we export getPalette and spy on it or check the canvas calls if they changed
  });

  it('has aria-hidden="true" on canvas for accessibility', () => {
    const { container } = render(
      <AstroMoodBackground
        sign="taurus"
        userId="user-1"
        dateKey="2026-03-14"
      />
    );
    const canvas = container.querySelector('canvas');
    expect(canvas).toHaveAttribute('aria-hidden', 'true');
  });

  describe('Utility Functions', () => {
    it('hashString is deterministic', () => {
      const input = 'test-seed-123';
      expect(hashString(input)).toBe(hashString(input));
      expect(hashString('a')).not.toBe(hashString('b'));
    });

    it('mulberry32 is deterministic', () => {
      const seed = 12345;
      const gen1 = mulberry32(seed);
      const gen2 = mulberry32(seed);
      expect(gen1()).toBe(gen2());
      expect(gen1()).toBe(gen2());
    });

    it('range returns values within specified range', () => {
      const rand = () => 0.5;
      expect(range(rand, 10, 20)).toBe(15);
      
      const rand0 = () => 0;
      expect(range(rand0, 10, 20)).toBe(10);
      
      const rand1 = () => 0.999999;
      expect(range(rand1, 10, 20)).toBeCloseTo(20);
    });

    it('getPalette returns different colors based on dayScore', () => {
      const low = getPalette(5);
      const mid = getPalette(12);
      const high = getPalette(18);

      expect(low.right).not.toBe(high.right);
      expect(mid.right).toBeDefined();
    });
  });

  it('cleans up resources on unmount', () => {
    const cancelSpy = vi.spyOn(window, 'cancelAnimationFrame');
    
    const { unmount } = render(
      <AstroMoodBackground
        sign="leo"
        userId="user-1"
        dateKey="2026-03-14"
      />
    );

    unmount();
    expect(cancelSpy).toHaveBeenCalled();
  });

  it('respects prefers-reduced-motion without crashing', () => {
    vi.stubGlobal('matchMedia', vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })));

    const { container } = render(
      <AstroMoodBackground sign="gemini" userId="u2" dateKey="2026-03-14" />
    );
    expect(container.querySelector('.astro-mood-background')).toBeInTheDocument();
  });

  it('cleans up animation frame and observer in StrictMode', () => {
    const cancelSpy = vi.spyOn(window, 'cancelAnimationFrame');
    const { unmount } = render(
      <React.StrictMode>
        <AstroMoodBackground sign="cancer" userId="u3" dateKey="2026-03-14" />
      </React.StrictMode>
    );
    
    // In React 18+ StrictMode, the component mounts, unmounts, and remounts immediately.
    // So cancelAnimationFrame is called at least once before we even unmount manually.
    expect(cancelSpy).toHaveBeenCalled();
    
    unmount();
    // After unmount, it should be called again
    expect(cancelSpy.mock.calls.length).toBeGreaterThanOrEqual(2);
  });
});

import { screen } from '@testing-library/react';
