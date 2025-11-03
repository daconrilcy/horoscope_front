import { create } from 'zustand';
import { eventBus } from '@/shared/api/eventBus';
import type { PaywallReason, PaywallPayload } from '@/shared/api/types';

interface PaywallState {
  visible: boolean;
  reason?: PaywallReason;
  upgradeUrl?: string;

  showPaywall: (payload: PaywallPayload) => void;
  hidePaywall: () => void;
}

/**
 * Store Zustand pour gérer l'affichage de l'UpgradeBanner
 * Souscrit à l'eventBus pour écouter les événements paywall:plan et paywall:rate
 */
export const usePaywallStore = create<PaywallState>((set) => {
  // Souscription aux événements de l'eventBus
  // Les fonctions de désabonnement sont conservées pour un nettoyage futur si nécessaire
  void eventBus.on('paywall:plan', (payload?: unknown) => {
    const p = payload as PaywallPayload | undefined;
    set({
      visible: true,
      reason: 'plan',
      upgradeUrl: p?.upgradeUrl,
    });
  });

  void eventBus.on('paywall:rate', (payload?: unknown) => {
    const p = payload as PaywallPayload | undefined;
    set({
      visible: true,
      reason: 'rate',
      upgradeUrl: p?.upgradeUrl,
    });
  });

  return {
    visible: false,
    reason: undefined,
    upgradeUrl: undefined,

    showPaywall: (payload: PaywallPayload) => {
      set({
        visible: true,
        reason: payload.reason,
        upgradeUrl: payload.upgradeUrl,
      });
    },

    hidePaywall: () => {
      set({
        visible: false,
        reason: undefined,
        upgradeUrl: undefined,
      });
    },
  };
});
