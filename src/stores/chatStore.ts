import { create } from 'zustand';
import {
  readChatHistory,
  writeChatHistory,
  type ChatMessage,
  type ChatHistoryData,
} from '@/shared/auth/chatHistory';
import { v4 as uuidv4 } from 'uuid';

interface ChatState {
  byChart: Record<string, ChatMessage[]>;
  hasHydrated: boolean;
  hydrateFromStorage: () => void;
  addMessage: (
    chartId: string,
    role: 'user' | 'assistant',
    content: string
  ) => void;
  getMessages: (chartId: string) => ChatMessage[];
  clearMessages: (chartId: string) => void;
}

const MAX_MESSAGES_PER_CHART = 50;

/**
 * Cap FIFO : si on dépasse MAX_MESSAGES_PER_CHART, supprimer les plus anciens
 */
function cappedPush(
  messages: ChatMessage[],
  newMessage: ChatMessage
): ChatMessage[] {
  const next = [...messages, newMessage];
  if (next.length > MAX_MESSAGES_PER_CHART) {
    next.splice(0, next.length - MAX_MESSAGES_PER_CHART);
  }
  return next;
}

/**
 * Store Zustand pour la gestion de l'historique de chat
 * Mémoire = source de vérité, localStorage sert uniquement d'appoint pour rehydrate au boot
 * hasHydrated permet de savoir si l'hydratation depuis localStorage est terminée
 * FIFO cap : si > MAX_MESSAGES_PER_CHART, supprimer les plus anciens
 */
export const useChatStore = create<ChatState>()((set, get) => ({
  byChart: {},
  hasHydrated: false,

  hydrateFromStorage: (): void => {
    const history = readChatHistory();
    set({ byChart: history, hasHydrated: true });
  },

  addMessage: (
    chartId: string,
    role: 'user' | 'assistant',
    content: string
  ): void => {
    const currentHistory = get().byChart;
    const chartMessages = currentHistory[chartId] || [];

    // Créer le nouveau message avec UUID et timestamp
    const newMessage: ChatMessage = {
      id: uuidv4(),
      role,
      content,
      ts: Date.now(),
    };

    // Appliquer le cap FIFO
    const updatedMessages = cappedPush(chartMessages, newMessage);

    // Mettre à jour l'état
    const newHistory: ChatHistoryData = {
      ...currentHistory,
      [chartId]: updatedMessages,
    };

    // Persister
    writeChatHistory(newHistory);
    set({ byChart: newHistory });
  },

  getMessages: (chartId: string): ChatMessage[] => {
    const currentHistory = get().byChart;
    const messages = currentHistory[chartId] || [];
    // Trier par timestamp (croissant) pour garantir l'ordre chronologique
    return [...messages].sort((a, b) => a.ts - b.ts);
  },

  clearMessages: (chartId: string): void => {
    const currentHistory = get().byChart;
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { [chartId]: _unused, ...rest } = currentHistory;

    // Persister
    writeChatHistory(rest);
    set({ byChart: rest });
  },
}));
