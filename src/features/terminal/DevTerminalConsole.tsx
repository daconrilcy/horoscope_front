import { useState } from 'react';
import { env } from '@/shared/config/env';
import {
  terminalService,
  TERMINAL_TEST_AMOUNTS,
  TERMINAL_TEST_CARDS,
} from '@/shared/api/terminal.service';
import { toast } from '@/app/AppProviders';
import { useTitle } from '@/shared/hooks/useTitle';

/**
 * États de la machine à états Terminal
 */
type TerminalState =
  | 'disconnected'
  | 'connected'
  | 'intent_created'
  | 'processing'
  | 'captured'
  | 'canceled'
  | 'refunded'
  | 'failed';

/**
 * Composant Console Terminal (dev-only)
 * Machine à états simple pour simuler les flux Stripe Terminal
 */
export function DevTerminalConsole(): JSX.Element | null {
  useTitle('Terminal Stripe (Dev)');

  // Tous les hooks doivent être appelés avant tout return conditionnel
  const [state, setState] = useState<TerminalState>('disconnected');
  const [connectionToken, setConnectionToken] = useState<string | null>(null);
  const [paymentIntentId, setPaymentIntentId] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  // clientSecret non utilisé dans le simulateur actuel
  const [selectedAmount, setSelectedAmount] = useState<number>(
    TERMINAL_TEST_AMOUNTS.SUCCESS
  );
  const [selectedCard, setSelectedCard] = useState<string>(
    TERMINAL_TEST_CARDS.SUCCESS
  );
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!(import.meta.env.DEV || env.VITE_DEV_TERMINAL === true)) {
    return null;
  }

  const handleConnect = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await terminalService.connect();
      setConnectionToken(response.connection_token);
      setState('connected');
      toast.success('Terminal connecté');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erreur de connexion';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateIntent = async (): Promise<void> => {
    if (state !== 'connected') {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await terminalService.createPaymentIntent({
        amount: selectedAmount,
        currency: 'eur',
        payment_method_types: ['card_present'],
      });
      setPaymentIntentId(response.payment_intent_id);
      // clientSecret non utilisé: omis
      setState('intent_created');
      toast.success('PaymentIntent créé');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erreur création PaymentIntent';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProcess = async (): Promise<void> => {
    if (
      state !== 'intent_created' ||
      paymentIntentId == null ||
      paymentIntentId === ''
    ) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await terminalService.process({
        payment_intent_id: paymentIntentId,
        payment_method: selectedCard,
      });

      if (response.status === 'succeeded') {
        setState('captured');
        toast.success('Paiement réussi');
      } else if (response.status === 'requires_payment_method') {
        setState('failed');
        const errorMessage =
          response.error_message != null && response.error_message !== ''
            ? response.error_message
            : 'Paiement échoué';
        setError(errorMessage);
        toast.error(errorMessage);
      } else {
        setState('processing');
        toast.info('Paiement en cours de traitement');
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erreur traitement paiement';
      setError(message);
      setState('failed');
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCapture = async (): Promise<void> => {
    if (
      state !== 'processing' ||
      paymentIntentId == null ||
      paymentIntentId === ''
    ) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await terminalService.capture({
        payment_intent_id: paymentIntentId,
      });
      if (response.status === 'succeeded') {
        setState('captured');
        toast.success('Paiement capturé');
      } else {
        setState('failed');
        setError('Échec de la capture');
        toast.error('Échec de la capture');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur capture';
      setError(message);
      setState('failed');
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = async (): Promise<void> => {
    if (
      (state !== 'intent_created' && state !== 'processing') ||
      paymentIntentId == null ||
      paymentIntentId === ''
    ) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await terminalService.cancel({
        payment_intent_id: paymentIntentId,
      });
      setState('canceled');
      toast.info('Paiement annulé');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erreur annulation';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefund = async (): Promise<void> => {
    if (
      state !== 'captured' ||
      paymentIntentId == null ||
      paymentIntentId === ''
    ) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await terminalService.refund({
        payment_intent_id: paymentIntentId,
      });
      setState('refunded');
      toast.success('Remboursement effectué');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Erreur remboursement';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = (): void => {
    setState('disconnected');
    setConnectionToken(null);
    setPaymentIntentId(null);
    setError(null);
    setSelectedAmount(TERMINAL_TEST_AMOUNTS.SUCCESS);
    setSelectedCard(TERMINAL_TEST_CARDS.SUCCESS);
  };

  const containerStyle: React.CSSProperties = {
    padding: '2rem',
    maxWidth: '800px',
    margin: '0 auto',
  };

  const sectionStyle: React.CSSProperties = {
    marginBottom: '2rem',
    padding: '1rem',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
  };

  const buttonStyle = (disabled: boolean): React.CSSProperties => ({
    padding: '0.75rem 1.5rem',
    backgroundColor: disabled ? '#ccc' : '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: 600,
    marginRight: '0.5rem',
    marginBottom: '0.5rem',
  });

  const amountSelectId = 'terminal-amount-select';
  const cardSelectId = 'terminal-card-select';
  const hasValue = (value: string | null): value is string =>
    value != null && value !== '';

  return (
    <div style={containerStyle}>
      <h1>Stripe Terminal Simulator (Dev Only)</h1>

      {/* État actuel */}
      <div style={sectionStyle}>
        <h2>État: {state}</h2>
        {hasValue(error) && (
          <div style={{ color: '#dc3545', marginTop: '0.5rem' }}>{error}</div>
        )}
        {hasValue(connectionToken) && (
          <div
            style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}
          >
            Connection Token: {connectionToken.slice(0, 20)}...
          </div>
        )}
        {hasValue(paymentIntentId) && (
          <div
            style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}
          >
            Payment Intent ID: {paymentIntentId}
          </div>
        )}
      </div>

      {/* Configuration */}
      {state === 'disconnected' ||
      state === 'connected' ||
      state === 'intent_created' ? (
        <div style={sectionStyle}>
          <h3>Configuration</h3>
          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor={amountSelectId}
              style={{ display: 'block', marginBottom: '0.5rem' }}
            >
              Montant (centimes):
            </label>
            <select
              id={amountSelectId}
              value={selectedAmount}
              onChange={(e) => {
                setSelectedAmount(Number.parseInt(e.target.value, 10));
              }}
              style={{ padding: '0.5rem', width: '100%', maxWidth: '300px' }}
            >
              <option value={TERMINAL_TEST_AMOUNTS.SUCCESS}>
                1.00 EUR - Succès
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.SUCCESS_01}>
                1.01 EUR - PIN offline
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.SUCCESS_02}>
                1.02 EUR - PIN online
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.SUCCESS_03}>
                1.03 EUR - Signature
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.SUCCESS_05}>
                1.05 EUR - 3D Secure
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.OFFLINE_PIN}>
                2.55 EUR - PIN offline (flow)
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.ONLINE_PIN}>
                2.65 EUR - PIN online (flow)
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.DECLINED}>
                2.00 EUR - Refusé
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.INSUFFICIENT_FUNDS}>
                2.01 EUR - Fonds insuffisants
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.EXPIRED_CARD}>
                2.02 EUR - Carte expirée
              </option>
              <option value={TERMINAL_TEST_AMOUNTS.PROCESSING_ERROR}>
                2.03 EUR - Erreur traitement
              </option>
            </select>
          </div>
          <div>
            <label
              htmlFor={cardSelectId}
              style={{ display: 'block', marginBottom: '0.5rem' }}
            >
              Carte de test:
            </label>
            <select
              id={cardSelectId}
              value={selectedCard}
              onChange={(e) => {
                setSelectedCard(e.target.value);
              }}
              style={{ padding: '0.5rem', width: '100%', maxWidth: '300px' }}
            >
              <option value={TERMINAL_TEST_CARDS.SUCCESS}>
                4242...4242 - Succès
              </option>
              <option value={TERMINAL_TEST_CARDS.DECLINED}>
                4000...0002 - Refusée
              </option>
              <option value={TERMINAL_TEST_CARDS.INSUFFICIENT_FUNDS}>
                4000...9995 - Fonds insuffisants
              </option>
              <option value={TERMINAL_TEST_CARDS.EXPIRED_CARD}>
                4000...0069 - Expirée
              </option>
              <option value={TERMINAL_TEST_CARDS.PROCESSING_ERROR}>
                4000...0119 - Erreur traitement
              </option>
              <option value={TERMINAL_TEST_CARDS.OFFLINE_PIN}>
                4000...0010 - PIN offline
              </option>
              <option value={TERMINAL_TEST_CARDS.ONLINE_PIN}>
                4000...0028 - PIN online
              </option>
            </select>
          </div>
        </div>
      ) : null}

      {/* Actions */}
      <div style={sectionStyle}>
        <h3>Actions</h3>
        {state === 'disconnected' && (
          <button
            type="button"
            onClick={() => {
              void handleConnect();
            }}
            disabled={isLoading}
            style={buttonStyle(isLoading)}
          >
            {isLoading ? 'Connexion...' : 'Connecter Terminal'}
          </button>
        )}

        {state === 'connected' && (
          <>
            <button
              type="button"
              onClick={() => {
                void handleCreateIntent();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              {isLoading ? 'Création...' : 'Créer PaymentIntent'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              disabled={isLoading}
              style={buttonStyle(false)}
            >
              Reset
            </button>
          </>
        )}

        {state === 'intent_created' && (
          <>
            <button
              type="button"
              onClick={() => {
                void handleProcess();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              {isLoading ? 'Traitement...' : 'Traiter Paiement'}
            </button>
            <button
              type="button"
              onClick={() => {
                void handleCancel();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={handleReset}
              disabled={isLoading}
              style={buttonStyle(false)}
            >
              Reset
            </button>
          </>
        )}

        {state === 'processing' && (
          <>
            <button
              type="button"
              onClick={() => {
                void handleCapture();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              {isLoading ? 'Capture...' : 'Capturer'}
            </button>
            <button
              type="button"
              onClick={() => {
                void handleCancel();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              Annuler
            </button>
          </>
        )}

        {state === 'captured' && (
          <>
            <button
              type="button"
              onClick={() => {
                void handleRefund();
              }}
              disabled={isLoading}
              style={buttonStyle(isLoading)}
            >
              {isLoading ? 'Remboursement...' : 'Rembourser'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              disabled={isLoading}
              style={buttonStyle(false)}
            >
              Reset
            </button>
          </>
        )}

        {(state === 'canceled' ||
          state === 'refunded' ||
          state === 'failed') && (
          <button
            type="button"
            onClick={handleReset}
            disabled={isLoading}
            style={buttonStyle(false)}
          >
            Nouveau Test
          </button>
        )}
      </div>
    </div>
  );
}
