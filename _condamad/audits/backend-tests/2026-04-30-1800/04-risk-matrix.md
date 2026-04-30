# Risk Matrix - backend-tests

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|

## Residual Risk Notes

Aucun finding actif n'est reference dans la matrice. Le risque residuel est couvert par les guards existants:

- `RG-010`: topologie pytest backend.
- `RG-011`: harnais DB des tests backend.
- `RG-012`: classification des anciens guards story-numbered.
- `RG-013`: imports entre modules executables de tests.
- `RG-014`: tests no-op.
- `RG-015`: ownership docs/scripts/secrets/security/ops.
- `RG-016`: tests de narration LLM sans dependance nominale a `LLMNarrator`.
