# Execution Brief

## Story

- Story key: `CS-013-propager-ids-correlation-narration-horoscope`
- Source: `_condamad/stories/CS-013-propager-ids-correlation-narration-horoscope/00-story.md`
- Objective: propager les `request_id` et `trace_id` canoniques du chemin API/service vers la narration horoscope daily, sans generation locale dans la projection publique.

## Boundaries

- In scope: API publique prediction, service prediction, projection publique, narration horoscope daily, tests backend cibles et preuves CONDAMAD.
- Out of scope: refonte observability, changement du payload public, nouveau systeme de tracing, frontend.

## Preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Preserver les changements preexistants.
- Confirmer le standard request id existant avant de coder.

## Write Rules

- Petit delta coherent.
- Aucune nouvelle dependance.
- Aucun fallback silencieux `uuid.uuid4()` dans `public_projection.py`.
- Aucun retour de `LLMNarrator`.
- Tout code Python execute uniquement apres activation de `.\.venv\Scripts\Activate.ps1`.

## Done Conditions

- Tous les AC ont des preuves code et validation.
- La garde anti-retour est executable.
- Les artefacts `correlation-before.md`, `correlation-source.md`, `correlation-after.md` sont presents.
- `_condamad/stories/story-status.md` est synchronise sur `ready-to-review`.

## Halt Conditions

- Aucun standard request id ne peut etre identifie.
- Les AC imposent un changement public de payload.
- Une validation obligatoire echoue et la cause n'est pas corrigeable dans le scope.
