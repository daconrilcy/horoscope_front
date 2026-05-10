# Story CS-137 converger-dark-mode-surfaces-frontend: Converger le dark mode des surfaces frontend auditees

Status: ready-to-review

## 1. Objective

Corriger les surfaces frontend qui restent visuellement incoherentes en `html.dark`
sur les routes auditees. Le dark mode doit conserver les contrastes lisibles, ne
pas afficher de grandes surfaces light non classees, et ne pas laisser de liens
bleu navigateur par defaut sur les layouts publics ou applicatifs.

## 2. Trigger / Source

- Source type: audit
- Source reference: `.codex-artifacts/dark-mode-audit-2026-05-10/audit-results.json#dark-mode-audit`
- Reason for change: l'audit dark mode du 2026-05-10 montre des contrastes
  insuffisants, des surfaces claires residuelles et des liens non styles sur des
  routes publiques et authentifiees.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend-theme`
- In scope:
  - Corriger les routes auditees en mode `html.dark` en priorisant les surfaces
    avec issues de contraste ou light surfaces.
  - Traiter les liens bleu navigateur par defaut sur les layouts publics.
  - Corriger les surfaces et textes dark via tokens CSS existants ou nouveaux
    tokens theme scopes, dans les fichiers CSS owners appropries.
  - Preserver les routes, donnees, contrats API, composants React et navigation.
  - Produire les artefacts `dark-mode-before.md` et `dark-mode-after.md` avec les
    scans, screenshots ou resultats d'audit pertinents.
  - Ajouter ou ajuster un guard qui bloque la regression des surfaces dark mode
    critiques.
- Out of scope:
  - Refaire la direction artistique globale ou le systeme de design complet.
  - Introduire des styles inline, des overrides dans `frontend/src/App.css` ou des
    corrections globales non scopees.
  - Modifier le backend, les contrats API, les droits d'acces ou les donnees de
    test.
  - Corriger des routes non couvertes par l'audit si elles ne partagent pas le
    meme owner CSS.
- Explicit non-goals:
  - Ne pas ajouter une deuxieme logique de theme.
  - Ne pas contourner les variables existantes par des couleurs hardcodees
    repetees.
  - Ne pas masquer les problemes par une allowlist large ou permanente.
  - Ne pas changer le layout, la largeur, la navigation ou les contenus metier.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: design-system-convergence
- Archetype reason: les surfaces dark doivent converger vers les tokens et owners
  CSS du theme au lieu de corrections locales concurrentes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Autorise: changements visuels strictement lies au dark mode, couleurs,
    backgrounds, borders, shadows et etats hover/focus tokenises.
  - Interdit: changement de routes, logique metier, contrats API, permissions,
    contenu affiche ou structure React non necessaire.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une surface claire est intentionnelle en dark mode et
  doit rester durablement comme exception produit documentee.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le rendu en `html.dark` et les CSS charges prouvent la couleur effective. |
| Baseline Snapshot | yes | L'audit initial et les screenshots doivent rester disponibles pour comparaison. |
| Ownership Routing | yes | Chaque correction doit vivre dans le fichier CSS owner, pas dans `App.css` ou en inline. |
| Allowlist Exception | yes | Toute surface claire restante doit etre exacte, justifiee et testee. |
| Contract Shape | no | Aucun DTO, payload, route HTTP ou schema n'est modifie. |
| Batch Migration | yes | Plusieurs routes et surfaces auditees convergent dans un meme lot borne. |
| Reintroduction Guard | yes | Les regressions dark mode critiques doivent etre bloquees par tests/scans. |
| Persistent Evidence | yes | Les preuves before/after et screenshots doivent persister avec la story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - CSS actifs des owners modifies dans `frontend/src/**/*.css`.
  - Tokens dans `frontend/src/styles/app/tokens.css` et fichiers de theme
    existants.
  - DOM rendu avec `html.dark` sur les routes auditees.
- Secondary evidence:
  - `.codex-artifacts/dark-mode-audit-2026-05-10/audit-results.json`.
  - screenshots de l'audit sous `.codex-artifacts/dark-mode-audit-2026-05-10/`.
  - tests `theme-tokens`, `design-system` et `visual-smoke`.
- Static scans alone are not sufficient because:
  - le contraste depend de la cascade CSS et du background effectif au runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-137-converger-dark-mode-surfaces-frontend/dark-mode-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-137-converger-dark-mode-surfaces-frontend/dark-mode-after.md`
- Required baseline content:
  - routes auditees avec `issueCount` et `lightSurfaceCount`;
  - selecteurs principaux en echec de contraste;
  - screenshots sources pertinents;
  - fichiers CSS owners candidats;
  - exceptions temporaires si une correction est reportee.
- Expected invariant:
  - en `html.dark`, les routes traitees ne presentent plus de grande surface light
    non classee, de lien bleu navigateur par defaut ou de texte clair illisible
    sur surface claire.
- Allowed differences:
  - ajustement des teintes dark, borders, shadows et opacites;
  - reutilisation ou extension mesuree des tokens existants;
  - conservation de surfaces claires uniquement si elles sont intentionnelles,
    scopees et documentees.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tokens theme partages | `frontend/src/styles/app/tokens.css` ou fichier theme existant | couleur hardcodee repetee dans plusieurs pages |
| Layout public landing/privacy | CSS du layout public et pages concernees | `frontend/src/App.css` |
| Surfaces applicatives | CSS owner du composant, feature ou page | style inline React |
| Avatar utilisateur | `frontend/src/components/ui/UserAvatar/UserAvatar.css` | override page-level |
| Etats loading/error/empty | CSS owner du composant ou de la page | correction globale non scopee |
| Exceptions dark | allowlist de test exacte | wildcard ou commentaire libre |

Rules:

- Chaque correction doit utiliser une classe CSS existante ou un owner CSS local.
- Les nouveaux tokens doivent etre nommes selon la taxonomie deja presente.
- Les couleurs hardcodees ne sont acceptees que si elles creent un token dans le
  fichier de tokens approprie.
- Les liens publics doivent avoir une couleur et un etat hover/focus definis pour
  le dark mode.

## 4e. Allowlist / Exception Register

Use a deterministic guard/register in the existing frontend test allowlists when
an exception dark mode remains.

| File / Route | Surface | Reason | Expiry or permanence decision |
|---|---|---|---|
| `.codex-artifacts/dark-mode-audit-2026-05-10/audit-results.json` | audit source | Baseline generated on 2026-05-10. | Permanent evidence. |
| routes admin redirigees vers `/dashboard` | duplicated dashboard issues | Les routes admin auditees retombent sur le dashboard avec le compte de test. | Re-evaluate when admin login/role fixture is available. |
| intentional light accent, if any | exact selector required | Aucune exception implicite autorisee. | Must be documented in `dark-mode-after.md`. |

## 5. Acceptance Criteria

1. Les fichiers `dark-mode-before.md` et `dark-mode-after.md` existent dans le
   dossier de story.
2. Les corrections dark mode utilisent les fichiers CSS owners, sans style inline.
3. Les routes auditees prioritaires ne montrent plus de lien bleu navigateur par
   defaut ni de grandes surfaces light non classees en `html.dark`.
4. Les contrastes critiques signales par l'audit sont corriges ou classes avec une
   exception exacte et temporaire.
5. `npm run test -- theme-tokens design-system visual-smoke` passe.
6. Les scans cibles confirment l'absence de corrections dark dans
   `frontend/src/App.css` et l'absence de nouveaux `style=`.

## 6. Verification Plan

- Depuis `frontend`:
  - `npm run test -- theme-tokens design-system visual-smoke`
  - e2e dark route audit equivalent a l'audit source
  - `rg -n "style=" src -g "*.tsx" -g "*.jsx"`
  - `rg -n "#0000ee|rgb\\(0, 0, 238\\)|color:\\s*blue" src -g "*.css" -g "*.scss"`
  - `rg -n "dark|html\\.dark" src/App.css`

## 7. Persistent Evidence

- `_condamad/stories/CS-137-converger-dark-mode-surfaces-frontend/dark-mode-before.md`
- `_condamad/stories/CS-137-converger-dark-mode-surfaces-frontend/dark-mode-after.md`
- `.codex-artifacts/dark-mode-audit-2026-05-10/audit-results.json`
- screenshots `.codex-artifacts/dark-mode-audit-2026-05-10/*.png`
