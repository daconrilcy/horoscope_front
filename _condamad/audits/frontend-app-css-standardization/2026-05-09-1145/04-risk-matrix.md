<!-- Matrice de risques pour la standardisation App.css. -->

# Risk Matrix - frontend-app-css-standardization

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | High | High | High | La centralisation continue d'augmenter `App.css` sans coherence visuelle transversale. | Medium | P1 |
| F-002 | High | High | High | Les memes layouts/etats/actions divergent par petites valeurs locales. | High | P1 |
| F-003 | Medium | High | Medium | Les composants visuels transverses restent non reutilisables. | High | P2 |
| F-004 | Medium | Medium | High | La dette revient sous forme tokenisee mais toujours page-specific. | Medium | P2 |
