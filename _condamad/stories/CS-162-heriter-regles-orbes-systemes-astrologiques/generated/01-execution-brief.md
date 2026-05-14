<!-- Brief d'execution CONDAMAD genere pour guider l'implementation de CS-162. -->

# Execution Brief

- Story key: `CS-162-heriter-regles-orbes-systemes-astrologiques`
- Objective: remplacer les copies physiques des regles d'orbes `traditional` dans `hellenistic` et `medieval` par un heritage explicite via `astral_systems.inherits_from_system_id`.
- Boundary: backend referentiels astrologiques, seed, repository, resolver d'orbes, tests backend et docs de recherche citees par la story.
- Non-goals: aucun changement frontend, aucun changement du scoring prediction, aucune nouvelle table d'heritage, aucune copie complete enfant, aucun fallback silencieux vers `modern`.
- Preflight required: `git status --short`, `AGENTS.md`, `00-story.md`, `_condamad/stories/regression-guardrails.md`, fichiers cibles et tests existants.
- Write rules: appliquer le plus petit delta coherent, conserver une seule source canonique, ajouter migration Alembic, adapter le seed sans shim, ajouter des guards anti-cycle et anti-duplication.
- Done: tous les AC ont une preuve code et validation, preuves avant/apres persistantes ecrites, story-status synchronise, revue CONDAMAD propre.
- Halt: divergence enfant non classable, migration incompatible sans correction sure, validation ciblee en echec sans correctif evident.
