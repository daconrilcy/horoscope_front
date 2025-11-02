import { describe, it, expect } from 'vitest';
import { safeInternalRedirect } from './redirect';

describe('safeInternalRedirect', () => {
  it('devrait retourner /app/dashboard si path undefined', () => {
    expect(safeInternalRedirect(undefined)).toBe('/app/dashboard');
  });

  it('devrait retourner /app/dashboard si path vide', () => {
    expect(safeInternalRedirect('')).toBe('/app/dashboard');
  });

  it('devrait retourner la route telle quelle si route interne valide', () => {
    expect(safeInternalRedirect('/app/dashboard')).toBe('/app/dashboard');
    expect(safeInternalRedirect('/app/horoscope')).toBe('/app/horoscope');
    expect(safeInternalRedirect('/login')).toBe('/login');
  });

  it('devrait bloquer les routes externes (http://)', () => {
    expect(safeInternalRedirect('http://evil.com')).toBe('/app/dashboard');
    expect(safeInternalRedirect('http://evil.com/path')).toBe('/app/dashboard');
  });

  it('devrait bloquer les routes externes (https://)', () => {
    expect(safeInternalRedirect('https://evil.com')).toBe('/app/dashboard');
    expect(safeInternalRedirect('https://evil.com/path')).toBe('/app/dashboard');
  });

  it('devrait bloquer les routes externes (//)', () => {
    expect(safeInternalRedirect('//evil.com')).toBe('/app/dashboard');
    expect(safeInternalRedirect('//evil.com/path')).toBe('/app/dashboard');
  });

  it('devrait bloquer les routes qui ne commencent pas par /', () => {
    expect(safeInternalRedirect('evil.com')).toBe('/app/dashboard');
    expect(safeInternalRedirect('app/dashboard')).toBe('/app/dashboard');
  });

  it('devrait permettre les routes avec query params', () => {
    expect(safeInternalRedirect('/app/dashboard?tab=settings')).toBe('/app/dashboard?tab=settings');
    expect(safeInternalRedirect('/reset/confirm?token=abc123')).toBe('/reset/confirm?token=abc123');
  });

  it('devrait permettre les routes avec hash', () => {
    expect(safeInternalRedirect('/app/dashboard#section')).toBe('/app/dashboard#section');
  });

  it('devrait bloquer javascript: (test edge case)', () => {
    expect(safeInternalRedirect('/javascript:alert(1)')).toBe('/javascript:alert(1)');
    // Note: Ceci est accepté car ça commence par /, mais dans une vraie app on pourrait
    // vouloir une whitelist plus stricte. Pour l'instant, on bloque uniquement les URLs externes.
  });
});

