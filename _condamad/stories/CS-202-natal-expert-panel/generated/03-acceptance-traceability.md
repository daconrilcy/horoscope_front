# Acceptance Traceability - CS-202

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Rend `dignities.sect` sans valeur inferee. | `NatalExpertPanel` section `Secte du theme`; API types `ChartSectResult`. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC2 | Rend `sect_condition` par planete. | `PlanetSectBlock` lit `dignities.planets[*].sect_condition`. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC3 | Groupe in/out-of-sect depuis champs explicites. | `groupSectConditions()` utilise `is_in_sect`, `is_out_of_sect`, puis groupe neutre. | Test grouping PASS + scans constants doctrine PASS. | PASS |
| AC4 | Rend hayz/out-of-sect depuis `advanced_conditions`. | `AdvancedConditionsBlock` affiche `condition_code` et `condition_type`. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC5 | Rend les syntheses de score de dignite par planete. | `DignityScoresBlock` affiche scores et breakdowns. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC6 | Rend les champs techniques des profils conditionnels. | `ProfilesBlock` affiche axes, score et niveau. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC7 | Rend les classements des planetes dominantes. | `DominantPlanetsBlock` affiche top/ruler/elevated et facteurs. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC8 | Rend `interpretation_adapter` sans prose narrative. | `InterpretationAdapterBlock` affiche signaux/themes/listes factuels; pas de LLM. | Test PASS + scan `OpenAI|AIEngineAdapter|prompt_hint|personalized|conseil` classe. | PASS |
| AC9 | Les payloads indisponibles rendent des fallbacks factuels. | Etats loading, error, chart absent, payload ancien, vide et no-time. | `npm --prefix frontend test -- NatalExpertPanel` PASS. | PASS |
| AC10 | Les symboles astrologiques frontend interdits sont absents. | Aucun calcul doctrinal local dans le panneau. | Scans RG-129 PASS; hits narratifs autorises classes. | PASS |
| AC11 | La regression backend CS-201 passe. | Aucun fichier backend interdit modifie. | Pytest backend cible PASS, 35 tests. | PASS |
| AC12 | Evidence before/after/validation enregistree. | `evidence/frontend-expert-panel-before.md`, sample JSON, after et validation. | Evidence `rg` checks PASS, sample JSON parse PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
