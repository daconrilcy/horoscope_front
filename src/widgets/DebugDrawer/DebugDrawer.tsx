import {
  useDebugDrawer,
  type BillingBreadcrumb,
} from '@/shared/hooks/useDebugDrawer';
import { toast } from '@/app/AppProviders';

/**
 * Composant DebugDrawer (dev-only)
 * Affiche les breadcrumbs des requêtes API avec request_id, latence, et bouton Copy CURL
 * Accessible via Ctrl+Shift+D
 */
export function DebugDrawer(): JSX.Element | null {
  const isDev = import.meta.env.DEV;
  const debugDrawer = useDebugDrawer();

  if (!isDev) {
    return null;
  }

  const { breadcrumbs, isOpen, toggle, clear } = debugDrawer;

  const copyCurl = (breadcrumb: BillingBreadcrumb): void => {
    if (breadcrumb.fullUrl == null || breadcrumb.fullUrl === '') {
      return;
    }
    const method =
      breadcrumb.method != null && breadcrumb.method !== ''
        ? breadcrumb.method
        : 'GET';
    const url = breadcrumb.fullUrl;
    let curlCommand = `curl -X ${method} "${url}"`;

    const headerEntries =
      breadcrumb.headers != null
        ? Object.entries(breadcrumb.headers).filter(
            ([key]) => key.toLowerCase() !== 'authorization'
          )
        : [];

    const requiresBody =
      method === 'POST' ||
      method === 'PUT' ||
      method === 'PATCH' ||
      method === 'DELETE';

    let hasContentType = false;

    headerEntries.forEach(([key, value]) => {
      curlCommand += ` \\\n  -H "${key}: ${value}"`;
      if (key.toLowerCase() === 'content-type') {
        hasContentType = true;
      }
    });

    if (requiresBody && !hasContentType) {
      curlCommand += ` \\\n  -H "Content-Type: application/json"`;
    }

    // Ajouter request_id si présent
    if (breadcrumb.requestId != null && breadcrumb.requestId !== '') {
      curlCommand += ` \\\n  -H "X-Request-ID: ${breadcrumb.requestId}"`;
    }

    // Ajouter body pour mutations (POST/PUT/PATCH/DELETE)
    if (
      breadcrumb.body != null &&
      (method === 'POST' ||
        method === 'PUT' ||
        method === 'PATCH' ||
        method === 'DELETE')
    ) {
      const bodyJson = JSON.stringify(breadcrumb.body, null, 2);
      curlCommand += ` \\\n  -d '${bodyJson}'`;
    }

    void navigator.clipboard.writeText(curlCommand);
    toast.success('CURL copié dans le presse-papiers');
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        width: '500px',
        maxHeight: '100vh',
        backgroundColor: '#1e1e1e',
        color: '#d4d4d4',
        borderLeft: '1px solid #3e3e3e',
        zIndex: 10000,
        overflowY: 'auto',
        fontFamily: 'monospace',
        fontSize: '12px',
      }}
    >
      <div
        style={{
          padding: '1rem',
          borderBottom: '1px solid #3e3e3e',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '14px' }}>Debug Drawer</h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={clear}
            style={{
              padding: '0.25rem 0.5rem',
              backgroundColor: '#3e3e3e',
              color: '#d4d4d4',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Clear
          </button>
          <button
            type="button"
            onClick={toggle}
            style={{
              padding: '0.25rem 0.5rem',
              backgroundColor: '#3e3e3e',
              color: '#d4d4d4',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Close
          </button>
        </div>
      </div>
      <div style={{ padding: '0.5rem' }}>
        {breadcrumbs.length === 0 ? (
          <div style={{ padding: '1rem', textAlign: 'center', color: '#888' }}>
            Aucune requête API enregistrée
          </div>
        ) : (
          breadcrumbs.map((breadcrumb, index) => {
            const statusColor =
              breadcrumb.status >= 500
                ? '#f44336'
                : breadcrumb.status >= 400
                  ? '#ff9800'
                  : breadcrumb.status >= 300
                    ? '#2196f3'
                    : '#4caf50';
            return (
              <div
                key={index}
                style={{
                  padding: '0.75rem',
                  borderBottom: '1px solid #3e3e3e',
                  marginBottom: '0.5rem',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    gap: '0.5rem',
                    alignItems: 'center',
                  }}
                >
                  <span
                    style={{
                      padding: '0.125rem 0.375rem',
                      backgroundColor: statusColor,
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: 'bold',
                    }}
                  >
                    {breadcrumb.status}
                  </span>
                  <span style={{ fontWeight: 'bold' }}>
                    {breadcrumb.method}
                  </span>
                  <span
                    style={{
                      flex: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {breadcrumb.endpoint}
                  </span>
                  {breadcrumb.duration != null && (
                    <span style={{ color: '#888', fontSize: '10px' }}>
                      {breadcrumb.duration}ms
                    </span>
                  )}
                </div>
                {breadcrumb.requestId != null &&
                  breadcrumb.requestId !== '' && (
                    <div
                      style={{
                        marginTop: '0.25rem',
                        fontSize: '10px',
                        color: '#888',
                      }}
                    >
                      Request ID: {breadcrumb.requestId}
                    </div>
                  )}
                {breadcrumb.fullUrl != null && breadcrumb.fullUrl !== '' && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        copyCurl(breadcrumb);
                      }}
                      style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#3e3e3e',
                        color: '#d4d4d4',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '10px',
                      }}
                      title="Copy CURL command"
                    >
                      📋 CURL
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
