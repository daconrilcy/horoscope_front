# Epic 54: Configurer les path aliases Vite/TS et les barrel exports par domaine

Status: split-into-stories

## Contexte

Les imports dans le codebase utilisent des chemins relatifs profonds :
```typescript
import { Button } from '../../components/ui/Button/Button'
import { authTranslations } from '../../../i18n/auth'
import { loginApi } from '../../api/auth'
```

Ces chemins longs sont fragiles (cassent au moindre déplacement de fichier), difficiles à lire et à maintenir.

## Objectif Produit

Configurer des path aliases Vite + TypeScript et des barrel exports de domaine pour simplifier tous les imports du projet en :
```typescript
import { Button } from '@ui'
import { authTranslations } from '@i18n'
import { loginApi } from '@api'
```

## Non-objectifs

- Ne pas changer la structure de dossiers
- Ne pas migrer les imports déjà courts (même dossier, fichiers adjacents)

## Découpage en stories

- 54.1 Configurer les path aliases dans `vite.config.ts` et `tsconfig.json`
- 54.2 Créer les barrel exports par domaine et migrer les imports du codebase

## Références

- [Source: frontend/vite.config.ts]
- [Source: frontend/tsconfig.json]
- [Source: frontend/src/components/ui/index.ts]
- [Source: frontend/src/i18n/index.ts]
