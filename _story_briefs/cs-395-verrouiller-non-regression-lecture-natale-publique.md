# CS-395 - Verrouiller La Non-Regression De La Lecture Natale Publique

<!-- Commentaire global: ce brief cadre les gardes et la QA finale de la refonte narrative /natal. -->

## Resume

Fermer la refonte narrative `/natal` par des gardes backend/frontend et une QA navigateur
multi-profils. La preuve finale doit garantir que la vue publique affiche des conclusions
narratives, que les justifications astrologiques restent vulgarisees et que les details
techniques ne fuient qu'apres ouverture explicite du mode astrologue autorise.

## Contexte

CS-390 a produit l'inventaire, CS-391 et CS-392 ont defini puis implemente le contrat narratif,
CS-393 a restructure la page et CS-394 a ajoute la justification de fin de lecture. Il faut
maintenant transformer les decisions produit en preuves executables et visuelles durables.

## Objectif

Prouver et verrouiller:

```text
vue publique = narration
fin de lecture = justification astrologique vulgarisee
mode astrologue = detail technique explicite et replie
```

## Perimetre inclus

1. Ajouter des tests backend sur la denylist de texte public narratif.
2. Ajouter des tests frontend DOM qui interdisent codes, scores et observabilite dans la vue
   publique repliee.
3. Tester free, basic et premium, avec mode astrologue ferme puis ouvert pour premium.
4. Tester les etats no-time, no-location, entitlement, loading, empty et rejected.
5. Capturer une QA navigateur desktop et mobile avec l'utilisateur test.
6. Produire un rapport final de non-regression.
7. Enrichir le registre `regression-guardrails.md` avec les invariants durables crees par
   CS-391 a CS-394.

## Hors perimetre

- Ajouter de nouvelles fonctionnalites produit.
- Modifier les calculs astrologiques.
- Affaiblir les gardes accepted/rejected.
- Autoriser des fuites techniques par allowlist large.

## Livrable attendu

Creer:

```text
_condamad/reports/cs-395-non-regression-lecture-natale-publique.md
```

Le rapport doit contenir:

1. Matrice free/basic/premium.
2. Matrice desktop/mobile.
3. Etats degrades testes.
4. Captures avant/apres.
5. Resultats backend/frontend.
6. Nouvelles lignes `RG-XXX` ajoutees au registre.
7. Risques residuels.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047`, `RG-052` - styles frontend canoniques.
  - `RG-071`, `RG-073` - ownership frontend natal preserve.
  - `RG-129` - pas de recalcul astrologique frontend.
  - `RG-149` - pipeline prompt natal moderne preserve.
  - `RG-150` - rejets LLM exclus des routes publiques.
  - `RG-151` - identite stable des aspects preservee.
- Registry enrichment required:
  - Ajouter un invariant sur la denylist publique narrative.
  - Ajouter un invariant sur la composition `/natal` en trois couches.
- Required regression evidence:
  - `pytest -q backend/tests -k "natal and (narrative or rejected or theme_astral)"`
  - `pnpm --dir frontend test -- NatalChartPage natalInterpretation natalInterpretationEvidence NatalAstrologerMode`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "visibility_expression|frustration_pressure|condition_axis:|centrality score|interpretive_signal_ids|audit_input|projection_version" frontend/src`
- Allowed differences:
  - Aucun delta fonctionnel hors corrections de non-regression identifiees par la QA.

## Criteres d'acceptation

1. Les tests backend refusent les fuites techniques dans le contrat narratif public.
2. Les tests frontend prouvent l'absence de codes, scores et metadata dans le DOM public.
3. Le mode astrologue ferme ne rend aucun detail technique.
4. Le mode astrologue premium ouvert continue d'afficher les donnees experts autorisees.
5. Les etats free/basic/premium et degrades sont couverts.
6. Les captures desktop et mobile montrent un parcours lisible en cinq chapitres.
7. Le rapport final trace commandes, resultats et risques residuels.
8. Le registre contient les nouveaux invariants durables.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or theme_astral)"
```

Frontend:

```powershell
cd frontend
pnpm test -- NatalChartPage natalInterpretation natalInterpretationEvidence NatalAstrologerMode
pnpm lint
pnpm build
```

Depuis la racine:

```powershell
rg -n "visibility_expression|frustration_pressure|condition_axis:|centrality score|interpretive_signal_ids|audit_input|projection_version" frontend/src
```

## Dependances

- CS-390 a CS-394.

## Risques

Le risque principal est d'accepter des allowlists trop larges qui masquent de nouvelles
fuites. Toute autorisation residuelle doit etre precise, justifiee et rattachee au mode
astrologue explicitement ouvert.
