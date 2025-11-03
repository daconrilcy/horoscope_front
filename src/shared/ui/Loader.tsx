import type { ReactNode } from 'react';

/**
 * Props pour le composant Loader
 */
export interface LoaderProps {
  /** Taille du loader */
  size?: 'sm' | 'md' | 'lg';
  /** Variante du loader */
  variant?: 'spinner' | 'skeleton';
  /** Afficher en inline */
  inline?: boolean;
}

/**
 * Composant Loader réutilisable avec deux variantes : spinner et skeleton
 */
export function Loader({
  size = 'md',
  variant = 'spinner',
  inline = false,
}: LoaderProps): JSX.Element {
  if (variant === 'spinner') {
    return <Spinner size={size} inline={inline} />;
  }

  return <Skeleton size={size} inline={inline} />;
}

/**
 * Composant Spinner (animation circulaire)
 */
function Spinner({
  size,
  inline,
}: {
  size: 'sm' | 'md' | 'lg';
  inline: boolean;
}): JSX.Element {
  const sizeMap: Record<'sm' | 'md' | 'lg', number> = {
    sm: 16,
    md: 24,
    lg: 32,
  };

  const spinnerSize = sizeMap[size];

  return (
    <div
      role="status"
      aria-busy="true"
      aria-label="Chargement"
      style={{
        display: inline ? 'inline-block' : 'block',
        width: `${spinnerSize}px`,
        height: `${spinnerSize}px`,
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          border: `2px solid #e5e7eb`,
          borderTopColor: '#3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

/**
 * Composant Skeleton (placeholder grisé)
 */
function Skeleton({
  size,
  inline,
}: {
  size: 'sm' | 'md' | 'lg';
  inline: boolean;
}): JSX.Element {
  const heightMap: Record<'sm' | 'md' | 'lg', number> = {
    sm: 16,
    md: 24,
    lg: 32,
  };

  const height = heightMap[size];

  return (
    <div
      role="status"
      aria-busy="true"
      aria-label="Chargement"
      style={{
        display: inline ? 'inline-block' : 'block',
        width: inline ? `${height * 2}px` : '100%',
        height: `${height}px`,
        backgroundColor: '#e5e7eb',
        borderRadius: '0.25rem',
        animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }}
    >
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  );
}
