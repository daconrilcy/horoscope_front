# CS-334 - Migrer Les Use Cases Natals Hors chart_json Legacy

<!-- Commentaire global: ce brief organise la migration des use cases natals vers l'entree LLM astrologique moderne. -->

## Resume

Migrer les use cases natals pour qu'ils declarent et consomment `llm_astrology_input_v1` comme entree astrologique moderne, au lieu de traiter `chart_json` ou `natal_data` comme owner prompt.

## Contexte

Les stories precedentes introduisent le contrat, son mapping, son branchement et son auditabilite. Cette story bascule les use cases natals vers cette surface moderne et confine le legacy.

Le but n'est pas de supprimer tout legacy immediatement, mais de faire du contrat moderne la voie normale.

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-331-mapper-richesse-astrologique-vers-llm-astrology-input.md`
- `_story_briefs/cs-332-brancher-llm-astrology-input-dans-execution-natale.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/03-legacy-transition.md`

Relire les fichiers de configuration:

- prompts et assemblies LLM natals;
- registry des use cases LLM;
- schemas d'input LLM;
- tests existants de gateway, renderer et service natal.

## Objectif

Faire de `llm_astrology_input_v1` l'entree declaree et testee des use cases natals modernes.

## Perimetre inclus

1. Identifier les use cases natals qui utilisent `chart_json`, `natal_data` ou des placeholders equivalents.
2. Mettre a jour les schemas d'input modernes pour declarer `llm_astrology_input_v1`.
3. Remplacer les placeholders `chart_json` par une entree structuree cible lorsque le use case est migre.
4. Nommer les branches de compatibilite restantes comme legacy transition.
5. Ajouter des tests de registry/configuration empechant un nouveau use case natal moderne de requerir `chart_json`.
6. Ajouter des tests de rendu prouvant que les use cases migres utilisent le contrat moderne.
7. Documenter les use cases non migres avec une raison explicite.

## Hors perimetre

- Modifier le contenu editorial fin des prompts.
- Modifier l'orchestration generale de generation LLM, les providers, retries, politiques d'appel ou workflows hors declaration d'entree.
- Traiter la securite, le CI ou les profils astrologues.
- Supprimer physiquement toutes les branches legacy.
- Modifier les endpoints publics ou le frontend.

## Criteres d'acceptation

1. Les use cases natals modernes declarent `llm_astrology_input_v1`.
2. Les placeholders ou schemas modernes ne traitent plus `chart_json` comme entree astrologique normale.
3. Les compatibilites restantes sont explicites et bornees.
4. Les tests de configuration detectent une regression vers `chart_json`.
5. Les tests de rendu prouvent que le payload moderne est utilise.
6. Aucun changement de fond editorial prompt n'est melange a la migration de donnees.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "llm_astrology_input_v1|chart_json|natal_data|input_schema|placeholder|legacy|fallback" app tests
```

Les occurrences legacy restantes doivent etre accompagnees d'une justification explicite: use case non migre documente, compatibilite temporaire bornee, ou guard negatif.

## Risques

Le risque principal est une migration partielle ou `llm_astrology_input_v1` existe mais ou `chart_json` reste le vrai contenu utile du prompt. Les tests doivent verifier la configuration et le rendu final.
