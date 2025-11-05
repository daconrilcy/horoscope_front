import { useBillingConfig } from './hooks/useBillingConfig';
import { billingConfigService } from '@/shared/api/billingConfig.service';
import { useClearPriceLookupCache } from './hooks/useClearPriceLookupCache';

/**
 * Composant Panel de debug billing (dev-only)
 * Affiche la configuration, les flags et avertit sur les mismatches d'URL
 */
export function BillingDebugPanel(): JSX.Element | null {
  const { data: config, isLoading, error } = useBillingConfig();
  const { mutate: clearCache, isPending: isClearingCache } =
    useClearPriceLookupCache();

  // Masquer complètement en production
  if (!import.meta.env.DEV) {
    return null;
  }

  // Panel invisible si pas de config
  if (isLoading || error || !config) {
    return null;
  }

  // Vérifier le mismatch d'URL
  const originCheck = billingConfigService.validateOrigin(config);

  const panelStyle: React.CSSProperties = {
    position: 'fixed',
    bottom: '1rem',
    right: '1rem',
    width: '400px',
    maxWidth: 'calc(100vw - 2rem)',
    backgroundColor: '#1e1e1e',
    border: '1px solid #444',
    borderRadius: '0.5rem',
    padding: '1rem',
    fontSize: '0.875rem',
    fontFamily: 'monospace',
    zIndex: 9999,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
  };

  const titleStyle: React.CSSProperties = {
    margin: '0 0 0.75rem 0',
    paddingBottom: '0.5rem',
    borderBottom: '1px solid #444',
    fontWeight: 600,
    color: '#fff',
  };

  const rowStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '0.5rem',
    color: '#ccc',
  };

  const labelStyle: React.CSSProperties = {
    color: '#888',
    marginRight: '0.5rem',
  };

  const badgeStyle = (enabled: boolean): React.CSSProperties => ({
    padding: '0.25rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem',
    fontWeight: 600,
    backgroundColor: enabled ? '#10b981' : '#6b7280',
    color: '#fff',
  });

  const warningStyle: React.CSSProperties = {
    marginTop: '0.75rem',
    padding: '0.5rem',
    backgroundColor: '#fef3c7',
    border: '1px solid #fbbf24',
    borderRadius: '0.25rem',
    color: '#92400e',
    fontSize: '0.8125rem',
  };

  const buttonStyle: React.CSSProperties = {
    marginTop: '0.75rem',
    padding: '0.5rem 1rem',
    backgroundColor: '#3b82f6',
    border: 'none',
    borderRadius: '0.25rem',
    color: '#fff',
    fontSize: '0.8125rem',
    fontWeight: 600,
    cursor: isClearingCache ? 'not-allowed' : 'pointer',
    opacity: isClearingCache ? 0.6 : 1,
    width: '100%',
  };

  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🔧 Billing Debug Panel (DEV)</div>

      <div style={rowStyle}>
        <span style={labelStyle}>Environment:</span>
        <span style={{ color: '#10b981', fontWeight: 600 }}>development</span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Public Base URL:</span>
        <span style={{ color: '#60a5fa' }}>{config.publicBaseUrl}</span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Success Path:</span>
        <span style={{ color: '#60a5fa' }}>{config.checkoutSuccessPath}</span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Cancel Path:</span>
        <span style={{ color: '#60a5fa' }}>{config.checkoutCancelPath}</span>
      </div>

      {config.portalReturnUrl != null && config.portalReturnUrl !== '' && (
        <div style={rowStyle}>
          <span style={labelStyle}>Portal Return URL:</span>
          <span style={{ color: '#60a5fa' }}>{config.portalReturnUrl}</span>
        </div>
      )}

      <div style={{ ...rowStyle, marginTop: '0.75rem' }}>
        <span style={labelStyle}>Trials:</span>
        <span style={badgeStyle(config.checkoutTrialsEnabled)}>
          {config.checkoutTrialsEnabled ? 'ENABLED' : 'DISABLED'}
        </span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Coupons:</span>
        <span style={badgeStyle(config.checkoutCouponsEnabled)}>
          {config.checkoutCouponsEnabled ? 'ENABLED' : 'DISABLED'}
        </span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Tax:</span>
        <span style={badgeStyle(config.stripeTaxEnabled)}>
          {config.stripeTaxEnabled ? 'ENABLED' : 'DISABLED'}
        </span>
      </div>

      {config.priceLookupHash != null && config.priceLookupHash !== '' && (
        <div style={rowStyle}>
          <span style={labelStyle}>Price Lookup:</span>
          <span style={{ color: '#60a5fa', fontSize: '0.75rem' }}>
            {config.priceLookupHash.slice(0, 8)}...
          </span>
        </div>
      )}

      <button
        type="button"
        onClick={() => {
          clearCache();
        }}
        disabled={isClearingCache}
        style={buttonStyle}
        title="Clear price_lookup cache on backend"
      >
        {isClearingCache ? 'Clearing...' : '🗑️ Clear Price Lookup Cache'}
      </button>

      {!originCheck.matches && (
        <div style={warningStyle}>
          ⚠️ Origin mismatch: current ({originCheck.current}) ≠ expected (
          {originCheck.expected})
        </div>
      )}
    </div>
  );
}
