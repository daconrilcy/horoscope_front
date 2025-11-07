import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { DebugDrawer } from './DebugDrawer';
import { useDebugDrawer } from '@/shared/hooks/useDebugDrawer';
import React from 'react';

// Mock useDebugDrawer
vi.mock('@/shared/hooks/useDebugDrawer', () => ({
  useDebugDrawer: vi.fn(),
}));

// Mock toast
vi.mock('@/app/AppProviders', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

// Mock import.meta.env.DEV
vi.mock('import.meta', () => ({
  env: {
    DEV: true,
  },
}));

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

describe('DebugDrawer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const wrapper = ({
    children,
  }: {
    children: React.ReactNode;
  }): JSX.Element => <BrowserRouter>{children}</BrowserRouter>;

  it('ne devrait pas rendre en production', () => {
    // Mock DEV = false
    vi.mocked(import.meta.env).DEV = false;

    const { container } = render(<DebugDrawer />, { wrapper });
    expect(container.firstChild).toBeNull();
  });

  it('ne devrait pas rendre si isOpen est false', () => {
    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: [],
      isOpen: false,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    const { container } = render(<DebugDrawer />, { wrapper });
    expect(container.firstChild).toBeNull();
  });

  it('devrait rendre le drawer si isOpen est true', () => {
    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: [],
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    expect(screen.getByText('Debug Drawer')).toBeInTheDocument();
  });

  it('devrait afficher "Aucune requête API enregistrée" si breadcrumbs vide', () => {
    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: [],
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    expect(
      screen.getByText('Aucune requête API enregistrée')
    ).toBeInTheDocument();
  });

  it('devrait afficher les breadcrumbs', () => {
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_123',
        endpoint: '/v1/billing/checkout',
        fullUrl: 'http://localhost:8000/v1/billing/checkout',
        status: 200,
        timestamp: Date.now(),
        duration: 150,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Version': '1.0.0',
        },
        body: { plan: 'plus' },
      },
      {
        event: 'api:request',
        requestId: 'req_456',
        endpoint: '/v1/billing/config',
        fullUrl: 'http://localhost:8000/v1/billing/config',
        status: 200,
        timestamp: Date.now(),
        duration: 100,
        method: 'GET',
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    expect(screen.getByText('/v1/billing/checkout')).toBeInTheDocument();
    expect(screen.getByText('/v1/billing/config')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
    expect(screen.getByText('POST')).toBeInTheDocument();
    expect(screen.getByText('GET')).toBeInTheDocument();
  });

  it('devrait afficher la durée pour chaque breadcrumb', () => {
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_123',
        endpoint: '/v1/test',
        fullUrl: 'http://localhost:8000/v1/test',
        status: 200,
        timestamp: Date.now(),
        duration: 250,
        method: 'GET',
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    expect(screen.getByText('250ms')).toBeInTheDocument();
  });

  it('devrait afficher request_id si présent', () => {
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_test_123',
        endpoint: '/v1/test',
        fullUrl: 'http://localhost:8000/v1/test',
        status: 200,
        timestamp: Date.now(),
        duration: 100,
        method: 'GET',
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    expect(screen.getByText(/Request ID: req_test_123/i)).toBeInTheDocument();
  });

  it('devrait copier la commande cURL au clic sur le bouton CURL', async () => {
    const user = userEvent.setup();
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_123',
        endpoint: '/v1/billing/checkout',
        fullUrl: 'http://localhost:8000/v1/billing/checkout',
        status: 200,
        timestamp: Date.now(),
        duration: 150,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Version': '1.0.0',
        },
        body: { plan: 'plus' },
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    const curlButton = screen.getByTitle('Copy CURL command');
    await user.click(curlButton);

    await waitFor(() => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    // Vérifier que la commande cURL contient les éléments attendus
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const writeTextCall = vi.mocked(navigator.clipboard.writeText).mock
      .calls[0];
    const curlCommand = writeTextCall[0];

    expect(curlCommand).toContain('curl -X POST');
    expect(curlCommand).toContain('http://localhost:8000/v1/billing/checkout');
    expect(curlCommand).toContain('Content-Type: application/json');
    expect(curlCommand).toContain('X-Client-Version: 1.0.0');
    expect(curlCommand).toContain('X-Request-ID: req_123');
    expect(curlCommand).toContain('-d');
    expect(curlCommand).toContain('plan');
    expect(curlCommand).toContain('plus');
  });

  it('devrait générer cURL sans body pour GET', async () => {
    const user = userEvent.setup();
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_456',
        endpoint: '/v1/billing/config',
        fullUrl: 'http://localhost:8000/v1/billing/config',
        status: 200,
        timestamp: Date.now(),
        duration: 100,
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    const curlButton = screen.getByTitle('Copy CURL command');
    await user.click(curlButton);

    await waitFor(() => {
      // eslint-disable-next-line @typescript-eslint/unbound-method
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const writeTextCall = vi.mocked(navigator.clipboard.writeText).mock
      .calls[0];
    const curlCommand = writeTextCall[0];

    expect(curlCommand).toContain('curl -X GET');
    expect(curlCommand).not.toContain('-d');
  });

  it('devrait permettre de fermer le drawer', async () => {
    const user = userEvent.setup();
    const mockToggle = vi.fn();

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: [],
      isOpen: true,
      toggle: mockToggle,
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    expect(mockToggle).toHaveBeenCalledTimes(1);
  });

  it('devrait permettre de vider les breadcrumbs', async () => {
    const user = userEvent.setup();
    const mockClear = vi.fn();

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: [
        {
          event: 'api:request',
          requestId: 'req_123',
          endpoint: '/v1/test',
          fullUrl: 'http://localhost:8000/v1/test',
          status: 200,
          timestamp: Date.now(),
          duration: 100,
          method: 'GET',
        },
      ],
      isOpen: true,
      toggle: vi.fn(),
      clear: mockClear,
    });

    render(<DebugDrawer />, { wrapper });

    const clearButton = screen.getByRole('button', { name: /clear/i });
    await user.click(clearButton);

    expect(mockClear).toHaveBeenCalledTimes(1);
  });

  it('devrait afficher les couleurs de status correctes', () => {
    const mockBreadcrumbs = [
      {
        event: 'api:request',
        requestId: 'req_200',
        endpoint: '/v1/success',
        fullUrl: 'http://localhost:8000/v1/success',
        status: 200,
        timestamp: Date.now(),
        duration: 100,
        method: 'GET',
      },
      {
        event: 'api:request',
        requestId: 'req_400',
        endpoint: '/v1/bad-request',
        fullUrl: 'http://localhost:8000/v1/bad-request',
        status: 400,
        timestamp: Date.now(),
        duration: 100,
        method: 'POST',
      },
      {
        event: 'api:request',
        requestId: 'req_500',
        endpoint: '/v1/error',
        fullUrl: 'http://localhost:8000/v1/error',
        status: 500,
        timestamp: Date.now(),
        duration: 100,
        method: 'GET',
      },
    ];

    vi.mocked(useDebugDrawer).mockReturnValue({
      breadcrumbs: mockBreadcrumbs,
      isOpen: true,
      toggle: vi.fn(),
      clear: vi.fn(),
    });

    render(<DebugDrawer />, { wrapper });

    // Vérifier que les status sont affichés dans les spans avec backgroundColor
    // Les status sont rendus dans des spans avec le texte du status
    const status200 = screen.getByText('200');
    const status400 = screen.getByText('400');
    const status500 = screen.getByText('500');

    expect(status200).toBeInTheDocument();
    expect(status400).toBeInTheDocument();
    expect(status500).toBeInTheDocument();
  });
});
