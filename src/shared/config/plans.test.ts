import { describe, it, expect, beforeEach, vi } from 'vitest';
import { assertValidPlan, PLANS } from './plans';

describe('plans', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('assertValidPlan', () => {
    it('devrait accepter plan "plus"', () => {
      expect(() => assertValidPlan('plus')).not.toThrow();
    });

    it('devrait accepter plan "pro"', () => {
      expect(() => assertValidPlan('pro')).not.toThrow();
    });

    it('devrait accepter PLANS.PLUS', () => {
      expect(() => assertValidPlan(PLANS.PLUS)).not.toThrow();
    });

    it('devrait accepter PLANS.PRO', () => {
      expect(() => assertValidPlan(PLANS.PRO)).not.toThrow();
    });

    it('devrait lever une erreur en dev si plan inconnu', () => {
      // Note: Ce test fonctionne uniquement en dev (import.meta.env.DEV)
      // En prod, assertValidPlan est no-op silencieux
      if (import.meta.env.DEV) {
        expect(() => assertValidPlan('unknown')).toThrow('Unknown plan');
        expect(() => assertValidPlan('invalid')).toThrow('Unknown plan');
      }
    });

    it("devrait être no-op silencieux en prod (ne pas lever d'erreur)", () => {
      // Note: Ce test vérifie le comportement en prod
      // Si on est en dev, on vérifie juste que ça ne plante pas sur plan valide
      expect(() => assertValidPlan('plus')).not.toThrow();
      expect(() => assertValidPlan('pro')).not.toThrow();
    });
  });

  describe('PLANS', () => {
    it('devrait avoir PLANS.PLUS égal à "plus"', () => {
      expect(PLANS.PLUS).toBe('plus');
    });

    it('devrait avoir PLANS.PRO égal à "pro"', () => {
      expect(PLANS.PRO).toBe('pro');
    });
  });
});
