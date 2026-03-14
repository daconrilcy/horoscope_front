# Story 51.3: Créer TwoColumnLayout (Chat) et WizardLayout (ConsultationWizard)

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux des layouts spécialisés `TwoColumnLayout` et `WizardLayout` extraits de leurs pages respectives,
afin que la mise en page deux-colonnes du Chat et la progression du Wizard de consultation soient réutilisables et séparées de la logique des pages.

## Acceptance Criteria

1. `frontend/src/layouts/TwoColumnLayout.tsx` existe avec les props `sidebar` (slot ReactNode), `main` (slot ReactNode), `sidebarWidth?`, `collapsibleOnMobile?`.
2. `frontend/src/layouts/WizardLayout.tsx` existe avec les props `steps` (tableau de labels), `currentStep` (index), `children` et `onBack?`.
3. `WizardLayout` affiche une barre de progression visuelle en haut avec les étapes numérotées/labellisées.
4. `ChatPage.tsx` utilise `TwoColumnLayout` pour sa structure deux-colonnes — la logique métier (chargement des conversations, envoi de messages) reste dans ChatPage.
5. `ConsultationWizardPage.tsx` utilise `WizardLayout` pour sa barre de progression — la logique du wizard reste dans ConsultationWizardPage.
6. Le rendu visuel de ChatPage et ConsultationWizardPage est identique avant/après la migration.
7. Les tests existants de ces pages passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire et analyser `ChatPage.tsx` (AC: 1, 4)
  - [ ] Identifier la structure deux-colonnes actuelle (liste conversations + fenêtre chat)
  - [ ] Identifier les classes CSS et styles responsables de la mise en page
  - [ ] Lister les props à extraire vers `TwoColumnLayout`

- [ ] Tâche 2 : Lire et analyser `ConsultationWizardPage.tsx` (AC: 2, 3, 5)
  - [ ] Identifier comment la barre de progression est actuellement rendue
  - [ ] Identifier `WizardProgress` ou composant équivalent existant
  - [ ] Lister les props à extraire vers `WizardLayout`

- [ ] Tâche 3 : Créer `TwoColumnLayout.tsx` (AC: 1)
  - [ ] Interface : `{ sidebar: ReactNode; main: ReactNode; sidebarWidth?: string; collapsibleOnMobile?: boolean; className?: string }`
  - [ ] CSS : grid two-column ou flex, sidebar fixe, main flex-grow
  - [ ] Responsive : sidebar masquée sur mobile si `collapsibleOnMobile`

- [ ] Tâche 4 : Créer `WizardLayout.tsx` (AC: 2, 3)
  - [ ] Interface : `{ steps: string[]; currentStep: number; children: ReactNode; onBack?: () => void; className?: string }`
  - [ ] Barre de progression : steps avec indicateur visuel (cercle numéroté, ligne de connexion)
  - [ ] Bouton retour si `onBack` fourni

- [ ] Tâche 5 : Migrer `ChatPage.tsx` → utiliser `TwoColumnLayout` (AC: 4, 6)
  - [ ] Remplacer le wrapper de mise en page par `<TwoColumnLayout sidebar={...} main={...} />`
  - [ ] Conserver toute la logique React (hooks, state, API calls) dans ChatPage

- [ ] Tâche 6 : Migrer `ConsultationWizardPage.tsx` → utiliser `WizardLayout` (AC: 5, 6)
  - [ ] Remplacer la barre de progression et le wrapper par `<WizardLayout steps={...} currentStep={...}>`
  - [ ] Conserver toute la logique du wizard dans ConsultationWizardPage

- [ ] Tâche 7 : Validation (AC: 6, 7)
  - [ ] Tester Chat sur desktop (deux colonnes) et mobile (une colonne)
  - [ ] Tester ConsultationWizard : navigation entre étapes, barre de progression
  - [ ] `npm run test` — tous les tests passent

## Dev Notes

### Contexte technique

**Prérequis** : Story 51.2 `done` (AppLayout + PageLayout établis).

### TwoColumnLayout — structure cible

```tsx
interface TwoColumnLayoutProps {
  sidebar: React.ReactNode
  main: React.ReactNode
  sidebarWidth?: string         // défaut: "320px"
  collapsibleOnMobile?: boolean // défaut: true
  className?: string
}

export function TwoColumnLayout({ sidebar, main, sidebarWidth = '320px', collapsibleOnMobile = true, className }: TwoColumnLayoutProps) {
  return (
    <div className={`two-col-layout ${className ?? ''}`} style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}>
      <div className={`two-col-layout__sidebar ${collapsibleOnMobile ? 'two-col-layout__sidebar--collapsible' : ''}`}>
        {sidebar}
      </div>
      <div className="two-col-layout__main">
        {main}
      </div>
    </div>
  )
}
```

### CSS TwoColumnLayout

```css
.two-col-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width, 320px) 1fr;
  height: 100%;
  overflow: hidden;
}

@media (max-width: 768px) {
  .two-col-layout__sidebar--collapsible {
    display: none;
  }
  .two-col-layout {
    grid-template-columns: 1fr;
  }
}
```

### WizardLayout — barre de progression

```tsx
export function WizardLayout({ steps, currentStep, children, onBack }: WizardLayoutProps) {
  return (
    <div className="wizard-layout">
      <div className="wizard-layout__progress" role="progressbar" aria-valuemin={0} aria-valuemax={steps.length - 1} aria-valuenow={currentStep}>
        {steps.map((label, i) => (
          <div key={i} className={`wizard-step ${i < currentStep ? 'wizard-step--done' : ''} ${i === currentStep ? 'wizard-step--active' : ''}`}>
            <div className="wizard-step__indicator">{i < currentStep ? '✓' : i + 1}</div>
            <span className="wizard-step__label">{label}</span>
            {i < steps.length - 1 && <div className="wizard-step__connector" />}
          </div>
        ))}
      </div>
      {onBack && (
        <button type="button" className="wizard-layout__back" onClick={onBack}>
          ← Retour
        </button>
      )}
      <div className="wizard-layout__content">
        {children}
      </div>
    </div>
  )
}
```

### Attention — ConsultationLayout dans features/consultations

`routes.tsx` montre que les routes de consultation utilisent `ConsultationLayout` de `features/consultations/` comme parent, et `ConsultationWizardPage` comme enfant. Vérifier si `ConsultationLayout` gère déjà une partie du layout avant de modifier `ConsultationWizardPage`.

### `WizardProgress` existant

Dans `features/consultations/components/`, il peut exister un composant `WizardProgress` ou similaire. Le lire avant d'implémenter `WizardLayout` pour éviter la duplication — potentiellement l'intégrer dans `WizardLayout` au lieu de le recréer.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/layouts/TwoColumnLayout.tsx` |
| Créer | `frontend/src/layouts/TwoColumnLayout.css` |
| Créer | `frontend/src/layouts/WizardLayout.tsx` |
| Créer | `frontend/src/layouts/WizardLayout.css` |
| Modifier | `frontend/src/layouts/index.ts` |
| Modifier | `frontend/src/pages/ChatPage.tsx` |
| Modifier | `frontend/src/pages/ConsultationWizardPage.tsx` |

### Project Structure Notes

- Ne pas modifier `features/consultations/` dans cette story — uniquement `ConsultationWizardPage.tsx`
- Le CSS de chat actuellement dans `App.css` (`.chat-form`, `.chat-layout` etc.) reste — le supprimer seulement si `TwoColumnLayout.css` les remplace entièrement

### References

- [Source: frontend/src/pages/ChatPage.tsx]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/features/consultations/components/]
- [Source: frontend/src/app/routes.tsx] (ConsultationLayout)
- [Source: frontend/src/App.css]
- [Source: _bmad-output/planning-artifacts/epic-51-architecture-layouts.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
