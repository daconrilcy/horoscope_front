<!-- Draft detaille du candidat d'audit avant contractualisation CONDAMAD. -->

# Draft CS-108 - Statuer les pages publiques et candidates layout

## Source

- Audit: `_condamad/audits/frontend-layouts/2026-05-08-1532`
- Candidate: `SC-101`
- Finding: `F-101`
- Domaine: `frontend-layouts`
- Archetype pressenti: `ownership-routing-refactor`

## Lecture du candidat

L'audit ne demande pas un nouveau refactor de hierarchie de layouts. Il indique
que CS-103 a CS-107 ont ferme la structure runtime et les guards, mais que cinq
fichiers restent volontairement bloques dans le registre de ownership:

| Fichier | Etat actuel | Decision a obtenir | Route interdite sans decision |
|---|---|---|---|
| `frontend/src/pages/PrivacyPolicyPage.tsx` | `needs-user-decision` | exposer sous un owner public explicite, conserver bloque, ou traiter par story de retrait dediee | oui |
| `frontend/src/pages/billing/BillingSuccessPage.tsx` | `needs-user-decision` | exposer comme callback billing, conserver bloque, ou traiter par story de retrait dediee | oui |
| `frontend/src/pages/billing/BillingCancelPage.tsx` | `needs-user-decision` | exposer comme callback billing, conserver bloque, ou traiter par story de retrait dediee | oui |
| `frontend/src/pages/HomePage.tsx` | `dead/unmounted-page-candidate` | conserver avec owner/expiry ou ouvrir une story de retrait dediee | oui |
| `frontend/src/pages/landing/sections/TestimonialsSection.tsx` | `dead/unmounted-page-candidate` | conserver avec owner/expiry, rattacher a `LandingPage`, ou ouvrir une story de retrait dediee | oui |

## Draft de story retenu

La story doit etre un contrat de decision et de mise a jour du registre, pas une
suppression silencieuse ni un routage opportuniste. Le dev agent devra obtenir
une decision explicite, la reporter dans les artefacts CS-107/CS-108, puis
adapter `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` et les tests uniquement si la
decision l'autorise.

## Conditions de fermeture

- Aucun fichier ne reste `needs-user-decision` sans decision explicite, owner et
  expiry.
- Aucun fichier `dead/unmounted-page-candidate` ne reste sans decision de
  conservation ou story de retrait dediee.
- `RG-068` reste respecte: les pages routees passent par `RootLayout` puis un
  owner explicite (`LandingLayout`, `AuthLayout`, `AppLayout` ou owner
  approuve).
- Aucun wildcard, alias, redirect de compatibilite, fallback ou `PASS with
  limitation` ne peut servir de preuve.

