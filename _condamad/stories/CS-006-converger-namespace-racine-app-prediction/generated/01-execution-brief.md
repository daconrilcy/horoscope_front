# Execution Brief - CS-006

## Story key

`CS-006-converger-namespace-racine-app-prediction`

## Objectif

Converger un premier lot du namespace racine `app.prediction` vers un owner canonique existant, sans facade de compatibilite, et prouver que la croissance du namespace est bloquee.

## Bornes d'implementation

- Traiter uniquement la story CS-006.
- Produire les artefacts persistants de cartographie, baseline avant/apres et evidence finale.
- Migrer le lot `engine_orchestrator.py` vers `app.services.prediction`, car il porte l'orchestration applicative.
- Mettre a jour les consommateurs internes vers le chemin canonique.
- Ne pas changer le comportement fonctionnel du moteur.

## Non-goals

- Ne pas migrer tout le moteur pur vers `app.domain.prediction`.
- Ne pas modifier les invariants LLM `RG-016`, `RG-017`, `RG-018`, `RG-019`.
- Ne pas recreer `app.prediction.llm_narrator`.
- Ne pas ajouter de shim, alias ou re-export depuis `app.prediction`.

## Preflight requis

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Lire les tests et consommateurs de `EngineOrchestrator`.

## Done conditions

- AC1 a AC5 ont evidence code et validation.
- Les imports actifs de `app.prediction.engine_orchestrator` sont supprimes.
- La garde AST bloque l'ancien fichier et les nouveaux fichiers non cartographies.
- Les commandes du plan de validation sont executees avec `.venv` active ou justifiees.
