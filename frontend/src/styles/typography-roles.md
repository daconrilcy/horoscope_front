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
| cta | `.type-cta` | `--type-cta-*` | texte de boutons et liens d'action |
| numeric | `.type-numeric` | `--type-numeric-*` | chiffres, scores, compteurs |

## Exceptions classees

| File | Literal | Reason | Exit condition |
|---|---|---|---|
| `frontend/src/layouts/LandingLayout.css` | landing-scale typography | echelle marketing expressive | decision UX dediee |
| `frontend/src/pages/landing/**` | landing-scale typography | pages marketing hors lot | decision UX dediee |
| `frontend/src/pages/AstrologerProfilePage.css` | profile editorial sizes | surface expressive volumineuse | migration par story dediee |
