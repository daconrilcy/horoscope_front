# CS-380 - Durcir Natal Expert Panel Contre Payloads Partiels Sans Masquer Contrat

<!-- Commentaire global: ce brief cadre la robustesse frontend du panneau expert natal face aux payloads partiels. -->

## Resume

Rendre `NatalExpertPanel` robuste face aux blocs experts partiels ou absents afin que la page de theme natal ne tombe plus dans l'error boundary, tout en conservant une detection visible des derives de contrat backend.

## Contexte

Apres generation, le backend repond `200 OK`, puis le front plante dans:

```text
TraditionalConditionsBlock -> condition.hayz.is_hayz
```

Le composant suppose que chaque entree de `traditional_conditions` contient `hayz` et `rejoicing`. Une correction frontend est necessaire pour proteger l'UX, mais elle ne doit pas recalculer les faits astrologiques ni inventer de `hayz` ou de joie planetaire.

Decision produit confirmee: hors donnees de naissance insuffisantes (`no_time`, `no_location_no_time`), un payload complet ne doit pas omettre `traditional_conditions` pour une raison de plan commercial. Le front peut proteger l'affichage contre un payload partiel, mais ne doit pas officialiser ce payload partiel comme contrat normal.

## Objectif

Le panneau expert doit:

- afficher les blocs complets quand le contrat public est complet;
- afficher un etat degrade localise quand une entree traditionnelle est partielle;
- ne jamais crasher la page complete;
- signaler clairement la derive de contrat dans le test et, si une convention existe, dans une trace non sensible;
- rester strictement consommateur de faits API.

## Perimetre inclus

1. Lire `NatalExpertPanel.tsx`, ses types et ses tests.
2. Introduire de petits guards de lecture pour `condition.hayz`, `condition.rejoicing` et tout sous-bloc optionnel expose par l'API.
3. Garder les types du contrat nominal stricts; ajouter seulement une garde de compatibilite locale si le payload runtime peut etre invalide ou ancien.
4. Ajouter un test Vitest reproduisant une entree `traditional_conditions` avec `hayz` absent.
5. Verifier que le rendu complet existant ne regresse pas.
6. Ne pas ajouter de style inline; utiliser le CSS existant si un nouvel etat visuel est necessaire.
7. Ne pas recalculer de condition astrologique dans React.

## Hors perimetre

- Corriger la source backend du payload invalide; voir CS-379.
- Changer la navigation, l'authentification ou la generation elle-meme.
- Ajouter une nouvelle dependance frontend.
- Refaire le design du panneau expert.
- Afficher des donnees prompt/provider internes dans l'UI publique.

## Sources obligatoires

- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.css`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/features/birth-profile/components/BirthProfileNatalGenerationSection.tsx`

## Criteres d'acceptation

1. Le test reproduisant `traditional_conditions.{planet}.hayz` absent ne provoque plus d'exception React.
2. Le composant affiche un message localise pour l'entree partielle, sans masquer les autres planetes valides.
3. Le test existant du rendu expert complet continue de prouver l'affichage de `hayz.is_hayz`, `hayz.chart_sect` et `rejoicing.rejoicing_house`.
4. Aucun calcul astrologique, scoring ou fallback doctrinal n'est ajoute cote frontend.
5. Les types TypeScript ne transforment pas un payload partiel invalide en contrat nominal; la tolerance reste localisee dans le rendu degrade.
6. Aucun style inline n'est introduit.
7. La page de theme natal reste utilisable apres une generation meme si un bloc expert partiel arrive temporairement.

## Commandes de validation minimales

```powershell
cd frontend
pnpm lint
pnpm test -- NatalExpertPanel
```

Validation elargie recommandee:

```powershell
pnpm test -- BirthProfilePage NatalChartPage natalInterpretation
pnpm build
```

QA navigateur minimale:

```powershell
pnpm dev
```

Puis, dans le navigateur, se connecter avec l'utilisateur test, renseigner les donnees de naissance, lancer la generation et verifier que la page ne bascule pas dans l'error boundary.

## Risques

Le risque principal est de rendre le front trop permissif et de cacher une derive backend. Les tests doivent distinguer "payload partiel tolere pour l'UX" et "contrat backend a corriger par CS-379".
