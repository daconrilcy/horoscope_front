import {
  describe,
  it,
  expect,
  beforeEach,
  vi,
  beforeAll,
  afterAll,
} from 'vitest';
import { legalService } from './legal.service';
import { ApiError, NetworkError } from './errors';
import { server } from '@/test/setup/msw.server';

// Mock le module env
vi.mock('../config/env', () => ({
  env: {
    VITE_API_BASE_URL: 'https://api.example.com',
  },
}));

// Mock fetch global
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('legalService', () => {
  // Désactiver MSW pour ce test car nous utilisons mockFetch directement
  beforeAll(() => {
    server.close();
  });

  afterAll(() => {
    server.listen({ onUnhandledRequest: 'warn' });
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getTos', () => {
    it('devrait réussir avec HTML valide et métadonnées', async () => {
      const mockHtml =
        "<html><body><h1>Conditions d'utilisation</h1></body></html>";
      const mockHeaders = new Headers({
        'content-type': 'text/html; charset=utf-8',
        etag: '"abc123"',
        'last-modified': 'Mon, 01 Jan 2024 12:00:00 GMT',
        'x-legal-version': '1.0.0',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getTos();

      expect(result.html).toBe(mockHtml);
      expect(result.etag).toBe('abc123'); // Guillemets retirés
      expect(result.lastModified).toBe('Mon, 01 Jan 2024 12:00:00 GMT');
      expect(result.version).toBe('1.0.0');
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/v1/legal/tos',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('devrait réussir sans métadonnées', async () => {
      const mockHtml = '<html><body><h1>TOS</h1></body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getTos();

      expect(result.html).toBe(mockHtml);
      expect(result.etag).toBeUndefined();
      expect(result.lastModified).toBeUndefined();
      expect(result.version).toBeUndefined();
    });

    it('devrait accepter text/plain comme Content-Type', async () => {
      const mockHtml = '<html><body><h1>TOS</h1></body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/plain; charset=utf-8',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getTos();

      expect(result.html).toBe(mockHtml);
    });

    it('devrait échouer si Content-Type est application/json', async () => {
      const mockJson = JSON.stringify({ message: 'Not HTML' });
      const mockHeaders = new Headers({
        'content-type': 'application/json',
      });

      const mockResponse = new Response(mockJson, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      await expect(legalService.getTos()).rejects.toThrow(ApiError);
      await expect(legalService.getTos()).rejects.toThrow(
        /Invalid content type/
      );
    });

    it('devrait gérer 404', async () => {
      const mockHeaders = new Headers({
        'content-type': 'application/json',
        'x-request-id': 'req-123',
      });

      const mockResponse = new Response(
        JSON.stringify({ message: 'Not found' }),
        {
          status: 404,
          headers: mockHeaders,
        }
      );

      mockFetch.mockResolvedValue(mockResponse);

      await expect(legalService.getTos()).rejects.toThrow(ApiError);

      try {
        await legalService.getTos();
      } catch (error) {
        if (error instanceof ApiError) {
          expect(error.status).toBe(404);
          expect(error.requestId).toBe('req-123');
        }
      }
    });

    it('devrait gérer 500', async () => {
      const mockHeaders = new Headers({
        'content-type': 'application/json',
      });

      const mockResponse = new Response(
        JSON.stringify({ message: 'Internal server error' }),
        {
          status: 500,
          headers: mockHeaders,
        }
      );

      mockFetch.mockResolvedValue(mockResponse);

      await expect(legalService.getTos()).rejects.toThrow(ApiError);
    });

    it('devrait gérer NetworkError (offline)', async () => {
      mockFetch.mockRejectedValue(new TypeError('Failed to fetch'));

      await expect(legalService.getTos()).rejects.toThrow(NetworkError);
      await expect(legalService.getTos()).rejects.toThrow(/offline/);
    });

    it('devrait gérer NetworkError (aborted)', async () => {
      const error = new Error('aborted');
      (error as { name?: string }).name = 'AbortError';
      mockFetch.mockRejectedValue(error);

      await expect(legalService.getTos()).rejects.toThrow(NetworkError);
      await expect(legalService.getTos()).rejects.toThrow(/aborted/);
    });
  });

  describe('getPrivacy', () => {
    it('devrait réussir avec HTML valide et métadonnées', async () => {
      const mockHtml =
        '<html><body><h1>Politique de confidentialité</h1></body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html; charset=utf-8',
        etag: '"def456"',
        'last-modified': 'Tue, 02 Jan 2024 12:00:00 GMT',
        'x-legal-version': '2.0.0',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getPrivacy();

      expect(result.html).toBe(mockHtml);
      expect(result.etag).toBe('def456');
      expect(result.lastModified).toBe('Tue, 02 Jan 2024 12:00:00 GMT');
      expect(result.version).toBe('2.0.0');
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/v1/legal/privacy',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('devrait gérer ETag sans guillemets', async () => {
      const mockHtml = '<html><body><h1>Privacy</h1></body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html',
        etag: 'abc123', // Sans guillemets
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getPrivacy();

      expect(result.etag).toBe('abc123');
    });

    it('devrait gérer ETag avec guillemets doubles', async () => {
      const mockHtml = '<html><body><h1>Privacy</h1></body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html',
        etag: '"xyz789"',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getPrivacy();

      expect(result.etag).toBe('xyz789'); // Guillemets retirés
    });

    it('devrait échouer si Content-Type est inattendu', async () => {
      const mockHeaders = new Headers({
        'content-type': 'application/xml',
      });

      const mockResponse = new Response('<xml>...</xml>', {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      await expect(legalService.getPrivacy()).rejects.toThrow(ApiError);
      await expect(legalService.getPrivacy()).rejects.toThrow(
        /Invalid content type/
      );
    });
  });

  describe('gestion des request_id', () => {
    it('devrait extraire x-request-id', async () => {
      const mockHtml = '<html><body>Test</body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html',
        'x-request-id': 'req-abc',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getTos();
      expect(result.html).toBe(mockHtml);

      // Test avec erreur pour vérifier requestId
      const errorHeaders = new Headers({
        'content-type': 'application/json',
        'x-request-id': 'req-error',
      });

      const errorResponse = new Response(JSON.stringify({ message: 'Error' }), {
        status: 500,
        headers: errorHeaders,
      });

      mockFetch.mockResolvedValue(errorResponse);

      try {
        await legalService.getTos();
      } catch (error) {
        if (error instanceof ApiError) {
          expect(error.requestId).toBe('req-error');
        }
      }
    });

    it('devrait extraire x-trace-id si x-request-id absent', async () => {
      const mockHtml = '<html><body>Test</body></html>';
      const mockHeaders = new Headers({
        'content-type': 'text/html',
        'x-trace-id': 'trace-xyz',
      });

      const mockResponse = new Response(mockHtml, {
        status: 200,
        headers: mockHeaders,
      });

      mockFetch.mockResolvedValue(mockResponse);

      const result = await legalService.getTos();
      expect(result.html).toBe(mockHtml);

      // Test avec erreur
      const errorHeaders = new Headers({
        'content-type': 'application/json',
        'x-trace-id': 'trace-error',
      });

      const errorResponse = new Response(JSON.stringify({ message: 'Error' }), {
        status: 500,
        headers: errorHeaders,
      });

      mockFetch.mockResolvedValue(errorResponse);

      try {
        await legalService.getTos();
      } catch (error) {
        if (error instanceof ApiError) {
          expect(error.requestId).toBe('trace-error');
        }
      }
    });
  });
});
