# Contrat Basic natal reading V2

<!-- Commentaire global: documentation technique du contrat Basic natal reading V2. -->

Ce contrat fixe le vocabulaire backend du futur moteur Basic sans brancher de nouvelle
generation narrative, sans route publique supplementaire et sans migration de donnees.

## Flux cible

`NatalResult` alimente `EligibilityContext`, puis `NatalFactGraph`,
`NatalSalienceModel`, `NatalNarrativeThemeModel`, `NatalSynthesis`,
`BasicNatalReadingPlan` et enfin `BasicNatalInterpretationV2`.

Le LLM est un redacteur controle: il transforme une matiere editoriale deja selectionnee
en texte lisible. Il n'est pas une source d'intelligence astrologique, ne choisit pas les
faits, ne calcule pas les priorites et ne recoit pas de donnees techniques publiques.

## Responsabilites

- `internal_evidence` reste reservee au backend pour l'audit, le diagnostic et la
  validation.
- `editorial_evidence` cadre le redacteur controle avec des faits selectionnes.
- `public_evidence` contient uniquement des justifications vulgarisees autorisees dans
  le payload public.
- `BasicNatalInterpretationV2` publie `locale`, `level=basic`,
  `engine_version=basic-natal-reading-v1` et
  `schema_version=basic_natal_interpretation_v2`.

Les champs techniques comme les scores, axes conditionnels, indices de prompt, entrees
d'audit et identifiants internes restent exclus du contrat public.
