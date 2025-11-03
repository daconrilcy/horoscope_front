import React, {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
} from 'react';

export interface ConfirmModalProps {
  /** Indique si le modal est ouvert */
  isOpen: boolean;
  /** Callback pour fermer le modal */
  onClose: () => void;
  /** Callback pour confirmer l'action */
  onConfirm: () => void;
  /** Titre du modal */
  title: string;
  /** Message d'avertissement */
  message: string;
  /** Texte à taper pour confirmer (défaut: "SUPPRIMER") */
  confirmText?: string;
  /** Label du bouton de confirmation (défaut: "Confirmer") */
  confirmButtonLabel?: string;
  /** Style personnalisé pour le bouton de confirmation */
  confirmButtonStyle?: React.CSSProperties;
}

/**
 * Composant modal de confirmation avec double saisie
 * Accessibilité complète: focus trap, aria-*, Escape, overlay
 */
export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'SUPPRIMER',
  confirmButtonLabel = 'Confirmer',
  confirmButtonStyle,
}: ConfirmModalProps): JSX.Element | null {
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Validation: le texte doit correspondre exactement (case-sensitive + trim)
  const isValid = inputValue.trim() === confirmText;

  // Focus trap: gérer le focus au clavier
  useEffect(() => {
    if (!isOpen) return;

    // Sauvegarder l'élément qui avait le focus
    previousFocusRef.current =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;

    // Focus sur l'input de confirmation au montage
    const timeoutId = setTimeout(() => {
      inputRef.current?.focus();
    }, 0);

    // Gestion Tab/Shift+Tab: focus trap
    const handleKeyDown = (e: Event): void => {
      const keyEvent = e as KeyboardEvent;
      if (keyEvent.key !== 'Tab') return;

      const modal = modalRef.current;
      if (!modal) return;

      // Trouver tous les éléments focusables dans le modal
      const focusableElements = modal.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];

      if (keyEvent.shiftKey) {
        // Shift+Tab: si on est sur le premier, aller au dernier
        if (document.activeElement === firstFocusable) {
          keyEvent.preventDefault();
          lastFocusable?.focus();
        }
      } else {
        // Tab: si on est sur le dernier, aller au premier
        if (document.activeElement === lastFocusable) {
          keyEvent.preventDefault();
          firstFocusable?.focus();
        }
      }
    };

    // Ajouter le listener sur le modal (bubbling)
    const modal = modalRef.current;
    if (modal) {
      modal.addEventListener('keydown', handleKeyDown);
    }

    // Gestion Escape: fermer le modal
    const handleEscape = (e: Event): void => {
      const keyEvent = e as KeyboardEvent;
      if (keyEvent.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);

    // Copier les refs dans des variables locales pour le cleanup
    const modalForCleanup = modalRef.current;
    const previousFocus = previousFocusRef.current;

    return () => {
      clearTimeout(timeoutId);
      if (modalForCleanup) {
        modalForCleanup.removeEventListener('keydown', handleKeyDown);
      }
      document.removeEventListener('keydown', handleEscape);

      // Restaurer le focus à l'élément précédent
      if (previousFocus) {
        previousFocus.focus();
      }
    };
  }, [isOpen, onClose]);

  // Fermeture au clic sur overlay
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Soumission du formulaire
  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    if (isValid) {
      onConfirm();
      setInputValue(''); // Reset après confirmation
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={handleOverlayClick}
      role="presentation"
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-modal-title"
        aria-describedby="confirm-modal-message"
        style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '2rem',
          maxWidth: '500px',
          width: '90%',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="confirm-modal-title"
          style={{
            marginTop: 0,
            marginBottom: '1rem',
            fontSize: '1.5rem',
            fontWeight: 600,
          }}
        >
          {title}
        </h2>

        <p
          id="confirm-modal-message"
          style={{
            marginBottom: '1.5rem',
            color: '#666',
          }}
        >
          {message}
        </p>

        <form onSubmit={handleSubmit}>
          <label
            htmlFor="confirm-input"
            style={{
              display: 'block',
              marginBottom: '0.5rem',
              fontWeight: 500,
            }}
          >
            Tapez <strong>{confirmText}</strong> pour confirmer :
          </label>
          <input
            ref={inputRef}
            id="confirm-input"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            aria-invalid={!isValid && inputValue.length > 0}
            aria-describedby="confirm-input-hint"
            style={{
              width: '100%',
              padding: '0.75rem',
              border:
                isValid && inputValue.length > 0
                  ? '1px solid #28a745'
                  : '1px solid #ccc',
              borderRadius: '4px',
              boxSizing: 'border-box',
              fontSize: '1rem',
            }}
            autoComplete="off"
            placeholder={confirmText}
          />
          <p
            id="confirm-input-hint"
            style={{
              marginTop: '0.5rem',
              marginBottom: '1rem',
              fontSize: '0.875rem',
              color: '#666',
            }}
          >
            La confirmation est case-sensitive et doit correspondre exactement.
          </p>

          <div
            style={{
              display: 'flex',
              gap: '1rem',
              justifyContent: 'flex-end',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '1rem',
              }}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={!isValid}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: isValid ? '#dc3545' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isValid ? 'pointer' : 'not-allowed',
                fontSize: '1rem',
                ...confirmButtonStyle,
              }}
            >
              {confirmButtonLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
