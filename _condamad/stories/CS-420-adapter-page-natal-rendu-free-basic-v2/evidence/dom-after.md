# DOM After - CS-420

Post-implementation rendered DOM evidence is held by:

- `natalInterpretation.test.tsx`: free_short complete payload renders title, summary, section, highlight, advice and disclaimer without regeneration message.
- `natalInterpretation.test.tsx`: Basic V2 renders title, introduction, theme narrative, conclusion, public evidence label/meaning, limitation and disclaimer.
- `natalPublicDomGuard.test.tsx`: public DOM excludes technical markers and Basic V2 evidence does not expose raw ids or scoring fields.
- `browser-login-redirect.png`: local `/natal` route starts and redirects unauthenticated users to login with `returnTo=/natal`.

No public DOM branch renders `.ni-evidence-tags`, `.ni-projections`, legacy factual cards or inline styles.
