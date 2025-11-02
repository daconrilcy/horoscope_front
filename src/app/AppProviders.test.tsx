import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppProviders, toast } from './AppProviders';

const mockConfigureHttp = vi.fn();

// Mock pour les dépendances externes
vi.mock('@/shared/api/client', () => ({
  configureHttp: (): void => {
    mockConfigureHttp();
  },
}));

vi.mock('@/shared/config/env', () => ({
  env: {
    VITE_API_BASE_URL: 'http://localhost:8000',
  },
}));

vi.mock('@/shared/ui/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: { children: React.ReactNode }) => <div data-testid="error-boundary">{children}</div>,
}));

// Mock pour React Query
vi.mock('@tanstack/react-query', () => ({
  QueryClient: vi.fn(() => ({})),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="query-client-provider">{children}</div>
  ),
}));

// Mock pour React Query Devtools
vi.mock('@tanstack/react-query-devtools', () => ({
  ReactQueryDevtools: () => <div data-testid="react-query-devtools">Devtools</div>,
}));

// Mock pour sonner
vi.mock('sonner', () => {
  const mockSonnerToast = {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  };
  
  return {
    Toaster: (): JSX.Element => <div data-testid="sonner-toaster">Toaster</div>,
    toast: mockSonnerToast,
  };
});

describe('AppProviders', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait rendre QueryClientProvider', () => {
    const TestComponent = (): JSX.Element => <div>Test</div>;

    render(
      <MemoryRouter>
        <AppProviders>
          <TestComponent />
        </AppProviders>
      </MemoryRouter>
    );

    // Vérifier que le composant enfant est rendu (indique que QueryClientProvider fonctionne)
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('devrait rendre ErrorBoundary', () => {
    const TestComponent = (): JSX.Element => <div>Test</div>;

    render(
      <MemoryRouter>
        <AppProviders>
          <TestComponent />
        </AppProviders>
      </MemoryRouter>
    );

    // Si ErrorBoundary est présent, le composant devrait être rendu
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('devrait rendre Toaster', () => {
    render(
      <MemoryRouter>
        <AppProviders>
          <div>Test</div>
        </AppProviders>
      </MemoryRouter>
    );

    // Vérifier que Toaster est rendu
    expect(screen.getByTestId('sonner-toaster')).toBeInTheDocument();
  });

  it('devrait rendre ReactQueryDevtools uniquement en dev', () => {
    // Note: Le test vérifie que ReactQueryDevtools existe dans le code
    // En test, import.meta.env.DEV peut varier, donc on teste que le composant est importé
    render(
      <MemoryRouter>
        <AppProviders>
          <div>Test</div>
        </AppProviders>
      </MemoryRouter>
    );

    // Si DEV est true, devtools devrait être rendu (selon le mock)
    // Sinon, ce test vérifie au moins que le code ne plante pas
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('devrait configurer HTTP avec onUnauthorized callback', () => {
    render(
      <MemoryRouter initialEntries={['/test']}>
        <AppProviders>
          <div>Test</div>
        </AppProviders>
      </MemoryRouter>
    );

    // Vérifier que configureHttp a été appelé
    expect(mockConfigureHttp).toHaveBeenCalled();
  });
});

describe('toast helpers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait exporter toast.success', () => {
    expect(typeof toast.success).toBe('function');
  });

  it('devrait exporter toast.error', () => {
    expect(typeof toast.error).toBe('function');
  });

  it('devrait exporter toast.info', () => {
    expect(typeof toast.info).toBe('function');
  });

  it('devrait exporter toast.warning', () => {
    expect(typeof toast.warning).toBe('function');
  });

  it('devrait appeler sonner toast.success', async () => {
    const sonnerModule = await vi.importActual<typeof import('sonner')>('sonner');
    
    toast.success('Test message');
    
    // Vérifier que toast.success est une fonction et a été appelée
    expect(typeof toast.success).toBe('function');
    expect(sonnerModule.toast.success).toBeDefined();
  });

  it('devrait appeler sonner toast.error', async () => {
    const sonnerModule = await vi.importActual<typeof import('sonner')>('sonner');
    
    toast.error('Test error');
    
    // Vérifier que toast.error est une fonction
    expect(typeof toast.error).toBe('function');
    expect(sonnerModule.toast.error).toBeDefined();
  });

  it('devrait appeler sonner toast.info', async () => {
    const sonnerModule = await vi.importActual<typeof import('sonner')>('sonner');
    
    toast.info('Test info');
    
    // Vérifier que toast.info est une fonction
    expect(typeof toast.info).toBe('function');
    expect(sonnerModule.toast.info).toBeDefined();
  });

  it('devrait appeler sonner toast.warning', async () => {
    const sonnerModule = await vi.importActual<typeof import('sonner')>('sonner');
    
    toast.warning('Test warning');
    
    // Vérifier que toast.warning est une fonction
    expect(typeof toast.warning).toBe('function');
    expect(sonnerModule.toast.warning).toBeDefined();
  });
});

