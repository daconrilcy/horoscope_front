# Story 60.1 : Cadrer la taxonomie publique des domaines

Status: ready-for-dev

## Story

En tant que développeur backend,
je veux définir une couche de projection publique qui fusionne les 12 domaines internes en 5 catégories publiques non redondantes,
afin que le front n'affiche plus "Carrière" et "Travail" séparément et que le wording soit homogène et premium.

## Acceptance Criteria

1. Un mapping explicite `domaine_interne → domaine_public` est défini et documenté dans un fichier Python dédié `backend/app/prediction/public_domain_taxonomy.py`.
2. Les 12 domaines internes (love, work, career, energy, mood, health, money, sex_intimacy, family_home, social_network, communication, pleasure_creativity) sont tous mappés vers exactement un domaine public.
3. Les 5 domaines publics cibles sont :
   - `pro_ambition` — "Pro & Ambition" (work + career)
   - `relations_echanges` — "Relations & échanges" (love + communication + social_network + sex_intimacy)
   - `energie_bienetre` — "Énergie & bien-être" (energy + health + mood)
   - `argent_ressources` — "Argent & ressources" (money)
   - `vie_personnelle` — "Vie personnelle" (pleasure_creativity + family_home)
4. Aucune catégorie publique n'est quasi synonyme d'une autre (validé par revue).
5. La fusion d'un domaine public agrège les scores internes par max (valeur la plus favorable de la catégorie publique).
6. L'ordre d'affichage par défaut est : pro_ambition, relations_echanges, energie_bienetre, argent_ressources, vie_personnelle.
7. Le fichier `public_domain_taxonomy.py` expose : `PUBLIC_DOMAINS` (dict ordonné de `PublicDomainEntry`), `map_internal_to_public(code: str) -> str | None`.
8. `pytest backend/` passe sans erreur. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Créer `backend/app/prediction/public_domain_taxonomy.py` (AC: 1, 2, 3, 6, 7)
  - [ ] T1.1 Définir `PublicDomainEntry(BaseModel)` : `key: str`, `label_fr: str`, `label_en: str`, `icon: str`, `internal_codes: list[str]`, `display_order: int`
  - [ ] T1.2 Remplir `PUBLIC_DOMAINS: dict[str, PublicDomainEntry]` avec les 5 entrées
  - [ ] T1.3 Implémenter `map_internal_to_public(code: str) -> str | None` — reverse lookup depuis `internal_codes`
  - [ ] T1.4 Implémenter `DISPLAY_ORDER: list[str]` = ordre d'affichage fixe
  - [ ] T1.5 Vérifier que tous les 12 codes internes sont couverts (assertion au module load ou test)

- [ ] T2 — Implémenter la règle de fusion de score (AC: 5)
  - [ ] T2.1 Créer `aggregate_public_domain_score(internal_scores: dict[str, float]) -> dict[str, float]`
  - [ ] T2.2 Règle : pour chaque domaine public, prendre le `max()` des scores des domaines internes qui lui appartiennent
  - [ ] T2.3 Si aucun code interne n'a de score → `None` (domaine absent du run)

- [ ] T3 — Brancher dans `PublicPredictionAssembler` (AC: 4)
  - [ ] T3.1 Lire `backend/app/prediction/public_projection.py` — classe `PublicPredictionAssembler`, méthode `assemble()`
  - [ ] T3.2 Dans `PublicCategoryPolicy`, ajouter une étape de mapping public avant construction des catégories
  - [ ] T3.3 Garder les catégories internes dans `_internal_categories` pour usage interne du moteur
  - [ ] T3.4 Ne pas supprimer les catégories internes du payload — les ajouter sous `categories_internal` (champ nouveau, rétrocompat)

- [ ] T4 — Mettre à jour les DTOs Pydantic (AC: 6)
  - [ ] T4.1 Dans `backend/app/api/v1/routers/predictions.py`, ajouter `DailyPredictionPublicDomain(BaseModel)` :
    `key: str, label: str, internal_codes: list[str], display_order: int`
  - [ ] T4.2 Ajouter champ `public_domains: list[DailyPredictionPublicDomain] | None = None` dans `DailyPredictionResponse`

- [ ] T5 — Mettre à jour les libellés i18n front (AC: 4)
  - [ ] T5.1 Localiser `frontend/src/utils/predictionI18n.ts`
  - [ ] T5.2 Ajouter les 5 entrées publiques en FR et EN
  - [ ] T5.3 Conserver les anciens codes internes (rétrocompat)

- [ ] T6 — Tests unitaires (AC: 8)
  - [ ] T6.1 Test : `map_internal_to_public("work")` → `"pro_ambition"`
  - [ ] T6.2 Test : `map_internal_to_public("career")` → `"pro_ambition"`
  - [ ] T6.3 Test : `map_internal_to_public("love")` → `"relations_echanges"`
  - [ ] T6.4 Test : tous les 12 codes internes ont un mapping valide
  - [ ] T6.5 Test : `aggregate_public_domain_score({"work": 14, "career": 18})` → `{"pro_ambition": 18}`
  - [ ] T6.6 Test : `PUBLIC_DOMAINS` contient exactement 5 entrées

## Dev Notes

### Domaines internes actuels (12 codes)
Source: `backend/app/prediction/domain_router.py`, seeds, `frontend/src/utils/predictionI18n.ts`

```
love, work, career, energy, mood, health,
money, sex_intimacy, family_home, social_network,
communication, pleasure_creativity
```

### Mapping cible

| Domaine interne | Domaine public | Clef publique |
|-----------------|---------------|---------------|
| work | Pro & Ambition | pro_ambition |
| career | Pro & Ambition | pro_ambition |
| love | Relations & échanges | relations_echanges |
| communication | Relations & échanges | relations_echanges |
| social_network | Relations & échanges | relations_echanges |
| sex_intimacy | Relations & échanges | relations_echanges |
| energy | Énergie & bien-être | energie_bienetre |
| health | Énergie & bien-être | energie_bienetre |
| mood | Énergie & bien-être | energie_bienetre |
| money | Argent & ressources | argent_ressources |
| pleasure_creativity | Vie personnelle | vie_personnelle |
| family_home | Vie personnelle | vie_personnelle |

### Règle de fusion (max)
Choisir le max car l'utilisateur bénéficie du point le plus favorable dans la catégorie publique.
Alternative à documenter si rejetée : mean (moins confiant pour l'utilisateur).

### PublicPredictionAssembler — point d'injection
- Fichier: `backend/app/prediction/public_projection.py`
- Classe: `PublicPredictionAssembler`
- Méthode: `assemble(snapshot, cat_id_to_code, engine_output, was_reused, reference_version, ruleset_version) -> dict`
- Ne pas casser la structure de retour existante (`categories`, `summary`, etc.)
- Ajouter `public_domain_ranking` comme nouveau champ optionnel

### Fichiers à NE PAS modifier dans cette story
- `backend/app/prediction/aggregator.py`
- `backend/app/prediction/calibrator.py`
- `backend/app/prediction/engine_orchestrator.py`
- Logique interne de scoring

### Project Structure Notes
- Nouveau fichier: `backend/app/prediction/public_domain_taxonomy.py`
- Modification: `backend/app/prediction/public_projection.py` (ajout couche projection)
- Modification: `backend/app/api/v1/routers/predictions.py` (nouveau DTO)
- Modification: `frontend/src/utils/predictionI18n.ts` (nouveaux libellés)

### References
- [Source: backend/app/prediction/public_projection.py] — PublicPredictionAssembler.assemble()
- [Source: backend/app/prediction/domain_router.py] — codes domaines internes
- [Source: backend/app/api/v1/routers/predictions.py] — DailyPredictionResponse, DailyPredictionCategory
- [Source: frontend/src/utils/predictionI18n.ts] — labels existants
- [Source: _bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
