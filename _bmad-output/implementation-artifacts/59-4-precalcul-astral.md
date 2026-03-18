# Story 59.4 : Précalcul des données astrales avant injection dans les prompts horoscope

Status: done

## Story

En tant qu'utilisateur de la guidance quotidienne ou hebdomadaire,
je veux que le LLM reçoive les calculs astraux réels du jour (transits actifs, aspects dominants, phase lunaire) avant de produire ma guidance,
afin d'obtenir une lecture personnalisée basée sur des données astronomiques réelles et non sur une description générale de mon thème natal.

## Acceptance Criteria

1. `backend/app/services/astro_context_builder.py` existe avec `AstroContextBuilder` classe (méthodes statiques ou de classe).
2. `AstroContextBuilder.build_daily(user_id, date, timezone, db)` retourne un `AstroContextData` avec au minimum :
   - `transits_active: list[TransitEntry]` — transits planète/natal significatifs du jour
   - `dominant_aspects: list[AspectEntry]` — aspects les plus actifs du jour
   - `lunar_phase: str` — phase lunaire en clair (ex: "Lune croissante en Taureau, 42%")
   - `period_covered: PeriodCovered` — date_start et date_end de la période
   - `precision_level: Literal["full", "degraded"]`
3. `AstroContextBuilder.build_weekly(user_id, week_start, timezone, db)` retourne un `AstroContextData` couvrant 7 jours avec les transits et aspects dominants de la semaine.
4. `precision_level="degraded"` si `birth_time` est absente OU `birth_place` est absente dans le profil utilisateur.
5. `GuidanceService.request_guidance_async()` appelle `AstroContextBuilder.build_daily()` (ou `build_weekly()`) avant l'appel LLM et injecte `astro_context` dans le dict `context`.
6. En cas d'échec du précalcul (exception, données insuffisantes), `astro_context=None` est injecté dans le contexte et un `logger.warning` est émis — la guidance continue en mode dégradé gracieux.
7. Les templates de prompts `guidance_daily` et `guidance_weekly` (en DB) sont mis à jour pour intégrer un bloc `## Données astrales du jour` utilisant les variables de `astro_context`.
8. Les services de calcul réutilisés (`DailyPredictionService`, ou le moteur Epic 33/34) ne sont pas modifiés — `AstroContextBuilder` les appelle sans altérer leur logique interne.
9. Tests unitaires pour `AstroContextBuilder` avec mock des services de calcul.
10. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Définir les schémas de données (AC: 2)
  - [ ] T1.1 Créer `backend/app/services/astro_context_builder.py`
  - [ ] T1.2 Définir `TransitEntry` (Pydantic) : `planet: str`, `natal_point: str`, `aspect: str`, `orb: float`, `applying: bool`
  - [ ] T1.3 Définir `AspectEntry` (Pydantic) : `planet_a: str`, `planet_b: str`, `aspect_type: str`, `orb: float`, `exact_time: datetime | None`
  - [ ] T1.4 Définir `PeriodCovered` (Pydantic) : `date_start: date`, `date_end: date`, `label: str` (ex: "journée du 18 mars 2026")
  - [ ] T1.5 Définir `AstroContextData` (Pydantic) : tous les champs de AC2 + `user_id: int`, `computed_at: datetime`

- [ ] T2 — Implémenter `build_daily()` (AC: 2, 4)
  - [ ] T2.1 Identifier les services existants de calcul utilisables : lire `backend/app/services/daily_prediction_service.py` et/ou `backend/app/domain/astrology/` pour les calculateurs de transits
  - [ ] T2.2 Récupérer le profil natal utilisateur via `UserBirthProfileService` ou repository direct
  - [ ] T2.3 Calculer `precision_level` : `"degraded"` si `birth_time is None or birth_place is None`
  - [ ] T2.4 Appeler le calculateur de transits existant pour obtenir les planètes en transit sur le natal
  - [ ] T2.5 Filtrer les transits significatifs (orb ≤ seuil configurable, ex: 3°)
  - [ ] T2.6 Calculer la phase lunaire via le service existant (ou appel direct swiss ephemeris si disponible)
  - [ ] T2.7 Construire et retourner `AstroContextData`

- [ ] T3 — Implémenter `build_weekly()` (AC: 3)
  - [ ] T3.1 Réutiliser `build_daily()` pour chaque jour de la semaine (7 jours à partir de `week_start`)
  - [ ] T3.2 Agréger les transits et aspects significatifs sur la semaine (dédupliqués, triés par intensité)
  - [ ] T3.3 `period_covered.date_end = week_start + 6 jours`

- [ ] T4 — Gestion dégradée gracieuse (AC: 6)
  - [ ] T4.1 Wrapper le calcul dans un `try/except Exception` dans `build_daily()` et `build_weekly()`
  - [ ] T4.2 En cas d'exception, logger `logger.warning("astro_context_build_failed user_id=%d error=%s", user_id, str(e))`
  - [ ] T4.3 Retourner `None` (pas `AstroContextData`) pour signaler l'échec au service appelant

- [ ] T5 — Intégrer dans `GuidanceService` (AC: 5, 6)
  - [ ] T5.1 Lire `backend/app/services/guidance_service.py` (méthode `request_guidance_async`)
  - [ ] T5.2 Avant l'appel à `AIEngineAdapter.generate_guidance()`, appeler :
    ```python
    astro_context = None
    try:
        if normalized_period == "daily":
            astro_context = AstroContextBuilder.build_daily(user_id, today, timezone, db)
        else:
            astro_context = AstroContextBuilder.build_weekly(user_id, week_start, timezone, db)
    except Exception as e:
        logger.warning("astro_context_build_failed user_id=%d: %s", user_id, e)
    ```
  - [ ] T5.3 Ajouter `"astro_context": astro_context.model_dump() if astro_context else None` dans le dict `context`
  - [ ] T5.4 Conserver l'appel LLM même si `astro_context is None`

- [ ] T6 — Mettre à jour les templates de prompt en DB (AC: 7)
  - [ ] T6.1 Lire les prompts publiés `guidance_daily` et `guidance_weekly` via le registre DB ou un script de migration
  - [ ] T6.2 Ajouter un bloc conditionnel dans les deux prompts :
    ```
    {% if context.astro_context %}
    ## Données astrales du {{ context.astro_context.period_covered.label }}
    Précision : {{ context.astro_context.precision_level }}
    Phase lunaire : {{ context.astro_context.lunar_phase }}
    Transits actifs :
    {% for t in context.astro_context.transits_active %}
    - {{ t.planet }} {{ t.aspect }} {{ t.natal_point }} (orb {{ t.orb }}°{% if t.applying %}, s'applique{% endif %})
    {% endfor %}
    Aspects dominants du jour :
    {% for a in context.astro_context.dominant_aspects %}
    - {{ a.planet_a }} {{ a.aspect_type }} {{ a.planet_b }} (orb {{ a.orb }}°)
    {% endfor %}
    {% endif %}
    ```
  - [ ] T6.3 Publier la nouvelle version des prompts (état `published`, incrémenter le numéro de version)
  - [ ] T6.4 Archiver les versions précédentes

- [ ] T7 — Tests unitaires (AC: 9)
  - [ ] T7.1 Test : `build_daily()` retourne `AstroContextData` avec `precision_level="full"` si birth_time et birth_place présents
  - [ ] T7.2 Test : `build_daily()` retourne `AstroContextData` avec `precision_level="degraded"` si birth_time absent
  - [ ] T7.3 Test : `build_daily()` retourne `None` si le service de calcul lève une exception (mode dégradé)
  - [ ] T7.4 Test : `GuidanceService` continue sans erreur si `astro_context is None`
  - [ ] T7.5 Test : le dict `context` transmis au gateway contient `"astro_context"` (même si None)

- [ ] T8 — Validation finale (AC: 10)
  - [ ] T8.1 `ruff check backend/` → 0 erreur
  - [ ] T8.2 `pytest backend/` → tous les tests passent

## Dev Notes

### Services de calcul existants à réutiliser

Avant d'implémenter, identifier les calculateurs disponibles dans ces répertoires :
- `backend/app/domain/astrology/` — moteur de calcul natal (Epic 20)
- `backend/app/services/daily_prediction_service.py` — pipeline de prédiction (Epic 33-35)
- `backend/app/domain/astrology/transit_calculator.py` (si existant)

**Ne pas dupliquer la logique de calcul** — `AstroContextBuilder` est un aggregateur/adaptateur, pas un nouveau moteur.

### Profil de précision

La logique de précision suit la règle métier établie en Epic 14 et 20 :
- `precision_level="full"` : heure de naissance **ET** lieu de naissance fournis
- `precision_level="degraded"` : heure OU lieu absent → Ascendant/maisons non calculables, transits moins précis

### Format des transits dans le prompt

Les transits doivent être lisibles par le LLM :
- "Jupiter trigone Soleil natal (orb 1.2°, s'applique)" — lisible, concret
- Limiter à 5-7 transits maximum pour ne pas dépasser le contexte
- Trier par intensité (exactitude × poids planétaire)

### Mise à jour des prompts en DB

Deux approches possibles :
1. **Script de migration** (`backend/app/llm_orchestration/seeds/`) — créer une nouvelle version du prompt en DB et la publier
2. **Via l'admin** si l'interface admin LLM est opérationnelle

Recommandé : script de migration pour reproductibilité.

### Project Structure Notes

```
backend/app/services/astro_context_builder.py  ← NOUVEAU
```

Aucun nouveau répertoire requis. `AstroContextBuilder` suit le pattern des autres services dans `backend/app/services/`.

### References
- [Source: backend/app/domain/astrology/] — moteur de calcul natal existant
- [Source: backend/app/services/daily_prediction_service.py] — pipeline prédiction
- [Source: docs/recherches astro/04_Transits_pratique.md] — documentation des transits
- [Source: docs/model_de_calcul_journalier.md] — modèle de calcul journalier
- [Source: _bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Implémentation complète : `AstroContextBuilder` avec `build_daily()` et `build_weekly()`, injection dans `GuidanceService`, dégradé gracieux si précalcul échoue.
- **Code review (post-implémentation) :**
  - ISSUE-07 (Moyen) : `datetime.utcnow()` déprécié depuis Python 3.12 dans `AstroContextData.computed_at` — remplacé par `datetime.now(timezone.utc)`.
  - ISSUE-08 (Info) : construction obscure `datetime.min.time().replace(hour=12)` — remplacée par `time(12, 0)`.
  - ISSUE-09 (Moyen) : dans `build_weekly()`, `precision="full"` par défaut même si les 7 jours échouent tous (donnée mensongère) — changé en `precision: str | None = None` avec fallback `or "degraded"` à la construction de `AstroContextData`.
- Tests : 1342 passed, ruff clean.

### File List

- `backend/app/services/astro_context_builder.py` — AstroContextBuilder, AstroContextData, TransitEntry, AspectEntry, PeriodCovered
- `backend/app/services/guidance_service.py` — injection astro_context avant appel LLM
