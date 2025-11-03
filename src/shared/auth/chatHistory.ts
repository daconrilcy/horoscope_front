/**
 * Helpers pour la gestion de l'historique de chat dans localStorage
 * Source de vérité = mémoire (Zustand), localStorage sert uniquement d'appoint pour rehydrate au boot
 */

const STORAGE_KEY = 'CHAT_HISTORY_V1';

export interface ChatMessage {
  id: string; // UUID v4
  role: 'user' | 'assistant';
  content: string;
  ts: number; // timestamp epoch ms
}

export interface ChatHistoryData {
  [chartId: string]: ChatMessage[];
}

/**
 * Lit l'historique de chat depuis localStorage
 * @returns ChatHistoryData ou objet vide si absent/invalide
 */
export function readChatHistory(): ChatHistoryData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored == null || stored === '') {
      return {};
    }

    // Essayer de parser comme JSON
    try {
      const parsed: unknown = JSON.parse(stored);
      // Vérifier que c'est un objet
      if (
        typeof parsed === 'object' &&
        parsed !== null &&
        !Array.isArray(parsed)
      ) {
        const data = parsed as Record<string, unknown>;
        const validHistory: ChatHistoryData = {};

        // Vérifier chaque chartId
        for (const [chartId, messages] of Object.entries(data)) {
          if (Array.isArray(messages)) {
            const validMessages: ChatMessage[] = [];
            for (const msg of messages) {
              if (typeof msg === 'object' && msg !== null) {
                const typedMsg = msg as Record<string, unknown>;
                if (
                  'id' in typedMsg &&
                  typeof typedMsg.id === 'string' &&
                  'role' in typedMsg &&
                  (typedMsg.role === 'user' || typedMsg.role === 'assistant') &&
                  'content' in typedMsg &&
                  typeof typedMsg.content === 'string' &&
                  'ts' in typedMsg &&
                  typeof typedMsg.ts === 'number'
                ) {
                  validMessages.push({
                    id: typedMsg.id,
                    role: typedMsg.role,
                    content: typedMsg.content,
                    ts: typedMsg.ts,
                  });
                }
              }
            }
            validHistory[chartId] = validMessages;
          }
        }
        return validHistory;
      }
      return {};
    } catch {
      // Si le parsing JSON échoue, retourner objet vide
      return {};
    }
  } catch {
    // Fallback en cas d'erreur (localStorage bloqué, etc.)
    return {};
  }
}

/**
 * Stocke l'historique de chat dans localStorage
 * @param history ChatHistoryData à persister
 */
export function writeChatHistory(history: ChatHistoryData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch {
    // Ignorer les erreurs (localStorage plein, etc.)
  }
}

/**
 * Purge l'historique de chat de localStorage
 */
export function clearChatHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignorer les erreurs
  }
}
