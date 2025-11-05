import { useState } from 'react';
import { terminalService } from '@/shared/api/terminal.service';
import type {
  TerminalConnection,
  PaymentIntent,
  TerminalProcessResponse,
  TerminalCaptureResponse,
  TerminalCancelResponse,
  TerminalRefundResponse,
} from '@/shared/api/terminal.service';
import { eventBus } from '@/shared/api/eventBus';

/**
 * États de la machine à états Terminal
 */
type TerminalState =
  | { type: 'idle' }
  | { type: 'connecting' }
  | { type: 'connected'; connection: TerminalConnection }
  | { type: 'creating_pi' }
  | { type: 'pi_created'; paymentIntent: PaymentIntent }
  | { type: 'processing' }
  | { type: 'processed'; processResponse: TerminalProcessResponse }
  | { type: 'capturing' }
  | { type: 'captured'; captureResponse: TerminalCaptureResponse }
  | { type: 'canceling' }
  | { type: 'canceled'; cancelResponse: TerminalCancelResponse }
  | { type: 'refunding' }
  | { type: 'refunded'; refundResponse: TerminalRefundResponse }
  | { type: 'error'; error: string };

/**
 * Composant console pour simuler Stripe Terminal (dev-only)
 * Machine à états pour gérer les flows : connect → payment_intent → process → capture/refund/cancel
 */
export function DevTerminalConsole(): JSX.Element | null {
  // Hooks doivent être appelés avant tout return conditionnel
  const [state, setState] = useState<TerminalState>({ type: 'idle' });
  const [amount, setAmount] = useState<string>('1000'); // 10.00 EUR par défaut
  const [currency, setCurrency] = useState<string>('eur');
  const [refundAmount, setRefundAmount] = useState<string>('');

  // Masquer complètement en production
  if (!import.meta.env.DEV) {
    return null;
  }

  // Guards pour éviter les double-soumissions
  const isProcessing =
    state.type === 'connecting' ||
    state.type === 'creating_pi' ||
    state.type === 'processing' ||
    state.type === 'capturing' ||
    state.type === 'canceling' ||
    state.type === 'refunding';

  const handleConnect = async (): Promise<void> => {
    if (isProcessing) return;

    setState({ type: 'connecting' });
    eventBus.emit('terminal:connect', {});

    try {
      const connection = await terminalService.connect();
      setState({ type: 'connected', connection });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur de connexion';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleCreatePaymentIntent = async (): Promise<void> => {
    if (isProcessing || state.type !== 'connected') return;

    const amountNum = parseInt(amount, 10);
    if (isNaN(amountNum) || amountNum <= 0) {
      setState({ type: 'error', error: 'Montant invalide' });
      return;
    }

    setState({ type: 'creating_pi' });
    eventBus.emit('terminal:payment_intent', { amount: amountNum, currency });

    try {
      const paymentIntent = await terminalService.createPaymentIntent(
        amountNum,
        currency
      );
      setState({ type: 'pi_created', paymentIntent });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur de création du PI';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleProcess = async (): Promise<void> => {
    if (isProcessing || state.type !== 'pi_created') return;

    const paymentIntentId = state.paymentIntent.payment_intent_id;
    setState({ type: 'processing' });
    eventBus.emit('terminal:process', { payment_intent_id: paymentIntentId });

    try {
      const processResponse = await terminalService.process(paymentIntentId);
      setState({ type: 'processed', processResponse });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur de traitement';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleCapture = async (): Promise<void> => {
    if (isProcessing || state.type !== 'processed') return;

    const paymentIntentId = state.processResponse.payment_intent_id;
    setState({ type: 'capturing' });
    eventBus.emit('terminal:capture', { payment_intent_id: paymentIntentId });

    try {
      const captureResponse = await terminalService.capture(paymentIntentId);
      setState({ type: 'captured', captureResponse });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur de capture';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleCancel = async (): Promise<void> => {
    if (isProcessing) {
      // Peut annuler depuis plusieurs états
      if (
        state.type !== 'pi_created' &&
        state.type !== 'processed' &&
        state.type !== 'captured'
      ) {
        return;
      }
    }

    const paymentIntentId =
      state.type === 'pi_created'
        ? state.paymentIntent.payment_intent_id
        : state.type === 'processed'
          ? state.processResponse.payment_intent_id
          : state.type === 'captured'
            ? state.captureResponse.payment_intent_id
            : null;

    if (!paymentIntentId) return;

    setState({ type: 'canceling' });
    eventBus.emit('terminal:cancel', { payment_intent_id: paymentIntentId });

    try {
      const cancelResponse = await terminalService.cancel(paymentIntentId);
      setState({ type: 'canceled', cancelResponse });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur d\'annulation';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleRefund = async (): Promise<void> => {
    if (isProcessing || state.type !== 'captured') return;

    const paymentIntentId = state.captureResponse.payment_intent_id;
    const refundAmountNum =
      refundAmount.trim() === ''
        ? undefined
        : parseInt(refundAmount, 10);

    if (refundAmountNum !== undefined && (isNaN(refundAmountNum) || refundAmountNum <= 0)) {
      setState({ type: 'error', error: 'Montant de remboursement invalide' });
      return;
    }

    setState({ type: 'refunding' });
    eventBus.emit('terminal:refund', {
      payment_intent_id: paymentIntentId,
      amount: refundAmountNum,
    });

    try {
      const refundResponse = await terminalService.refund(
        paymentIntentId,
        refundAmountNum
      );
      setState({ type: 'refunded', refundResponse });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur de remboursement';
      setState({ type: 'error', error: errorMessage });
    }
  };

  const handleReset = (): void => {
    setState({ type: 'idle' });
    setAmount('1000');
    setCurrency('eur');
    setRefundAmount('');
  };

  const containerStyle: React.CSSProperties = {
    maxWidth: '800px',
    margin: '2rem auto',
    padding: '1.5rem',
    backgroundColor: '#1e1e1e',
    borderRadius: '0.5rem',
    fontFamily: 'monospace',
    color: '#fff',
  };

  const titleStyle: React.CSSProperties = {
    margin: '0 0 1.5rem 0',
    paddingBottom: '0.75rem',
    borderBottom: '1px solid #444',
    fontSize: '1.25rem',
    fontWeight: 600,
  };

  const sectionStyle: React.CSSProperties = {
    marginBottom: '1.5rem',
    padding: '1rem',
    backgroundColor: '#2a2a2a',
    borderRadius: '0.25rem',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '0.5rem 1rem',
    marginRight: '0.5rem',
    marginBottom: '0.5rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '0.25rem',
    cursor: isProcessing ? 'not-allowed' : 'pointer',
    opacity: isProcessing ? 0.5 : 1,
    fontSize: '0.875rem',
    fontWeight: 500,
  };

  const inputStyle: React.CSSProperties = {
    padding: '0.5rem',
    marginRight: '0.5rem',
    marginBottom: '0.5rem',
    backgroundColor: '#1e1e1e',
    color: '#fff',
    border: '1px solid #444',
    borderRadius: '0.25rem',
    fontSize: '0.875rem',
    fontFamily: 'monospace',
  };

  const stateStyle: React.CSSProperties = {
    padding: '0.75rem',
    marginBottom: '1rem',
    backgroundColor: '#2a2a2a',
    borderRadius: '0.25rem',
    fontSize: '0.875rem',
  };

  const errorStyle: React.CSSProperties = {
    padding: '0.75rem',
    marginBottom: '1rem',
    backgroundColor: '#dc3545',
    color: '#fff',
    borderRadius: '0.25rem',
    fontSize: '0.875rem',
  };

  const getStateLabel = (): string => {
    switch (state.type) {
      case 'idle':
        return '🟢 Idle';
      case 'connecting':
        return '🟡 Connecting...';
      case 'connected':
        return '🟢 Connected';
      case 'creating_pi':
        return '🟡 Creating Payment Intent...';
      case 'pi_created':
        return '🟢 Payment Intent Created';
      case 'processing':
        return '🟡 Processing...';
      case 'processed':
        return '🟢 Processed';
      case 'capturing':
        return '🟡 Capturing...';
      case 'captured':
        return '🟢 Captured';
      case 'canceling':
        return '🟡 Canceling...';
      case 'canceled':
        return '🟢 Canceled';
      case 'refunding':
        return '🟡 Refunding...';
      case 'refunded':
        return '🟢 Refunded';
      case 'error':
        return '🔴 Error';
      default:
        return 'Unknown';
    }
  };

  return (
    <div style={containerStyle}>
      <h2 style={titleStyle}>🔧 Stripe Terminal Simulator (DEV)</h2>

      {/* État actuel */}
      <div style={stateStyle}>
        <strong>État:</strong> {getStateLabel()}
        {state.type === 'error' && (
          <div style={errorStyle}>{state.error}</div>
        )}
      </div>

      {/* Connect */}
      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem' }}>
          1. Connect
        </h3>
          <button
            type="button"
            onClick={() => {
              void handleConnect();
            }}
            disabled={isProcessing || state.type !== 'idle'}
            style={buttonStyle}
          >
            Connect to Terminal
          </button>
        {state.type === 'connected' && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
            Terminal ID: {state.connection.terminal_id ?? 'N/A'}
            <br />
            Connection Token: {state.connection.connection_token.slice(0, 20)}...
          </div>
        )}
      </div>

      {/* Create Payment Intent */}
      {state.type === 'connected' && (
        <div style={sectionStyle}>
          <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem' }}>
            2. Create Payment Intent
          </h3>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount (centimes)"
            disabled={isProcessing}
            style={inputStyle}
          />
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            disabled={isProcessing}
            style={inputStyle}
          >
            <option value="eur">EUR</option>
            <option value="usd">USD</option>
            <option value="gbp">GBP</option>
          </select>
          <button
            type="button"
            onClick={() => {
              void handleCreatePaymentIntent();
            }}
            disabled={isProcessing}
            style={buttonStyle}
          >
            Create Payment Intent
          </button>
          {state.type === 'pi_created' && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
              PI ID: {state.paymentIntent.payment_intent_id}
              <br />
              Amount: {state.paymentIntent.amount / 100} {state.paymentIntent.currency.toUpperCase()}
              <br />
              Status: {state.paymentIntent.status}
            </div>
          )}
        </div>
      )}

      {/* Process */}
      {state.type === 'pi_created' && (
        <div style={sectionStyle}>
          <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem' }}>
            3. Process Payment
          </h3>
          <button
            type="button"
            onClick={() => {
              void handleProcess();
            }}
            disabled={isProcessing}
            style={buttonStyle}
          >
            Process Payment
          </button>
          {state.type === 'processed' && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
              Status: {state.processResponse.status}
            </div>
          )}
        </div>
      )}

      {/* Capture / Cancel / Refund */}
      {state.type === 'processed' && (
        <div style={sectionStyle}>
          <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem' }}>
            4. Capture or Cancel
          </h3>
          <button
            type="button"
            onClick={() => {
              void handleCapture();
            }}
            disabled={isProcessing}
            style={buttonStyle}
          >
            Capture
          </button>
          <button
            type="button"
            onClick={() => {
              void handleCancel();
            }}
            disabled={isProcessing}
            style={{ ...buttonStyle, backgroundColor: '#dc3545' }}
          >
            Cancel
          </button>
          {state.type === 'captured' && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
              Amount Captured: {state.captureResponse.amount_captured / 100} {currency.toUpperCase()}
              <br />
              Status: {state.captureResponse.status}
            </div>
          )}
        </div>
      )}

      {/* Refund */}
      {state.type === 'captured' && (
        <div style={sectionStyle}>
          <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1rem' }}>
            5. Refund (optional)
          </h3>
          <input
            type="number"
            value={refundAmount}
            onChange={(e) => setRefundAmount(e.target.value)}
            placeholder="Refund amount (centimes, empty = full refund)"
            disabled={isProcessing}
            style={inputStyle}
          />
          <button
            type="button"
            onClick={() => {
              void handleRefund();
            }}
            disabled={isProcessing}
            style={{ ...buttonStyle, backgroundColor: '#ffc107', color: '#000' }}
          >
            Refund
          </button>
          {state.type === 'refunded' && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
              Refund ID: {state.refundResponse.refund_id}
              <br />
              Amount: {state.refundResponse.amount / 100} {currency.toUpperCase()}
              <br />
              Status: {state.refundResponse.status}
            </div>
          )}
        </div>
      )}

      {/* Cancel (depuis plusieurs états) */}
      {(state.type === 'pi_created' ||
        state.type === 'processed' ||
        state.type === 'captured') && (
        <div style={sectionStyle}>
          <button
            type="button"
            onClick={() => {
              void handleCancel();
            }}
            disabled={isProcessing}
            style={{ ...buttonStyle, backgroundColor: '#dc3545' }}
          >
            Cancel Payment
          </button>
          {state.type === 'canceled' && (
            <div style={{ marginTop: '0.5rem', fontSize: '0.8125rem', color: '#888' }}>
              Status: {state.cancelResponse.status}
            </div>
          )}
        </div>
      )}

      {/* Reset */}
      {state.type !== 'idle' && (
        <div style={sectionStyle}>
          <button
            type="button"
            onClick={handleReset}
            disabled={isProcessing}
            style={{ ...buttonStyle, backgroundColor: '#6c757d' }}
          >
            Reset
          </button>
        </div>
      )}
    </div>
  );
}
