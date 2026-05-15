# Execution Brief

- Story key: `remplacer-house-axes-constante-par-db`
- Objectif: faire consommer les axes de maisons par le pipeline natal depuis les tables de reference DB.
- Frontiere: backend runtime astrology, repository de reference, DTO de reference et tests cibles.
- Non-objectifs: modifier les migrations existantes, changer le schema public au-dela des valeurs deja exposees, lancer les suites globales.
- Preflight: lire `AGENTS.md`, consulter le registre de regression, verifier `git status --short`, rechercher les usages de `house_axes`.
- Regles d'ecriture: petit delta, pas de fallback constant, docstrings/commentaires francais pour fichiers applicatifs modifies.
- Definition de termine: ACs traces, tests cibles OK, lint cible OK, scans legacy classes, preuve finale complete.
- Halt: besoin d'une nouvelle dependance, schema DB absent, tests cibles irreparables sans elargir le scope.

