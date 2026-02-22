# Story 2.6: Interface utilisateur signin et signout

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want acceder a un formulaire de connexion et a un bouton de deconnexion,
so that je puisse m authentifier et me deconnecter depuis l interface de l application.

## Acceptance Criteria

1. **Given** un utilisateur non authentifie **When** il ouvre l application **Then** une page d accueil est affichee avec les boutons "Se connecter" et "Creer un compte" ; **When** il clique sur "Se connecter" **Then** le formulaire signin est affiche (email + password + bouton Se connecter). *(AC mis a jour 2026-02-21 : flux home→signin introduit par stories 12-x)*
2. Le formulaire valide les champs avec React Hook Form + Zod (email valide, password non vide).
3. Les etats `loading/error/empty` sont geres explicitement : spinner/disabled pendant la requete, message d erreur non technique en cas d identifiants incorrects.
4. En cas de succes, `setAccessToken()` est appele avec le `access_token` retourne, et l interface personnalisee est affichee (la vue natale + navigation).
5. **Given** un utilisateur authentifie **When** il navigue dans l application **Then** un bouton "Se deconnecter" est accessible dans l interface.
6. Le clic sur "Se deconnecter" appelle `clearAccessToken()` et retourne a la page d accueil. *(mis a jour 2026-02-21 : retour sur HomePage, pas directement sur le formulaire)*
7. La navigation clavier est fonctionnelle : tabulation sur tous les champs et boutons, activation Entree/Espace, conformite WCAG 2.1 AA (NFR13, NFR14, NFR15 — contraste 4.5:1 minimum sur texte).

## Tasks / Subtasks

- [x] Installer les dependances React Hook Form + Zod (AC: 2)
  - [x] `npm install react-hook-form @hookform/resolvers zod` dans `frontend/`
  - [x] Verifier que les types TypeScript sont couverts (pas de `@types/*` necessaire : les deux libs sont bundled)
- [x] Creer `frontend/src/api/auth.ts` — fonction `loginApi` (AC: 1, 3, 4)
  - [x] Appeler `POST /v1/auth/login` via `apiFetch` avec `{ email, password }`
  - [x] Parser la reponse `{ data: { tokens: { access_token }, user: { id, role } }, meta }`
  - [x] Lever une erreur typee (`AuthApiError`) avec `code` et `message` en cas d echec (401/400)
- [x] Creer `frontend/src/components/SignInForm.tsx` (AC: 1, 2, 3, 4)
  - [x] Formulaire avec champs `email` (type="email") et `password` (type="password") + bouton "Se connecter"
  - [x] Integration React Hook Form v7 + Zod v4 : schema `{ email: z.string().email(), password: z.string().min(1) }`
  - [x] Etat loading : bouton desactive + indicateur visuel pendant la requete
  - [x] Etat erreur : message non technique (ex: "Identifiants incorrects. Veuillez reessayer.") dans `.chat-error`
  - [x] En cas de succes : appeler `setAccessToken(data.tokens.access_token)`
  - [x] Attributs WCAG : `<label htmlFor>` sur chaque champ, `aria-describedby` sur les erreurs, focus visible
- [x] Modifier `frontend/src/App.tsx` — integrer SignInForm et bouton signout (AC: 5, 6)
  - [x] Remplacer le `<section className="panel"><p>Aucun token detecte...</p></section>` par `<SignInForm />`
  - [x] Ajouter un bouton "Se deconnecter" dans AppShell ou dans la navigation (visible seulement si `accessToken` present)
  - [x] Le clic sur "Se deconnecter" appelle `clearAccessToken()`
- [x] Tests unitaires/integration (AC: 1–7)
  - [x] `frontend/src/tests/SignInForm.test.tsx` : affichage formulaire, erreurs de validation, loading, succes (appel setAccessToken), erreur API
  - [x] Mettre a jour `frontend/src/tests/App.test.tsx` : adapter les tests qui cherchent le texte "Aucun token detecte..." (remplace par le formulaire signin)
- [x] Validation finale
  - [x] `npm run lint` (tsc --noEmit) sans erreur
  - [x] `npm run test` (vitest run) sans regression

## Dev Notes

### Architecture Compliance

- Respecter la separation `api/ → components/ → pages/` — la logique d appel API reste dans `frontend/src/api/auth.ts`, le composant ne fait qu appeler la fonction.
- Pas de logique metier astrologique dans ce composant.
- Le token est stocke dans `localStorage` via `setAccessToken()` / `clearAccessToken()` (pattern etabli dans `utils/authToken.ts`).
- Utiliser `apiFetch` de `frontend/src/api/client.ts` (gestion du timeout a 20s, pas de fetch natif direct).

### Bibliotheques et versions

- **React Hook Form v7** (`react-hook-form@^7.x`) — deja mentionne dans l architecture, mais **NON installe** dans `package.json` actuel → installation obligatoire.
- **Zod v4** (`zod@^4.x`) + **`@hookform/resolvers`** (resolver Zod pour RHF) — memes remarques, a installer.
- **@tanstack/react-query v5** — deja installe. Pour la mutation login, utiliser `useMutation` si souhaite, ou un simple `useState` + appel direct est acceptable pour ce formulaire simple.
- **React 19** — `useActionState` disponible, mais React Hook Form + Zod reste la cible explicite des AC.

> ⚠️ ATTENTION : `react-hook-form`, `@hookform/resolvers` et `zod` ne sont PAS dans `package.json`. Le premier acte du dev est `npm install react-hook-form @hookform/resolvers zod` dans `frontend/`.

### Endpoint backend existant

```
POST /v1/auth/login
Body:  { "email": "user@example.com", "password": "secret" }
→ 200: { "data": { "tokens": { "access_token": "...", "refresh_token": "..." },
                   "user": { "id": 42, "role": "user" } },
         "meta": { "request_id": "..." } }
→ 401: { "error": { "code": "invalid_credentials", "message": "...", ... } }
→ 400: { "error": { "code": "...", "message": "...", ... } }
```

L endpoint est pleinement implementé dans `backend/app/api/v1/routers/auth.py` (ligne 234). Pas de modification backend requise.

### Etat actuel de App.tsx (impact)

`App.tsx` affiche actuellement (lignes 92-95) :
```tsx
{!accessToken ? (
  <section className="panel">
    <p>Aucun token detecte. Connectez-vous pour acceder aux fonctionnalités protegees.</p>
  </section>
) : null}
```
Ce bloc doit etre **remplace** par `<SignInForm />` (conditionnel sur `!accessToken`).

> ⚠️ Le test `App.test.tsx` ligne 42 cherche ce texte exact — ce test devra etre adapte pour chercher le formulaire de connexion a la place.

### Bouton signout

Le bouton "Se deconnecter" doit etre visible et accessible quand `accessToken` est present. Options :
- Option A (recommandee) : l ajouter dans la section Navigation existante de `App.tsx` (section `.panel` contenant les boutons de navigation).
- Option B : l ajouter dans `AppShell.tsx` (actuellement vide, simple `<main>`).

L architecture ne definit pas de layout header/footer — option A est la plus simple et coherente avec le code existant.

### CSS disponibles (sans modification necessaire)

- `.panel` — conteneur standard
- `.chat-form` — formulaire vertical (flex column, gap 0.5rem) — parfait pour le formulaire signin
- `.chat-form input` — style des inputs (deja defini dans `App.css`)
- `.chat-error` — erreur rouge
- `.state-line .state-loading` — indicateur de chargement
- `button:disabled` — opacite 0.6, cursor not-allowed

### Structure fichiers cibles

```
frontend/src/
  api/
    auth.ts          ← NOUVEAU (fonction loginApi)
  components/
    SignInForm.tsx   ← NOUVEAU (composant formulaire)
    AppShell.tsx     ← inchange (ou optionnellement bouton signout si option B)
  App.tsx            ← MODIFIER (remplacer message par SignInForm, ajouter bouton signout)
  tests/
    SignInForm.test.tsx   ← NOUVEAU
    App.test.tsx          ← MODIFIER (adapter les assertions existantes)
```

### Pattern de test existant (reference)

```tsx
// Fichiers de reference : frontend/src/tests/App.test.tsx, BillingPanel.test.tsx
import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, render, screen, fireEvent } from "@testing-library/react"
import { AppProviders } from "../state/providers"

afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear() })

// Mock fetch :
vi.stubGlobal("fetch", vi.fn(async (input) => {
  if (String(input).endsWith("/v1/auth/login")) {
    return { ok: true, status: 200,
      json: async () => ({ data: { tokens: { access_token: "tok.eyJzdWIiOiI0MiIsInJvbGUiOiJ1c2VyIn0.sig" }, user: { id: 42, role: "user" } }, meta: { request_id: "r1" } }) }
  }
  return { ok: false, status: 401, json: async () => ({ error: { code: "invalid_credentials", message: "Identifiants invalides" } }) }
}))
```

### NFR applicables

- **NFR3** : feedback visuel <= 200ms sur envoi du formulaire (bouton disabled immediat).
- **NFR13/NFR14** : WCAG 2.1 AA — navigation clavier complete, labels explicites, messages d erreur accessibles.
- **NFR15** : contraste 4.5:1 pour le texte (les CSS existants respectent deja ce point avec les variables `--text-1`, `--primary`).

### Project Structure Notes

- Alignement avec la structure definie dans l architecture : `frontend/src/api/`, `frontend/src/components/`.
- Aucun conflit detecte avec les fichiers existants — `auth.ts` n existe pas encore dans `api/`.
- `SignInForm.tsx` suit la convention `PascalCase.tsx` etablie.

### References

- Epics/Story source : `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.6, lignes 323-343)
- Architecture : `_bmad-output/planning-artifacts/architecture.md` (Frontend Architecture, Forms/validation, NFR coverage)
- Utilitaires auth : `frontend/src/utils/authToken.ts`
- Client HTTP : `frontend/src/api/client.ts`
- App actuel : `frontend/src/App.tsx`
- Backend endpoint : `backend/app/api/v1/routers/auth.py` (login, lignes 234-283)
- CSS disponibles : `frontend/src/App.css`
- Test pattern : `frontend/src/tests/App.test.tsx`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- create-story workflow execution — 2026-02-21
- dev-story workflow execution — 2026-02-21

### Completion Notes List

- Story purement frontend (aucune modification backend requise pour loginApi).
- react-hook-form@7.71.2, @hookform/resolvers@5.2.2, zod@4.3.6 installes (types bundled, aucun @types/* necessaire).
- SignInForm utilise useState + appel direct loginApi (pas useMutation) — adequat pour ce formulaire simple.
- Bouton signout integre dans la section Navigation de App.tsx (Option A recommandee) : visible uniquement si accessToken present.
- App.test.tsx adapte : les assertions sur "Aucun token detecte..." remplacees par presence/absence du bouton "Se connecter".
- 6 tests unitaires/integration dans SignInForm.test.tsx couvrant : affichage, validation email, validation password, loading, succes (localStorage), erreur API.
- 95 tests / 26 fichiers — zero regression.
- `npm run lint` : zero erreur TypeScript (apres suppression de ViewDefinition.render lors du 2e code review).
- Tous les AC satisfaits. Navigation clavier : labels htmlFor, aria-describedby, aria-invalid, focus natif HTML preserves.
- **[M1 — 2e review]** auth.ts exporte aussi `registerApi` (endpoint /v1/auth/register) — ajoute dans le meme fichier pour les stories 12-x, hors scope initial 2-6. Documente ici pour tracabilite.
- **[M2 — 2e review]** SignInForm.tsx : prop `onRegister?: () => void` et bouton "Creer un compte" ajoutes pour stories 12-x — 3 tests de couverture ajoutes dans SignInForm.test.tsx (apparition conditionnelle, invocation callback).
- **[M3 — 2e review]** 6 fichiers stagues appartenant aux stories 12-x sont dans le meme changeset non-committe : SignUpForm.tsx, birthProfile.ts, BirthProfilePage.tsx, BirthProfilePage.test.tsx, SignUpForm.test.tsx, constants.ts — a committer separement dans leurs stories respectives.

### File List

- frontend/package.json (modifie — ajout react-hook-form, @hookform/resolvers, zod)
- frontend/package-lock.json (modifie)
- frontend/src/api/auth.ts (nouveau — loginApi scope 2-6 ; registerApi ajoutee hors scope pour stories 12-x)
- frontend/src/components/SignInForm.tsx (nouveau — prop onRegister ajoutee pour stories 12-x)
- frontend/src/App.tsx (modifie — flux home/signin/register introduit par stories 12-x ; ViewDefinition.render corrige au 2e review)
- frontend/src/tests/SignInForm.test.tsx (nouveau — +3 tests onRegister ajoutes au 2e review)
- frontend/src/tests/App.test.tsx (modifie — tests flux home/signin/register ajoutes par stories 12-x)
- frontend/src/App.css (modifie — refonte theme sombre : panels, boutons, couleurs)
- frontend/src/index.css (modifie — variables CSS theme sombre)
- frontend/index.html (modifie — lang="fr", titre page)

## Senior Developer Review (AI)

**Reviewer :** Cyril — 2026-02-21
**Résultat :** APPROUVÉ après corrections

### Findings résolus automatiquement

| ID | Sévérité | Description | Fichier | Statut |
|----|----------|-------------|---------|--------|
| H1 | HIGH | AC7 non testée : navigation clavier / aria non vérifiée (aria-invalid, aria-describedby, type=submit) | SignInForm.test.tsx | ✅ Corrigé — 3 tests ajoutés |
| M1 | MEDIUM | auth.ts : response.json() sans try/catch sur réponse d'erreur non-JSON (502, proxy) | auth.ts:24 | ✅ Corrigé — try/catch ajouté |
| M2 | MEDIUM | Test loading : promise non résolue après resolveLogin → risque act() warning | SignInForm.test.tsx:87 | ✅ Corrigé — waitFor ajouté |
| M3 | MEDIUM | File List incomplète : App.css, index.css, index.html modifiés mais non documentés | story File List | ✅ Corrigé — 3 fichiers ajoutés |
| M4 | MEDIUM | Absence de test pour erreur réseau (fetch qui rejette) | SignInForm.test.tsx | ✅ Corrigé — test ajouté |

### Findings laissés en l'état (LOW — acceptés)

- L1 : `<form>` sans aria-labelledby (h2 non lié). role="alert" compense.
- L2 : `apiError` span sans id. role="alert" compense.
- L3 : Duplication `!accessToken` / `!authMe.data` dans useMemo App.tsx.
- L4 : NatalChartPage rendue simultanément avec SignInForm (comportement intentionnel).

### Validation post-corrections (1er review)

- Tests : **100 / 100 passent** (26 fichiers, 0 régression, +5 nouveaux tests)
- Lint TypeScript : **0 erreur**
- Tous les AC satisfaits

---

## Senior Developer Review (AI) — 2e passe

**Reviewer :** Cyril — 2026-02-21
**Résultat :** APPROUVÉ après corrections

### Findings résolus automatiquement

| ID | Sévérité | Description | Fichier | Statut |
|----|----------|-------------|---------|--------|
| H1 | HIGH | `ViewDefinition.render: () => ReactNode` déclaré dans le type mais absent de tous les objets → erreur TypeScript (strict: true) ; champ mort, rendu géré par `renderView()` switch | App.tsx:42 | ✅ Corrigé — champ `render` retiré du type, import `ReactNode` nettoyé |
| H2 | HIGH | AC1 violée : `SignInForm` n'est plus affiché directement à l'ouverture — `HomePage` (flux home→signin) introduite par stories 12-x sans mise à jour de l'AC | story AC1 + AC6 | ✅ Corrigé — AC1 et AC6 mis à jour pour décrire le flux réel |
| M1 | MEDIUM | `auth.ts` exporte `registerApi` hors scope 2-6, non documentée dans File List ni Completion Notes | auth.ts:48-50 | ✅ Corrigé — documenté dans File List et Completion Notes |
| M2 | MEDIUM | `SignInForm.tsx` prop `onRegister` + bouton "Créer un compte" sans aucune couverture de test | SignInForm.test.tsx | ✅ Corrigé — 3 tests ajoutés (apparition, absence, callback) |
| M3 | MEDIUM | 6 fichiers stagés (stories 12-x) dans le même changeset non-committé, non tracés dans story 2-6 | git staging | ✅ Documenté — note dans Completion Notes, commit séparé recommandé |

### Findings laissés en l'état (LOW — acceptés)

- L1 : `apiError` span sans `id` (role="alert" compense). Déjà accepté au 1er review.
- L2 : Tests App.test.tsx pour flux home/signin/register logiquement dans stories 12-x mais dans ce fichier. Acceptable pour la cohérence du fichier de test.

### Validation post-corrections (2e review)

- Tests : **133 / 133 passent** (28 fichiers, 0 régression, +3 nouveaux tests SignInForm onRegister)
- Lint TypeScript : **0 erreur** (`ViewDefinition.render` retiré, `clearErrors` BirthProfilePage nettoyé)
- AC1 et AC6 mis à jour pour refléter le flux réel

## Change Log

- 2026-02-21 : Implementation story 2.6 — ajout formulaire signin (SignInForm.tsx + auth.ts), bouton signout dans navigation, 6 tests unitaires, adaptation App.test.tsx. Lint et suite de tests 100% verts (95 tests).
- 2026-02-21 : Code review adversarial 1 (claude-sonnet-4-6) — 5 findings HIGH/MEDIUM corrigés : robustification auth.ts, 5 tests ajoutés (aria, réseau, erreur non-JSON, loading), File List complété. 100 tests / 0 regression.
- 2026-02-21 : Code review adversarial 2 (claude-sonnet-4-6) — 5 findings corrigés : H1 ViewDefinition.render TypeScript error (App.tsx), H2 AC1+AC6 mis à jour (flux HomePage), M1 registerApi documentée, M2 +3 tests onRegister (SignInForm.test.tsx), M3 fichiers 12-x documentés.
