# Review adversariale des briefs CS-436 a CS-440

Date: 2026-06-01

## Perimetre

Review des briefs crees pour supprimer le legacy natal residuel:

- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md`
- `_story_briefs/cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md`
- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`
- `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`
- `_story_briefs/cs-440-zero-hit-legacy-natal-tests-guards.md`

## Verdict

Apres correction, les briefs sont coherents avec l'objectif "suppression du
legacy identifie" et ne proposent plus de compatibilite publique ou de chemin
runtime legacy comme solution acceptable.

## Issues trouvees et corrigees

1. `CS-436` autorisait encore une option "rendre non executable" pour
   `AIEngineAdapter.generate_natal_interpretation`.
   - Correction: exigence de suppression physique du symbole, sans stub, alias,
     facade ou garde runtime.

2. `CS-437` autorisait une conservation `archive/dev-only` dans des chemins
   potentiellement executables.
   - Correction: conservation autorisee uniquement comme preuve documentaire
     sous `_condamad`; aucun script legacy ne doit rester sous `backend/scripts`
     ou `backend/app/ops/llm/bootstrap`.

3. `CS-438` autorisait encore une compatibilite publique 410 et une migration
   readonly temporaire ambigue.
   - Correction: ancien POST absent de l'OpenAPI et de l'inventaire runtime
     public; anciennes donnees limitees a purge, admin/debug hors public ou
     migration one-shot vers slots modernes.

4. `CS-439` ne verrouillait pas assez le retrait des enveloppes front
   `NatalInterpretationResult`.
   - Correction: interdiction de conserver ce type comme enveloppe de
     compatibilite silencieuse dans le flux theme natal moderne.

5. `CS-440` pouvait encore laisser vivre des allowlists larges.
   - Correction: allowlists fermees aux preuves `_condamad` et tests
     d'extinction; aucun code runtime legacy sous `backend/app` ou `frontend/src`.

## Validation documentaire

Commandes executees:

```powershell
rg -n "ou rendu|deprecier|stub|facade publique 410|compatibilite 410|archive/dev-only|script executable|temporair|peut rester|si une compat" _story_briefs\cs-436-supprimer-service-generation-natale-legacy.md _story_briefs\cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md _story_briefs\cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md _story_briefs\cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md _story_briefs\cs-440-zero-hit-legacy-natal-tests-guards.md
rg -n "^# CS-|## Resume|## Perimetre Inclus|## Hors Perimetre|## Sources Obligatoires|## Regression Guardrails|## Criteres D'acceptation|## Commandes De Validation Minimales|## Dependances|## Risques" _story_briefs\cs-436-supprimer-service-generation-natale-legacy.md _story_briefs\cs-437-supprimer-catalogues-seeds-scripts-prompts-nataux-legacy.md _story_briefs\cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md _story_briefs\cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md _story_briefs\cs-440-zero-hit-legacy-natal-tests-guards.md
```

Les hits restants sont intentionnels:

- `stub` apparait dans CS-436 pour l'interdire.
- `script executable` apparait dans CS-437 pour l'interdire.
- `facade publique 410` et `compatibilite 410` apparaissent dans CS-438 pour les interdire.
- `peut rester` apparait dans CS-439 uniquement pour `variant_code` hors commande de generation.
- `temporaires` apparait dans CS-440 pour decrire les anciennes allowlists a fermer.

## Risques residuels

- Les futurs implementateurs devront verifier que les tests admin LLM ne gardent
  pas les anciens use cases comme fixtures positives.
- La suppression de l'API historique peut imposer de retirer ou remplacer les
  actions PDF/delete si aucun endpoint moderne n'existe encore.
