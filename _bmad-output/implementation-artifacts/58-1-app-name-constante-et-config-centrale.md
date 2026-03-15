# Story 58.1 : Constante APP_NAME et configuration centrale de l'application

Status: in-progress

## Story

En tant que développeur,
je veux disposer d'une constante centrale `APP_NAME = "Astrorizon"` et d'un accès normalisé au logo de l'application,
afin que toutes les stories suivantes de l'Epic 58 (et les composants futurs) puissent les importer depuis un unique point de vérité, permettant un changement global instantané.

## Acceptance Criteria

1. `APP_NAME = "Astrorizon"` est défini dans `frontend/src/utils/constants.ts` et peut être importé via l'alias `@utils/constants`.
2. Le fichier logo `docs/interfaces/logo_horoscope02.png` est copié dans `frontend/src/assets/logo.png` afin d'être importable comme module Vite.
3. Un fichier `frontend/src/utils/appConfig.ts` exporte `APP_NAME` (importé depuis constants) et `APP_LOGO` (chemin vers l'asset logo) comme point d'entrée unique pour la configuration de l'app.
4. La valeur `t.header.appTitle` dans `frontend/src/i18n/common.ts` est mise à jour pour retourner `APP_NAME` pour les 3 langues (`fr`, `en`, `es`), remplaçant les valeurs en dur `"Horoscope"` / `"Horóscopo"`.
5. Le Header existant (`frontend/src/components/layout/Header.tsx`) continue d'afficher le titre de l'app via `t.header.appTitle` sans régression — aucune modification de la logique de rendu dans cette story.
6. `tsc --noEmit` passe sans erreur.
7. Les tests Vitest existants (≥ 1052) passent tous sans régression.

## Tasks / Subtasks

- [x] T1 — Ajouter `APP_NAME` dans `constants.ts` (AC: 1)
  - [x] T1.1 Ajouter `export const APP_NAME = "Astrorizon"` avec commentaire JSDoc expliquant le rôle de cette constante
  - [x] T1.2 Vérifier que rien d'autre dans le codebase ne définit un app name (grep pour "Horoscope", "appTitle", "Astrorizon")

- [x] T2 — Copier le logo et l'exposer (AC: 2, 3)
  - [x] T2.1 Copier `docs/interfaces/logo_horoscope02.png` vers `frontend/src/assets/logo.png`
  - [x] T2.2 Créer `frontend/src/utils/appConfig.ts` :
    ```ts
    import appLogoSrc from "../assets/logo.png"
    export { APP_NAME } from "./constants"
    export const APP_LOGO: string = appLogoSrc
    ```
  - [x] T2.3 Vérifier que Vite importe correctement le PNG (pas d'erreur de build)

- [x] T3 — Mettre à jour `i18n/common.ts` (AC: 4, 5)
  - [x] T3.1 Importer `APP_NAME` depuis `@utils/constants` dans `common.ts`
  - [x] T3.2 Remplacer les 3 occurrences de `appTitle` (`"Horoscope"`, `"Horoscope"`, `"Horóscopo"`) par `APP_NAME`
  - [x] T3.3 Vérifier que `Header.tsx` qui utilise `t.header.appTitle` affiche toujours "Astrorizon"

- [ ] T4 — Vérification (AC: 6, 7)
  - [ ] T4.1 `tsc --noEmit` sans erreur
  - [x] T4.2 `npx vitest run` — 1052+ tests passent

## Dev Notes

### Contraintes critiques du projet

- **Pas de Tailwind** : Ce projet utilise un système de CSS variables custom (`--color-*`, `--space-*`, `--radius-*`). Ne jamais écrire de classes Tailwind.
- **`verbatimModuleSyntax: true`** dans `tsconfig.json` : Toute importation de type doit utiliser `import type X` ou `import { type X }`. Exemple incorrect : `import { APP_NAME } from "./constants"` quand `APP_NAME` est une valeur (ici c'est une valeur, donc OK sans `type`). Pour les interfaces : `import type { ErrorWithRequestId } from "./constants"`.
- **Path aliases** : `@utils` → `frontend/src/utils/`, `@components` → `frontend/src/components/`, `@ui` → `frontend/src/components/ui/`.
- **Langues i18n** : `AstrologyLang = "fr" | "en" | "es"` (type défini dans `frontend/src/i18n/astrology.ts`).

### État actuel du code à modifier

**`frontend/src/utils/constants.ts`** — contient actuellement :
- `GENERATION_TIMEOUT_LABEL = "60s"`
- `ANONYMOUS_SUBJECT = "anonymous"`
- `formatBirthPlace(city, country)` — formatter string
- `ErrorWithRequestId` interface
- `logSupportRequestId()` — log helper
→ **Ajouter `APP_NAME` en tête de fichier avec JSDoc.**

**`frontend/src/i18n/common.ts`** — contient `appTitle: "Horoscope"` (fr), `appTitle: "Horoscope"` (en), `appTitle: "Horóscopo"` (es).
→ **Remplacer par `APP_NAME`** importé de `@utils/constants`.
→ Attention : `common.ts` utilise déjà `import type { AstrologyLang } from "./astrology"` — respecter ce pattern.

**`frontend/src/components/layout/Header.tsx`** — utilise `t.header.appTitle` pour l'affichage.
→ **Aucun changement requis dans cette story** — la valeur sera automatiquement correcte via i18n.

### Assets Vite

Les assets dans `frontend/src/assets/` sont importables comme modules ES :
```ts
import logoSrc from "../assets/logo.png"
// logoSrc est une string URL résolue par Vite
```
Les assets dans `frontend/public/` sont servis statiquement et référencés par `/nom-du-fichier`.
→ **Choix retenu : `frontend/src/assets/logo.png`** (importable en module, bundlé par Vite, hashé en prod).

### appConfig.ts — point d'entrée unique

Le fichier `appConfig.ts` est la source de vérité pour la configuration de l'app (nom, logo). Les stories suivantes (58.2+) importeront depuis `@utils/appConfig`.

```ts
// frontend/src/utils/appConfig.ts
import appLogoSrc from "../assets/logo.png"
export { APP_NAME } from "./constants"
export const APP_LOGO: string = appLogoSrc
```

Note : `"../assets/logo.png"` fonctionne depuis `utils/appConfig.ts` car `src/utils/` → `src/assets/` = `../assets/`.

### Déclaration de type pour les imports PNG (si nécessaire)

Si TypeScript retourne une erreur `Cannot find module '*.png'`, vérifier si un fichier `frontend/src/vite-env.d.ts` ou `frontend/src/env.d.ts` contient déjà :
```ts
/// <reference types="vite/client" />
```
Cela suffit pour que Vite gère les imports d'assets. Si absent, ajouter cette référence.

### Project Structure Notes

- L'alias `@utils` est défini dans `frontend/vite.config.ts` et `frontend/tsconfig.json` (mappage `@utils/*` → `src/utils/*`).
- `appConfig.ts` doit être dans `frontend/src/utils/` pour bénéficier de l'alias `@utils/appConfig`.
- Ne pas ajouter `appConfig.ts` au barrel `@ui` — c'est une config utilitaire, pas un composant UI.

### References

- Epic 58 planning : `_bmad-output/planning-artifacts/epic-58-global-app-shell-topbar-sidebar-user-menu.md`
- `constants.ts` actuel : `frontend/src/utils/constants.ts`
- `common.ts` actuel : `frontend/src/i18n/common.ts`
- `Header.tsx` actuel : `frontend/src/components/layout/Header.tsx`
- Assets zodiac existants : `frontend/src/assets/zodiac/` (pattern de référence pour les assets)
- Logo source : `docs/interfaces/logo_horoscope02.png`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `rg -n "Horoscope|Horóscopo|Astrorizon|appTitle" frontend/src`
- `npx vite build`
- `npm run lint`
- `npm test`

### Completion Notes List

- Centralisation du nom applicatif via `APP_NAME` dans `constants.ts` et `appConfig.ts`.
- Synchronisation de `common.ts` sur `APP_NAME` pour les trois langues sans changer la logique de rendu du header.
- Mise à jour des tests de rendu du header pour refléter le nouveau titre `Astrorizon`.
- Import Vite du logo validé par `npx vite build`.
- Validation incomplète : `npm run lint` échoue sur un passif TypeScript hors scope de la story ; `npm test` est vert à 1052 tests.

### File List

- `frontend/src/utils/constants.ts` (modifié — ajout APP_NAME)
- `frontend/src/assets/logo.png` (créé — copie du logo)
- `frontend/src/utils/appConfig.ts` (créé — config centrale)
- `frontend/src/i18n/common.ts` (modifié — appTitle → APP_NAME)
- `frontend/src/tests/layout/Header.test.tsx` (modifié — assertions alignées sur `Astrorizon`)
- `frontend/src/tests/App.test.tsx` (modifié — assertion de redirection dashboard stabilisée)
- `frontend/src/tests/DailyHoroscopePage.test.tsx` (modifié — conservation de l’assertion sur le titre métier de la page)
- `frontend/src/tests/router.test.tsx` (modifié — assertions adaptées entre shell et titre métier dashboard)

### Change Log

- 2026-03-15 : Implémentation de la story 58.1, centralisation `APP_NAME`/logo, synchronisation i18n et mise à jour des tests associés.
- 2026-03-15 : Revue de code du delta 58.1, aucune régression fonctionnelle trouvée ; validation Vite ajoutée et assertions de tests ajustées.
