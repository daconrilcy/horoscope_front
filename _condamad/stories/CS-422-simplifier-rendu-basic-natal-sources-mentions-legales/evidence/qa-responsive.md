# Responsive QA evidence - CS-422

<!-- Commentaire global: ce fichier documente la verification responsive disponible pour la passe finale CS-422. -->

Date: 2026-06-01

## Status

- Desktop browser QA on authenticated `/natal`: NOT_RUN in this alignment pass.
- Mobile browser QA on authenticated `/natal`: NOT_RUN in this alignment pass.
- Local frontend startup: PASS, Vite responded on `http://127.0.0.1:5173/`; process stopped.

## Compensating evidence

- Rendered DOM tests cover Basic V2 source deduplication, legal deduplication and absence of inline theme evidence.
- CSS changes use existing `ni-*` classes and variables; inline style scan is clean.
- Build and lint pass.

## Residual risk

- Low residual visual risk remains until authenticated desktop and mobile `/natal` are manually inspected with real Basic V2 data.
