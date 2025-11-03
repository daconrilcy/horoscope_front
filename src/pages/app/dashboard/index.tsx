import { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import { usePlan } from '@/features/billing/hooks/usePlan';
import { usePaywall } from '@/features/billing/hooks/usePaywall';
import { QuotaBadge } from '@/widgets/QuotaBadge/QuotaBadge';
import { PlanBanner } from '@/widgets/PlanBanner/PlanBanner';
import { InlineError } from '@/shared/ui/InlineError';
import { ROUTES } from '@/shared/config/routes';
import { FEATURES } from '@/shared/config/features';

/**
 * Page Dashboard (privée)
 * Résumé de l'état + raccourcis actionnables
 */
export function DashboardPage(): JSX.Element {
  useTitle('Tableau de bord');
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const userRef = useAuthStore((state) => state.userRef);
  const logout = useAuthStore((state) => state.logout);
  const recentCharts = useHoroscopeStore((state) => state.recentCharts);
  const { isLoading: isPlanLoading } = usePlan();
  const chatPaywall = usePaywall(FEATURES.CHAT_MSG_PER_DAY);

  // Refetch plan/quotas au mount (et au retour Stripe)
  useEffect(() => {
    void queryClient.invalidateQueries({ queryKey: ['paywall'] });
  }, [queryClient]);

  // Prefetch idle : préfetcher les pages clés après un délai
  useEffect(() => {
    const prefetchIdle = (): void => {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(
          () => {
            // Préfetcher les pages horoscope et chat
            void import('@/pages/app/horoscope');
            void import('@/pages/app/chat');
          },
          { timeout: 2000 }
        );
      } else {
        // Fallback pour navigateurs sans requestIdleCallback
        setTimeout(() => {
          void import('@/pages/app/horoscope');
          void import('@/pages/app/chat');
        }, 2000);
      }
    };

    prefetchIdle();
  }, []);

  // Prefetch paresseux au survol des cartes
  const prefetchHoroscope = useCallback(() => {
    void import('@/pages/app/horoscope');
  }, []);

  const prefetchChat = useCallback(() => {
    void import('@/pages/app/chat');
  }, []);

  const prefetchAccount = useCallback(() => {
    void import('@/pages/app/account');
  }, []);

  const handleLogout = useCallback((): void => {
    logout(queryClient);
    void navigate(ROUTES.LOGIN, { replace: true });
  }, [logout, queryClient, navigate]);

  const handleHoroscopeClick = useCallback(() => {
    if (recentCharts.length > 0) {
      // Si chart existe, aller à Today
      void navigate(ROUTES.APP.HOROSCOPE);
    } else {
      // Sinon, aller à la création de thème natal
      void navigate(ROUTES.APP.HOROSCOPE);
    }
  }, [navigate, recentCharts]);

  const handleChatClick = useCallback(() => {
    void navigate(ROUTES.APP.CHAT);
  }, [navigate]);

  const handleAccountClick = useCallback(() => {
    void navigate(ROUTES.APP.ACCOUNT);
  }, [navigate]);

  const lastChart = recentCharts.length > 0 ? recentCharts[0] : null;
  const hasCharts = recentCharts.length > 0;

  return (
    <main>
      <h1>Tableau de bord</h1>

      {/* Carte Auth */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f9fafb',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: '1rem',
            fontSize: '1.125rem',
            fontWeight: 600,
          }}
        >
          Mon compte
        </h2>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <p style={{ margin: 0, fontSize: '1rem', color: '#374151' }}>
              Email : <strong>{userRef?.email ?? 'Non disponible'}</strong>
            </p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontWeight: 500,
            }}
            aria-label="Se déconnecter"
          >
            Se déconnecter
          </button>
        </div>
      </div>

      {/* Section "Mon offre" avec Plan et Quotas */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f9fafb',
          borderRadius: '0.5rem',
          border: '1px solid #e5e7eb',
        }}
      >
        <h2
          style={{
            marginTop: 0,
            marginBottom: '1rem',
            fontSize: '1.125rem',
            fontWeight: 600,
          }}
        >
          Mon offre
        </h2>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem',
          }}
        >
          {/* PlanBanner : affiche le plan actuel avec CTAs */}
          {isPlanLoading ? (
            <div
              style={{
                padding: '1rem',
                backgroundColor: '#f3f4f6',
                borderRadius: '0.5rem',
                textAlign: 'center',
              }}
              aria-busy="true"
              aria-live="polite"
            >
              <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                Chargement du plan...
              </p>
            </div>
          ) : (
            <PlanBanner />
          )}

          {/* QuotaBadge : affiche l'état des quotas */}
          <div>
            <h3
              style={{
                marginTop: 0,
                marginBottom: '0.75rem',
                fontSize: '1rem',
                fontWeight: 600,
              }}
            >
              État des quotas
            </h3>
            <QuotaBadge
              showRetryAfter={true}
              features={[
                FEATURES.CHAT_MSG_PER_DAY,
                FEATURES.HORO_TODAY_PREMIUM,
              ]}
            />
          </div>
        </div>
      </div>

      {/* Quick Cards : Raccourcis vers les features clés */}
      <div
        style={{
          marginTop: '2rem',
        }}
      >
        <h2
          style={{
            marginBottom: '1rem',
            fontSize: '1.125rem',
            fontWeight: 600,
          }}
        >
          Accès rapide
        </h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem',
          }}
        >
          {/* Carte Horoscope */}
          <button
            type="button"
            onClick={handleHoroscopeClick}
            style={{
              padding: '1.5rem',
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'box-shadow 0.2s',
            }}
            onMouseEnter={(e) => {
              prefetchHoroscope();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onFocus={(e) => {
              prefetchHoroscope();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            onBlur={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            aria-label={
              hasCharts
                ? `Voir Today pour le thème ${lastChart?.label ?? lastChart?.chartId ?? ''}`
                : 'Créer mon thème natal'
            }
          >
            <h3
              style={{
                marginTop: 0,
                marginBottom: '0.5rem',
                fontSize: '1.125rem',
                fontWeight: 600,
              }}
            >
              Horoscope
            </h3>
            {hasCharts ? (
              <div>
                <p
                  style={{
                    margin: '0 0 0.5rem 0',
                    fontSize: '0.875rem',
                    color: '#6b7280',
                  }}
                >
                  Dernier thème :{' '}
                  {lastChart?.label ?? lastChart?.chartId ?? 'Sans nom'}
                </p>
                <p
                  style={{
                    margin: 0,
                    fontSize: '0.875rem',
                    color: '#374151',
                    fontWeight: 500,
                  }}
                >
                  Voir Today →
                </p>
              </div>
            ) : (
              <p
                style={{
                  margin: 0,
                  fontSize: '0.875rem',
                  color: '#374151',
                  fontWeight: 500,
                }}
              >
                Créer mon thème natal →
              </p>
            )}
          </button>

          {/* Carte Chat */}
          <button
            type="button"
            onClick={handleChatClick}
            style={{
              padding: '1.5rem',
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'box-shadow 0.2s',
              position: 'relative',
            }}
            onMouseEnter={(e) => {
              prefetchChat();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onFocus={(e) => {
              prefetchChat();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            onBlur={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            aria-label="Accéder au chat"
          >
            <h3
              style={{
                marginTop: 0,
                marginBottom: '0.5rem',
                fontSize: '1.125rem',
                fontWeight: 600,
              }}
            >
              Chat
            </h3>
            {!chatPaywall.isLoading && !chatPaywall.isAllowed && (
              <span
                style={{
                  display: 'inline-block',
                  padding: '0.25rem 0.5rem',
                  backgroundColor: '#fef3c7',
                  color: '#92400e',
                  borderRadius: '0.25rem',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  marginBottom: '0.5rem',
                }}
              >
                Plus requis
              </span>
            )}
            <p
              style={{
                margin: 0,
                fontSize: '0.875rem',
                color: '#374151',
                fontWeight: 500,
              }}
            >
              Discuter avec l'IA →
            </p>
          </button>

          {/* Carte Account */}
          <button
            type="button"
            onClick={handleAccountClick}
            style={{
              padding: '1.5rem',
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'box-shadow 0.2s',
            }}
            onMouseEnter={(e) => {
              prefetchAccount();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onFocus={(e) => {
              prefetchAccount();
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            onBlur={(e) => {
              e.currentTarget.style.boxShadow = 'none';
            }}
            aria-label="Gérer mon compte"
          >
            <h3
              style={{
                marginTop: 0,
                marginBottom: '0.5rem',
                fontSize: '1.125rem',
                fontWeight: 600,
              }}
            >
              Compte
            </h3>
            <p
              style={{
                margin: 0,
                fontSize: '0.875rem',
                color: '#374151',
                fontWeight: 500,
              }}
            >
              Export & Paramètres →
            </p>
          </button>
        </div>
      </div>

      {/* Affichage des erreurs paywall si présentes */}
      {chatPaywall.error && (
        <div style={{ marginTop: '2rem' }}>
          <InlineError error={chatPaywall.error} dismissible={false} />
        </div>
      )}
    </main>
  );
}
