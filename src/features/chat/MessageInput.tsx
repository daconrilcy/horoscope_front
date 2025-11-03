import React, { useState, useRef, useEffect } from 'react';

/**
 * Props pour le composant MessageInput
 */
export interface MessageInputProps {
  /** Callback appelé lors de l'envoi */
  onSend: (question: string) => void | Promise<void>;
  /** Indique si une requête est en cours */
  isPending?: boolean;
  /** Indique si le champ est désactivé */
  disabled?: boolean;
}

const MAX_LENGTH = 1000;
const MIN_LENGTH = 3;

/**
 * Composant pour la saisie de message
 * Textarea auto-resize, compteur chars, Enter pour envoyer
 */
export function MessageInput({
  onSend,
  isPending = false,
  disabled = false,
}: MessageInputProps): JSX.Element {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = (): void => {
    const trimmed = question.trim();
    if (trimmed.length >= MIN_LENGTH && !isPending && !disabled) {
      void onSend(trimmed);
      setQuestion('');
    }
  };

  const isQuestionValid = question.trim().length >= MIN_LENGTH;
  const charsRemaining = MAX_LENGTH - question.length;

  return (
    <div
      style={{
        borderTop: '1px solid #e0e0e0',
        padding: '1rem',
        backgroundColor: '#f9f9f9',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isPending}
          maxLength={MAX_LENGTH}
          placeholder="Posez votre question... (Entrée pour envoyer)"
          style={{
            width: '100%',
            minHeight: '60px',
            maxHeight: '200px',
            padding: '0.75rem',
            border: '1px solid #ccc',
            borderRadius: '0.5rem',
            resize: 'none',
            fontFamily: 'inherit',
            fontSize: '1rem',
          }}
          aria-label="Question"
          aria-busy={isPending}
          aria-invalid={!isQuestionValid && question.length > 0}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span
            style={{
              fontSize: '0.875rem',
              color: charsRemaining < 50 ? '#dc3545' : '#666',
            }}
          >
            {question.length}/{MAX_LENGTH}
          </span>
          <button
            type="button"
            onClick={handleSend}
            disabled={!isQuestionValid || isPending || disabled}
            style={{
              padding: '0.5rem 1.5rem',
              backgroundColor:
                !isQuestionValid || isPending || disabled ? '#ccc' : '#007bff',
              color: '#fff',
              border: 'none',
              borderRadius: '0.5rem',
              cursor:
                !isQuestionValid || isPending || disabled
                  ? 'not-allowed'
                  : 'pointer',
              fontWeight: 500,
            }}
          >
            {isPending ? 'Envoi...' : 'Envoyer'}
          </button>
        </div>
      </div>
    </div>
  );
}
