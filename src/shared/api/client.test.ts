import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { http, configureHttp } from './client';
import { ApiError, NetworkError } from './errors';
import { eventBus } from './eventBus';

// Mock fetch global
globalThis.fetch = vi.fn();

// Mock useAuthStore
vi.mock('@/stores/authStore', () => ({
  useAuthStore: {
    getState: vi.fn(() => ({
      getToken: vi.fn(() => 'mock-token'),
    })),
  },
}));

// Mock eventBus
vi.mock('./eventBus', () => ({
  eventBus: {
    emit: vi.fn(),
    clear: vi.fn(),
  },
}));

describe('HTTP Client', () => {
  let emitSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
    emitSpy = vi.spyOn(eventBus, 'emit');
    configureHttp({ baseURL: 'https://api.example.com' });
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockClear();
  });

  afterEach(() => {
    eventBus.clear?.();
  });

  describe('Headers', () => {
    it('devrait injecter Authorization quand auth !== false', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.get('/test', { auth: true });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Authorization')).toBe('Bearer mock-token');
    });

    it('ne devrait pas injecter Authorization quand auth: false', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.get('/test', { auth: false });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Authorization')).toBeNull();
    });

    it('devrait injecter Idempotency-Key sur POST avec idempotency: true', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.post('/test', { data: 'test' }, { idempotency: true });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);
      const idempotencyKey = headers.get('Idempotency-Key');

      expect(idempotencyKey).toBeTruthy();
      // UUID v4 format
      expect(idempotencyKey).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      );
    });

    it('devrait injecter Idempotency-Key sur PUT avec idempotency: true', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.put('/test', { data: 'test' }, { idempotency: true });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Idempotency-Key')).toBeTruthy();
    });

    it('devrait injecter Idempotency-Key sur DELETE avec idempotency: true', async () => {
      const mockResponse = new Response(undefined, {
        status: 204,
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.del('/test', { idempotency: true });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Idempotency-Key')).toBeTruthy();
    });

    it('ne devrait pas injecter Idempotency-Key sur GET même si idempotency: true', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const consoleWarnSpy = vi
        .spyOn(console, 'warn')
        .mockImplementation(() => {
          // No-op
        });

      await http.get('/test', { idempotency: true });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Idempotency-Key')).toBeNull();
      // Warning en dev (ici on est en test, donc peut-être pas DEV, mais on vérifie quand même la logique)
      // Le warning sera vérifié si import.meta.env.DEV est true

      consoleWarnSpy.mockRestore();
    });

    it('ne devrait pas injecter Idempotency-Key quand idempotency: false', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.post('/test', { data: 'test' }, { idempotency: false });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Idempotency-Key')).toBeNull();
    });

    it('ne devrait pas injecter Idempotency-Key quand idempotency non défini', async () => {
      const mockResponse = new Response(JSON.stringify({ data: 'test' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await http.post('/test', { data: 'test' });

      const fetchCall = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
        .calls[0];
      const requestInit = fetchCall[1] as RequestInit | undefined;
      const headers =
        requestInit?.headers instanceof Headers
          ? requestInit.headers
          : new Headers(requestInit?.headers);

      expect(headers.get('Idempotency-Key')).toBeNull();
    });
  });

  describe('Error mapping', () => {
    it('devrait mapper 401 → événement unauthorized', async () => {
      const mockResponse = new Response(
        JSON.stringify({ message: 'Unauthorized' }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        }
      );

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(http.get('/test')).rejects.toThrow(ApiError);

      expect(emitSpy).toHaveBeenCalledWith('unauthorized');
    });

    it('devrait mapper 402 → événement paywall avec payload', async () => {
      const mockResponse = new Response(
        JSON.stringify({
          message: 'Payment required',
          upgrade_url: 'https://example.com/upgrade',
        }),
        {
          status: 402,
          headers: { 'Content-Type': 'application/json' },
        }
      );

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(http.get('/test')).rejects.toThrow(ApiError);

      expect(emitSpy).toHaveBeenCalledWith('paywall', {
        reason: 'plan',
        upgradeUrl: 'https://example.com/upgrade',
      });
    });

    it('devrait mapper 429 → événement quota avec payload', async () => {
      const mockResponse = new Response(
        JSON.stringify({
          message: 'Too many requests',
          upgrade_url: 'https://example.com/upgrade',
        }),
        {
          status: 429,
          headers: { 'Content-Type': 'application/json' },
        }
      );

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(http.get('/test')).rejects.toThrow(ApiError);

      expect(emitSpy).toHaveBeenCalledWith('quota', {
        reason: 'rate',
        upgradeUrl: 'https://example.com/upgrade',
      });
    });

    it('ne devrait pas rediriger sur 401 si URL contient /login', async () => {
      const onUnauthorizedSpy = vi.fn();
      configureHttp({
        baseURL: 'https://api.example.com',
        onUnauthorized: onUnauthorizedSpy,
      });

      const mockResponse = new Response(
        JSON.stringify({ message: 'Unauthorized' }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        }
      );

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(http.get('/login')).rejects.toThrow(ApiError);

      // L'événement est émis, mais le callback n'est pas appelé
      expect(emitSpy).toHaveBeenCalledWith('unauthorized');
      expect(onUnauthorizedSpy).not.toHaveBeenCalled();
    });
  });

  describe('Timeout', () => {
    it('devrait retourner NetworkError timeout', async () => {
      // Simuler un fetch qui ne répond jamais (timeout)
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockImplementation(
        () =>
          new Promise((_resolve, reject) => {
            // Ne jamais résoudre, le timeout du client va l'abort
            setTimeout(() => {
              const error = new Error('aborted');
              (error as { name?: string }).name = 'AbortError';
              reject(error);
            }, 150);
          })
      );

      try {
        await http.get('/test', { timeoutMs: 100 });
        expect.fail('Should have thrown NetworkError');
      } catch (error) {
        expect(error).toBeInstanceOf(NetworkError);
        if (error instanceof NetworkError) {
          expect(error.reason).toBe('timeout');
        }
      }
    }, 10000);
  });

  describe('Parsing', () => {
    it('devrait retourner undefined pour 204 No Content', async () => {
      const mockResponse = new Response(undefined, {
        status: 204,
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await http.del('/test');

      expect(result).toBeUndefined();
    });

    it('devrait parser JSON quand Content-Type est application/json', async () => {
      const mockData = { data: 'test' };
      const mockResponse = new Response(JSON.stringify(mockData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await http.get<typeof mockData>('/test');

      expect(result).toEqual(mockData);
    });

    it('devrait retourner blob pour application/pdf', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
      const mockResponse = new Response(mockBlob, {
        status: 200,
        headers: { 'Content-Type': 'application/pdf' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await http.get<Blob>('/test');

      // Vérifier que c'est un Blob ou au moins qu'il a les propriétés d'un Blob
      expect(result).toBeDefined();
      expect(typeof result?.size).toBe('number');
      expect(result?.type).toBe('application/pdf');
    });

    it('devrait retourner text pour text/html', async () => {
      const mockHtml = '<html><body>Test</body></html>';
      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: { 'Content-Type': 'text/html' },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await http.get<string>('/test');

      expect(result).toBe(mockHtml);
    });

    it('devrait lancer ApiError si JSON invalide avec Content-Type application/json', async () => {
      // Créer une réponse avec JSON invalide
      const mockResponse = {
        status: 200,
        ok: true,
        headers: new Headers({ 'Content-Type': 'application/json' }),
        text: vi.fn().mockResolvedValue('invalid json'),
        blob: vi.fn(),
      };

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse as unknown as Response
      );

      try {
        await http.get('/test');
        expect.fail('Should have thrown ApiError');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.message).toBe('invalid-json');
        }
      }
    });
  });

  describe('request_id extraction', () => {
    it('devrait extraire request_id depuis headers x-request-id', async () => {
      const mockResponse = new Response(JSON.stringify({ message: 'Error' }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          'x-request-id': 'req-123',
        },
      });

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      try {
        await http.get('/test');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.requestId).toBe('req-123');
        }
      }
    });

    it('devrait extraire request_id depuis body si absent dans headers', async () => {
      const mockResponse = new Response(
        JSON.stringify({ message: 'Error', request_id: 'req-456' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );

      (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      try {
        await http.get('/test');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.requestId).toBe('req-456');
        }
      }
    });
  });

  describe('Retry policy', () => {
    it('ne devrait pas retry sur POST (mutation)', async () => {
      let attemptCount = 0;
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockImplementation(() => {
        attemptCount++;
        return Promise.reject(new TypeError('Network error'));
      });

      await expect(http.post('/test', { data: 'test' })).rejects.toThrow();

      // Pas de retry sur mutations
      expect(attemptCount).toBe(1);
    });

    it('devrait retry sur GET si NetworkError (max 2 retries)', async () => {
      let attemptCount = 0;
      (globalThis.fetch as ReturnType<typeof vi.fn>).mockImplementation(() => {
        attemptCount++;
        if (attemptCount < 3) {
          return Promise.reject(new TypeError('Network error'));
        }
        return Promise.resolve(
          new Response(JSON.stringify({ data: 'success' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      });

      await http.get('/test');

      // 1 tentative initiale + 2 retries = 3 tentatives
      expect(attemptCount).toBe(3);
    });
  });
});
