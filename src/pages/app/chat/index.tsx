import { useEffect } from 'react';
import { useTitle } from '@/shared/hooks/useTitle';
import { useHoroscopeStore } from '@/stores/horoscopeStore';
import { useChatStore } from '@/stores/chatStore';
import { ChatBox } from '@/features/chat/ChatBox';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/shared/config/routes';

/**
 * Page Chat (privée)
 * Affiche le chat RAG pour le dernier chart créé
 */
function ChatPage(): JSX.Element {
  useTitle('Chat');
  const hydrateHoroscope = useHoroscopeStore(
    (state) => state.hydrateFromStorage
  );
  const hydrateChat = useChatStore((state) => state.hydrateFromStorage);
  const recentCharts = useHoroscopeStore((state) => state.recentCharts);
  const lastChart = recentCharts[0];

  // Hydrater les stores au montage
  useEffect(() => {
    hydrateHoroscope();
    hydrateChat();
  }, [hydrateHoroscope, hydrateChat]);

  if (lastChart === undefined) {
    return (
      <div>
        <h1>Chat Astrologique</h1>
        <p>Créez d'abord un thème natal pour pouvoir poser des questions.</p>
        <Link
          to={ROUTES.APP.HOROSCOPE}
          style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#007bff',
            color: '#fff',
            textDecoration: 'none',
            borderRadius: '0.5rem',
            marginTop: '1rem',
          }}
        >
          Créer un thème natal
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Chat Astrologique</h1>
      <p>
        Posez vos questions sur votre thème natal{' '}
        {lastChart.label !== undefined && `(${lastChart.label})`}
      </p>
      <ChatBox chartId={lastChart.chartId} />
    </div>
  );
}

export { ChatPage };
