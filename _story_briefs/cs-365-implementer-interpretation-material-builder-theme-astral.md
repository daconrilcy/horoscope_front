# CS-365 - Implementer Interpretation Material Builder Theme Astral

<!-- Commentaire global: ce brief cadre le builder qui transforme les calculs astrologiques et tables metier en matiere interpretative pour le LLM. -->

## Resume

Implementer un `InterpretationMaterialBuilder` pour la feature `theme_astral`, capable de consommer les calculs astrologiques complets et les textes/logiques d'interpretation existants afin de produire une matiere interpretative structuree, scoree et exploitable par le LLM.

## Contexte

Le payload actuel expose surtout des faits astrologiques. Le nouveau contrat exige un bloc `interpretation_material` issu des tables et logiques metier:

- interpretations planete-signe;
- interpretations planete-maison;
- interpretations d'aspects;
- dominantes;
- tensions;
- ressources;
- leviers d'integration;
- warnings et limites.

## Objectif

Construire un builder domain/service qui:

- recupere les textes d'interpretation existants;
- les rattache aux faits calculees;
- selectionne les textes pertinents pour `theme_astral`;
- score et hierarchise les themes;
- produit une structure stable pour `theme_astral_llm_input_v1`;
- garde les preuves et references en validation/audit-only.

## Perimetre inclus

1. Lire CS-361 et CS-363.
2. Identifier les repositories/services de textes a reutiliser.
3. Implementer le builder sans dupliquer les requetes et sans SQL cache dans UI.
4. Ajouter des DTO/contrats si necessaire.
5. Ajouter des tests unitaires de matching calcul -> texte.
6. Ajouter des tests de non-invention: aucun `interpretation_material` sans source.
7. Ajouter des tests de quantite par delivery profile.

## Hors perimetre

- Modifier le gateway provider.
- Modifier les output schemas.
- Supprimer le legacy.
- Appeler un provider LLM.
- Ajouter une nouvelle source de textes si les tables existantes suffisent.

## Sources obligatoires

- `_condamad/audits/theme-astral-prompt-contract/**/01-audit-usage-tables-textes-interpretation.md`
- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/domain/astrology/**`
- `backend/app/infra/db/repositories/**`
- `backend/app/infra/db/models/**`
- `backend/tests/unit/domain/astrology/**`
- `backend/tests/integration/**`

## Structure cible de `interpretation_material`

Le builder doit produire une forme stable de ce type:

```json
{
  "planet_sign_interpretations": [],
  "planet_house_interpretations": [],
  "aspect_interpretations": [],
  "dominant_themes": [],
  "tensions": [],
  "resources": [],
  "integration_levers": [],
  "warnings": []
}
```

Chaque item doit contenir au minimum:

- `source_ref`;
- `fact_ref`;
- `theme`;
- `keywords`;
- `interpretive_text` ou `writing_hint`;
- `risk`;
- `resource`;
- `weight`;
- `selection_reason`.

## Criteres d'acceptation

1. Le builder existe et a un owner clair.
2. Les textes viennent de sources existantes auditees, pas de constantes inventees.
3. Chaque item interpretatif reference un fait astrologique calcule.
4. Les items sont scores et limites selon le delivery profile.
5. La structure est identique entre `free`, `basic`, `premium`.
6. Les quantites varient par delivery profile.
7. Les tests prouvent que les textes tables atteignent le contrat LLM.
8. Les tests prouvent qu'aucun texte d'interpretation absent de source n'est fabrique.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/domain/astrology tests/integration --tb=short
rg -n "InterpretationMaterialBuilder|interpretation_material|planet_sign_interpretations|aspect_interpretations|integration_levers|source_ref|fact_ref" app tests
```

## Risques

Le risque principal est de reintroduire un dump encyclopedique. Le builder doit selectionner et hierarchiser la matiere, pas tout transmettre.
