# Execution Brief - CS-314

Story `CS-314-capturer-pack-screenshots-profils-natal-cs310` closes the CS-310 residual QA gap by adding a real Chromium screenshot pack for `/natal`.

Scope:

- Use the CS-310 profile set as the source of truth.
- Capture the five synthetic profiles in a browser-rendered `/natal` surface.
- Include mobile captures for `cs310-missing-time-paris` and `cs310-controlled-incomplete`.
- Persist screenshot and anomaly ledgers under the story capsule.
- Run targeted frontend and backend validations from the story.

Non-goals:

- Do not change product behavior unless a blocking reproducible bug is found.
- Do not modify the source brief.
- Do not enrich the shared regression guardrail registry during implementation.
