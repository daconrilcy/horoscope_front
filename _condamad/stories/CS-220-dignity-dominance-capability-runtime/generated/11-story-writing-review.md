<!-- Preuve de review redactionnelle de la story CS-220. -->

# CS-220 Story Writing Review

## Iteration 1 - findings

Verdict: CHANGES_REQUESTED

Findings:

- `00-story.md` melangeait les champs requis des payloads dignity et dominance,
  ce qui pouvait laisser croire que chaque payload devait porter tous les
  scores.
- L'evidence d'etat courant sur `PlanetDominanceEngine().calculate` contenait
  une phrase grammaticalement incorrecte.
- La section `Regression Guardrails` classait `RG-001` a `RG-143` comme
  non-applicables tout en listant `RG-135`, `RG-141` et `RG-142` comme
  applicables.
- Plusieurs criteres d'acceptation citaient des fichiers de test sans chemin
  complet, contrairement au niveau de precision attendu par le plan de
  validation.
- Les AC qui parlaient de projectors, enrichers et absence de texte narratif
  ne couvraient qu'un cote dignity ou dominance alors que l'exigence etait
  bilaterale.
- La numerotation sautait de la section 15 a la section 17 sans section
  `Internal Usage Search`, contrairement au format des stories voisines.

Corrections appliquees:

- Separation explicite des champs requis par payload et ajout d'une regle de
  projection sans recalcul.
- Correction de la phrase d'evidence 9.
- Reclassification des invariants non-applicables pour ne plus contredire les
  invariants applicables.
- Qualification des commandes de validation AC avec des chemins complets.
- Extension des AC6, AC7, AC8 et AC13 pour couvrir dignity et dominance.
- Ajout de la section `16. Internal Usage Search`.

## Iteration 2 - findings

Verdict: CHANGES_REQUESTED

Findings:

- Les corrections de chemins complets dans le tableau des AC faisaient depasser
  plusieurs lignes au-dela de la limite stricte de 180 caracteres.

Corrections appliquees:

- Ajout d'une note de prefixe pour les tests sous
  `backend/tests/unit/domain/astrology/`.
- Raccourcissement des cellules du tableau AC sans retirer les commandes
  completes du Validation Plan.

## Iteration 3 - findings

Verdict: CHANGES_REQUESTED

Findings:

- Les raccourcis de preuves des AC6, AC7, AC8 et AC13 etaient lisibles, mais
  plus assez concrets pour les validateurs de story.

Corrections appliquees:

- Separation des exigences dignity et dominance en AC distincts.
- Maintien de commandes `pytest` concretes dans chaque AC sans depasser la
  limite de longueur de ligne.
- Mise a jour des references AC des taches 2 et 4.

## Iteration 4 - findings

Verdict: CHANGES_REQUESTED

Findings:

- Trois lignes du tableau AC restaient au-dessus de la limite stricte de 180
  caracteres apres separation des AC.

Corrections appliquees:

- Raccourcissement des libelles AC6 et AC17.
- Raccourcissement de la preuve AC16 en s'appuyant sur le chemin relatif deja
  defini pour l'artefact `evidence/validation.md`.

## Iteration 5 - findings

Verdict: CHANGES_REQUESTED

Findings:

- La ligne AC17 restait a 183 caracteres.

Correction appliquee:

- Raccourcissement du libelle AC17 sans changer sa preuve executable.

## Iteration 6 - findings

Verdict: CHANGES_REQUESTED

Findings:

- La story couvrait le coeur du brief, mais ne rendait pas assez explicite la
  semantique de `supports_dignities` et `supports_dominance`.
- Les objets a exclure par defaut des dignites, comme angles, cuspides, maisons
  et etoiles fixes, n'etaient pas assez visibles dans les objectifs.
- Les tests attendus du brief sur les donnees minimales absentes, payloads sans
  capacite et payloads ciblant un code inconnu n'etaient pas portes par des AC
  dedies.
- Le guardrail anti-eligibilite par type ne couvrait pas explicitement les
  branches par code nominal ou liste `TRADITIONAL_PLANETS`.

Corrections appliquees:

- Ajout de la semantique des capacites dans le scope et l'etat cible.
- Ajout des exclusions par defaut pour les objets non dignifiables sans
  doctrine explicite.
- Ajout des AC21 a AC24 pour erreurs explicites, payloads incoherents,
  non-dignifiabilite par defaut et branches nominales.
- Extension des chemins interdits et scans de validation a `TRADITIONAL_PLANETS`,
  `planet_name ==` et `code in`.

## Iteration 7 - findings

Verdict: CLEAN

Aucune issue redactionnelle restante identifiee apres relecture complete.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
