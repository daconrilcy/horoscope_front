import { useMutation } from '@tanstack/react-query';
import { chatService } from '@/shared/api/chat.service';
import { ApiError, NetworkError } from '@/shared/api/errors';
import { toast } from '@/app/AppProviders';
import { useChatStore } from '@/stores/chatStore';
import { usePaywall } from '@/features/billing/hooks/usePaywall';
import { FEATURES } from '@/shared/config/features';

/**
 * Interface du résultat du hook useChat
 */
export interface UseChatResult {
  /** Fonction pour envoyer une question */
  ask: (question: string) => Promise<void>;
  /** Indique si une mutation est en cours */
  isPending: boolean;
  /** Erreur de la dernière mutation */
  error: Error | null;
  /** Messages récupérés depuis le store */
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    ts: number;
  }>;
  /** Indique si l'utilisateur est autorisé à utiliser le chat */
  isAllowed: boolean;
  /** Raison du blocage (si allowed: false) */
  reason?: 'plan' | 'rate';
  /** Nombre de secondes avant retry (si 429) */
  retryAfter?: number;
}

/**
 * Hook React Query pour le chat RAG
 * Guards paywall, anti double-submit, optimistic UI
 */
export function useChat(chartId: string): UseChatResult {
  const { isAllowed, reason, retryAfter } = usePaywall(
    FEATURES.CHAT_MSG_PER_DAY
  );
  const addMessage = useChatStore((state) => state.addMessage);
  const getMessages = useChatStore((state) => state.getMessages);

  const { mutateAsync, isPending, error } = useMutation({
    mutationFn: async (question: string) => {
      return await chatService.advise({
        chart_id: chartId,
        question,
      });
    },
    onSuccess: (_data) => {
      // Ajouter la réponse assistant au store
      // Le message user a déjà été ajouté de manière optimistic
      addMessage(chartId, 'assistant', _data.answer);
    },
    onError: (err) => {
      // En cas d'erreur 402/429, le message user reste dans le store
      // On ne fait rien d'autre ici car l'erreur sera exposée via error
      // Les événements paywall sont déjà émis par le client HTTP
      if (err instanceof ApiError) {
        // 401 → laisse le wrapper déclencher l'unauthorized (redir login)
        // 402/429 → événements déjà émis, on laisse le composant gérer
        if (err.status !== 401 && err.status !== 402 && err.status !== 429) {
          toast.error(err.message || 'Une erreur est survenue');
        }
      } else if (err instanceof NetworkError) {
        toast.error('Erreur réseau, réessayez');
      } else {
        toast.error('Une erreur inattendue est survenue');
      }
    },
  });

  /**
   * Fonction pour envoyer une question avec guards paywall
   */
  const ask = async (question: string): Promise<void> => {
    // Guard : vérifier si autorisé
    if (!isAllowed) {
      const message =
        reason === 'rate'
          ? "Quota atteint pour aujourd'hui. Passez à un plan supérieur pour continuer."
          : 'Cette fonctionnalité est réservée au plan Plus.';
      toast.info(message);
      return;
    }

    // Guard : anti double-submit
    if (isPending) {
      return;
    }

    // Optimistic UI : ajouter le message user AVANT l'appel
    addMessage(chartId, 'user', question);

    // Appeler le service (les erreurs sont gérées dans onError)
    await mutateAsync(question);
  };

  // Récupérer les messages depuis le store
  const messages = getMessages(chartId);

  return {
    ask,
    isPending,
    error: error ?? null,
    messages,
    isAllowed,
    reason,
    retryAfter,
  };
}
