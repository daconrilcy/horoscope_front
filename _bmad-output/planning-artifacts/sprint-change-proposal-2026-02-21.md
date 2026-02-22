# Sprint Change Proposal — 2026-02-21
## Objet : UI Signin/Signout manquante (Story 2-1 incomplète)

---

## 1) Résumé du problème

### Déclencheur
- **Story concernée :** `2-1 — Inscription et authentification utilisateur (JWT)` — statut `done`
- **Découverte :** Analyse du code source frontend lors d'une revue d'implémentation (2026-02-21)

### Énoncé du problème
La story 2-1 a été implémentée côté **backend uniquement**. Les endpoints suivants sont pleinement fonctionnels :
- `POST /v1/auth/register` — inscription email/password
- `POST /v1/auth/login` — connexion email/password
- `POST /v1/auth/refresh` — renouvellement du token
- `GET /v1/auth/me` — récupération du profil connecté

Cependant, **aucune interface utilisateur n'a été créée côté frontend** :
- Pas de formulaire de connexion (`LoginPage.tsx` prévu dans l'architecture, absent)
- Pas de bouton de déconnexion accessible
- L'application affiche "Aucun token détecté. Connectez-vous..." sans proposer de formulaire
- Le token doit être placé manuellement dans `localStorage["access_token"]` pour que l'app fonctionne

**En production, aucun utilisateur ne peut se connecter ni se déconnecter via l'interface.**

### Type de problème
Implémentation partielle d'une story (backend implémenté, frontend oublié)

### Preuves
- `frontend/src/utils/authToken.ts` : gestion du token localStorage en place, mais pas d'appel à `POST /v1/auth/login`
- `frontend/src/App.tsx` : message "Aucun token" sans lien vers un formulaire
- Aucun fichier `LoginPage.tsx`, `LoginForm.tsx`, `LogoutButton.tsx` dans le projet
- Architecture (`architecture.md`) mentionne `frontend/src/pages/LoginPage.tsx` → jamais créé
- `frontend/src/api/auth.ts` prévu → absent (seul `authMe.ts` existe)
- NFR2 (parcours inscription < 5 min) : **non conforme** sans UI de connexion

---

## 2) Analyse d'impact

### Impact Épics
- **Epic 2 (Compte Utilisateur et Première Valeur)** : marquée `done` mais contient un écart fonctionnel majeur bloquant en production
- **Épics 3, 4, 5, 6, 7** : tous les flux utilisateurs authentifiés sont inaccessibles en production tant que le signin n'est pas implémenté côté UI
- Aucun epic n'est obsolète ; aucun nouveau epic n'est nécessaire

### Impact Stories
- Story `2-1` : à considérer comme **incomplète** (critères d'acceptance backend satisfaits, UI omise)
- Une nouvelle story `2-6` est nécessaire pour compléter la livraison

### Conflits artefacts
| Artefact | Conflit | Action requise |
|---|---|---|
| PRD | FR9, NFR2 non conformes en prod | Aucune modification PRD — l'exigence est juste |
| Architecture | `LoginPage.tsx` et `api/auth.ts` prévus, absents | Aucune décision nouvelle — patterns en place |
| UX Design | Écran login non décrit dans le spec | Story 2-6 devra inclure spécification UI |
| Tests frontend | `App.test.tsx` simule le token manuellement | Tests formulaire à ajouter dans story 2-6 |

### Impact technique
- Pas de refonte architecturale nécessaire
- Les conventions sont prêtes : React Hook Form + Zod (formulaires), `authToken.ts` (stockage), TanStack Query (état serveur)
- Effort frontend estimé : 2–4h

---

## 3) Approche recommandée

**Option retenue : Direct Adjustment — Création de la Story 2-6**

**Rationale :**
- Le backend est complet et fonctionnel
- Les utilitaires frontend sont en place (`authToken.ts`, `useAuthMe`)
- Les conventions de formulaire sont définies (React Hook Form + Zod)
- Aucun risque architectural — simple complétion d'une fonctionnalité UI
- Effort minimal, risque faible, valeur immédiate (déblocage de tous les flux utilisateurs)

**Alternatives rejetées :**
- Rollback de story 2-1 : détruirait un backend fonctionnel sans bénéfice (Non viable)
- Réduction de scope MVP : non applicable, l'authentification est un prérequis absolu (Non applicable)

---

## 4) Propositions de changements détaillées

### Proposition A — Nouvelle Story 2-6 dans epics.md

**Section Epic 2 — ajout après Story 2.5 :**

```markdown
### Story 2.6: Interface utilisateur signin et signout

As a user,
I want accéder à un formulaire de connexion et à un bouton de déconnexion,
So that je puisse m'authentifier et me déconnecter depuis l'interface de l'application.

**Acceptance Criteria:**

**Given** un utilisateur non authentifié
**When** il ouvre l'application
**Then** un formulaire signin est affiché (email + password + bouton "Se connecter")
**And** le formulaire valide les champs avec React Hook Form + Zod
**And** les états loading/error/empty sont gérés explicitement (NFR3)
**And** en cas d'identifiants incorrects, un message d'erreur non technique est affiché
**And** en cas de succès, setAccessToken() est appelé et l'interface personnalisée est affichée

**Given** un utilisateur authentifié
**When** il navigue dans l'application
**Then** un bouton "Se déconnecter" est accessible dans l'interface
**And** le clic appelle clearAccessToken() et retourne au formulaire de connexion
**And** la navigation clavier est fonctionnelle (NFR14 — WCAG 2.1 AA)
```

**Notes techniques :**
- Créer `frontend/src/pages/LoginPage.tsx` (prévu dans `architecture.md`, jamais créé)
- Créer `frontend/src/api/auth.ts` avec fonction `loginUser(email, password)` → `POST /v1/auth/login`
- Stocker `access_token` + `refresh_token` via `setAccessToken()` depuis `authToken.ts`
- Le logout appelle `clearAccessToken()` déjà implémenté dans `authToken.ts`
- Ajouter tests unitaires/intégration dans `frontend/src/tests/`

### Proposition B — Mise à jour sprint-status.yaml

```yaml
# Changements à appliquer :
epic-2: in-progress           # revenir de done à in-progress (story 2-6 à faire)
2-6-interface-utilisateur-signin-signout: backlog
```

---

## 5) Impact MVP et plan d'action

### Impact MVP
- FR9 (création de compte + authentification) : **non conforme** en l'état — sera résolu par story 2-6
- NFR2 (parcours inscription < 5 min) : **non conforme** en l'état — sera résolu par story 2-6
- Aucune réduction de scope MVP nécessaire

### Plan d'action séquentiel (nouvelle fenêtre de contexte pour chaque workflow)

| Étape | Workflow BMAD | Agent | Action |
|---|---|---|---|
| 1 | `/bmad-bmm-create-story` | 🏃 Bob (SM) | Créer et affiner la story 2-6 |
| 2 | `/bmad-bmm-dev-story` | 💻 Amelia (Dev) | Implémenter LoginPage.tsx + auth.ts + LogoutButton |
| 3 | `/bmad-bmm-code-review` | 💻 Amelia (Dev) | Revue du code implémenté |

---

## 6) Plan de handoff

### Classification du changement
**Minor** — Complétion d'une fonctionnalité UI ciblée, backend intact, aucun impact architectural

### Responsabilités

| Rôle | Action |
|---|---|
| **Scrum Master (Bob)** | Créer story 2-6 via `/bmad-bmm-create-story` ; mettre à jour sprint-status.yaml et epics.md |
| **Developer (Amelia)** | Implémenter l'UI signin/signout via `/bmad-bmm-dev-story` |
| **PM/Architect** | Aucune intervention requise |

### Critères de succès
- `frontend/src/pages/LoginPage.tsx` créé et fonctionnel
- `frontend/src/api/auth.ts` créé avec `loginUser()`
- Bouton de déconnexion accessible dans l'UI authentifiée
- Tests unitaires couvrant le formulaire signin et le logout
- Story 2-6 marquée `done`
- Sprint-status.yaml : epic-2 repassée `done`, story 2-6 `done`

---

## 7) Statut de la checklist

### Section 1 — Déclencheur et contexte
- [x] 1.1 Story déclencheuse identifiée (2-1)
- [x] 1.2 Problème défini (implémentation partielle — UI manquante)
- [x] 1.3 Preuves collectées (code source exploré)

### Section 2 — Impact Épics
- [x] 2.1 Epic 2 évaluée (action requise : story 2-6)
- [x] 2.2 Changements epic déterminés (nouvelle story 2-6)
- [x] 2.3 Épics suivantes examinées (bloquées en prod — débloquées par 2-6)
- [x] 2.4 Aucun epic invalidé / aucun nouveau epic nécessaire
- [N/A] 2.5 Ordre des épics inchangé

### Section 3 — Conflits artefacts
- [x] 3.1 PRD — aucune modification nécessaire
- [x] 3.2 Architecture — aucune décision nouvelle requise
- [x] 3.3 UX Design — story 2-6 doit inclure spec UI signin/signout
- [x] 3.4 Tests — à ajouter dans story 2-6

### Section 4 — Chemin à suivre
- [x] 4.1 Option 1 (story 2-6) — Viable, Low effort, Low risk
- [x] 4.2 Option 2 (rollback) — Non viable
- [x] 4.3 Option 3 (réduction MVP) — Non applicable
- [x] 4.4 Recommandation sélectionnée : Option 1

### Section 5 — Composants du proposal
- [x] 5.1 Résumé du problème rédigé
- [x] 5.2 Impact epic et artefacts documenté
- [x] 5.3 Chemin recommandé avec justification
- [x] 5.4 Impact MVP + plan d'action séquentiel
- [x] 5.5 Plan de handoff avec responsabilités
