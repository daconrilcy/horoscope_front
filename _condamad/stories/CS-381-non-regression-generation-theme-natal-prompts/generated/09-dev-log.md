# Dev Log

## 2026-05-29

- Reprise: les logs `_condamad/codex-runs/cs-381-*.log` montrent une story rédigée, validée et revue `CLEAN`,
  sans preuve d'implémentation applicative complète.
- Preflight: capsule complète et `condamad_validate.py` PASS avant chargement des fichiers generated.
- Implémentation conservée et complétée depuis les changements déjà présents dans les tests backend/frontend.
- Correction E2E: les locators sont bilingues et l'assertion console cible les erreurs React liées à `NatalExpertPanel`.
- Correction Playwright: `PLAYWRIGHT_SKIP_WEBSERVER=1` permet de tester contre un serveur Vite explicite,
  car la gestion `webServer` intégrée timeoute dans cet environnement Windows.
- Validation: backend, frontend, E2E, scans de garde, build et capsule validés.
- Nettoyage: `frontend/test-results` supprimé après validation; aucun serveur Vite de validation CS-381 laissé actif.
