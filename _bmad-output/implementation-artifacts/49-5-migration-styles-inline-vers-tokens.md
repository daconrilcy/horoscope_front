# Story 49.5: Migrer les styles inline et valeurs magiques vers les tokens CSS

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que tous les objets `style={}` inline et les valeurs hardcodées dans les composants React soient remplacés par des classes CSS ou des variables issues des design tokens,
afin qu'aucune valeur de style ne soit isolée dans un composant JSX et que les modifications visuelles se fassent uniquement dans les fichiers CSS.

## Acceptance Criteria

1. `DayPredictionCard.tsx` ne contient plus aucun objet `style={}` avec des valeurs magiques — chaque style est remplacé par une classe CSS ou une variable token.
2. `DashboardHoroscopeSummaryCard.tsx` ne contient plus la logique `theme === 'dark' ? 'white' : undefined` pour les couleurs — la variable `--color-text-adaptive` gère cela.
3. Les anciennes variables CSS dupliquées entre `index.css` et `theme.css` (ex: `--text-1` défini deux fois) sont nettoyées — une seule source de vérité reste, soit dans `design-tokens.css`, soit dans `theme.css` comme alias.
4. Aucun composant TSX n'utilise de valeur de couleur, d'espacement, de rayon ou d'ombre en dur dans un style inline (ex: `style={{ color: 'rgba(255,255,255,0.7)' }}` est interdit).
5. Les tests Vitest existants passent sans modification.
6. Le rendu visuel de toutes les pages est pixel-perfect identique avant et après la migration.

## Tasks / Subtasks

- [ ] Tâche 1 : Migrer `DayPredictionCard.tsx` (AC: 1)
  - [ ] Lire le fichier entier et lister tous les objets `style={}` (environ 20+)
  - [ ] Pour chaque style inline, créer la classe CSS correspondante dans un nouveau fichier `DayPredictionCard.css` ou dans le CSS existant de la prédiction
  - [ ] Remplacer chaque `style={}` par `className`
  - [ ] Les couleurs dynamiques (ex: `textColor` calculé selon `isAstro && theme`) → utiliser `--color-text-adaptive` ou variables CSS sur le conteneur

- [ ] Tâche 2 : Migrer `DashboardHoroscopeSummaryCard.tsx` (AC: 2)
  - [ ] Supprimer `style={{ color: theme === 'dark' ? 'white' : undefined }}`
  - [ ] Supprimer `style={{ width: "80%", marginBottom: "0.5rem" }}` → classes utilitaires
  - [ ] S'appuyer sur `--color-text-adaptive` défini dans `design-tokens.css` (story 49.3)

- [ ] Tâche 3 : Audit et nettoyage des autres composants avec styles inline (AC: 4)
  - [ ] Grep `style={{` dans `frontend/src/components/` et `frontend/src/pages/`
  - [ ] Pour chaque occurrence : évaluer si la valeur est dynamique (donnée, état) ou statique (style pur)
  - [ ] Migrer les styles statiques vers CSS
  - [ ] Conserver uniquement les styles **vraiment dynamiques** (ex: `style={{ width: `${progress}%` }}`)

- [ ] Tâche 4 : Nettoyage des variables dupliquées (AC: 3)
  - [ ] Vérifier que chaque variable CSS n'est déclarée qu'une seule fois comme valeur réelle (les alias sont autorisés)
  - [ ] Supprimer les déclarations dupliquées dans `index.css` et `theme.css` devenues redondantes avec `design-tokens.css`

- [ ] Tâche 5 : Validation finale (AC: 5, 6)
  - [ ] Exécuter `npm run test` dans `frontend/` — tous les tests passent
  - [ ] Review visuelle complète : Dashboard, Daily Horoscope, Settings, Chat, Consultations
  - [ ] Tester light et dark mode
  - [ ] Tester mobile et desktop

## Dev Notes

### Contexte technique

**Prérequis** : Stories 49.1, 49.2, 49.3 et 49.4 doivent être `done`.

**Cette story est la dernière de l'Epic 49** et finalise la migration. C'est aussi un prérequis pour les Epics 50+ (composants UI primitifs) qui utiliseront les tokens.

### Inventaire des styles inline à migrer

#### `DayPredictionCard.tsx` — styles inline prioritaires

```tsx
// Ligne ~49
style={{ marginTop: '1.5rem' }}
→ className="mt-6"  (classe utilitaire de 49.3)

// Ligne ~50
style={{ fontSize: "1.125rem", lineHeight: "1.6", color: textColor }}
→ className="text-adaptive" + CSS class pour font/lineheight

// Lignes ~56-68 : calibration note box (8 propriétés inline)
style={{
  background: 'rgba(255,255,255,0.08)',
  border: '1px solid rgba(255,255,255,0.15)',
  borderRadius: '12px',
  padding: '12px 16px',
  marginTop: '1rem',
  fontSize: '0.85rem',
  color: textMuted,
  lineHeight: '1.5'
}}
→ Créer la classe `.prediction-note` dans DayPredictionCard.css

// Lignes ~71-77 : best window box (5 propriétés inline)
→ Créer la classe `.prediction-best-window`

// Variables dynamiques à conserver (vraiment basées sur données)
const textColor = ... // → remplacer par --color-text-adaptive
const textMuted = ... // → remplacer par var(--color-text-secondary) ou --color-text-adaptive-muted
```

#### `DashboardHoroscopeSummaryCard.tsx` — styles inline

```tsx
// Skeleton loaders
style={{ width: "80%", marginBottom: "0.5rem" }}
style={{ width: "60%" }}
→ Créer des classes `.skeleton`, `.skeleton--wide`, `.skeleton--narrow`
  (ou utiliser le composant Skeleton de l'Epic 50)

// Couleur texte conditionnelle
style={{ color: theme === 'dark' ? 'white' : undefined }}
→ Supprimer complètement, laisser --color-text-adaptive faire le travail
```

### Règle pour distinguer styles dynamiques vs statiques

**Conserver en `style={}`** uniquement si la valeur est calculée à partir de données ou d'un état :
```tsx
// OK — valeur issue de données
style={{ width: `${progress}%` }}
style={{ background: badgeColor }}  // couleur vient d'une prop
style={{ transform: `rotate(${angle}deg)` }}
```

**Migrer vers CSS** si la valeur est une constante hardcodée :
```tsx
// À migrer
style={{ marginTop: '1.5rem' }}     // constante
style={{ fontSize: "1.125rem" }}    // constante
style={{ color: 'rgba(...)' }}      // constante de couleur
```

### Fichiers probablement impactés par le grep `style={{`

D'après l'analyse du codebase :
- `frontend/src/components/prediction/DayPredictionCard.tsx` — 20+ occurrences (priorité maximale)
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx` — 4 occurrences
- Possibles occurrences dans les pages admin et settings (à vérifier)

### Nouveaux fichiers CSS à créer si nécessaire

Si un composant TSX possède des styles inline mais pas de fichier CSS associé, créer le fichier CSS :
- `frontend/src/components/prediction/DayPredictionCard.css` (si non existant)
- Importer via `import './DayPredictionCard.css'` en haut du TSX

### Commande de vérification finale

```bash
# Dans frontend/ — doit retourner 0 lignes de styles inline statiques
grep -rn 'style={{ [a-z]' src/components/ src/pages/ | grep -v "// OK"
# Et run tests
npm run test
```

### Project Structure Notes

- Les nouveaux fichiers CSS de composants (ex: `DayPredictionCard.css`) vont à côté du TSX dans `frontend/src/components/prediction/`
- Ne pas créer de fichier CSS global pour les styles de prédiction — rester local au composant
- Les classes utilitaires `.mt-6`, `.text-adaptive` etc. sont disponibles grâce aux stories 49.2 et 49.3

### References

- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/styles/design-tokens.css]
- [Source: frontend/src/styles/utilities.css]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]
- [Source: _bmad-output/implementation-artifacts/49-3-classes-css-utilitaires-partagees.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
