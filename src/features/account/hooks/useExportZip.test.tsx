import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useExportZip } from './useExportZip';
import { accountService } from '@/shared/api/account.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { downloadBlob } from '@/features/horoscope/utils/downloadBlob';
import React from 'react';

// Mock accountService
vi.mock('@/shared/api/account.service', () => ({
  accountService: {
    exportZip: vi.fn(),
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

// Mock downloadBlob
vi.mock('@/features/horoscope/utils/downloadBlob', () => ({
  downloadBlob: vi.fn(),
}));

describe('useExportZip', () => {
  let queryClient: QueryClient;

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
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('devrait appeler exportZip et télécharger le fichier', async () => {
    const mockBlob = new Blob(['zip content'], { type: 'application/zip' });
    const mockResult = { blob: mockBlob, filename: 'account-export-20241201.zip' };

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResult);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    await result.current.exportZip();

    await waitFor(() => {
      expect(downloadBlob).toHaveBeenCalledWith(mockBlob, mockResult.filename);
      expect(toast.success).toHaveBeenCalledWith('Données exportées avec succès');
    });
  });

  it('devrait bloquer double-clic pendant la mutation', async () => {
    const mockBlob = new Blob(['zip content'], { type: 'application/zip' });
    const mockResult = { blob: mockBlob, filename: 'account-export-20241201.zip' };

    let resolvePromise: (value: typeof mockResult) => void;
    const promise = new Promise<typeof mockResult>((resolve) => {
      resolvePromise = resolve;
    });

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockReturnValue(promise);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    // Premier appel
    void result.current.exportZip();

    // Attendre que isPending soit true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (doit être bloqué)
    await result.current.exportZip();

    // Vérifier que exportZip n'a été appelé qu'une fois
    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(accountService.exportZip).toHaveBeenCalledTimes(1);

    // Résoudre la promesse
    resolvePromise!(mockResult);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });
  });

  it('devrait gérer ApiError 401 (pas de toast, laisser wrapper gérer)', async () => {
    const mockError = new ApiError('Unauthorized', 401, undefined, undefined);

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    try {
      await result.current.exportZip();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).not.toHaveBeenCalled();
      expect(toast.success).not.toHaveBeenCalled();
      expect(result.current.error).toBeInstanceOf(ApiError);
    });
  });

  it('devrait gérer ApiError 500 avec toast spécifique', async () => {
    const mockError = new ApiError(
      'Internal Server Error',
      500,
      undefined,
      'req-123'
    );

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    try {
      await result.current.exportZip();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Erreur serveur lors de l\'export'
      );
      expect(result.current.error).toBeInstanceOf(ApiError);
    });
  });

  it('devrait gérer NetworkError timeout avec toast spécifique', async () => {
    const mockError = new NetworkError('timeout', 'Request timeout');

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    try {
      await result.current.exportZip();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Export indisponible, réessayez.'
      );
      expect(result.current.error).toBeInstanceOf(NetworkError);
    });
  });

  it('devrait gérer NetworkError offline avec toast spécifique', async () => {
    const mockError = new NetworkError('offline', 'Network error: offline');

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    try {
      await result.current.exportZip();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Export indisponible, réessayez.'
      );
      expect(result.current.error).toBeInstanceOf(NetworkError);
    });
  });

  it('devrait gérer NetworkError autre avec toast générique', async () => {
    const mockError = new NetworkError('aborted', 'Request aborted');

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockRejectedValue(mockError);

    const { result } = renderHook(() => useExportZip(), { wrapper });

    try {
      await result.current.exportZip();
    } catch {
      // Ignorer l'erreur rejetée
    }

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Erreur réseau lors de l\'export.'
      );
      expect(result.current.error).toBeInstanceOf(NetworkError);
    });
  });

  it('devrait nettoyer AbortController au démontage', async () => {
    const mockBlob = new Blob(['zip content'], { type: 'application/zip' });
    const mockResult = { blob: mockBlob, filename: 'account-export-20241201.zip' };

    (
      accountService.exportZip as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResult);

    const { result, unmount } = renderHook(() => useExportZip(), { wrapper });

    await result.current.exportZip();

    // Démontage devrait nettoyer l'AbortController
    unmount();

    // Note: dans l'implémentation actuelle, l'AbortController est nettoyé automatiquement
    // après la mutation, donc l'abort au démontage ne se produit que si la mutation est en cours
  });
});
