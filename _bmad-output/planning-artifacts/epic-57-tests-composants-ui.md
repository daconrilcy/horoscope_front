# Epic 57: Ajouter les tests unitaires des composants UI primitifs

Status: split-into-stories

## Contexte

Les 65+ tests existants couvrent principalement la logique métier backend et les hooks de données. Les composants UI primitifs créés dans l'Epic 50 (Button, Field, Select, Form, Modal, Card, Skeleton, Badge) ont chacun un fichier de test créé mais les tests sont à écrire.

Des composants UI non testés créent un risque de régression silencieuse lors des refactorisations.

## Objectif Produit

Atteindre une couverture de test complète sur les composants UI primitifs de l'Epic 50 :
- Rendu sans crash de chaque variant/état
- Comportements interactifs (click, input, toggle)
- Accessibilité de base (rôles ARIA, labels)
- Intégration entre composants (FormField utilisant Field et Button)

## Non-objectifs

- Ne pas faire de tests end-to-end (Playwright/Cypress) — uniquement tests unitaires Vitest + Testing Library
- Ne pas tester les pages complètes dans cet epic
- Ne pas viser 100% de couverture de lignes — viser la couverture des comportements utilisateur

## Découpage en stories

- 57.1 Tests Button, Field, Select — composants de saisie
- 57.2 Tests Form/FormField, Modal, Card — composants de structure
- 57.3 Tests Skeleton, EmptyState, Badge/IconBadge — composants d'état et micro-UI

## Références

- [Source: frontend/src/components/ui/]
- [Source: frontend/src/tests/] (patterns de tests existants)
- [Source: frontend/vitest.config.ts]
- [Source: _bmad-output/planning-artifacts/epic-50-bibliotheque-composants-ui-primitifs.md]
