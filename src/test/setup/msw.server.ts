import { setupServer } from 'msw/node';
import { handlers as authHandlers } from './handlers/auth';
import { handlers as billingHandlers } from './handlers/billing';
import { handlers as paywallHandlers } from './handlers/paywall';
import { handlers as horoscopeHandlers } from './handlers/horoscope';
import { handlers as chatHandlers } from './handlers/chat';
import { handlers as accountHandlers } from './handlers/account';
import { handlers as legalHandlers } from './handlers/legal';

// Combine tous les handlers
export const handlers = [
  ...authHandlers,
  ...billingHandlers,
  ...paywallHandlers,
  ...horoscopeHandlers,
  ...chatHandlers,
  ...accountHandlers,
  ...legalHandlers,
];

// Crée le serveur MSW pour Node.js (tests)
export const server = setupServer(...handlers);
