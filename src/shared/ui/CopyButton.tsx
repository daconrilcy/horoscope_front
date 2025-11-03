import { useState, useCallback } from 'react';

/**
 * Props pour le composant CopyButton
 */
export interface CopyButtonProps {
  /** Texte à copier (peut être une fonction async) */
  text: string | (() => string | Promise<string>);
  /** Label du bouton */
  label?: string;
  /** Callback appelé après copie réussie */
  onCopy?: () => void;
}

/**
 * Composant bouton pour copier du texte dans le presse-papier
 * Supporte texte statique et fonction asynchrone
 * Gère permissions Clipboard API + fallback document.execCommand
 */
export function CopyButton({
  text,
  label = 'Copier',
  onCopy,
}: CopyButtonProps): JSX.Element {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCopy = useCallback(async () => {
    try {
      // Obtenir le texte (sync ou async)
      let textToCopy: string;
      if (typeof text === 'function') {
        textToCopy = await text();
      } else {
        textToCopy = text;
      }

      // Essayer Clipboard API d'abord
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        // Fallback : document.execCommand
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);

        if (!success) {
          throw new Error('Impossible de copier dans le presse-papier');
        }
      }

      // Succès
      setCopied(true);
      setError(null);
      onCopy?.();

      // Réinitialiser après 2 secondes
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Erreur lors de la copie';
      setError(errorMessage);
      setCopied(false);
    }
  }, [text, onCopy]);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        type="button"
        onClick={handleCopy}
        aria-label={copied ? 'Copié !' : label}
        aria-live="polite"
        style={{
          padding: '0.5rem 1rem',
          backgroundColor: copied ? '#10b981' : '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.25rem',
          cursor: 'pointer',
          fontWeight: 500,
          transition: 'background-color 0.2s',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}
      >
        {copied ? (
          <>
            <span>✓</span>
            <span>Copié !</span>
          </>
        ) : (
          <span>{label}</span>
        )}
      </button>
      {error && (
        <div
          role="alert"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            marginTop: '0.25rem',
            padding: '0.25rem 0.5rem',
            backgroundColor: '#fee2e2',
            color: '#991b1b',
            borderRadius: '0.25rem',
            fontSize: '0.75rem',
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
}
