# Story 63.12: Artefact obsolète — remplacé par le découpage email 63.12 à 63.15

Status: obsolete

## Note

Cet artefact fusionnait à tort quatre responsabilités distinctes :

1. l'email J0 transactionnel,
2. l'abstraction provider et la traçabilité,
3. le désabonnement marketing,
4. le scheduler J+1 à J+7.

Le découpage canonique est désormais :

- `63.12` : email de bienvenue J0 transactionnel,
- `63.13` : abstraction provider + `EmailLog`,
- `63.14` : désabonnement marketing tokenisé,
- `63.15` : scheduler et templates J+1 à J+7.

Ne pas implémenter cet artefact.

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
