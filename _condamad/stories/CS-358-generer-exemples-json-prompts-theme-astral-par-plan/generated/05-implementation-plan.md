# Implementation Plan - CS-358

1. Keep the change limited to `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/` plus CONDAMAD evidence.
2. Use backend runtime and documentation as shape sources, but do not call a provider or alter runtime files.
3. Create one shared `intermediate-data.json` for normalized birth input, assumptions, prompt signals, plan differences, and limits.
4. Create three final provider-handoff payload files with ordered structured-mode messages and plan-visible differences.
5. Validate JSON shape, prompt/audit boundaries, no-provider-call behavior, backend prompt-boundary tests, and unchanged runtime/frontend status.
