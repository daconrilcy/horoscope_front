import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useChatStore } from './chatStore';
import * as chatHistoryHelpers from '@/shared/auth/chatHistory';

describe('chatStore - Hydratation', () => {
  beforeEach(() => {
    // Reset store et localStorage
    useChatStore.setState({
      byChart: {},
      hasHydrated: false,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chatHistoryHelpers, 'readChatHistory').mockReturnValue({});
  });

  it('devrait initialiser hasHydrated à false', () => {
    const state = useChatStore.getState();
    expect(state.hasHydrated).toBe(false);
  });

  it('devrait hydrater depuis localStorage via hydrateFromStorage', () => {
    const mockHistory = {
      'chart-1': [
        {
          id: 'msg-1',
          role: 'user' as const,
          content: 'Première question',
          ts: 1000,
        },
      ],
    };
    vi.spyOn(chatHistoryHelpers, 'readChatHistory').mockReturnValue(
      mockHistory
    );

    useChatStore.getState().hydrateFromStorage();

    const state = useChatStore.getState();
    expect(state.byChart).toEqual(mockHistory);
    expect(state.hasHydrated).toBe(true);
  });

  it('devrait mettre hasHydrated à true même si pas de messages', () => {
    vi.spyOn(chatHistoryHelpers, 'readChatHistory').mockReturnValue({});

    useChatStore.getState().hydrateFromStorage();

    const state = useChatStore.getState();
    expect(state.byChart).toEqual({});
    expect(state.hasHydrated).toBe(true);
  });
});

describe('chatStore - AddMessage', () => {
  beforeEach(() => {
    useChatStore.setState({
      byChart: {},
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chatHistoryHelpers, 'writeChatHistory').mockImplementation(
      () => {}
    );
  });

  it('devrait ajouter un message utilisateur', () => {
    const chartId = 'chart-1';
    const content = 'Ma question';

    useChatStore.getState().addMessage(chartId, 'user', content);

    const state = useChatStore.getState();
    expect(state.byChart[chartId]).toHaveLength(1);
    expect(state.byChart[chartId][0].role).toBe('user');
    expect(state.byChart[chartId][0].content).toBe(content);
    expect(state.byChart[chartId][0].id).toBeDefined();
    expect(state.byChart[chartId][0].ts).toBeDefined();
    expect(chatHistoryHelpers.writeChatHistory).toHaveBeenCalled();
  });

  it('devrait ajouter un message assistant', () => {
    const chartId = 'chart-1';
    const content = 'Réponse du bot';

    useChatStore.getState().addMessage(chartId, 'assistant', content);

    const state = useChatStore.getState();
    expect(state.byChart[chartId]).toHaveLength(1);
    expect(state.byChart[chartId][0].role).toBe('assistant');
    expect(state.byChart[chartId][0].content).toBe(content);
    expect(chatHistoryHelpers.writeChatHistory).toHaveBeenCalled();
  });

  it('devrait générer des IDs uniques pour chaque message', () => {
    const chartId = 'chart-1';

    useChatStore.getState().addMessage(chartId, 'user', 'Q1');
    useChatStore.getState().addMessage(chartId, 'assistant', 'R1');
    useChatStore.getState().addMessage(chartId, 'user', 'Q2');

    const state = useChatStore.getState();
    expect(state.byChart[chartId]).toHaveLength(3);
    const ids = state.byChart[chartId].map((m) => m.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(3); // Tous les IDs sont uniques
  });

  it('devrait ajouter des messages à des charts différents', () => {
    useChatStore.getState().addMessage('chart-1', 'user', 'Question chart 1');
    useChatStore.getState().addMessage('chart-2', 'user', 'Question chart 2');

    const state = useChatStore.getState();
    expect(state.byChart['chart-1']).toHaveLength(1);
    expect(state.byChart['chart-2']).toHaveLength(1);
    expect(state.byChart['chart-1'][0].content).toBe('Question chart 1');
    expect(state.byChart['chart-2'][0].content).toBe('Question chart 2');
  });
});

describe('chatStore - Cap FIFO', () => {
  beforeEach(() => {
    useChatStore.setState({
      byChart: {},
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chatHistoryHelpers, 'writeChatHistory').mockImplementation(
      () => {}
    );
  });

  it('devrait limiter à 50 messages max par chart (FIFO)', () => {
    const chartId = 'chart-1';

    // Ajouter 51 messages
    for (let i = 1; i <= 51; i++) {
      useChatStore.getState().addMessage(chartId, 'user', `Message ${i}`);
    }

    const state = useChatStore.getState();
    expect(state.byChart[chartId]).toHaveLength(50);
    // Le premier message (Message 1) doit être supprimé
    expect(state.byChart[chartId][0].content).toBe('Message 2');
    // Le dernier message (Message 51) doit être présent
    expect(state.byChart[chartId][49].content).toBe('Message 51');
  });

  it('devrait conserver tous les messages si < 50', () => {
    const chartId = 'chart-1';

    for (let i = 1; i <= 30; i++) {
      useChatStore.getState().addMessage(chartId, 'user', `Message ${i}`);
    }

    const state = useChatStore.getState();
    expect(state.byChart[chartId]).toHaveLength(30);
  });
});

describe('chatStore - GetMessages', () => {
  beforeEach(() => {
    useChatStore.setState({
      byChart: {
        'chart-1': [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Q1',
            ts: 1000,
          },
          {
            id: 'msg-2',
            role: 'assistant',
            content: 'R1',
            ts: 2000,
          },
        ],
      },
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('devrait retourner les messages pour un chart existant', () => {
    const messages = useChatStore.getState().getMessages('chart-1');

    expect(messages).toHaveLength(2);
    expect(messages[0].content).toBe('Q1');
    expect(messages[1].content).toBe('R1');
  });

  it('devrait retourner tableau vide pour un chart inexistant', () => {
    const messages = useChatStore.getState().getMessages('chart-nonexistant');

    expect(messages).toEqual([]);
  });

  it('devrait retourner messages triés par timestamp', () => {
    useChatStore.setState({
      byChart: {
        'chart-1': [
          {
            id: 'msg-3',
            role: 'user',
            content: 'Dernier',
            ts: 3000,
          },
          {
            id: 'msg-1',
            role: 'user',
            content: 'Premier',
            ts: 1000,
          },
          {
            id: 'msg-2',
            role: 'user',
            content: 'Milieu',
            ts: 2000,
          },
        ],
      },
      hasHydrated: true,
    });

    const messages = useChatStore.getState().getMessages('chart-1');

    expect(messages).toHaveLength(3);
    expect(messages[0].content).toBe('Premier');
    expect(messages[1].content).toBe('Milieu');
    expect(messages[2].content).toBe('Dernier');
  });
});

describe('chatStore - ClearMessages', () => {
  beforeEach(() => {
    useChatStore.setState({
      byChart: {
        'chart-1': [
          {
            id: 'msg-1',
            role: 'user',
            content: 'Q1',
            ts: 1000,
          },
        ],
        'chart-2': [
          {
            id: 'msg-2',
            role: 'user',
            content: 'Q2',
            ts: 2000,
          },
        ],
      },
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
    vi.spyOn(chatHistoryHelpers, 'writeChatHistory').mockImplementation(
      () => {}
    );
  });

  it("devrait supprimer les messages d'un chart spécifique", () => {
    useChatStore.getState().clearMessages('chart-1');

    const state = useChatStore.getState();
    expect(state.byChart['chart-1']).toBeUndefined();
    // chart-2 doit toujours être présent
    expect(state.byChart['chart-2']).toHaveLength(1);
    expect(chatHistoryHelpers.writeChatHistory).toHaveBeenCalled();
  });

  it("devrait ne rien faire si chart n'existe pas", () => {
    useChatStore.getState().clearMessages('chart-nonexistant');

    const state = useChatStore.getState();
    expect(state.byChart['chart-1']).toHaveLength(1);
    expect(state.byChart['chart-2']).toHaveLength(1);
  });
});

describe('chatStore - Persistance', () => {
  beforeEach(() => {
    useChatStore.setState({
      byChart: {},
      hasHydrated: true,
    });
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('devrait appeler writeChatHistory à chaque addMessage', () => {
    const writeSpy = vi
      .spyOn(chatHistoryHelpers, 'writeChatHistory')
      .mockImplementation(() => {});

    useChatStore.getState().addMessage('chart-1', 'user', 'Q1');
    useChatStore.getState().addMessage('chart-1', 'assistant', 'R1');

    expect(writeSpy).toHaveBeenCalledTimes(2);
  });

  it('devrait appeler writeChatHistory lors de clearMessages', () => {
    const writeSpy = vi
      .spyOn(chatHistoryHelpers, 'writeChatHistory')
      .mockImplementation(() => {});

    useChatStore.getState().addMessage('chart-1', 'user', 'Q1');
    useChatStore.getState().clearMessages('chart-1');

    expect(writeSpy).toHaveBeenCalledTimes(2);
  });
});
