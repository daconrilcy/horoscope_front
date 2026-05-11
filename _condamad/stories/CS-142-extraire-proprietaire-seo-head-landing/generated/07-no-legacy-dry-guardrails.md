# No Legacy / DRY CS-142

- `LandingPage.tsx` n'a plus de mutation brute `document.`.
- `LandingHead.tsx` est l'unique owner SEO/head landing.
- Aucun provider global speculatif ou dependance externe.
- Aucun fallback silencieux ou compatibility wrapper.
