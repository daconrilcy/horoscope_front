# CS-374 - Renforcer Exemples JSON Theme Astral Avec Textes Interpretation Reels

<!-- Commentaire global: ce brief cadre la regeneration des exemples JSON theme astral avec des sources interpretatives plus representatives des tables metier. -->

## Resume

Regenerer les exemples JSON `theme_astral` afin qu'ils demontrent mieux l'usage de textes d'interpretation reels ou production-like issus des tables metier, et pas seulement des textes minimaux seedes pour prouver le plumbing.

## Contexte

Les exemples CS-371 prouvent le squelette, les quotas et le passage par le repository. Mais les textes seedes localement restent generiques:

- `texte source issu du profil planetaire DB`;
- `contexte issu du profil maison DB`;
- `articulation issue du profil aspect DB`.

Pour valider la qualite redactionnelle future, les exemples doivent porter une matiere interpretative plus riche, representative et tracable.

## Objectif

Produire des exemples `free/basic/premium` qui contiennent:

- des textes interpretatifs plus proches des tables existantes;
- des `source_ref` explicites;
- une couverture claire des familles planetes, maisons, aspects, dominantes et signaux;
- des differences de densite lisibles entre profils;
- aucun appel provider LLM.

## Perimetre inclus

1. Identifier les sources existantes les plus representatives et autorisees.
2. Prioriser les textes deja presents dans les tables ou seeds applicatifs existants.
3. Reutiliser `InterpretationMaterialSourceRepository` autant que possible.
4. Eviter les textes inventes directement dans le generateur d'exemples.
5. Si une base locale de test est necessaire, seeder des textes production-like documentes et expliquer pourquoi les tables applicatives ne peuvent pas etre consommees directement.
6. Regenerer les trois payloads du scenario Paris 1973.
7. Mettre a jour `source-coverage.md` et `structure-comparison.md`.
8. Ajouter une validation qui echoue si les textes restent trop generiques.

## Hors perimetre

- Appeler un provider LLM.
- Modifier les regles astrologiques.
- Ajouter une nouvelle famille d'interpretation sans owner.
- Importer des textes non autorises ou non sources.

## Sources obligatoires

- `backend/app/infra/db/repositories/interpretation_material_source_repository.py`
- `backend/app/domain/astrology/interpretation/interpretation_material_builder.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/generate_examples.py`
- `_condamad/stories/CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan/evidence/validate_examples.py`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`
- `_condamad/audits/theme-astral-prompt-contract/**`

## Criteres d'acceptation

1. Les exemples sont regeneres par le chemin applicatif final ou un script qui reutilise les builders runtime.
2. Les textes d'interpretation ne sont pas des placeholders generiques.
3. Les sources DB ou production-like sont explicites dans `source_coverage`.
4. `interpretation_material` reste non vide dans les trois payloads.
5. La densite augmente de `free` vers `basic` puis `premium`.
6. Les JSON restent valides.
7. Aucun provider LLM n'est appele.
8. Le README explique clairement la nature des sources: production reelle, fixture production-like, ou mixte.
9. `validate_examples.py` echoue si des textes generiques connus reapparaissent.
10. Si des fixtures restent necessaires, elles sont nommees `production-like` et ne sont pas presentees comme preuve de contenu production.

## Commandes de validation minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B ..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\generate_examples.py
python -B ..\_condamad\stories\CS-371-generer-exemples-json-theme-astral-llm-v1-par-plan\evidence\validate_examples.py
```

Scans:

```powershell
rg -n "texte source issu|contexte issu|articulation issue|Texte source verifie|theme_astral_example_source" ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
rg -n "source_ref|interpretive_text|writing_hint|source_coverage|table_source_count" ..\_condamad\examples\prompt-generation-cartography\1973-04-24-1100-paris-theme-astral-v1
```

Le premier scan doit ne retourner aucun resultat dans les payloads finaux, sauf si une mention apparait dans un document de preuve pour expliquer une ancienne fixture supprimee.

## Risques

Le risque principal est de confondre exemple exploitable et verite de production. Si les textes restent des fixtures, ils doivent etre riches, explicitement declares comme fixtures production-like, et passer par le meme repository que le runtime.
