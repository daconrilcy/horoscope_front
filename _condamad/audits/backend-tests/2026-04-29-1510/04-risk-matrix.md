# Risk Matrix - backend-tests

| Risk | Probability | Impact | Current control | Gap | Recommended response |
|---|---:|---:|---|---|---|
| DB tests utilisent une session autre que celle attendue | Medium | High | conftest global + suite complete verte | imports directs `SessionLocal` dans 89 fichiers | SC-101 |
| Nouveau test ajoute hors racines collectees | Low | Medium | `testpaths` plus complet qu'avant | pas de garde de topologie | SC-102 |
| Import croise ajoute dans `backend/tests` | Medium | Medium | scan manuel zero-hit | garde automatique ne couvre pas `backend/tests` | SC-103 |
| Tests ops ralentissent ou bloquent la suite applicative | Medium | Medium | suite verte actuelle | ownership non decide | SC-104 |
| Suppression future de `LLMNarrator` casse des tests tardivement | Low | Low | warnings visibles | pas de classification/migration | SC-105 |

## Risques Reduits Depuis Le Dernier Audit

- Decouverte pytest: risque reduit fortement, les racines conservees sont maintenant collectees.
- Story-numbered guards: risque reduit, aucun `test_story_*.py` actif.
- Cross-test imports: risque reduit par extraction et scan zero-hit, malgre la garde a corriger.
- Tests no-op: risque reduit par garde AST et remplacement du facade seed.
