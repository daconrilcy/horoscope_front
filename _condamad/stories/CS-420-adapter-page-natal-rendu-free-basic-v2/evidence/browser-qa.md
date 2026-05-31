# Browser QA - CS-420

- Browser plugin attempt: `iab` unavailable in this session.
- Fallback: `playwright-cli`.
- Dev server: `http://127.0.0.1:5174/` after `5173` was occupied.
- Checked URL: `http://127.0.0.1:5174/natal`.
- Observed URL: `http://127.0.0.1:5174/login?returnTo=%2Fnatal`.
- Observed DOM: login form with heading `Connexion`, email/password fields and `Se connecter`.
- Result: local app starts and route protection preserves the `/natal` return target.
- Screenshot: `evidence/browser-login-redirect.png`.
- Limitation: no authenticated browser flow; backend/auth services were not started.
