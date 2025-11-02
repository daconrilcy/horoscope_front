import { useTitle } from '@/shared/hooks/useTitle';

/**
 * Page de connexion (placeholder)
 */
export function LoginPage(): JSX.Element {
  useTitle('Horoscope - Connexion');

  return (
    <div>
      <h1>Connexion</h1>
      <p>Page de connexion (à implémenter)</p>
      <form style={{ marginTop: '2rem', maxWidth: '400px' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem' }}>
            Email
          </label>
          <input
            id="email"
            type="email"
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
            placeholder="votre@email.com"
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem' }}>
            Mot de passe
          </label>
          <input
            id="password"
            type="password"
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
            placeholder="••••••••"
          />
        </div>
        <button
          type="submit"
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Se connecter
        </button>
      </form>
    </div>
  );
}

