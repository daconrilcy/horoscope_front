import { useDebugDrawer } from '@/shared/hooks/useDebugDrawer';

const MAX_BREADCRUMBS = 200;

/**
 * Composant DebugDrawer (dev-only)
 * Affiche les derniers breadcrumbs billing/terminal pour corrélation
 * Accessible via Ctrl+Shift+D
 */
export function DebugDrawer(): JSX.Element | null {
  const { breadcrumbs, isOpen, toggle, clear } = useDebugDrawer();

  // Masquer complètement en production
  if (!import.meta.env.DEV) {
    return null;
  }

  const overlayStyle: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    zIndex: 10000,
    display: isOpen ? 'flex' : 'none',
    alignItems: 'center',
    justifyContent: 'center',
  };

  const drawerStyle: React.CSSProperties = {
    backgroundColor: '#1e1e1e',
    border: '1px solid #444',
    borderRadius: '0.5rem',
    padding: '1rem',
    width: '80vw',
    maxWidth: '900px',
    maxHeight: '80vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1rem',
    paddingBottom: '0.75rem',
    borderBottom: '1px solid #444',
  };

  const titleStyle: React.CSSProperties = {
    color: '#fff',
    fontSize: '1.25rem',
    fontWeight: 600,
    margin: 0,
  };

  const buttonStyle: React.CSSProperties = {
    padding: '0.5rem 1rem',
    borderRadius: '0.25rem',
    border: 'none',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: 500,
  };

  const primaryButtonStyle: React.CSSProperties = {
    ...buttonStyle,
    backgroundColor: '#3b82f6',
    color: '#fff',
  };

  const secondaryButtonStyle: React.CSSProperties = {
    ...buttonStyle,
    backgroundColor: '#6b7280',
    color: '#fff',
    marginLeft: '0.5rem',
  };

  const listStyle: React.CSSProperties = {
    flex: 1,
    overflowY: 'auto',
    listStyle: 'none',
    padding: 0,
    margin: 0,
  };

  const itemStyle: React.CSSProperties = {
    padding: '0.75rem',
    marginBottom: '0.5rem',
    backgroundColor: '#2a2a2a',
    borderRadius: '0.25rem',
    border: '1px solid #444',
    color: '#ccc',
    fontSize: '0.875rem',
    fontFamily: 'monospace',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  };

  const itemLeftStyle: React.CSSProperties = {
    flex: 1,
    minWidth: 0,
  };

  const itemRightStyle: React.CSSProperties = {
    marginLeft: '1rem',
    textAlign: 'right',
    whiteSpace: 'nowrap',
  };

  const statusColor = (status: number): string => {
    if (status >= 500) return '#ef4444'; // red
    if (status >= 400) return '#f59e0b'; // amber
    if (status >= 200) return '#10b981'; // green
    return '#6b7280'; // gray
  };

  const formatTime = (timestamp: number): string => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDuration = (duration?: number): string => {
    if (!duration) return '-';
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(2)}s`;
  };

  const copyRequestId = (requestId?: string): void => {
    if (requestId) {
      void navigator.clipboard.writeText(requestId);
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div style={overlayStyle} onClick={toggle}>
      <div style={drawerStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h2 style={titleStyle}>🐛 Debug Drawer</h2>
          <div>
            <button onClick={clear} style={secondaryButtonStyle}>
              Clear
            </button>
            <button onClick={toggle} style={primaryButtonStyle}>
              Close
            </button>
          </div>
        </div>

        {breadcrumbs.length === 0 ? (
          <div style={{ color: '#888', textAlign: 'center', padding: '2rem' }}>
            Aucun breadcrumb enregistré
            <br />
            <small>Les requêtes billing/terminal apparaîtront ici</small>
          </div>
        ) : (
          <ul style={listStyle}>
            {breadcrumbs.map((breadcrumb, idx) => (
              <li key={idx} style={itemStyle}>
                <div style={itemLeftStyle}>
                  <div style={{ marginBottom: '0.25rem' }}>
                    <span style={{ color: '#888' }}>[{breadcrumb.method}]</span>{' '}
                    <strong style={{ color: '#fff' }}>
                      {breadcrumb.endpoint}
                    </strong>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {breadcrumb.event}
                    {breadcrumb.requestId && (
                      <>
                        {' • '}
                        <button
                          onClick={() => copyRequestId(breadcrumb.requestId)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#60a5fa',
                            cursor: 'pointer',
                            textDecoration: 'underline',
                          }}
                        >
                          ID: {breadcrumb.requestId.slice(0, 8)}...
                        </button>
                      </>
                    )}
                  </div>
                </div>
                <div style={itemRightStyle}>
                  <div style={{ color: statusColor(breadcrumb.status) }}>
                    {breadcrumb.status}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {formatTime(breadcrumb.timestamp)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {formatDuration(breadcrumb.duration)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}

        <div
          style={{
            marginTop: '1rem',
            paddingTop: '0.75rem',
            borderTop: '1px solid #444',
            fontSize: '0.75rem',
            color: '#666',
            textAlign: 'center',
          }}
        >
          Total: {breadcrumbs.length} / {MAX_BREADCRUMBS} • Press{' '}
          <kbd
            style={{
              padding: '0.125rem 0.375rem',
              backgroundColor: '#2a2a2a',
              borderRadius: '0.25rem',
              border: '1px solid #444',
            }}
          >
            Ctrl+Shift+D
          </kbd>{' '}
          to toggle
        </div>
      </div>
    </div>
  );
}

