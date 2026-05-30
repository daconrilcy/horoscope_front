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
| Desktop | Fil continu couvert par tests ; QA authentifiée locale rejouée sur `/natal` |
| Mobile | Ordre responsive couvert par CSS et tests ; nouvelle capture locale à rejouer après redémarrage de la stack |

## États dégradés

- `no_time`, `no_location` : alertes conservées (tests `NatalChartPage`)
- Interprétation rejetée : message contrôlé, pas de narrative (RG-150)
- Interprétation `complete` sans `narrative_natal_reading_v1` : message « Lecture complète à régénérer » (pas de fallback UI legacy)
- Quota / free lock : CTAs conservés dans `NatalInterpretationSection`

## Commandes exécutées (fix review)

```text
python -B -m pytest -q app/tests/integration/test_natal_interpretation_endpoint.py app/tests/integration/test_llm_qa_seed.py app/tests/integration/test_llm_qa_router.py tests/unit/test_narrative_natal_reading_v1.py tests/architecture/test_narrative_natal_reading_public_boundary.py --tb=short
python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or theme_astral)"
ruff check .
pnpm --dir frontend test -- NatalChartPage natalInterpretation natalInterpretationEvidence NatalAstrologerMode astrology-i18n
pnpm --dir frontend lint
pnpm --dir frontend build
```

Résultats : backend `9 passed`, pack CS-395 backend `17 passed`, frontend `182 passed`,
`ruff check .`, lint TypeScript et build Vite `PASS`.

Suites complètes rejouées :

- Backend : un défaut d'index documentaire a été détecté puis corrigé en classant le contrat
  narratif et ses trois exemples dans `backend/docs/ownership-index.md`. Relance finale :
  `3542 passed`, `2 skipped`, `1244 deselected`.
- Frontend : `1288 passed`, `8 skipped`, `5 failed`. Le test route intermittent repasse seul ;
  les quatre gardes déterministes restants portent sur une dette antérieure au delta
  (`NatalInterpretationContent` importe encore deux composants feature, le type local importe
  encore l'API, `NatalInterpretationEvidence` est orphelin et la fixture de garde de matrice
  manque déjà dans `HEAD`).

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
- Construction de `narrative_natal_reading_v1` étendue aux réponses complètes V1/V2/V3
  effectivement acceptées par le runtime ; une réponse legacy trop courte reste servie sans
  narrative pour demander une régénération, sans faire échouer l'endpoint.
- Suppression de la clé backend-only `evidence` du JSON public, y compris en relecture
  historique `GET /v1/natal/interpretations/{id}`.
- Priorité Basic/Premium donnée à la dernière interprétation complète persistée ; résumé
  legacy masqué sur une lecture complète sans narrative.
- Préférence de langue persistée prioritaire sur `navigator.language`.
- Seed QA natal opt-in aligné sur `daconrilcy@hotmail.com` / `admin123`, avec profil Paris
  et thème natal documentés dans `backend/README.md`.

## QA locale rejouée

- Connexion locale `daconrilcy@hotmail.com` : `PASS`.
- Compte local : profil naissance présent, un thème natal persisté.
- `/natal` desktop : hero Soleil/Lune/Ascendant lisible, interface et mentions légales FR.
- Mode astrologue fermé : `#natal-astrologer-mode-panel` absent du DOM.
- Interprétation complète historique sans narrative : message contrôlé « Lecture complète à
  régénérer », sans résumé legacy principal.
- Instance backend lancée avec le code courant sur `:8002` : relecture publique historique
  `public_has_evidence_key=False`.
- Captures authentifiées archivées : `output/playwright/cs-395-qa-natal-loaded.png`,
  `output/playwright/cs-395-qa-natal-scrolled.png`,
  `output/playwright/cs-395-qa-natal-desktop-complete.png`.

## Risques résiduels

- Le backend déjà lancé sur `:8001` pendant la QA utilisait encore le processus pré-patch ;
  le redémarrer avant la prochaine matrice live complète.
- La capture navigateur post-patch expire localement sur `Page.captureScreenshot`; les
  captures authentifiées archivées restent disponibles, mais la variante mobile post-patch
  doit encore être produite.
- La matrice live Premium avec mode astrologue ouvert et les états dégradés `no_time` /
  `no_location` restent à rejouer visuellement ; leurs gardes automatisés passent.
- La suite frontend complète reste rouge sur quatre gardes d'architecture natal préexistantes ;
  le pack fonctionnel CS-395, lint et build passent.
