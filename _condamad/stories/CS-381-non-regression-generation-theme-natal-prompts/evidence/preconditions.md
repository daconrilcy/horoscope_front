# Preconditions Locales

- Backend: Python exécuté après activation `.\.venv\Scripts\Activate.ps1`.
- Frontend: commandes lancées via `pnpm --dir frontend`.
- E2E: le scénario mocke auth, profil de naissance, géocoding, `POST /v1/users/me/natal-chart` et `/latest`.
- Provider LLM réel: non utilisé; la preuve provider repose sur fixtures/tests déterministes.
- Données couvertes: `1973-04-24 11:00`, Paris, France, `Europe/Paris`.
- Note Playwright: dans cet environnement, le runner intégré `webServer` timeoute; la validation E2E PASS utilise
  `PLAYWRIGHT_SKIP_WEBSERVER=1` avec un serveur Vite local lancé et arrêté dans la même commande.
