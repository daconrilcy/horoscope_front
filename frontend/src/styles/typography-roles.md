<!-- Registre des roles typographiques semantiques frontend. -->

# Typography Roles

Les roles ci-dessous sont la voie canonique pour les repetitions de
typographie dans les surfaces migrees. Les tokens `--type-*` vivent dans
`frontend/src/styles/design-tokens.css`; les classes utilitaires vivent dans
`frontend/src/styles/utilities.css`.

| Role | Class | Tokens | Usage |
|---|---|---|---|
| page-title | `.type-page-title` | `--type-page-title-*` | titres de page applicatifs |
| section-title | `.type-section-title` | `--type-section-title-*` | titres de section |
| card-title | `.type-card-title` | `--type-card-title-*` | titres dans cards et panneaux |
| body | `.type-body` | `--type-body-*` | texte principal |
| body-muted | `.type-body-muted` | `--type-body-muted-*` | texte secondaire |
| metadata | `.type-metadata` | `--type-metadata-*` | metadonnees compactes |
| label | `.type-label` | `--type-label-*` | labels et libelles de formulaire |
| eyebrow | `.type-eyebrow` | `--type-eyebrow-*` | micro-titres en capitales |
| ui-group-label | n/a | `--type-ui-group-letter-spacing` | libelles de groupes compacts dans les primitives UI |
| ui-role-label | n/a | `--type-ui-role-letter-spacing` | roles utilisateur compacts dans les primitives UI |
| cta | `.type-cta` | `--type-cta-*` | texte de boutons et liens d'action |
| numeric | `.type-numeric` | `--type-numeric-*` | chiffres, scores, compteurs |
| admin-compact | n/a | `--type-admin-compact-*` | metadonnees techniques tres compactes dans les tableaux admin |
| admin-control | n/a | `--type-admin-control-*` | controles et infobulles denses du cluster admin |
| landing-marketing | n/a | `--landing-type-*` | echelle marketing landing declaree par `frontend/src/layouts/LandingLayout.css` et consommee par `frontend/src/pages/landing/**` |
| residual-css-token-cluster | n/a | `--font-*`, `--line-height-*`, `--letter-spacing-*` | cluster residuel frontend design-system migre sans literals typographiques locaux |
