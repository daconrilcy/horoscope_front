# CS-404 - Ajouter Des Accordeons Narratifs Modernes Et Compacter Les Actions /natal

<!-- Commentaire global: ce brief cadre la divulgation progressive moderne de la lecture natale publique. -->

## Resume

Restaurer une lecture progressive sur `/natal` avec des accordeons accessibles pour les cinq
chapitres narratifs. Ne pas reutiliser l'ancien rendu legacy `sections/highlights`: la page
doit conserver le contrat `NatalNarrativeReading`, afficher le premier chapitre ouvert par
defaut et alleger la zone d'actions avant la lecture.

## Contexte

La refonte CS-393 a remplace les anciennes cartes et accordéons legacy par cinq cartes
narratives statiques ouvertes. Cette structure respecte la suppression legacy mais degrade
la lisibilite: tous les paragraphes sont deroules, tandis que PDF, historique et upsell
occupent une place importante avant le contenu. `NatalReadingSources` dispose deja d'un
dropdown accessible et doit rester le modele d'interaction.

## Objectif

Mettre en place:

```text
hero concis -> lecture narrative progressive -> sources repliees -> mode astrologue replie
```

## Perimetre inclus

1. Faire de `NatalNarrativeReading` l'owner des accordeons des cinq chapitres.
2. Ouvrir le premier chapitre par defaut et replier les quatre suivants.
3. Ajouter bouton, `aria-expanded`, `aria-controls`, panneau associe et navigation clavier.
4. Afficher pour chaque chapitre replie un titre et un apercu court non duplique.
5. Reutiliser les variables CSS existantes; aucun style inline.
6. Conserver `NatalReadingSources` replie apres les chapitres.
7. Regrouper PDF, historique et options secondaires dans une barre d'actions compacte sans
   casser leurs parcours.
8. Conserver upsell, quota, loading, empty, error, regeneration et mode astrologue.
9. Mettre a jour `RG-154`: interdire l'accordeon legacy, mais autoriser explicitement
   l'accordeon narratif moderne base sur `narrative_natal_reading_v1`.

## Hors perimetre

- Reintroduire `NatalInterpretationLegacyBody` dans le chemin public complet.
- Rendre `sections`, `highlights`, codes moteur ou evidence IDs comme contenu public.
- Modifier backend, prompts, calculs astrologiques ou quotas.
- Ajouter un style inline.

## Sources obligatoires

- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.css`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique.
  - `RG-052` - reutiliser les tokens CSS canoniques.
  - `RG-071`, `RG-073` - conserver les responsabilites frontend natal existantes.
  - `RG-129` - aucune regle astrologique locale React.
  - `RG-153` - conserver la composition publique en trois couches.
  - `RG-154` - conserver la denylist publique et l'absence de fallback legacy.
  - `RG-158` - conserver les accordeons narratifs modernes accessibles et les actions compactes.
- Required regression evidence:
  - `pnpm --dir frontend test -- natalNarrativeReading natalPublicDomGuard NatalChartPage`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "ni-evidence-tags|ni-projections|LockedSection" frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
  - `rg -n "NatalInterpretationLegacyBody|style=" frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- Allowed differences:
  - `RG-154` est precise pour distinguer l'accordeon narratif moderne autorise de l'accordeon
    legacy interdit.

## Criteres d'acceptation

1. Le premier chapitre est ouvert par defaut; les quatre suivants sont replies.
2. Chaque chapitre se deplie et se replie au clavier et a la souris.
3. Les attributs ARIA lient chaque bouton a son panneau.
4. Les actions secondaires occupent moins de place avant la lecture sans perdre leur fonction.
5. Les sources et le mode astrologue restent replies par defaut.
6. Aucun composant legacy, code moteur ou raw evidence ID n'apparait dans le DOM public.
7. Desktop et mobile restent lisibles sans style inline.

## Commandes De Validation Minimales

```powershell
cd frontend
pnpm test -- natalNarrativeReading natalPublicDomGuard NatalChartPage
pnpm lint
pnpm build
rg -n "ni-evidence-tags|ni-projections|LockedSection" src/components/natal-interpretation/NatalInterpretationContent.tsx
rg -n "NatalInterpretationLegacyBody|style=" src/features/natal-chart/NatalNarrativeReading.tsx
```

QA navigateur:

```text
Ouvrir /natal en desktop et mobile avec l'utilisateur test; verifier ouverture initiale,
toggle clavier/souris, sources repliees, actions compactes et mode astrologue replie.
```

## Dependances

- CS-396.

## Risques

Le risque principal est d'affaiblir `RG-154` en restaurant indirectement le chemin legacy.
La modification du registre doit nommer precisement le composant narratif autorise.
