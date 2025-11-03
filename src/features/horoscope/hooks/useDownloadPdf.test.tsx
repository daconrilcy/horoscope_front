import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDownloadPdf } from './useDownloadPdf';
import { horoscopeService } from '@/shared/api/horoscope.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { downloadBlob } from '../utils/downloadBlob';
import React from 'react';

// Mock horoscopeService
vi.mock('@/shared/api/horoscope.service', () => ({
  horoscopeService: {
    getNatalPdfStream: vi.fn(),
  },
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock downloadBlob
vi.mock('../utils/downloadBlob', () => ({
  downloadBlob: vi.fn(),
}));

describe('useDownloadPdf', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
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

  it('devrait télécharger le PDF avec succès', async () => {
    const chartId = 'chart-123';
    const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });
    const mockResponse = {
      blob: mockBlob,
      filename: `natal-${chartId}.pdf`,
    };

    (
      horoscopeService.getNatalPdfStream as ReturnType<typeof vi.fn>
    ).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useDownloadPdf(), { wrapper });

    expect(result.current.isPending).toBe(false);
    expect(result.current.error).toBeNull();

    await result.current.downloadPdf(chartId);

    await waitFor(() => {
      expect(result.current.isPending).toBe(false);
    });

    // eslint-disable-next-line @typescript-eslint/unbound-method
    expect(horoscopeService.getNatalPdfStream).toHaveBeenCalledWith(chartId);
    expect(downloadBlob).toHaveBeenCalledWith(mockBlob, `natal-${chartId}.pdf`);
    expect(toast.success).toHaveBeenCalledWith('PDF téléchargé avec succès');
  });

  it('devrait empêcher double-submit (isPending)', async () => {
    const chartId = 'chart-123';
    const mockBlob = new Blob(['PDF content'], { type: 'application/pdf' });
    const mockResponse = {
      blob: mockBlob,
      filename: `natal-${chartId}.pdf`,
    };

    (
      horoscopeService.getNatalPdfStream as ReturnType<typeof vi.fn>
    ).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => resolve(mockResponse), 100);
        })
    );

    const { result } = renderHook(() => useDownloadPdf(), { wrapper });

    // Premier appel
    const promise1 = result.current.downloadPdf(chartId);

    // Attendre que isPending soit true
    await waitFor(() => {
      expect(result.current.isPending).toBe(true);
    });

    // Deuxième appel (devrait être bloqué)
    const promise2 = result.current.downloadPdf(chartId);

    await expect(promise2).resolves.toBeUndefined();

    await promise1;
  });

  it('devrait gérer les erreurs 404', async () => {
    const chartId = 'not-found';
    const error = new ApiError('Chart not found', 404);

    (
      horoscopeService.getNatalPdfStream as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useDownloadPdf(), { wrapper });

    await result.current.downloadPdf(chartId).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Thème natal introuvable');
    });

    expect(result.current.error).toBeInstanceOf(ApiError);
    expect((result.current.error as ApiError).status).toBe(404);
  });

  it('devrait gérer les erreurs 500', async () => {
    const chartId = 'chart-123';
    const error = new ApiError('Server error', 500);

    (
      horoscopeService.getNatalPdfStream as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useDownloadPdf(), { wrapper });

    await result.current.downloadPdf(chartId).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        'Erreur lors du téléchargement du PDF'
      );
    });

    expect(result.current.error).toBeInstanceOf(ApiError);
  });

  it('devrait gérer NetworkError', async () => {
    const chartId = 'chart-123';
    const error = new NetworkError('timeout', 'Request timeout');

    (
      horoscopeService.getNatalPdfStream as ReturnType<typeof vi.fn>
    ).mockRejectedValue(error);

    const { result } = renderHook(() => useDownloadPdf(), { wrapper });

    await result.current.downloadPdf(chartId).catch(() => {
      // Attendu que la promise soit rejetée
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Erreur réseau, réessayez');
    });

    expect(result.current.error).toBeInstanceOf(NetworkError);
  });
});
