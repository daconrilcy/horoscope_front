import { useState, useEffect } from 'react';
import { eventBus } from '@/shared/api/eventBus';

/**
 * Interface pour un breadcrumb d'observabilité
 */
export interface BillingBreadcrumb {
  event: string;
  requestId?: string;
  endpoint: string;
  fullUrl?: string; // URL complète pour générer CURL
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

    // Écouter l'événement générique api:request pour toutes les requêtes HTTP
    const unsubscribeApiRequest = eventBus.on('api:request', (payload?: unknown) => {
      if (payload != null && typeof payload === 'object') {
        const p = payload as Partial<BillingBreadcrumb>;
        const breadcrumb: BillingBreadcrumb = {
          event: 'api:request',
          requestId: p.requestId,
          endpoint: p.endpoint != null && p.endpoint !== '' ? p.endpoint : '',
          fullUrl: p.fullUrl,
          status: p.status != null && p.status !== 0 ? p.status : 0,
          timestamp: p.timestamp != null && p.timestamp !== 0 ? p.timestamp : Date.now(),
          duration: p.duration,
          method: p.method != null && p.method !== '' ? p.method : 'UNKNOWN',
        };

        setBreadcrumbs((prev) => {
          const updated = [breadcrumb, ...prev];
          // Garder seulement les MAX_BREADCRUMBS derniers
          return updated.slice(0, MAX_BREADCRUMBS);
        });
      }
    });

    // Écouter aussi les événements billing/terminal spécifiques pour un contexte supplémentaire
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
        if (payload != null && typeof payload === 'object') {
          const p = payload as Partial<BillingBreadcrumb>;
          const breadcrumb: BillingBreadcrumb = {
            event,
            requestId: p.requestId,
            endpoint: p.endpoint != null && p.endpoint !== '' ? p.endpoint : '',
            fullUrl: p.fullUrl,
            status: p.status != null && p.status !== 0 ? p.status : 0,
            timestamp: p.timestamp != null && p.timestamp !== 0 ? p.timestamp : Date.now(),
            duration: p.duration,
            method: p.method != null && p.method !== '' ? p.method : 'UNKNOWN',
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
      unsubscribeApiRequest();
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


