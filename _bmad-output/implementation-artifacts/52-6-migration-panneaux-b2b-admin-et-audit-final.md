# Story 52.6: Migrer panneaux B2B/Admin vers i18n et audit final zéro texte en dur

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les panneaux B2B et Admin n'aient plus de textes hardcodés et que l'audit final confirme zéro string en dur dans les composants,
afin que le produit soit entièrement internationalisé.

## Acceptance Criteria

1. `i18n/admin.ts` est complété avec les textes manquants des panneaux B2B (`B2BAstrologyPanel`, `B2BBillingPanel`, `B2BEditorialPanel`, `B2BUsagePanel`, `B2BReconciliationPanel`).
2. Chacun des 5 panneaux B2B utilise `useTranslation('admin')` (ou le namespace approprié) pour tous ses textes.
3. Un audit `grep` sur `frontend/src/components/` et `frontend/src/pages/` confirme l'absence de strings en français hardcodées dans le JSX (hors commentaires et noms de variables).
4. Les textes techniques non traduisibles (noms de clés API, formats de dates, valeurs numériques) sont acceptés comme exceptions documentées.
5. Tous les tests existants passent.
6. `npm run build` se termine sans erreurs TypeScript.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire les 5 panneaux B2B et inventorier les textes (AC: 1)
  - [ ] Lire `B2BAstrologyPanel.tsx`, `B2BBillingPanel.tsx`, `B2BEditorialPanel.tsx`, `B2BUsagePanel.tsx`, `B2BReconciliationPanel.tsx`
  - [ ] Lire `i18n/admin.ts` existant pour voir ce qui y est déjà
  - [ ] Lister les textes manquants dans admin.ts

- [ ] Tâche 2 : Compléter `i18n/admin.ts` (AC: 1)
  - [ ] Ajouter une section `b2b` dans `AdminTranslation` avec les textes des panneaux B2B
  - [ ] Traductions FR, EN, ES pour chaque clé
  - [ ] Couvrir : titres, états vides ("Aucun contenu..."), messages d'erreur ("Erreur API B2B: ..."), labels de colonnes

- [ ] Tâche 3 : Migrer les 5 panneaux B2B (AC: 2)
  - [ ] Ajouter `const t = useTranslation('admin')` dans chaque panneau
  - [ ] Remplacer chaque string hardcodée par la clé `t.b2b.*`
  - [ ] Les messages d'erreur dynamiques (`error.message`, `error.code`) restent dynamiques mais leur template string est externalisé

- [ ] Tâche 4 : Audit final (AC: 3, 4)
  - [ ] Grep des patterns de strings en dur dans le JSX :
    ```bash
    # Strings FR entre guillemets dans JSX (approximatif)
    grep -rn '"[A-ZÀ-Ü][a-zà-ü]' frontend/src/components/ frontend/src/pages/ | grep -v ".test." | grep -v "// "
    ```
  - [ ] Pour chaque occurrence trouvée : corriger ou documenter comme exception acceptable
  - [ ] Documenter les exceptions (ex: "API", "JSON", formats techniques)

- [ ] Tâche 5 : Validation finale (AC: 5, 6)
  - [ ] `npm run test` — tous les tests passent
  - [ ] `npm run build` — pas d'erreurs TypeScript
  - [ ] Review visuelle des panneaux B2B en FR et EN

## Dev Notes

### Contexte technique

**Prérequis** : Stories 52.1-52.5 doivent être `done`. Story 52.4 (useTranslation hook) est particulièrement importante pour simplifier cette migration.

### Textes B2B identifiés dans l'analyse codebase

**`B2BAstrologyPanel.tsx`** :
```
"API B2B Astrologie"                          → t.b2b.astrology.title
"Aucun contenu astrologique disponible..."    → t.b2b.astrology.empty
"Erreur API B2B: {msg} ({code})"              → t.b2b.astrology.error (avec interpolation)
```

**`B2BBillingPanel.tsx`** :
```
"Erreur facturation B2B"                      → t.b2b.billing.title
Messages d'erreur formatés                    → t.b2b.billing.error
```

**Autres panneaux B2B** : à identifier à la lecture.

### Gestion des messages d'erreur avec interpolation

Les messages comme `"Erreur API B2B: {error.message} ({error.code})"` nécessitent une interpolation. Deux approches :

**Option A — Template function** :
```typescript
// Dans i18n/admin.ts
b2b: {
  astrology: {
    error: (message: string, code: string | number) =>
      `Erreur API B2B: ${message} (${code})`
  }
}
// EN: error: (msg, code) => `B2B API Error: ${msg} (${code})`
```

**Option B — Template string avec placeholder** :
```typescript
// Dans i18n/admin.ts
b2b: { astrology: { error: "Erreur API B2B: {{message}} ({{code}})" } }
// Et un helper: interpolate(t.b2b.astrology.error, { message: e.message, code: e.code })
```

**Recommandation** : Option A (functions) — plus simple, pas besoin de helper d'interpolation, et TypeScript type-safe.

### Audit final — exceptions acceptables

Certains textes **ne doivent PAS** être dans i18n :
- Noms techniques : "API", "JSON", "HTTP", codes d'erreur HTTP (`"404"`, `"401"`)
- Valeurs de propriétés non-affichées : `className`, `type`, `id`, `name`
- Textes de dev/debug (logs, commentaires)
- Textes générés par le backend (messages LLM, contenus astrologiques dynamiques)

### Structure de `i18n/admin.ts` après complétion

```typescript
// Avant (structure existante approximative)
adminTranslations = {
  page: { fr: { title: "...", backToHub: "..." }, en: {...}, es: {...} },
  sections: { fr: { pricing: "...", monitoring: "..." }, en: {...}, es: {...} }
}

// Après — ajouter b2b
adminTranslations = {
  page: { ... },
  sections: { ... },
  b2b: {
    fr: {
      astrology: { title: "...", empty: "...", error: (msg, code) => `...` },
      billing:   { title: "...", error: (msg) => `...` },
      editorial: { ... },
      usage:     { ... },
      reconciliation: { ... },
    },
    en: { ... },
    es: { ... },
  }
}
```

**Attention** : `admin.ts` utilise peut-être un pattern objet différent de celui des autres fichiers i18n. Lire le fichier en entier avant de le modifier.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Modifier | `frontend/src/i18n/admin.ts` (ajouter section b2b) |
| Modifier | `frontend/src/components/B2BAstrologyPanel.tsx` |
| Modifier | `frontend/src/components/B2BBillingPanel.tsx` |
| Modifier | `frontend/src/components/B2BEditorialPanel.tsx` |
| Modifier | `frontend/src/components/B2BUsagePanel.tsx` |
| Modifier | `frontend/src/components/B2BReconciliationPanel.tsx` |

### Project Structure Notes

- `useTranslation('admin')` est disponible depuis story 52.4 — utiliser ce hook dans les panneaux B2B
- Si le type de retour de `useTranslation('admin')` ne couvre pas la section `b2b`, mettre à jour le type dans `AdminTranslation` et dans le hook

### References

- [Source: frontend/src/components/B2BAstrologyPanel.tsx]
- [Source: frontend/src/components/B2BBillingPanel.tsx]
- [Source: frontend/src/components/B2BEditorialPanel.tsx]
- [Source: frontend/src/components/B2BUsagePanel.tsx]
- [Source: frontend/src/components/B2BReconciliationPanel.tsx]
- [Source: frontend/src/i18n/admin.ts]
- [Source: _bmad-output/planning-artifacts/epic-52-i18n-complet.md]
- [Source: _bmad-output/implementation-artifacts/52-4-hook-usetranslation-centralise.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
