# Story 63.11: Page d'inscription produit optimisée conversion

Status: done

## Mise en oeuvre réelle

- `SignUpForm` reste limité à `email + mot de passe`, avec conservation du contexte de plan via `?plan=...`.
- La micro-réassurance sous le bouton de création de compte a été finalisée avec une structure dédiée (`auth-reassurance-item`) et des séparateurs décoratifs non interactifs, pour éviter tout rendu collé ou illisible.
- La feuille `SignUpForm.css` est désormais importée explicitement par le composant afin que les styles locaux de la page `/register` soient réellement appliqués en production.
- Le lien d'alternative `Se connecter` a été restylé comme une action secondaire premium en capsule, cohérente avec le ton visuel de la landing et de l'écran d'inscription.

## Story

As a visiteur non authentifié ayant cliqué sur un CTA de la landing page,
I want une page d'inscription produit claire et rapide avec un formulaire minimal,
so que je puisse créer mon compte applicatif en moins de 60 secondes et être redirigé vers l'onboarding.

## Acceptance Criteria

### AC1 — Périmètre explicite (bloquant)

1. **Cette story implémente la création de compte applicatif**, pas un double opt-in marketing ni une simple capture d'email. L'issue ici est la création d'un utilisateur en base avec session active.
2. Pas de liste email marketing créée ou enrichie ici — cette responsabilité appartient à la story 63.12 (email transactionnel J0 post-inscription).
3. Le formulaire ne collecte que les données strictement nécessaires à la création de compte : **email + mot de passe uniquement** à l'étape visible. Toute autre donnée (prénom, date de naissance) est collectée en onboarding post-inscription.

### AC2 — Formulaire minimal

4. La page `/register` (composant `SignUpForm`) n'affiche que 2 champs : Email et Mot de passe.
5. Un bouton "Créer mon compte" déclenche la soumission.
6. Lien "Déjà inscrit ? Se connecter" → `/login`.
7. Micro-réassurance sous le formulaire : "Sans carte bancaire", "Annulation à tout moment", "Données protégées RGPD".

### AC3 — Option OAuth Google

8. Bouton "Continuer avec Google" au-dessus du formulaire, séparé par un "— ou —".
9. Le bouton utilise le logo Google officiel (SVG) et le texte standardisé Google ("Continuer avec Google").
10. Si l'endpoint OAuth Google n'est pas implémenté côté backend, le bouton affiche un toast "Disponible prochainement" sans crash — **graceful degradation obligatoire**, pas de bouton cassé.
11. Le bouton OAuth n'est rendu que si la feature est déclarée disponible dans la config (`VITE_GOOGLE_OAUTH_ENABLED=true`).

### AC4 — Validation et retours

12. Validation Zod côté client (schema existant dans `frontend/src/i18n/zod/auth.ts` ou à créer) :
    - Email : format valide
    - Mot de passe : minimum 8 caractères
13. Messages d'erreur affichés **inline sous chaque champ**, pas uniquement en toast.
14. Sur soumission réussie : redirect vers `/profile` (saisie données natales — onboarding naturel existant).
15. Sur erreur serveur (email déjà utilisé, etc.) : message inline clair, pas de page blanche.

### AC5 — Contexte plan (continuité du funnel)

16. Si l'URL contient `?plan={PlanCode}` avec une valeur appartenant aux codes canoniques définis dans `pricingConfig.ts` :
    - Afficher un badge contextuel : "Plan sélectionné : {nom du plan}" (formulation factuelle, pas "Vous accédez au plan Premium" qui implique un droit immédiat)
    - Stocker la valeur dans `sessionStorage` sous la clé `intended_plan`
    - **Ce contexte ne crée aucun abonnement** et n'est qu'une intention d'achat préservée pour le checkout post-onboarding
17. Toute valeur de `plan` inconnue (hors codes canoniques `free` / `trial` / `basic` / `premium`) est **ignorée silencieusement** — aucune erreur, aucun badge affiché.
18. Le badge contextuel ne contient aucun prix ni promesse de durée — seulement le nom du plan sélectionné.

### AC6 — Style cohérent avec la landing

19. La page d'inscription hérite du même fond que la landing (`RootLayout` > `AuthLayout`) — le fond `app-bg` gradient et le `StarfieldBackground` sont déjà rendus par `RootLayout`, visible via `AuthLayout` qui est dans la même arborescence. Aucun fond à recréer.
20. `AuthLayout` est actuellement un simple conteneur centré (max-width 480px) — c'est suffisant. Si un style plus proche de la landing est souhaité, surcharger via `.auth-layout-landing` plutôt que modifier `AuthLayout`.
21. Aucun style inline : modifications CSS dans `frontend/src/components/SignUpForm.css` (existant) ou surcharge via classe contextuelle.
22. Tokens à utiliser dans SignUpForm : `var(--premium-glass-surface-1)`, `var(--premium-glass-border)`, `backdrop-filter: blur(18px)`, `var(--premium-radius-card)` pour le container du formulaire.

### AC7 — Tests

21. Les tests existants de `SignUpForm` doivent passer après modification.
22. Ajouter un test de régression : soumission avec `?plan=unknown_value` → aucun badge, aucune erreur.
23. Ajouter un test : rendu avec `?plan=premium` → badge "Plan sélectionné : Premium" visible.

### Definition of Done QA

- [ ] Formulaire visible avec 2 champs uniquement (email + mot de passe) — pas de champs supplémentaires
- [ ] `?plan=premium` → badge "Plan sélectionné : Premium" visible
- [ ] `?plan=valeur_inconnue` → aucun badge, pas d'erreur console
- [ ] Bouton Google avec `VITE_GOOGLE_OAUTH_ENABLED=false` → bouton absent du DOM (pas masqué CSS)
- [ ] Message d'erreur email invalide affiché inline sous le champ (pas toast seul)
- [ ] Sur succès : redirect vers `/profile`
- [ ] Tests existants auth toujours verts

## Tasks / Subtasks

- [ ] T1 — Modifier `SignUpForm` (AC: 3–7)
  - [ ] Lire `frontend/src/components/SignUpForm.tsx` en entier avant modification
  - [ ] Réduire à email + password uniquement
  - [ ] Micro-réassurance sous formulaire
  - [ ] Lien vers /login
- [ ] T2 — OAuth Google (AC: 8–11)
  - [ ] Feature flag `VITE_GOOGLE_OAUTH_ENABLED`
  - [ ] Bouton conditionnel + graceful degradation
- [ ] T3 — Validation Zod (AC: 12–15)
  - [ ] Schéma Zod `SignUpSchema` avec email + password 8 chars
  - [ ] Messages inline par champ
  - [ ] Redirect `/profile` sur succès
- [ ] T4 — Contexte plan (AC: 16–18)
  - [ ] Lecture `?plan` + vérification des codes canoniques depuis `pricingConfig.ts`
  - [ ] Badge contextuel factuel
  - [ ] Stockage `sessionStorage.intended_plan`
- [ ] T5 — Style (AC: 19, 20)
  - [ ] Alignement visuel avec la landing
- [ ] T6 — Tests (AC: 21–23)
  - [ ] Tests régression plan inconnu
  - [ ] Test badge plan connu

## Dev Notes

- **Lire SignUpForm en entier avant de modifier** : `frontend/src/components/SignUpForm.tsx`. Ne pas casser le flux auth existant.
- **Codes de plan canoniques** : importés depuis `frontend/src/config/pricingConfig.ts` (créé en story 63.7). Les valeurs à supporter sont `free`, `trial`, `basic`, `premium`.
- **sessionStorage vs localStorage** : `sessionStorage` est préférable ici car l'intention de plan doit expirer à la fermeture du navigateur — pas de persistance multi-session de cette donnée.
- **Schema Zod** : vérifier `frontend/src/i18n/zod/auth.ts` — si un schema `signUp` existe, l'étendre plutôt que d'en créer un nouveau.
- **Ne pas implémenter le checkout** dans cette story : le plan stocké dans sessionStorage sera consommé par une story de l'epic 61 (post-onboarding checkout). Cette story s'arrête à la création de compte.

### Project Structure Notes

```
frontend/src/
├── components/
│   └── SignUpForm.tsx          # modifier
├── config/
│   └── pricingConfig.ts        # lire — créé en 63.7 (ou déclarer les codes canoniques localement)
└── i18n/
    └── zod/
        └── auth.ts             # vérifier schema signUp
```

### References

- SignUpForm : [frontend/src/components/SignUpForm.tsx](frontend/src/components/SignUpForm.tsx)
- Zod auth : [frontend/src/i18n/zod/auth.ts](frontend/src/i18n/zod/auth.ts)
- pricingConfig : [frontend/src/config/pricingConfig.ts](frontend/src/config/pricingConfig.ts) (story 63.7)
- Document funnel — Capture/Activation : [docs/funnel/landing_funnel.md](docs/funnel/landing_funnel.md#étape-captureactivation)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
