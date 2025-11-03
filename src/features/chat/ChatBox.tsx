import React from 'react';
import { useChat } from './hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { PaywallGate } from '@/features/billing/PaywallGate';
import { useChatStore } from '@/stores/chatStore';

/**
 * Props pour le composant ChatBox
 */
export interface ChatBoxProps {
  /** ID du thème natal */
  chartId: string;
}

/**
 * Composant container pour le chat RAG
 * Layout : MessageList + PaywallGate(MessageInput)
 */
export function ChatBox({ chartId }: ChatBoxProps): JSX.Element {
  const { ask, isPending, error, messages } = useChat(chartId);
  const clearMessagesHandler = useChatStore((state) => state.clearMessages);
  const clearMessages = React.useCallback(() => {
    if (
      window.confirm(
        "Êtes-vous sûr de vouloir effacer l'historique de ce chat ?"
      )
    ) {
      clearMessagesHandler(chartId);
    }
  }, [chartId, clearMessagesHandler]);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        overflow: 'hidden',
        backgroundColor: '#fff',
      }}
    >
      <MessageList
        messages={messages}
        isLoading={isPending}
        onClear={clearMessages}
      />

      <div>
        <PaywallGate feature="chat.messages/day" onUpgrade={() => undefined}>
          <MessageInput onSend={ask} isPending={isPending} />
        </PaywallGate>
      </div>

      {error && (
        <div
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#fee2e2',
            color: '#991b1b',
            fontSize: '0.875rem',
          }}
        >
          {error.message}
        </div>
      )}
    </div>
  );
}
