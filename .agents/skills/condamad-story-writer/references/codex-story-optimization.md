# Codex Story Optimization

<!-- Regles d'ecriture pour rendre une story exploitable par Codex. -->

## Write For Execution

Codex performs best when the story is structured around visible constraints and
evidence instead of long prose.

Use:

- short headings;
- tables for ACs;
- concrete file paths;
- explicit commands;
- clear forbidden paths;
- small task groups mapped to ACs.

Avoid:

- decorative narrative;
- implied scope;
- unstated dependencies;
- broad cleanup;
- multiple equivalent routes to completion.

## Token Discipline

Keep the story shorter than a framework planning document but stricter than a
normal ticket. Every paragraph should answer one of these questions:

- what must change;
- where it must change;
- what must not change;
- how completion is proven;
- what risk remains.

## Agent Guardrails

The story should make bad implementation routes visibly invalid. Place the
guardrails near the ACs and validation plan, not only in background notes.

