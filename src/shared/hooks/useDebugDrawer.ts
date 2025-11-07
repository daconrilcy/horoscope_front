import { useState, useEffect } from 'react';
import { eventBus } from '@/shared/api/eventBus';

/**
 * Interface pour un breadcrumb d'API
 */
export interface BillingBreadcrumb {
  event: string;
  requestId?: string;
  endpoint: string;
  fullUrl?: string;
  status: number;
  timestamp: number;
  duration?: number;
  method: string;
  headers?: Record<string, string>;
  body?: unknown;
}

const MAX_BREADCRUMBS = 50;

/**
 * Hook pour gérer le drawer de debug (dev-only)
 * Écoute les événements api:request et maintient une liste de breadcrumbs
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
    if (!import.meta.env.DEV) {
      return;
    }

    // Cache pour stocker les informations depuis l'événement 'start' et les associer à 'end'/'error'
    const requestCache = new Map<
      string,
      { headers?: Record<string, string>; body?: unknown }
    >();

    // Écouter les événements api:request
    const unsubscribeApiRequest = eventBus.on(
      'api:request',
      (payload?: unknown) => {
        if (payload != null && typeof payload === 'object') {
          const p = payload as {
            id?: string;
            phase?: string;
            requestId?: string;
            url?: string;
            fullUrl?: string;
            status?: number;
            ts?: number;
            durationMs?: number;
            method?: string;
            headers?: Record<string, string>;
            body?: unknown;
          };
          // Stocker les informations provenant de l'événement 'start'
          if (p.phase === 'start' && p.id != null) {
            requestCache.set(p.id, {
              headers: p.headers,
              body: p.body,
            });
          }
          // Ne garder que les événements 'end' et 'error' (pas 'start')
          if (p.phase === 'end' || p.phase === 'error') {
            // Récupérer les informations du cache si disponibles
            const cached = p.id != null ? requestCache.get(p.id) : undefined;
            const breadcrumb: BillingBreadcrumb = {
              event: 'api:request',
              requestId: p.requestId,
              endpoint: p.url != null && p.url !== '' ? p.url : '',
              fullUrl: p.fullUrl,
              status: p.status != null && p.status !== 0 ? p.status : 0,
              timestamp: p.ts != null && p.ts !== 0 ? p.ts : Date.now(),
              duration: p.durationMs,
              method:
                p.method != null && p.method !== '' ? p.method : 'UNKNOWN',
              headers: p.headers ?? cached?.headers,
              body:
                cached !== undefined && cached.body !== undefined
                  ? cached.body
                  : p.body,
            };
            setBreadcrumbs((prev) =>
              [breadcrumb, ...prev].slice(0, MAX_BREADCRUMBS)
            );
            // Nettoyer le cache après utilisation
            if (p.id != null) {
              requestCache.delete(p.id);
            }
          }
        }
      }
    );

    // Raccourci clavier Ctrl+Shift+D pour toggler
    const handleKeyDown = (e: KeyboardEvent): void => {
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      unsubscribeApiRequest();
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const toggle = (): void => {
    setIsOpen((prev) => !prev);
  };

  const clear = (): void => {
    setBreadcrumbs([]);
  };

  return {
    breadcrumbs,
    isOpen,
    toggle,
    clear,
  };
}
