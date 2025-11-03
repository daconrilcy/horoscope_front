import { describe, it, expect, beforeEach, vi } from 'vitest';
import { horoscopeService } from './horoscope.service';
import { ApiError } from './errors';
import { http } from './client';

// Mock le client HTTP
vi.mock('./client', () => ({
  configureHttp: vi.fn(),
  http: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('horoscopeService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createNatal', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        chart_id: 'chart-12345678',
        created_at: '2024-01-01T12:00:00Z',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await horoscopeService.createNatal({
        date: '2024-01-01',
        time: '12:00',
        latitude: 48.8566,
        longitude: 2.3522,
        timezone: 'Europe/Paris',
      });

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/horoscope/natal', {
        date: '2024-01-01',
        time: '12:00',
        latitude: 48.8566,
        longitude: 2.3522,
        timezone: 'Europe/Paris',
      });
    });

    it('devrait échouer si chart_id trop court (validation Zod)', async () => {
      const mockResponse = {
        chart_id: 'short', // Trop court
        created_at: '2024-01-01T12:00:00Z',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        horoscopeService.createNatal({
          date: '2024-01-01',
          time: '12:00',
          latitude: 48.8566,
          longitude: 2.3522,
          timezone: 'Europe/Paris',
        })
      ).rejects.toThrow();
    });

    it('devrait exposer details dans ApiError pour 422', async () => {
      const mockError = new ApiError(
        'Validation failed',
        422,
        undefined,
        undefined,
        {
          latitude: ['Latitude invalide'],
          longitude: ['Longitude invalide'],
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.createNatal({
          date: '2024-01-01',
          time: '12:00',
          latitude: 48.8566,
          longitude: 2.3522,
          timezone: 'Europe/Paris',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait gérer 401 (non authentifié)', async () => {
      const mockError = new ApiError('Unauthorized', 401);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.createNatal({
          date: '2024-01-01',
          time: '12:00',
          latitude: 48.8566,
          longitude: 2.3522,
          timezone: 'Europe/Paris',
        })
      ).rejects.toThrow(mockError);
    });
  });

  describe('getToday', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        content: 'Votre horoscope du jour...',
        generated_at: '2024-01-01T12:00:00Z',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await horoscopeService.getToday('chart-12345678');

      expect(result).toEqual(mockResponse);
      expect(mockHttpGet).toHaveBeenCalledWith(
        '/v1/horoscope/today/chart-12345678'
      );
    });

    it('devrait échouer si chartId inconnu (404)', async () => {
      const mockError = new ApiError('Chart not found', 404);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(horoscopeService.getToday('unknown-chart')).rejects.toThrow(
        mockError
      );
    });

    it('devrait échouer si réponse invalide (ZodError)', async () => {
      const mockResponse = {
        content: '', // Contenu vide (invalide)
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      await expect(
        horoscopeService.getToday('chart-12345678')
      ).rejects.toThrow();
    });
  });

  describe('getTodayPremium', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        content: 'Votre horoscope premium...',
        premium_insights: 'Insights premium...',
        generated_at: '2024-01-01T12:00:00Z',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);

      const result = await horoscopeService.getTodayPremium('chart-12345678');

      expect(result).toEqual(mockResponse);
      expect(mockHttpGet).toHaveBeenCalledWith(
        '/v1/horoscope/today/premium/chart-12345678'
      );
    });

    it('devrait échouer si chartId inconnu (404)', async () => {
      const mockError = new ApiError('Chart not found', 404);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.getTodayPremium('unknown-chart')
      ).rejects.toThrow(mockError);
    });

    it('devrait gérer 402 (plan insuffisant)', async () => {
      const mockError = new ApiError('Payment Required', 402);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.getTodayPremium('chart-12345678')
      ).rejects.toThrow(mockError);
    });
  });

  describe('getNatalPdfStream', () => {
    it('devrait réussir avec blob PDF valide', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockResolvedValue(mockBlob);

      const result = await horoscopeService.getNatalPdfStream('chart-12345678');

      expect(result.blob).toBe(mockBlob);
      expect(result.filename).toBe('natal-chart-12345678.pdf');
      expect(mockHttpGet).toHaveBeenCalledWith(
        '/v1/horoscope/pdf/natal/chart-12345678',
        { parseAs: 'blob' }
      );
    });

    it('devrait échouer si chartId inconnu (404)', async () => {
      const mockError = new ApiError('Chart not found', 404);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.getNatalPdfStream('unknown-chart')
      ).rejects.toThrow('Chart not found');
    });

    it('devrait gérer 500 (génération échouée)', async () => {
      const mockError = new ApiError('Internal Server Error', 500);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpGet = vi.mocked(http.get);
      (mockHttpGet as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        horoscopeService.getNatalPdfStream('chart-12345678')
      ).rejects.toThrow(mockError);
    });
  });
});
