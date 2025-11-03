import { describe, it, expect, beforeEach, vi } from 'vitest';
import { chatService } from './chat.service';
import { ApiError } from './errors';
import { NetworkError } from './errors';
import { http } from './client';

// Mock le client HTTP
vi.mock('./client', () => ({
  http: {
    post: vi.fn(),
  },
}));

describe('chatService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('advise', () => {
    it('devrait retourner réponse valide avec answer', async () => {
      const mockResponse = {
        answer:
          'Vous avez une forte présence martienne dans votre thème natal.',
        generated_at: '2024-01-01T12:00:00Z',
        request_id: 'req-123456',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await chatService.advise({
        chart_id: 'chart-12345678',
        question: 'Parle-moi de mon ascendant',
      });

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/chat/advise', {
        chart_id: 'chart-12345678',
        question: 'Parle-moi de mon ascendant',
      });
    });

    it('devrait réussir avec answer minimal sans metadata', async () => {
      const mockResponse = {
        answer: 'Réponse simple',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await chatService.advise({
        chart_id: 'chart-12345678',
        question: 'Quoi de neuf?',
      });

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith('/v1/chat/advise', {
        chart_id: 'chart-12345678',
        question: 'Quoi de neuf?',
      });
    });

    it('devrait appeler avec body exact { chart_id, question }', async () => {
      const mockResponse = {
        answer: 'Test réponse',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await chatService.advise({
        chart_id: 'chart-87654321',
        question: 'Quelle est ma destinée?',
      });

      expect(mockHttpPost).toHaveBeenCalledWith('/v1/chat/advise', {
        chart_id: 'chart-87654321',
        question: 'Quelle est ma destinée?',
      });
    });

    it('devrait throw ApiError si 401 Unauthorized', async () => {
      const mockError = new ApiError('Unauthorized', 401, 'unauthorized');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait throw ApiError si 402 Payment Required', async () => {
      const mockError = new ApiError(
        'Payment required',
        402,
        'payment_required'
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait throw ApiError si 429 Too Many Requests', async () => {
      const mockError = new ApiError('Too many requests', 429, 'rate_limit');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait throw ApiError si 500 Internal Server Error', async () => {
      const mockError = new ApiError('Internal server error', 500);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait throw NetworkError si erreur réseau timeout', async () => {
      const mockError = new NetworkError('timeout', 'Request timeout');

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow(mockError);
    });

    it('devrait throw ZodError si answer manquant', async () => {
      const mockResponse = {}; // Pas de answer

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow('Invalid advise response');
    });

    it('devrait throw ZodError si answer vide', async () => {
      const mockResponse = { answer: '' }; // answer vide

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow('Invalid advise response');
    });

    it('devrait throw ZodError si generated_at format invalide', async () => {
      const mockResponse = {
        answer: 'Réponse OK',
        generated_at: 'not-a-valid-datetime',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        chatService.advise({
          chart_id: 'chart-12345678',
          question: 'Question test',
        })
      ).rejects.toThrow('Invalid advise response');
    });
  });
});
