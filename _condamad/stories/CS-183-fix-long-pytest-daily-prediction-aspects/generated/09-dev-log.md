# Dev Log

## 2026-05-18

- Dirty file préexistant: `.discord/bot.py`.
- Correction menée sur les aspects des prédictions quotidiennes et la projection publique.
- Incident de validation: une première commande pytest a été lancée depuis `backend` avec un chemin de venv erroné; les relances suivantes utilisent l'activation depuis la racine du repo.
- Implémentation: résolution d'orbes natales par paire de corps via règles ciblées puis orbe canonique `default_orb_deg`.
- Implémentation: propagation de `default_orb_deg` dans les profils d'aspects chargés et gelés.
- Implémentation: projection publique chargée par `reference_version_id` persistant du snapshot.
- Implémentation: EventDetector utilise l'orbe canonique de définition si aucune règle ciblée ne correspond.
- Mise à jour des tests et fixtures de régression après activation des orbes canoniques.
- Validation finale: `ruff check .` OK et `pytest -q --long` OK (`3778 passed, 12 skipped`).
