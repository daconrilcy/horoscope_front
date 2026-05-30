# CS-395 — Non-régression lecture natale publique

Date: 2026-05-30 (fix review 2026-05-30).

## Matrices

| Profil | Backend narrative | Frontend lecture | Mode astrologue |
|---|---|---|---|
| free | Profil `free`, éléments limités | Résumé court (niveau `short`) | Masqué / upsell |
| basic | Profil `basic` | 5 chapitres + sources, ou message de régénération si narrative absente | Selon entitlement |
| premium | Profil `premium` | 5 chapitres + sources, ou message de régénération si narrative absente | Repliable, données expert |

| Viewport | Vérification |
|---|---|
| Desktop | Fil continu couvert par tests ; capture authentifiée locale bloquée par le compte de test invalide |
| Mobile | Ordre responsive couvert par CSS ; capture authentifiée locale bloquée par le compte de test invalide |

## États dégradés

- `no_time`, `no_location` : alertes conservées (tests `NatalChartPage`)
- Interprétation rejetée : message contrôlé, pas de narrative (RG-150)
- Interprétation `complete` sans `narrative_natal_reading_v1` : message « Lecture complète à régénérer » (pas de fallback UI legacy)
- Quota / free lock : CTAs conservés dans `NatalInterpretationSection`

## Commandes exécutées (fix review)

```text
pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py backend/tests/architecture/test_narrative_natal_reading_public_boundary.py
pytest -q backend/tests -k "natal and (narrative or rejected or theme_astral)"
pytest -q backend/tests
pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard natalInterpretationEvidence NatalAstrologerMode
pnpm --dir frontend lint
pnpm --dir frontend build
```

## Invariants ajoutés

- RG-152 — denylist narrative publique backend
- RG-153 — composition `/natal` trois couches
- RG-154 — denylist DOM lecture narrative publique (fix review)

## Correctifs appliqués (fix review)

- Suppression `EvidenceTags` de la vue publique ; `title` des pills = libellé lisible (mode astrologue)
- Suppression composants legacy orphelins (9 composants + 9 tests)
- Suppression du fallback UI legacy dans `InterpretationContent` (highlights, sections, projections B2C)
- Conservation des interprétations pré-`narrative_natal_reading_v1` avec message de régénération ;
  la révision Alembic `20260530_0141` reste une révision de compatibilité sans purge.
- Tests `natalPublicDomGuard` + scénario page `NatalChartPage` CS-395
- Documentation projection builder canonique (CS-392) dans le contrat

## Risques résiduels

- Le navigateur MCP Windows échoue avant navigation avec `windows sandbox failed: spawn setup refresh`.
- Le fallback Playwright atteint `/login`, mais le compte de test documenté répond `Invalid credentials`.
- Captures locales archivées : `output/playwright/cs-395-natal-initial.png` et `output/playwright/cs-395-login-result.png`.
- Les captures authentifiées desktop/mobile restent à produire avec un compte local valide.
