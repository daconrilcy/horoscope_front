import { useEffect, useRef } from 'react';
import { MessageItem, type MessageItemProps } from './MessageItem';

/**
 * Props pour le composant MessageList
 */
export interface MessageListProps {
  /** Messages à afficher */
  messages: MessageItemProps['message'][];
  /** Indique si une requête est en cours */
  isLoading?: boolean;
  /** Callback pour effacer l'historique */
  onClear?: () => void;
}

/**
 * Composant pour afficher la liste des messages de chat
 * Auto-scroll vers le bas à chaque nouveau message
 */
export function MessageList({
  messages,
  isLoading,
  onClear,
}: MessageListProps): JSX.Element {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll vers le bas à chaque nouveau message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages.length]);

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1rem',
        backgroundColor: '#fff',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
        }}
      >
        <h3 style={{ margin: 0 }}>Historique du chat</h3>
        {messages.length > 0 && onClear && (
          <button
            type="button"
            onClick={onClear}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc3545',
              color: '#fff',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer',
            }}
          >
            Effacer
          </button>
        )}
      </div>

      <div ref={scrollRef} role="log" aria-live="polite" aria-atomic="false">
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '2rem',
              color: '#666',
            }}
          >
            Aucun message pour le moment. Posez votre première question !
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageItem key={msg.id} message={msg} />
            ))}
            {isLoading === true && (
              <div
                style={{
                  padding: '0.75rem',
                  fontStyle: 'italic',
                  color: '#666',
                }}
              >
                Assistant écrit...
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
