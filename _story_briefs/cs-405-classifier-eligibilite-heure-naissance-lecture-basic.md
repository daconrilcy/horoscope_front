# CS-405 - Classifier L'Eligibilite De L'Heure De Naissance Pour La Lecture Basic

<!-- Commentaire global: ce brief cadre la gestion robuste des lectures natales Basic avec heure complete, approximative ou absente. -->

## Resume

Introduire `EligibilityContext` pour que le mode Basic fonctionne pour tous les utilisateurs,
y compris ceux sans heure de naissance fiable. Les maisons, angles, maitres de maisons et
noeuds par maison doivent etre automatiquement actives, prudentes ou exclues selon les
donnees disponibles.

## Contexte

Le plan source identifie un risque P1: le plan initial supposait une heure de naissance.
Or une lecture Basic doit rester utile avec une date seule. Sans heure fiable, le backend ne
doit pas interpreter l'Ascendant, le MC, les maisons, l'angularite ou les rulers de maisons.

## Objectif

Produire un contexte d'eligibilite stable:

```json
{
  "birth_time_status": "full_birth_time",
  "can_use_houses": true,
  "can_use_angles": true,
  "can_use_house_rulers": true,
  "can_use_lunar_nodes_by_house": true,
  "limitations": []
}
```

Les variantes minimales sont `full_birth_time`, `approximate_birth_time` et `date_only`.

## Perimetre Inclus

1. Identifier les sources existantes de date, heure locale, timezone, lieu et statut de
   resolution du theme.
2. Creer le builder `EligibilityContext` dans le domaine ou le service applicatif canonique.
3. Classifier `full_birth_time`, `approximate_birth_time` et `date_only`.
4. Desactiver automatiquement les familles dependantes des maisons et angles quand l'heure
   manque.
5. Produire une limitation publique lisible quand les maisons et l'Ascendant ne sont pas
   interpretes.
6. Ajouter des tests pour heure complete, heure approximative, date seule, timezone absente
   et theme calcule partiellement.
7. Ajouter des guards empechant un composant aval de re-activer localement les maisons sans
   passer par `EligibilityContext`.

## Hors Perimetre

- Modifier le calcul astrologique de base.
- Inventer une heure par defaut pour obtenir des maisons.
- Afficher une UI de saisie d'heure.
- Generer le texte narratif final.
- Changer les quotas ou entitlements.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `backend/app/services/user_profile/natal_chart_service.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/fixtures/golden/natal_test.yaml`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-144` - ne pas casser `NatalResult.chart_objects` ni les collections historiques.
  - `RG-145` a `RG-148` - consommer les payloads runtime existants sans recalcul local.
  - `RG-152` - ne pas exposer de donnees techniques dans la lecture publique.
  - `RG-154` - les limitations publiques ne doivent pas contenir d'identifiants internes.
  - `RG-156` - la matiere editoriale Basic reste diversifiee meme sans maisons.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_eligibility_context.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py`
  - `rg -n "house_number|ascendant|mc|house_ruler|angular" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant l'interdiction d'interpreter maisons/angles sans
    eligibilite.
- Allowed differences:
  - Les lectures sans heure perdent explicitement les sections maison/angle et gagnent une
    limitation publique.

## Criteres D'acceptation

1. Une naissance avec heure fiable active maisons, angles et rulers.
2. Une heure approximative active les surfaces sensibles avec niveau de confiance reduit.
3. Une date seule exclut Ascendant, MC, maisons, angularite et rulers de maisons.
4. La limitation publique est claire et non technique.
5. Les faits solaires, lunaires, signes, elements, modalites et aspects non dependants de
   l'heure restent disponibles.
6. Aucun fallback d'heure `12:00` ne sert a produire des interpretations de maisons.
7. Les tests prouvent que les composants aval respectent l'eligibilite.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_eligibility_context.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_date_only_reading_guards.py --tb=short
```

## Dependances

- CS-404.

## Risques

Le risque principal est de produire une lecture date-only faussement complete. La story doit
preferer une lecture plus courte et honnete a une interpretation precise fondee sur une heure
absente.
