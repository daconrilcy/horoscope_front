import { useState, type FormEvent, type KeyboardEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { authService } from '@/shared/api/auth.service';
import { useAuthStore } from '@/stores/authStore';
import { safeInternalRedirect } from '@/shared/auth/redirect';
import { toast } from '@/app/AppProviders';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page de connexion
 */
export function LoginPage(): JSX.Element {
  useTitle('Horoscope - Connexion');
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const redirectAfterLogin = useAuthStore((state) => state.redirectAfterLogin);
  const setRedirectAfterLogin = useAuthStore(
    (state) => state.setRedirectAfterLogin
  );

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [pending, setPending] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    general?: string;
  }>({});

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (pending) return;

    // Reset errors
    setErrors({});

    // Validation côté client
    const clientErrors: { email?: string; password?: string } = {};
    if (!email.trim()) {
      clientErrors.email = 'Email requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      clientErrors.email = 'Email invalide';
    }
    if (!password) {
      clientErrors.password = 'Mot de passe requis';
    }

    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      return;
    }

    setPending(true);

    try {
      // Normaliser email (trim + lowercase) avant appel API
      const normalizedEmail = email.trim().toLowerCase();

      const response = await authService.login(normalizedEmail, password);

      // Login réussi : stocker token + userRef
      login(response.token, response.user);

      // Toast success
      toast.success('Connexion réussie');

      // Redirection sécurisée
      const redirectPath = safeInternalRedirect(redirectAfterLogin);
      setRedirectAfterLogin(undefined); // Clear après utilisation
      void navigate(redirectPath, { replace: true });
    } catch (error) {
      // Gestion erreurs
      if (error instanceof ApiError) {
        if (error.status === 422 || error.status === 400) {
          // Erreurs de validation : afficher details par champ
          const fieldErrors: {
            email?: string;
            password?: string;
            general?: string;
          } = {};
          if (error.details != null) {
            const details = error.details as Record<string, string[]>;
            if (details.email && details.email.length > 0) {
              fieldErrors.email = details.email[0];
            }
            if (details.password && details.password.length > 0) {
              fieldErrors.password = details.password[0];
            }
            // Erreur générale si pas de champ spécifique
            if (
              error.message != null &&
              error.message !== '' &&
              Object.keys(fieldErrors).length === 0
            ) {
              fieldErrors.general = error.message;
            }
          } else {
            fieldErrors.general = error.message;
          }
          setErrors(fieldErrors);
        } else if (error.status != null && error.status >= 500) {
          // Erreur serveur : toast générique
          toast.error('Erreur serveur. Veuillez réessayer plus tard.');
          setErrors({
            general: 'Une erreur est survenue. Veuillez réessayer.',
          });
        } else if (error.status === 401) {
          // Non autorisé (mauvais identifiants)
          setErrors({ general: 'Email ou mot de passe incorrect' });
        } else {
          // Autres erreurs API
          toast.error(error.message || 'Erreur lors de la connexion');
          setErrors({
            general: error.message || 'Erreur lors de la connexion',
          });
        }
      } else if (error instanceof NetworkError) {
        // Erreur réseau : toast générique
        toast.error('Erreur réseau. Vérifiez votre connexion.');
        setErrors({ general: 'Erreur réseau. Vérifiez votre connexion.' });
      } else {
        // Erreur inconnue
        toast.error('Une erreur inattendue est survenue');
        setErrors({ general: 'Une erreur inattendue est survenue' });
      }
    } finally {
      setPending(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLFormElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey && !pending) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent<HTMLFormElement>).catch(() => {
        // Erreur déjà gérée dans handleSubmit
      });
    }
  };

  const emailHasError = Boolean(errors.email);
  const passwordHasError = Boolean(errors.password);

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem' }}>Connexion</h1>

      {errors.general && (
        <div
          role="alert"
          style={{
            padding: '0.75rem',
            marginBottom: '1rem',
            backgroundColor: '#fee',
            color: '#c33',
            border: '1px solid #c33',
            borderRadius: '4px',
          }}
        >
          {errors.general}
        </div>
      )}

      <form
        onSubmit={(e) => {
          void handleSubmit(e);
        }}
        onKeyDown={handleKeyDown}
        style={{ marginTop: '2rem' }}
        noValidate
      >
        <div style={{ marginBottom: '1rem' }}>
          <label
            htmlFor="email"
            style={{ display: 'block', marginBottom: '0.5rem' }}
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-invalid={emailHasError}
            aria-describedby={emailHasError ? 'email-error' : ''}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: emailHasError ? '1px solid #c33' : '1px solid #ccc',
              borderRadius: '4px',
              boxSizing: 'border-box',
            }}
            placeholder="votre@email.com"
            disabled={pending}
          />
          {errors.email && (
            <div
              id="email-error"
              role="alert"
              style={{
                marginTop: '0.25rem',
                color: '#c33',
                fontSize: '0.875rem',
              }}
            >
              {errors.email}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label
            htmlFor="password"
            style={{ display: 'block', marginBottom: '0.5rem' }}
          >
            Mot de passe
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            aria-invalid={passwordHasError}
            aria-describedby={passwordHasError ? 'password-error' : ''}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: passwordHasError ? '1px solid #c33' : '1px solid #ccc',
              borderRadius: '4px',
              boxSizing: 'border-box',
            }}
            placeholder="••••••••"
            disabled={pending}
          />
          {errors.password && (
            <div
              id="password-error"
              role="alert"
              style={{
                marginTop: '0.25rem',
                color: '#c33',
                fontSize: '0.875rem',
              }}
            >
              {errors.password}
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={pending}
          style={{
            width: '100%',
            padding: '0.75rem 1.5rem',
            backgroundColor: pending ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: pending ? 'not-allowed' : 'pointer',
            marginBottom: '1rem',
          }}
        >
          {pending ? 'Connexion...' : 'Se connecter'}
        </button>
      </form>

      <div
        style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}
      >
        <Link
          to={ROUTES.RESET.REQUEST}
          style={{ color: '#007bff', textDecoration: 'none' }}
        >
          Mot de passe oublié ?
        </Link>
      </div>

      <div
        style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}
      >
        Pas encore de compte ?{' '}
        <Link
          to={ROUTES.SIGNUP}
          style={{ color: '#007bff', textDecoration: 'none' }}
        >
          S'inscrire
        </Link>
      </div>
    </div>
  );
}
