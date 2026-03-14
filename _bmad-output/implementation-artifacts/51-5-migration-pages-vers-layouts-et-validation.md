# Story 51.5: Migrer toutes les pages restantes vers les nouveaux layouts et valider la non-régression

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que toutes les pages non encore migrées utilisent le layout approprié,
afin que la hiérarchie de layouts soit complète et qu'aucune page ne gère sa propre mise en page de conteneur.

## Acceptance Criteria

1. Les pages `AstrologersPage`, `AstrologerProfilePage`, `ConsultationsPage`, `ConsultationResultPage`, `BillingPanel`, `PrivacyPanel` utilisent `PageLayout`.
2. `ConsultationsPage` (liste des consultations, pas le wizard) utilise `PageLayout`.
3. `EnterpriseLayout` utilise `TwoColumnLayout` ou `PageLayout` selon sa structure réelle.
4. `NotFoundPage` utilise `AuthLayout` ou un layout centré minimal.
5. Aucune page n'a de déclaration `max-width`, `margin: 0 auto` ou `padding` de conteneur racine qui duplique `PageLayout`.
6. L'ensemble des routes définies dans `routes.tsx` fonctionne correctement — navigation, guards, redirections.
7. Tous les tests Vitest existants passent.
8. Review visuelle complète : toutes les pages, light et dark mode, mobile (375px) et desktop (1024px+).

## Tasks / Subtasks

- [ ] Tâche 1 : Audit des pages restantes (AC: 1, 2, 3, 4)
  - [ ] Lire `AstrologersPage.tsx`, `AstrologerProfilePage.tsx`, `ConsultationsPage.tsx`
  - [ ] Lire `ConsultationResultPage.tsx`, `BillingPanel.tsx`, `PrivacyPanel.tsx`
  - [ ] Lire `EnterpriseLayout.tsx` pour déterminer quel layout lui convient
  - [ ] Lire `NotFoundPage.tsx`
  - [ ] Pour chaque page : identifier wrapper racine actuel et valeur de max-width/padding si présente

- [ ] Tâche 2 : Migrer les pages simples vers `PageLayout` (AC: 1, 2)
  - [ ] `AstrologersPage.tsx` → `<PageLayout>`
  - [ ] `AstrologerProfilePage.tsx` → `<PageLayout>`
  - [ ] `ConsultationsPage.tsx` → `<PageLayout>`
  - [ ] `ConsultationResultPage.tsx` → `<PageLayout>`
  - [ ] `BillingPanel.tsx` → `<PageLayout>` (si applicable) ou conserver son layout propre
  - [ ] `PrivacyPanel.tsx` → `<PageLayout>` (si applicable)

- [ ] Tâche 3 : Migrer `EnterpriseLayout` (AC: 3)
  - [ ] Analyser la structure actuelle de `EnterpriseLayout.tsx`
  - [ ] Utiliser `TwoColumnLayout` si deux colonnes, `PageLayout` sinon

- [ ] Tâche 4 : Migrer `NotFoundPage` (AC: 4)
  - [ ] Page centrée sans navigation — utiliser `AuthLayout` ou un layout centré minimal

- [ ] Tâche 5 : Audit et nettoyage des CSS orphelins (AC: 5)
  - [ ] Grep `max-width` et `margin: 0 auto` dans les pages migrées
  - [ ] Supprimer les déclarations devenues redondantes avec `PageLayout`

- [ ] Tâche 6 : Validation complète (AC: 6, 7, 8)
  - [ ] `npm run test` — tous les tests passent
  - [ ] Naviguer sur chaque route : `/dashboard`, `/dashboard/horoscope`, `/natal`, `/chat`, `/profile`, `/consultations`, `/consultations/new`, `/astrologers`, `/settings/account`, `/admin`, `/enterprise/credentials`
  - [ ] Vérifier light et dark mode
  - [ ] Vérifier mobile 375px et desktop 1024px+

## Dev Notes

### Contexte technique

**Prérequis** : Stories 51.1, 51.2, 51.3, 51.4 doivent être `done`.

### Pages non migrées après 51.1-51.4

Après les stories précédentes, les pages suivantes restent à migrer :
- `AstrologersPage` — liste des astrologues
- `AstrologerProfilePage` — profil d'un astrologue
- `ConsultationsPage` — liste des consultations
- `ConsultationResultPage` — résultat d'une consultation
- `BillingPanel` — facturation
- `PrivacyPanel` — RGPD/vie privée
- `EnterpriseLayout` — layout enterprise (déjà un layout, à évaluer)
- `NotFoundPage` — 404

### Stratégie pour les panels (BillingPanel, PrivacyPanel)

`BillingPanel` et `PrivacyPanel` sont dans `frontend/src/components/` (pas dans `pages/`). Ce sont des composants-pages à part entière. Les lire pour vérifier s'ils gèrent leur propre conteneur. S'ils ont un wrapper `<div className="panel">` ou similaire, le remplacer par `<PageLayout>`.

### EnterpriseLayout — attention

`EnterpriseLayout.tsx` est déjà un layout (pas une page). Il wrape les routes `/enterprise/*`. Il a peut-être déjà une structure deux-colonnes (navigation B2B + contenu). **Ne pas le casser** — évaluer si son refacto avec `TwoColumnLayout` apporte de la valeur ou si le laisser tel quel est plus sage.

### NotFoundPage

Page 404 — elle doit être accessible même sans authentification (erreur de navigation). Utiliser `AuthLayout` (centré, sans navigation) ou créer un layout centré minimal dédié. Ne pas l'afficher dans AppLayout car l'utilisateur peut ne pas être connecté.

### Suppression des CSS orphelins

Après migration de toutes les pages, certaines règles CSS dans `App.css` ou les fichiers CSS de pages peuvent être orphelines. Ne pas supprimer en masse — uniquement les règles clairement dupliquées par `PageLayout`. Préserver les règles incertaines pour une refactorisation CSS ultérieure.

### Commande de vérification finale

```bash
cd frontend
npm run test
npm run build  # vérifier qu'aucune erreur TypeScript
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/pages/AstrologersPage.tsx` |
| Modifier | `frontend/src/pages/AstrologerProfilePage.tsx` |
| Modifier | `frontend/src/pages/ConsultationsPage.tsx` |
| Modifier | `frontend/src/pages/ConsultationResultPage.tsx` |
| Modifier | `frontend/src/components/BillingPanel.tsx` |
| Modifier | `frontend/src/components/PrivacyPanel.tsx` |
| Évaluer | `frontend/src/components/layout/EnterpriseLayout.tsx` |
| Modifier | `frontend/src/pages/NotFoundPage.tsx` |
| Nettoyer | `frontend/src/App.css` (règles orphelines si identifiées) |

### Project Structure Notes

- Imports des layouts : `import { PageLayout } from '../layouts'`
- Si une page est dans `components/` (comme BillingPanel), chemin relatif : `import { PageLayout } from '../layouts'`
- Ne pas déplacer les composants-pages vers `pages/` dans cette story — juste ajouter les layouts

### References

- [Source: frontend/src/pages/AstrologersPage.tsx]
- [Source: frontend/src/pages/ConsultationsPage.tsx]
- [Source: frontend/src/components/BillingPanel.tsx]
- [Source: frontend/src/components/PrivacyPanel.tsx]
- [Source: frontend/src/components/layout/EnterpriseLayout.tsx]
- [Source: frontend/src/pages/NotFoundPage.tsx]
- [Source: frontend/src/layouts/] (stories 51.1-51.4)
- [Source: _bmad-output/planning-artifacts/epic-51-architecture-layouts.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
