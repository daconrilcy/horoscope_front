# PR: FE-7 — Account (RGPD)

Closes #(issue number)

## Description

Implémentation de la fonctionnalité Account (RGPD) permettant aux utilisateurs d'exporter leurs données au format ZIP et de supprimer leur compte avec confirmation double saisie. Cette fonctionnalité respecte les exigences RGPD pour le droit à la portabilité des données et le droit à l'effacement.

## Type de changement

- [x] Nouvelle fonctionnalité (feature)
- [ ] Correction de bug (bugfix)
- [ ] Refactoring
- [ ] Documentation

## Checklist

- [x] J'ai vérifié que mon code suit les conventions du projet
- [x] J'ai auto-reviewé mon code
- [x] Mes commentaires sont utiles et clairs
- [x] J'ai documenté les changements complexes si nécessaire
- [x] Mes tests passent localement
- [x] J'ai mis à jour la documentation si nécessaire

## Résumé des changements

### Nouveaux fichiers

1. `src/shared/api/account.service.ts` - Service account avec export ZIP et delete
2. `src/shared/api/account.service.test.ts` - Tests service (13 tests)
3. `src/features/account/hooks/useExportZip.ts` - Hook export ZIP avec AbortController
4. `src/features/account/hooks/useExportZip.test.tsx` - Tests hook export (9 tests)
5. `src/features/account/hooks/useDeleteAccount.ts` - Hook delete avec logout dur
6. `src/features/account/hooks/useDeleteAccount.test.tsx` - Tests hook delete (8 tests)
7. `src/shared/ui/ConfirmModal.tsx` - Composant modal de confirmation avec double saisie
8. `src/shared/ui/ConfirmModal.test.tsx` - Tests modal (16 tests)
9. `src/pages/app/account/index.tsx` - Page Account avec sections Export et Delete
10. `FE-7-account-rgpd-issue.md` - Issue GitHub
11. `FE-7-account-rgpd-pr.md` - Description PR

### Fichiers modifiés

1. `src/app/router.tsx` - Ajout route `/app/account` lazy + Suspense

## Détails techniques

### AccountService (7.1)

- **exportZip()**: Export ZIP avec Content-Type guard, timeout 60s, support AbortController, filename fallback daté
- **deleteAccount()**: Suppression compte avec gestion erreurs 409 (opérations en cours), 401, 500

### Page Account (7.2)

- **Section Export**: Bouton téléchargement avec état de chargement, gestion erreurs
- **Section Delete**: Bouton suppression avec modal de confirmation double saisie case-sensitive
- **Modal ConfirmModal**: Accessibilité complète (focus trap, aria-*, Escape), validation stricte

### Hooks React Query

- **useExportZip**: Mutation avec AbortController, protection double-clic, gestion erreurs (401, 500, NetworkError)
- **useDeleteAccount**: Mutation avec logout "dur" (purge complète stores + localStorage + React Query cache), gestion 409 spécifique

### Accessibilité (A11y)

- Focus trap dans le modal (Tab/Shift+Tab)
- Attributs aria-* corrects (role="dialog", aria-modal, aria-labelledby, aria-describedby)
- Gestion Escape pour fermer
- Retour du focus à l'élément déclencheur après fermeture
- Validation case-sensitive avec trim()

## Critères d'acceptation

- [x] **Export**: Content-Type vérifié (ZIP/octet-stream), filename issu de fallback daté, URL blob révoquée, bouton désactivé pendant export, abort/timeout gérés
- [x] **Delete**: 204 → logout + purge stores/caches + redirect /, 409 → toast métier (aucune purge/redirect), 401 → flux unauthorized standard
- [x] **Modal**: focus trap, Escape, aria-* corrects, double saisie case-sensitive
- [x] **Qualité**: lint/typecheck OK, tests verts

## Tests

- **AccountService**: 13 tests (succès, erreurs 401/500/409, blob invalide, NetworkError, AbortController)
- **useExportZip**: 9 tests (succès, double-clic, erreurs 401/500/NetworkError, AbortController cleanup)
- **useDeleteAccount**: 8 tests (succès avec purge, double-clic, erreurs 401/409/500/NetworkError, redirection même si purge échoue)
- **ConfirmModal**: 16 tests (ouverture/fermeture, validation case-sensitive, focus trap, Escape, aria-*, Tab navigation)

**Total**: 46 tests

## Notes importantes

- Le ZIP n'est pas streamé dans l'UI (spinner indéterminé pendant le téléchargement)
- La modale applique une confirmation case-sensitive stricte (trim + comparaison exacte)
- Après suppression, toutes les caches/stores sont nettoyées avant la redirection
- Le logout "dur" purge également les stores Zustand (chat, horoscope, paywall) et toutes les clés localStorage du projet
