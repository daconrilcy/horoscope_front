<!-- Synthese executive de l'audit de standardisation App.css. -->

# Executive Summary - frontend-app-css-standardization

## Verdict

Le domaine est `phased-with-map`. La tokenisation precedente est techniquement gardee, mais elle ne repond pas a l'objectif utilisateur: `App.css` reste une accumulation de styles specifiques et non un systeme de classes generiques reutilisables.

## Findings By Severity

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 2 |
| Low | 0 |
| Info | 0 |

## Key Evidence

- `frontend/src/App.css` contient 4146 lignes selon l'analyse Node.
- 442 variables `--app-*`; 439 sont utilisees une seule fois.
- 482 classes uniques; 243 classes contiennent un mot de domaine/page.
- Les tests design-system ciblés passent: 125 tests.
- Le lint frontend passe.

## Story Plan

1. `CS-121` - definir les primitives generiques et le contrat de migration.
2. `CS-122` - migrer layouts, etats et actions.
3. `CS-123` - migrer cartes, listes, badges et modales.
4. `CS-124` - ajouter la garde finale anti-retour.

## Top Risks

- Migration trop large sans baseline visuel.
- Conservation d'anciens noms via alias de classe, ce qui annulerait la standardisation.
- Garde trop permissive qui laisse revenir des noms page-specific tokenises.

