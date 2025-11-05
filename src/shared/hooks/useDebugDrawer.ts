import { useState, useEffect } from 'react';
import { eventBus } from '@/shared/api/eventBus';

/**
 * Interface pour un breadcrumb d'observabilité
 */
export interface BillingBreadcrumb {
  event: string;
  requestId?: string;
  endpoint: string;
  status: number;
  timestamp: number;
  duration?: number;
  method: string;
}

/**
 * Taille maximale du buffer de breadcrumbs
 */
const MAX_BREADCRUMBS = 200;

/**
 * Hook pour gérer le DebugDrawer (dev-only)
 * Écoute les événements billing/terminal et stocke les breadcrumbs
 */
export function useDebugDrawer(): {
  breadcrumbs: BillingBreadcrumb[];
  isOpen: boolean;
  toggle: () => void;
  clear: () => void;
} {
  const [breadcrumbs, setBreadcrumbs] = useState<BillingBreadcrumb[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Masquer complètement en production (tree-shake)
    if (!import.meta.env.DEV) {
      return;
    }

    // Écouter tous les événements billing/terminal
    const events: Array<
      | 'billing:checkout'
      | 'billing:portal'
      | 'terminal:connect'
      | 'terminal:payment_intent'
      | 'terminal:process'
      | 'terminal:capture'
      | 'terminal:cancel'
      | 'terminal:refund'
    > = [
      'billing:checkout',
      'billing:portal',
      'terminal:connect',
      'terminal:payment_intent',
      'terminal:process',
      'terminal:capture',
      'terminal:cancel',
      'terminal:refund',
    ];

    const unsubscribers = events.map((event) => {
      return eventBus.on(event, (payload?: unknown) => {
        if (payload && typeof payload === 'object') {
          const p = payload as Partial<BillingBreadcrumb>;
          const breadcrumb: BillingBreadcrumb = {
            event,
            requestId: p.requestId,
            endpoint: p.endpoint || '',
            status: p.status || 0,
            timestamp: p.timestamp || Date.now(),
            duration: p.duration,
            method: p.method || 'UNKNOWN',
          };

          setBreadcrumbs((prev) => {
            const updated = [breadcrumb, ...prev];
            // Garder seulement les MAX_BREADCRUMBS derniers
            return updated.slice(0, MAX_BREADCRUMBS);
          });
        }
      });
    });

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, []);

  // Raccourci clavier Ctrl+Shift+D
  useEffect(() => {
    if (!import.meta.env.DEV) {
      return;
    }

    const handleKeyDown = (e: KeyboardEvent): void => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const toggle = (): void => {
    setIsOpen((prev) => !prev);
  };

  const clear = (): void => {
    setBreadcrumbs([]);
  };

  return { breadcrumbs, isOpen, toggle, clear };
}


