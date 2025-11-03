import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChat } from './useChat';
import { chatService } from '@/shared/api/chat.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useChatStore } from '@/stores/chatStore';
import { usePaywall } from '@/features/billing/hooks/usePaywall';
import React from 'react';

// Mock chatService
vi.mock('@/shared/api/chat.service', () => ({
  chatService: {
    advise: vi.fn(),
  },
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

// Mock usePaywall
vi.mock('@/features/billing/hooks/usePaywall', () => ({
  usePaywall: vi.fn(),
}));

// Mock useChatStore
vi.mock('@/stores/chatStore', () => ({
  useChatStore: vi.fn(),
}));

describe('useChat', () => {
  let queryClient: QueryClient;
  let mockAddMessage: ReturnType<typeof vi.fn>;
  let mockGetMessages: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();

    mockAddMessage = vi.fn();
    mockGetMessages = vi.fn(
      () =>
        [] as Array<{
          id: string;
          role: 'user' | 'assistant';
          content: string;
          ts: number;
        }>
    );

    // Mock useChatStore
    vi.mocked(useChatStore).mockImplementation((selector) => {
      return selector({
        addMessage: mockAddMessage,
        getMessages: mockGetMessages as (chartId: string) => Array<{
          id: string;
          role: 'user' | 'assistant';
          content: string;
          ts: number;
        }>,
        clearMessages: vi.fn(),
        byChart: {},
        hasHydrated: true,
        hydrateFromStorage: vi.fn(),
      });
    });

    // Mock usePaywall par défaut (autorisé)
    (vi.mocked(usePaywall) as ReturnType<typeof vi.fn>).mockReturnValue({
      isAllowed: true,
      reason: undefined,
      retryAfter: undefined,
      isLoading: false,
      error: null,
    });
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait appeler chatService.advise et ajouter message assistant sur succès', async () => {
    const mockResponse = {
      answer: 'Réponse du bot',
      generated_at: '2024-01-01T12:00:00Z',
    };

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await result.current.ask('Ma question');

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    expect(mockAdvise).toHaveBeenCalledWith({
      chart_id: 'chart-123',
      question: 'Ma question',
    });

    // Vérifier que le message user a été ajouté (optimistic)
    expect(mockAddMessage).toHaveBeenCalledWith(
      'chart-123',
      'user',
      'Ma question'
    );
    // Vérifier que la réponse assistant a été ajoutée
    expect(mockAddMessage).toHaveBeenCalledWith(
      'chart-123',
      'assistant',
      mockResponse.answer
    );
  });

  it("devrait bloquer l'envoi si isAllowed=false (plan insuffisant)", async () => {
    (vi.mocked(usePaywall) as ReturnType<typeof vi.fn>).mockReturnValue({
      isAllowed: false,
      reason: 'plan',
      retryAfter: undefined,
      isLoading: false,
      error: null,
    });

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await result.current.ask('Ma question');

    // Aucun appel au service
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(chatService.advise).not.toHaveBeenCalled();
    // Toast info affiché
    expect(toast.info).toHaveBeenCalledWith(
      'Cette fonctionnalité est réservée au plan Plus.'
    );
  });

  it("devrait bloquer l'envoi si isAllowed=false (quota)", async () => {
    (vi.mocked(usePaywall) as ReturnType<typeof vi.fn>).mockReturnValue({
      isAllowed: false,
      reason: 'rate',
      retryAfter: 3600,
      isLoading: false,
      error: null,
    });

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await result.current.ask('Ma question');

    // Aucun appel au service
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(chatService.advise).not.toHaveBeenCalled();
    // Toast info affiché
    expect(toast.info).toHaveBeenCalledWith(
      "Quota atteint pour aujourd'hui. Passez à un plan supérieur pour continuer."
    );
  });

  it('devrait bloquer les appels supplémentaires si isPending (double-submit)', async () => {
    let resolvePromise: (value: {
      answer: string;
      generated_at?: string;
      request_id?: string;
    }) => void;
    const mockResponse = {
      answer: 'Réponse',
    };

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePromise = resolve as typeof resolvePromise;
        })
    );

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    // Premier appel (en cours)
    void result.current.ask('Q1');

    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (doit être ignoré)
    await result.current.ask('Q2');

    // Vérifier qu'un seul appel a été fait
    expect(mockAdvise).toHaveBeenCalledTimes(1);

    // Résoudre le premier appel
    resolvePromise!(mockResponse);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait exposer retryAfter depuis usePaywall', () => {
    (vi.mocked(usePaywall) as ReturnType<typeof vi.fn>).mockReturnValue({
      isAllowed: true,
      reason: undefined,
      retryAfter: 1800,
      isLoading: false,
      error: null,
    });

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    expect(result.current.retryAfter).toBe(1800);
  });

  it('devrait exposer reason depuis usePaywall', () => {
    (vi.mocked(usePaywall) as ReturnType<typeof vi.fn>).mockReturnValue({
      isAllowed: false,
      reason: 'rate',
      retryAfter: undefined,
      isLoading: false,
      error: null,
    });

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    expect(result.current.isAllowed).toBe(false);
    expect(result.current.reason).toBe('rate');
  });

  it('devrait ajouter uniquement le message user si erreur 402', async () => {
    const mockError = new ApiError('Payment required', 402, 'payment_required');

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    // Message user ajouté (optimistic)
    expect(mockAddMessage).toHaveBeenCalledWith(
      'chart-123',
      'user',
      'Ma question'
    );
    // Pas de message assistant
    expect(mockAddMessage).not.toHaveBeenCalledWith(
      'chart-123',
      'assistant',
      expect.any(String)
    );
  });

  it('devrait ajouter uniquement le message user si erreur 429', async () => {
    const mockError = new ApiError('Too many requests', 429, 'rate_limit');

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    // Message user ajouté (optimistic)
    expect(mockAddMessage).toHaveBeenCalledWith(
      'chart-123',
      'user',
      'Ma question'
    );
    // Pas de message assistant
    expect(mockAddMessage).not.toHaveBeenCalledWith(
      'chart-123',
      'assistant',
      expect.any(String)
    );
  });

  it('devrait afficher toast sur erreur 500', async () => {
    const mockError = new ApiError('Internal server error', 500);

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Internal server error');
    });
  });

  it('devrait afficher toast sur NetworkError', async () => {
    const mockError = new NetworkError('timeout', 'Request timeout');

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erreur réseau, réessayez');
    });
  });

  it('devrait ne pas afficher toast sur erreur 401', async () => {
    const mockError = new ApiError('Unauthorized', 401);

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    // Pas de toast pour 401 (géré par wrapper)
    expect(toast.error).not.toHaveBeenCalled();
  });

  it('devrait récupérer les messages depuis getMessages', () => {
    const mockMessages = [
      {
        id: 'msg-1',
        role: 'user' as const,
        content: 'Q1',
        ts: 1000,
      },
      {
        id: 'msg-2',
        role: 'assistant' as const,
        content: 'R1',
        ts: 2000,
      },
    ];

    mockGetMessages.mockReturnValue(mockMessages);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    expect(result.current.messages).toEqual(mockMessages);
  });

  it('devrait exposer error après échec', async () => {
    const mockError = new ApiError('Bad Request', 400);

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockAdvise = vi.mocked(chatService.advise);
    mockAdvise.mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat('chart-123'), { wrapper });

    await expect(result.current.ask('Ma question')).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.error).toBe(mockError);
    });
  });
});
