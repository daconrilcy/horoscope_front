import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDebugDrawer } from './useDebugDrawer';
import { eventBus } from '@/shared/api/eventBus';

// Mock eventBus
vi.mock('@/shared/api/eventBus', () => {
  const listeners = new Map<string, Set<(payload?: unknown) => void>>();

  return {
    eventBus: {
      on: vi.fn((event: string, callback: (payload?: unknown) => void): (() => void) => {
        if (!listeners.has(event)) {
          listeners.set(event, new Set());
        }
        listeners.get(event)!.add(callback);
        return (): void => {
          listeners.get(event)?.delete(callback);
        };
      }),
      emit: (event: string, payload?: unknown): void => {
        listeners.get(event)?.forEach((callback) => {
          callback(payload);
        });
      },
      clear: (): void => {
        listeners.clear();
      },
    },
  };
});

describe('useDebugDrawer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock import.meta.env.DEV
    vi.stubGlobal('import_meta_env_DEV', true);
  });

  it('devrait initialiser avec un tableau de breadcrumbs vide', () => {
    const { result } = renderHook(() => useDebugDrawer());
    expect(result.current.breadcrumbs).toEqual([]);
    expect(result.current.isOpen).toBe(false);
  });

  it('devrait ajouter un breadcrumb quand un événement api:request est émis', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    const payload = {
      method: 'GET',
      endpoint: '/v1/config',
      fullUrl: 'https://api.example.com/v1/config',
      status: 200,
      requestId: 'req-123',
      timestamp: Date.now(),
      duration: 150,
    };

    eventBus.emit('api:request', payload);

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(1);
    });

    expect(result.current.breadcrumbs[0]).toMatchObject({
      event: 'api:request',
      method: 'GET',
      endpoint: '/v1/config',
      fullUrl: 'https://api.example.com/v1/config',
      status: 200,
      requestId: 'req-123',
      duration: 150,
    });
  });

  it('devrait limiter le nombre de breadcrumbs à MAX_BREADCRUMBS', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    // Émettre plus de MAX_BREADCRUMBS événements
    for (let i = 0; i < 250; i++) {
      eventBus.emit('api:request', {
        method: 'GET',
        endpoint: `/v1/test/${i}`,
        status: 200,
        timestamp: Date.now(),
        duration: 100,
      });
    }

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(200); // MAX_BREADCRUMBS
    });
  });

  it('devrait ajouter les breadcrumbs dans l\'ordre chronologique inverse', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    const timestamp1 = Date.now();
    const timestamp2 = timestamp1 + 1000;

    eventBus.emit('api:request', {
      method: 'GET',
      endpoint: '/v1/first',
      status: 200,
      timestamp: timestamp1,
    });

    eventBus.emit('api:request', {
      method: 'POST',
      endpoint: '/v1/second',
      status: 201,
      timestamp: timestamp2,
    });

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(2);
    });

    // Le dernier événement doit être en premier
    expect(result.current.breadcrumbs[0].endpoint).toBe('/v1/second');
    expect(result.current.breadcrumbs[1].endpoint).toBe('/v1/first');
  });

  it('devrait permettre de toggle l\'ouverture du drawer', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    expect(result.current.isOpen).toBe(false);

    result.current.toggle();
    await waitFor(() => {
      expect(result.current.isOpen).toBe(true);
    });

    result.current.toggle();
    await waitFor(() => {
      expect(result.current.isOpen).toBe(false);
    });
  });

  it('devrait permettre de clear les breadcrumbs', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    eventBus.emit('api:request', {
      method: 'GET',
      endpoint: '/v1/test',
      status: 200,
      timestamp: Date.now(),
    });

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(1);
    });

    result.current.clear();

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(0);
    });
  });

  it('devrait écouter les événements billing/terminal', async () => {
    const { result } = renderHook(() => useDebugDrawer());

    eventBus.emit('billing:checkout', {
      method: 'POST',
      endpoint: '/v1/billing/checkout',
      status: 200,
      requestId: 'req-billing',
      timestamp: Date.now(),
    });

    await waitFor(() => {
      expect(result.current.breadcrumbs.length).toBe(1);
    });

    expect(result.current.breadcrumbs[0].event).toBe('billing:checkout');
  });
});
