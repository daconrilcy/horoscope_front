# CS-422 - Simplifier Le Rendu Basic Natal Sources Et Mentions Legales

<!-- Commentaire global: ce brief cadre la correction frontend du rendu Basic natal pour supprimer les repetitions et presenter la lecture comme un rapport. -->

## Resume

Adapter le rendu `/natal` du contrat `basic_natal_interpretation_v2` pour que le lecteur voie
d'abord une interpretation, puis les sources en annexe, et une seule zone de mentions legales.

L'exemple utilisateur affiche aujourd'hui:

- un bloc `Ce que j'ai utilise...` dans chaque theme;
- le meme bloc de sources repete ensuite en fin de lecture;
- une section `Limites de cette lecture`;
- un bloc `Mentions legales`;
- un footer `Mentions legales` avec trois lignes supplementaires;
- des cartes qui morcellent le rapport au lieu de le faire lire comme un texte suivi.

La story doit rendre le Basic V2 lisible sans masquer les preuves publiques ni les disclaimers
necessaires.

## Analyse Produit

Le contrat Basic peut rester structure, mais le rendu public ne doit pas exposer la structure de
validation comme experience principale. Pour un utilisateur non initie, les sources doivent servir
a comprendre d'ou vient la lecture, pas interrompre chaque paragraphe.

Le moyen propose:

- afficher `title`, `introduction`, `themes`, `conclusion` comme un rapport continu;
- presenter les sources publiques une seule fois, apres la conclusion, dans un detail/accordeon
  accessible ou un bloc annexe compact;
- fusionner limitations et mentions legales Basic dans une zone unique, avec deduplication stricte,
  sans changer le comportement legal des rendus free short et `narrative_natal_reading_v1`;
- ne jamais afficher les preuves inline dans chaque theme sauf decision UX explicite ulterieure;
- garder les tests DOM qui prouvent l'absence de marqueurs techniques et de repetitions.

## Objectif

La page `/natal` doit permettre de lire le theme Basic sans recherche supplementaire:

```text
Titre
Introduction
Theme 1
Theme 2
Theme 3...
Conclusion
Sources utilisees (annexe compacte, une seule fois)
Limites et mentions legales (une seule fois)
```

## Perimetre Inclus

1. Modifier `BasicV2Reading` pour ne plus rendre `PublicEvidenceList` dans chaque theme.
2. Rendre les preuves publiques Basic une seule fois en fin de lecture.
3. Dedoublonner les preuves globalement avec une cle stable independante du theme:
   `source_id` si disponible, sinon `normalized(label + meaning + source_type)`.
4. Fusionner les limitations et disclaimers Basic avec les lignes legales globales dans un seul
   composant public uniquement pour la branche Basic V2.
5. Eviter deux titres `Mentions legales` dans le DOM public.
6. Ajouter un test DOM qui compte les repetitions:
   - maximum un bloc de sources publiques;
   - maximum un titre de mentions legales;
   - aucune source brute dans les paragraphes principaux.
7. Si une preuve est utilisee dans plusieurs themes, conserver les themes d'usage dans
   `used_in_sections` ou equivalent compact sans dupliquer la preuve dans l'annexe.
8. Conserver le rendu free short, narrative v1 et legacy obsolete existants.
9. Ajouter les styles necessaires dans les CSS existants, sans style inline et en reutilisant les
   variables de couleur/marge/bordure deja presentes.
10. Verifier responsive desktop/mobile pour que les blocs longs ne se chevauchent pas.
11. Ne pas deplacer l'orchestration de `NatalInterpretation` hors de son owner feature.

## Hors Perimetre

- Changer le contrat backend ou le contenu genere.
- Supprimer les preuves publiques du contrat.
- Reintroduire les cartes factuelles legacy interdites.
- Modifier les quotas, exports PDF ou offres commerciales.
- Ajouter une nouvelle bibliotheque UI.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- Piece jointe utilisateur: DOM actuel `/natal` du 31/05/2026 18:22.
- `_story_briefs/cs-420-adapter-page-natal-rendu-free-basic-v2.md`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- Feuilles CSS existantes portant les classes `ni-*`, `natal-*` et variables associees.
- `frontend/src/styles/css-fallback-allowlist.md` si une variable CSS avec fallback est touchee.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-153` - `/natal` reste centre sur une lecture publique, sans cartes factuelles legacy.
  - `RG-154` - le DOM public ne doit pas exposer les marqueurs techniques denylistes.
  - `RG-158` - les accordeons narratifs modernes restent accessibles pour `narrative_natal_reading_v1`.
  - `RG-168` - `basic_natal_interpretation_v2` reste le contrat public canonique Basic V2.
  - `RG-048` - aucune nouvelle valeur fallback CSS non classee si les styles sont modifies.
  - `RG-073` - l'orchestration feature `NatalInterpretation` reste sous `frontend/src/features/natal-chart`.
- Required regression evidence:
  - `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
  - `rg -n "var\\(--[^,)]+," frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/styles`
  - `rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
  - `rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" frontend/src/components/natal-interpretation frontend/src/features/natal-chart`
- Registry enrichment expected:
  - Ajouter un nouvel invariant `RG-170` si la story cree une garde durable anti-duplication des
    sources et mentions legales Basic dans le DOM public.
- Allowed differences:
  - Le DOM Basic V2 devient plus court et moins repetitif.
  - Les sources publiques restent visibles mais deplacees en annexe unique.
  - Les lignes legales peuvent etre dedupliquees et fusionnees.

## Criteres D'acceptation

1. Un payload Basic V2 affiche le titre, l'introduction, les themes et la conclusion comme contenu
   principal, dans cet ordre.
2. Les preuves publiques ne sont plus rendues dans chaque theme.
3. Le DOM public contient au plus un bloc/titre `Ce que j'ai utilise pour ecrire cette interpretation`
   ou equivalent.
4. Le DOM public contient au plus un titre `Mentions legales`.
5. Les limitations et disclaimers Basic ne sont pas perdus; ils sont fusionnes/dedupliques dans un
   bloc final unique sans supprimer les mentions legales attendues par les autres branches.
6. Une meme preuve utilisee dans plusieurs themes n'apparait qu'une fois dans l'annexe; ses themes
   d'usage peuvent etre affiches en metadata compacte.
7. Aucun texte de source brute (`Luminaire: moon`, `Position planetaire: saturn, gemini`, etc.)
   n'apparait dans le corps principal.
8. Le rendu free short reste fonctionnel et n'affiche pas le message de regeneration.
9. Le rendu `narrative_natal_reading_v1` conserve ses accordeons et sources modernes.
10. Aucun style inline n'est ajoute.
11. Les tests couvrent Basic V2 avec sources dupliquees multi-themes, disclaimers dupliques et
    version propre.

## Commandes De Validation Minimales

Frontend:

```powershell
pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading
pnpm --dir frontend lint
pnpm --dir frontend build
```

Scans:

```powershell
rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "var\\(--[^,)]+," frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/styles
rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" frontend/src/components/natal-interpretation frontend/src/features/natal-chart
```

QA visuelle:

```powershell
# Demarrer la stack locale selon le script projet.
# Ouvrir /natal avec daconrilcy@hotmail.com et verifier desktop + mobile.
```

## Dependances

- CS-420 pour le rendu Free/Basic V2.
- CS-421 pour la qualite du contenu Basic.

## Risques

Le risque principal est de supprimer de la repetition en supprimant aussi de la tracabilite. La
story doit conserver les preuves publiques en annexe unique et verifier qu'elles restent
accessibles.

Risque secondaire: mutualiser trop largement les mentions legales et modifier les rendus free ou
narrative v1. Les tests doivent prouver que seule la branche Basic V2 change de structure.
