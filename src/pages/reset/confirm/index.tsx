import { useState, useEffect, type FormEvent, type KeyboardEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useTitle } from '@/shared/hooks/useTitle';
import { authService } from '@/shared/api/auth.service';
import { toast } from '@/app/AppProviders';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page de confirmation de réinitialisation de mot de passe
 */
export function ResetConfirmPage(): JSX.Element {
  useTitle('Horoscope - Nouveau mot de passe');
  const navigate = useNavigate();
  const location = useLocation();

  // Lire token depuis URL
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pending, setPending] = useState(false);
  const [errors, setErrors] = useState<{ token?: string; password?: string; confirmPassword?: string; general?: string }>({});

  useEffect(() => {
    // Extraire token depuis URL params
    const params = new URLSearchParams(location.search);
    const tokenFromUrl = params.get('token');
    if (tokenFromUrl != null && tokenFromUrl !== '') {
      setToken(tokenFromUrl);
    } else {
      setErrors({ token: 'Token de réinitialisation manquant' });
    }
  }, [location.search]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (pending || token == null || token === '') return;

    // Reset errors
    setErrors({});

    // Validation côté client
    const clientErrors: { password?: string; confirmPassword?: string } = {};
    if (!password) {
      clientErrors.password = 'Mot de passe requis';
    } else if (password.length < 8) {
      clientErrors.password = 'Le mot de passe doit contenir au moins 8 caractères';
    }
    if (!confirmPassword) {
      clientErrors.confirmPassword = 'Confirmation du mot de passe requise';
    } else if (password !== confirmPassword) {
      clientErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    if (Object.keys(clientErrors).length > 0) {
      setErrors(clientErrors);
      return;
    }

    setPending(true);

    try {
      await authService.confirmReset(token, password);

      // Succès : toast + redirection
      toast.success('Mot de passe réinitialisé');
      void navigate(ROUTES.LOGIN, { replace: true });
    } catch (error) {
      // Gestion erreurs
      if (error instanceof ApiError) {
        if (error.status === 422 || error.status === 400) {
          // Erreurs de validation : afficher details par champ
          const fieldErrors: { password?: string; confirmPassword?: string; token?: string; general?: string } = {};
          if (error.details != null) {
            const details = error.details as Record<string, string[]>;
            if (details.password && details.password.length > 0) {
              fieldErrors.password = details.password[0];
            }
            if (details.token && details.token.length > 0) {
              fieldErrors.token = details.token[0];
            }
            // Erreur générale si pas de champ spécifique
            if (error.message != null && error.message !== '' && Object.keys(fieldErrors).length === 0) {
              fieldErrors.general = error.message;
            }
          } else {
            fieldErrors.general = error.message;
          }
          setErrors(fieldErrors);
        } else if (error.status != null && error.status >= 500) {
          // Erreur serveur : toast générique
          toast.error('Erreur serveur. Veuillez réessayer plus tard.');
          setErrors({ general: 'Une erreur est survenue. Veuillez réessayer.' });
        } else {
          // Token invalide/expiré ou autres erreurs API
          const errorMessage = error.message || 'Token invalide ou expiré';
          toast.error(errorMessage);
          setErrors({ general: errorMessage });
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
    if (e.key === 'Enter' && !e.shiftKey && !pending && token != null && token !== '') {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent<HTMLFormElement>).catch(() => {
        // Erreur déjà gérée dans handleSubmit
      });
    }
  };

  const passwordHasError = Boolean(errors.password);
  const confirmPasswordHasError = Boolean(errors.confirmPassword);
  const hasTokenError = Boolean(errors.token);

  if ((token == null || token === '') && !hasTokenError) {
    return (
      <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
        <p>Chargement...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem' }}>Nouveau mot de passe</h1>

      {errors.token && (
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
          {errors.token}
        </div>
      )}

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

      {!hasTokenError && (
        <form
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
          onKeyDown={handleKeyDown}
          style={{ marginTop: '2rem' }}
          noValidate
        >
          <input type="hidden" value={token || ''} readOnly />

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem' }}>
              Nouveau mot de passe
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
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
              placeholder="•••••••• (min. 8 caractères)"
              disabled={pending || token == null || token === ''}
            />
            {errors.password && (
              <div
                id="password-error"
                role="alert"
                style={{ marginTop: '0.25rem', color: '#c33', fontSize: '0.875rem' }}
              >
                {errors.password}
              </div>
            )}
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '0.5rem' }}>
              Confirmer le mot de passe
            </label>
            <input
              id="confirmPassword"
              type="password"
              autoComplete="new-password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              aria-invalid={confirmPasswordHasError}
              aria-describedby={confirmPasswordHasError ? 'confirmPassword-error' : ''}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: confirmPasswordHasError ? '1px solid #c33' : '1px solid #ccc',
                borderRadius: '4px',
                boxSizing: 'border-box',
              }}
              placeholder="••••••••"
              disabled={pending || token == null || token === ''}
            />
            {errors.confirmPassword && (
              <div
                id="confirmPassword-error"
                role="alert"
                style={{ marginTop: '0.25rem', color: '#c33', fontSize: '0.875rem' }}
              >
                {errors.confirmPassword}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={pending || token == null || token === ''}
            style={{
              width: '100%',
              padding: '0.75rem 1.5rem',
              backgroundColor: pending || token == null || token === '' ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: pending || token == null || token === '' ? 'not-allowed' : 'pointer',
              marginBottom: '1rem',
            }}
          >
            {pending ? 'Réinitialisation...' : 'Réinitialiser le mot de passe'}
          </button>
        </form>
      )}

      <div style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}>
        <Link
          to={ROUTES.LOGIN}
          style={{ color: '#007bff', textDecoration: 'none' }}
        >
          Retour à la connexion
        </Link>
      </div>
    </div>
  );
}

