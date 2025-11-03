/**
 * Props pour le composant MessageItem
 */
export interface MessageItemProps {
  /** Message à afficher */
  message: {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    ts: number;
  };
}

/**
 * Composant pour afficher un message de chat
 * Style : bulles différenciées user (droite) / assistant (gauche)
 */
export function MessageItem({ message }: MessageItemProps): JSX.Element {
  const isUser = message.role === 'user';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '1rem',
      }}
    >
      <div
        style={{
          maxWidth: '70%',
          padding: '0.75rem 1rem',
          borderRadius: '1rem',
          backgroundColor: isUser ? '#007bff' : '#f0f0f0',
          color: isUser ? '#fff' : '#000',
        }}
      >
        <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {message.content}
        </div>
        <div
          style={{
            fontSize: '0.75rem',
            opacity: 0.7,
            marginTop: '0.5rem',
          }}
        >
          {new Date(message.ts).toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
