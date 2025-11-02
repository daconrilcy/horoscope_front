import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { http, configureHttp } from './client';
import { useAuthStore } from '@/stores/authStore';
import { eventBus } from './eventBus';
import { ApiError, NetworkError } from './errors';

// Mock fetch
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).fetch = vi.fn();

describe('HTTP Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    configureHttp({
      baseURL: 'http://localhost:8000',
      onUnauthorized: vi.fn(),
    });
    useAuthStore.getState().clearToken();
    eventBus.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Configuration', () => {
    it('should configure baseURL correctly', async () => {
      configureHttp({
        baseURL: 'http://api.example.com',
        onUnauthorized: vi.fn(),
      });

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.get('/test');

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect((globalThis as any).fetch).toHaveBeenCalledWith(
        'http://api.example.com/test',
        expect.any(Object)
      );
    });
  });

  describe('Bearer Token Injection', () => {
    it('should inject Authorization header when auth is true and token exists', async () => {
      const token = 'test-jwt-token';
      useAuthStore.getState().setToken(token);

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.get('/test', { auth: true });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Authorization')).toBe(`Bearer ${token}`);
    });

    it('should not inject Authorization header when auth is false', async () => {
      const token = 'test-jwt-token';
      useAuthStore.getState().setToken(token);

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.get('/test', { auth: false });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Authorization')).toBeNull();
    });

    it('should not inject Authorization header when token is missing', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.get('/test', { auth: true });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Authorization')).toBeNull();
    });
  });

  describe('Idempotency-Key', () => {
    it('should add Idempotency-Key header only for /v1/billing/checkout', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.post('/v1/billing/checkout', {}, { idempotency: true });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Idempotency-Key')).toBeTruthy();
      expect(headers.get('Idempotency-Key')).toMatch(
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      );
    });

    it('should not add Idempotency-Key for other endpoints', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.post('/v1/auth/login', {}, { idempotency: true });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Idempotency-Key')).toBeNull();
    });

    it('should not add Idempotency-Key when idempotency is false', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{}',
      });

      await http.post('/v1/billing/checkout', {}, { idempotency: false });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const headers = callArgs[1]?.headers as Headers;
      expect(headers.get('Idempotency-Key')).toBeNull();
    });
  });

  describe('Response Parsing', () => {
    it('should parse JSON response by default', async () => {
      const data = { message: 'test' };
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify(data),
      });

      const result = await http.get<{ message: string }>('/test');
      expect(result).toEqual(data);
    });

    it('should handle 204 No Content without parsing', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers(),
      });

      const result = await http.del('/test');
      expect(result).toBeUndefined();
    });

    it('should parse blob for PDF content', async () => {
      const blob = new Blob(['pdf content'], { type: 'application/pdf' });
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/pdf' }),
        blob: async () => blob,
      });

      const result = await http.get<Blob>('/test.pdf');
      expect(result).toBeInstanceOf(Blob);
    });

    it('should parse text for HTML content', async () => {
      const html = '<html><body>Test</body></html>';
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'text/html' }),
        text: async () => html,
      });

      const result = await http.get<string>('/test.html', { parseAs: 'text' });
      expect(result).toBe(html);
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 and emit unauthorized event', async () => {
      const onUnauthorized = vi.fn();
      configureHttp({
        baseURL: 'http://localhost:8000',
        onUnauthorized,
      });

      const unauthorizedHandler = vi.fn();
      eventBus.on('unauthorized', unauthorizedHandler);

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify({ message: 'Unauthorized' }),
      });

      await expect(http.get('/test')).rejects.toThrow(ApiError);
      expect(unauthorizedHandler).toHaveBeenCalled();
      expect(onUnauthorized).toHaveBeenCalled();
    });

    it('should handle 402 and emit paywall event', async () => {
      const paywallHandler = vi.fn();
      eventBus.on('paywall', paywallHandler);

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 402,
        statusText: 'Payment Required',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () =>
          JSON.stringify({ message: 'Payment required', upgrade_url: 'https://checkout.example.com' }),
      });

      await expect(http.get('/test')).rejects.toThrow(ApiError);
      expect(paywallHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: 'plan',
          upgradeUrl: 'https://checkout.example.com',
        })
      );
    });

    it('should handle 429 and emit quota event', async () => {
      const quotaHandler = vi.fn();
      eventBus.on('quota', quotaHandler);

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify({ message: 'Rate limit exceeded' }),
      });

      await expect(http.get('/test')).rejects.toThrow(ApiError);
      expect(quotaHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: 'rate',
        })
      );
    });

    it('should handle 5xx with request_id from header', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: new Headers({
          'content-type': 'application/json',
          'x-request-id': 'req-12345',
        }),
        text: async () => JSON.stringify({ message: 'Server error' }),
      });

      try {
        await http.get('/test');
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(500);
        expect((error as ApiError).requestId).toBe('req-12345');
      }
    });

    it('should handle 5xx with request_id from body', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify({ message: 'Server error', request_id: 'req-body-123' }),
      });

      try {
        await http.get('/test');
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(500);
        expect((error as ApiError).requestId).toBe('req-body-123');
      }
    });

    it('should handle 400/422 with validation details', async () => {
      const validationErrors = { email: ['Invalid email'], password: ['Too short'] };
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify({ message: 'Validation failed', errors: validationErrors }),
      });

      try {
        await http.post('/test', {});
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(422);
        expect((error as ApiError).details).toEqual(validationErrors);
      }
    });

    it('should handle 404 without auto-redirect', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => JSON.stringify({ message: 'Resource not found' }),
      });

      await expect(http.get('/test')).rejects.toThrow(ApiError);
      // Aucun événement spécifique ne doit être émis pour 404
    });
  });

  describe('Network Errors', () => {
    it('should handle timeout', async () => {
      const controller = new AbortController();
      controller.abort();

      (global.fetch as ReturnType<typeof vi.fn>).mockImplementationOnce(() => {
        return Promise.reject(new Error('The operation was aborted'));
      });

      await expect(http.get('/test', { timeoutMs: 100 })).rejects.toThrow(NetworkError);
    });

    it('should handle offline errors', async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new TypeError('Failed to fetch'));

      await expect(http.get('/test')).rejects.toThrow(NetworkError);
    });
  });

  describe('Retry Logic', () => {
    it('should retry GET requests on NetworkError', async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockImplementation(() => {
        callCount++;
        if (callCount < 2) {
          return Promise.reject(new TypeError('Failed to fetch'));
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          headers: new Headers({ 'content-type': 'application/json' }),
          text: async () => '{}',
        });
      });

      const result = await http.get('/test');
      expect(callCount).toBe(2);
      expect(result).toEqual({});
    });

    it('should not retry POST requests', async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new TypeError('Failed to fetch'));

      await expect(http.post('/test', {})).rejects.toThrow(NetworkError);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect((globalThis as any).fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry when noRetry is true', async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new TypeError('Failed to fetch'));

      await expect(http.get('/test', { noRetry: true })).rejects.toThrow(NetworkError);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect((globalThis as any).fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry /v1/billing/checkout even for GET', async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new TypeError('Failed to fetch'));

      await expect(http.get('/v1/billing/checkout', { idempotency: true })).rejects.toThrow(
        NetworkError
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect((globalThis as any).fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('HTTP Methods', () => {
    it('should support GET', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{"method":"GET"}',
      });

      const result = await http.get('/test');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[1]?.method).toBe('GET');
      expect(result).toEqual({ method: 'GET' });
    });

    it('should support POST', async () => {
      const body = { test: 'data' };
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{"method":"POST"}',
      });

      await http.post('/test', body);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[1]?.method).toBe('POST');
      expect(callArgs[1]?.body).toBe(JSON.stringify(body));
    });

    it('should support PUT', async () => {
      const body = { test: 'data' };
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        text: async () => '{"method":"PUT"}',
      });

      await http.put('/test', body);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[1]?.method).toBe('PUT');
    });

    it('should support DELETE', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers(),
      });

      await http.del('/test');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const callArgs = ((globalThis as any).fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(callArgs[1]?.method).toBe('DELETE');
    });
  });
});

