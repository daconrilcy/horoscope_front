import { describe, it, expect, beforeEach, vi } from 'vitest';
import { authService } from './auth.service';
import { ApiError } from './errors';
import { http } from './client';

// Mock le client HTTP
vi.mock('./client', () => ({
  configureHttp: vi.fn(),
  http: {
    post: vi.fn(),
  },
}));

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('signup', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        token: 'valid-token-1234567890',
        user: {
          id: '123e4567-e89b-12d3-a456-426614174000',
          email: 'test@example.com',
        },
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await authService.signup(
        'test@example.com',
        'password123'
      );

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/auth/signup',
        { email: 'test@example.com', password: 'password123' },
        { auth: false }
      );
    });

    it('devrait échouer si réponse invalide (validation Zod)', async () => {
      const mockResponse = {
        token: 'short', // Token trop court
        user: {
          id: '123',
          email: 'invalid-email', // Email invalide
        },
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        authService.signup('test@example.com', 'password123')
      ).rejects.toThrow();
    });

    it('devrait exposer details dans ApiError pour 422', async () => {
      const mockError = new ApiError(
        'Validation failed',
        422,
        undefined,
        undefined,
        {
          email: ['Email déjà utilisé'],
          password: ['Mot de passe trop faible'],
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        authService.signup('test@example.com', 'password123')
      ).rejects.toThrow(ApiError);

      try {
        await authService.signup('test@example.com', 'password123');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(422);
          expect(error.details).toEqual({
            email: ['Email déjà utilisé'],
            password: ['Mot de passe trop faible'],
          });
        }
      }
    });

    it('devrait propager ApiError 400', async () => {
      const mockError = new ApiError('Bad request', 400);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        authService.signup('test@example.com', 'password123')
      ).rejects.toThrow(ApiError);
    });
  });

  describe('login', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        token: 'valid-token-1234567890',
        user: {
          id: '123e4567-e89b-12d3-a456-426614174000',
          email: 'test@example.com',
        },
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await authService.login('test@example.com', 'password123');

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/auth/login',
        { email: 'test@example.com', password: 'password123' },
        { auth: false }
      );
    });

    it('devrait échouer si réponse invalide (validation Zod)', async () => {
      const mockResponse = {
        token: 'short', // Token trop court
        user: {
          id: '123',
          email: 'invalid-email', // Email invalide
        },
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        authService.login('test@example.com', 'password123')
      ).rejects.toThrow();
    });

    it('devrait propager ApiError 401', async () => {
      const mockError = new ApiError('Unauthorized', 401);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        authService.login('test@example.com', 'password123')
      ).rejects.toThrow(ApiError);
    });

    it('devrait exposer details dans ApiError pour 422', async () => {
      const mockError = new ApiError(
        'Validation failed',
        422,
        undefined,
        undefined,
        {
          email: ['Email invalide'],
          password: ['Mot de passe requis'],
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      try {
        await authService.login('test@example.com', 'password123');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(422);
          expect(error.details).toEqual({
            email: ['Email invalide'],
            password: ['Mot de passe requis'],
          });
        }
      }
    });
  });

  describe('requestReset', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        message: 'Email envoyé',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await authService.requestReset('test@example.com');

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/auth/reset/request',
        { email: 'test@example.com' },
        { auth: false }
      );
    });

    it('devrait échouer si réponse invalide (validation Zod)', async () => {
      const mockResponse = {
        // message manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        authService.requestReset('test@example.com')
      ).rejects.toThrow();
    });

    it('devrait propager ApiError 400', async () => {
      const mockError = new ApiError('Bad request', 400);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        authService.requestReset('test@example.com')
      ).rejects.toThrow(ApiError);
    });
  });

  describe('confirmReset', () => {
    it('devrait réussir avec réponse valide', async () => {
      const mockResponse = {
        message: 'Mot de passe réinitialisé',
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      const result = await authService.confirmReset(
        'token-123',
        'newpassword123'
      );

      expect(result).toEqual(mockResponse);
      expect(mockHttpPost).toHaveBeenCalledWith(
        '/v1/auth/reset/confirm',
        { token: 'token-123', password: 'newpassword123' },
        { auth: false }
      );
    });

    it('devrait échouer si réponse invalide (validation Zod)', async () => {
      const mockResponse = {
        // message manquant
      };

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockResolvedValue(
        mockResponse
      );

      await expect(
        authService.confirmReset('token-123', 'newpassword123')
      ).rejects.toThrow();
    });

    it('devrait exposer details dans ApiError pour 422', async () => {
      const mockError = new ApiError(
        'Validation failed',
        422,
        undefined,
        undefined,
        {
          token: ['Token invalide ou expiré'],
          password: ['Mot de passe trop faible'],
        }
      );

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      try {
        await authService.confirmReset('token-123', 'newpassword123');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(422);
          expect(error.details).toEqual({
            token: ['Token invalide ou expiré'],
            password: ['Mot de passe trop faible'],
          });
        }
      }
    });

    it('devrait propager ApiError 400', async () => {
      const mockError = new ApiError('Bad request', 400);

      // eslint-disable-next-line @typescript-eslint/unbound-method
      const mockHttpPost = vi.mocked(http.post);
      (mockHttpPost as ReturnType<typeof vi.fn>).mockRejectedValue(mockError);

      await expect(
        authService.confirmReset('token-123', 'newpassword123')
      ).rejects.toThrow(ApiError);
    });
  });
});
