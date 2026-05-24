# CS-246 — Define Canonical Astrology Graph Family Registry

## Résumé

Créer le registre canonique des familles de graphes astrologiques afin que `CalculationGraph` devienne une base transversale gouvernée plutôt qu'une collection de codes dispersés.

Cette story remappe `SC-ARCH-001` depuis `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`.

## Contexte

CS-245 établit que `natal_chart_v1` existe, mais que les futures familles comme transits, synastrie, returns, progressions, profections, forecasting, scoring IA et narration ne disposent pas encore d'un propriétaire runtime explicite.

Sans registre, chaque nouvelle technique peut créer son propre code de famille, son propre modèle d'inputs et ses propres limites de cache. Le risque principal est une plateforme astrologique non gouvernable.

## Objectif

Définir une source de vérité interne listant chaque famille astrologique cible avec :

- un code stable ;
- un statut ;
- un owner cible ;
- les inputs requis ;
- le type de graphe attendu ;
- les objets requis ;
- les surfaces publiques autorisées ;
- les surfaces internes ;
- les besoins trace/replay ;
- la frontière cache/invalidation ;
- les blockers et décisions utilisateur.

## Périmètre inclus

1. Créer ou compléter un registre de familles runtime.
2. Couvrir au minimum `natal_chart_v1`, `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `lunar_return_v1`, `progressed_chart_v1`, `composite_chart_v1`, `profection_v1`, `forecasting_v1`, `ai_scoring_v1`, `narrative_generation_v1`.
3. Ajouter une validation empêchant les familles inconnues ou dupliquées.
4. Relier `natal_chart_v1` au registre sans changer son comportement public.
5. Documenter les blockers : astronomie, produit, doctrine, multi-chart, trace, cache.
6. Ajouter des tests unitaires ou architecture ciblés.

## Hors périmètre

- Implémenter une technique temporelle.
- Modifier l'API publique ou le frontend.
- Ajouter une migration DB.
- Exposer `chart_objects`.
- Choisir la première technique temporelle ; cette décision est portée par CS-253.

## Contrat attendu

Le registre doit permettre de répondre de façon déterministe à :

```text
Quel owner possède transit_chart_v1 ?
Quels inputs sont requis par synastry_chart_v1 ?
Quelle famille est bloquée par preuve astronomique ?
Quelle frontière de cache s'applique à natal_chart_v1 ?
```

Un format dataclass, enum + mapping typé, ou Pydantic interne est acceptable si le codebase le justifie. Le brief ne force pas un mécanisme spécifique, mais le contrat doit être typé et testable.

## Critères d'acceptation

1. Les familles obligatoires de CS-245 sont présentes dans une source canonique unique.
2. Chaque famille a un statut, un owner cible, des inputs, des blockers et une politique cache/trace.
3. `natal_chart_v1` reste compatible avec le runtime existant.
4. Les familles temporelles sont marquées bloquées tant que CS-250 n'est pas traitée ou risk-accepted.
5. Les tests échouent en cas de code de famille dupliqué ou non déclaré.
6. Aucun changement frontend/API public n'est introduit.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter une commande ciblée pour les tests du registre, par exemple `pytest -q app/tests/...`.

## Dépendances

- Source architecture : CS-245.
- Doit précéder CS-247, CS-248 et CS-253 pour les nouveaux graphes.

## Risques

Le risque principal est de sur-spécifier les familles non implémentées. Les valeurs inconnues doivent rester explicites (`blocked-by-product-decision`, `blocked-by-doctrine-decision`, `missing`) plutôt que d'inventer une implémentation.
