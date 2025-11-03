import { useEffect, useRef } from 'react';
import { useTitle } from '@/shared/hooks/useTitle';
import { usePrivacy } from '@/features/legal/hooks/usePrivacy';
import { sanitizeLegalHtml } from '@/shared/utils/sanitizeLegalHtml';
import { env } from '@/shared/config/env';
import { ApiError, NetworkError } from '@/shared/api/errors';

/**
 * Page Politique de confidentialité
 */
export function PrivacyPolicyPage(): JSX.Element {
  useTitle('Horoscope - Politique de confidentialité');
  const { html, isLoading, isError, error, refetch } = usePrivacy();
  const contentRef = useRef<HTMLDivElement>(null);

  // Sécuriser les liens externes après injection
  useEffect(() => {
    if (!contentRef.current || !html) {
      return;
    }

    const links =
      contentRef.current.querySelectorAll<HTMLAnchorElement>('a[href]');
    links.forEach((link) => {
      const href = link.getAttribute('href');
      if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
        // Lien externe : ajouter rel="noopener" target="_blank"
        if (!link.hasAttribute('target')) {
          link.setAttribute('target', '_blank');
        }
        if (!link.hasAttribute('rel')) {
          link.setAttribute('rel', 'noopener noreferrer');
        } else {
          const rel = link.getAttribute('rel') || '';
          if (!rel.includes('noopener')) {
            link.setAttribute('rel', `${rel} noopener noreferrer`.trim());
          }
        }
      }
    });
  }, [html]);

  // Sanitization du HTML
  const sanitizedHtml = html ? sanitizeLegalHtml(html) : '';

  // Détection de liens relatifs (pour injection de <base> si nécessaire)
  const hasRelativeLinks =
    sanitizedHtml.includes('href="') || sanitizedHtml.includes("href='");

  return (
    <article aria-label="Politique de confidentialité">
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        {/* Header avec titre et bouton Imprimer */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '2rem',
          }}
        >
          <h1>Politique de confidentialité</h1>
          <button
            type="button"
            onClick={() => {
              window.print();
            }}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
              background: 'white',
              cursor: 'pointer',
            }}
          >
            📄 Imprimer
          </button>
        </div>

        {/* Loader */}
        {isLoading && (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              color: '#666',
            }}
          >
            <p>Chargement de la politique de confidentialité...</p>
          </div>
        )}

        {/* Erreur */}
        {isError && error && (
          <div
            style={{
              padding: '2rem',
              border: '1px solid #f00',
              borderRadius: '4px',
              background: '#ffe6e6',
              color: '#c00',
            }}
          >
            <h2>Erreur de chargement</h2>
            <p>
              {error instanceof ApiError
                ? `Erreur ${error.status}: ${error.message}`
                : error instanceof NetworkError
                  ? 'Erreur réseau. Vérifiez votre connexion internet.'
                  : error.message ||
                    'Une erreur est survenue lors du chargement.'}
            </p>
            {error instanceof ApiError && error.requestId && (
              <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                ID de requête : {error.requestId}
              </p>
            )}
            <div style={{ marginTop: '1rem' }}>
              <button
                type="button"
                onClick={() => {
                  refetch();
                }}
                style={{
                  padding: '0.5rem 1rem',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#007bff',
                  color: 'white',
                  cursor: 'pointer',
                  marginRight: '1rem',
                }}
              >
                Réessayer
              </button>
              <a
                href="mailto:support@horoscope.com"
                style={{ color: '#007bff', textDecoration: 'underline' }}
              >
                Contacter le support
              </a>
            </div>
          </div>
        )}

        {/* Contenu HTML */}
        {!isLoading && !isError && sanitizedHtml && (
          <div>
            {/* Injecter <base> si nécessaire pour liens relatifs */}
            {hasRelativeLinks && (
              <base href={`${env.VITE_API_BASE_URL}/v1/legal/`} />
            )}
            <div
              ref={contentRef}
              dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
              style={{
                lineHeight: '1.6',
                color: '#333',
              }}
            />
          </div>
        )}

        {/* Version (si disponible) */}
        {!isLoading && !isError && html && (
          <div
            style={{
              marginTop: '3rem',
              paddingTop: '2rem',
              borderTop: '1px solid #ddd',
              fontSize: '0.9rem',
              color: '#666',
              textAlign: 'center',
            }}
          >
            <p>
              Dernière mise à jour :{' '}
              {new Date().toLocaleDateString('fr-FR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        )}
      </div>
    </article>
  );
}
