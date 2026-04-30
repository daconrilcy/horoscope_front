# Finding Register - backend-tests

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-101 | High | High | data-integrity-risk | backend tests DB harness | E-009 | Les tests passent mais dependent encore d'une redirection globale `SessionLocal`, ce qui masque les frontieres de fixture et rend l'isolation fragile. | Migrer les tests DB vers une fixture/session explicite, puis retirer la redirection globale du conftest. | yes |
| F-102 | Medium | High | missing-canonical-owner | backend tests topology | E-001, E-002 | Toutes les racines sont collectees, mais la propriete canonique entre `app/tests` et `tests/*` reste implicite. | Documenter les racines autorisees et ajouter une garde qui compare les fichiers de tests aux `testpaths` approuves. | yes |
| F-103 | Medium | High | missing-guard-coverage | backend tests helpers | E-007 | La correction d'import croise est validee par scan manuel, mais la garde automatique ne surveille pas `backend/tests`. | Corriger le calcul de racine dans `test_backend_test_helper_imports.py` et ajouter une assertion de couverture des deux racines. | yes |
| F-104 | Medium | Medium | needs-user-decision | quality/ops tests | E-010 | Les checks docs, scripts PowerShell, backup/restore, secrets et securite sont melanges aux tests application backend. | Decider si ces tests restent dans pytest backend ou deviennent une suite qualite/ops explicite. | needs-user-decision |
| F-105 | Low | High | deprecation-warning | prediction tests | E-004 | La suite reste verte, mais 7 tests exercent une classe depreciee `LLMNarrator`. | Classifier ces tests comme garde de compatibilite temporaire ou migrer vers l'adapter canonique. | yes |

## F-101 - Harnais DB encore global et couplé à `SessionLocal`

- Severity: High
- Confidence: High
- Category: data-integrity-risk
- Domain: backend tests DB harness
- Evidence: E-009
- Expected rule: les tests DB doivent utiliser un acces explicite fourni par fixture/helper, sans dependance a une redirection globale de module.
- Actual state: 89 fichiers importent directement `SessionLocal`; `backend/app/tests/conftest.py` remplace globalement `engine`, `SessionLocal` et `_local_schema_ready`.
- Impact: l'ordre d'import et les globals de module restent une condition implicite de validite; une nouvelle racine ou un subprocess peut contourner le harnais.
- Recommended action: introduire un helper/fixture canonique, migrer les imports directs par lots, puis supprimer la redirection globale.

## F-102 - Topologie collectee mais ownership implicite

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend tests topology
- Evidence: E-001, E-002
- Expected rule: les racines de tests backend autorisees doivent etre documentees et gardees.
- Actual state: `app/tests` et `tests/*` sont tous collectes, mais aucun registre ne dit quelles racines sont canoniques, opt-in ou temporaires.
- Impact: le precedent probleme de decouverte peut revenir sous une autre racine sans signal d'architecture clair.
- Recommended action: creer un registre de topologie et une garde qui echoue si un test backend existe hors racines autorisees ou si `testpaths` diverge.

## F-103 - Garde anti import croise incomplète

- Severity: Medium
- Confidence: High
- Category: missing-guard-coverage
- Domain: backend tests helpers
- Evidence: E-007
- Expected rule: la garde doit scanner `backend/app/tests` et `backend/tests`.
- Actual state: `test_backend_test_helper_imports.py` definit `BACKEND_ROOT` avec `parents[2]`, ce qui vaut `backend/app`; la garde scanne donc `backend/app/tests`, mais pas `backend/tests`.
- Impact: un import croise ajoute dans `backend/tests` pourrait passer la garde, meme si le scan manuel actuel est propre.
- Recommended action: corriger la racine en `parents[3]` et ajouter un test qui prouve que `backend/tests` est dans les racines scannees.

## F-104 - Ownership des tests ops/qualite non decide

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: quality/ops tests
- Evidence: E-010
- Expected rule: les tests application backend et les checks qualite/ops doivent avoir une frontiere explicite.
- Actual state: les tests PowerShell, backup/restore, secrets scan, security verification et gouvernance docs restent collectes par `pytest`.
- Impact: la suite application peut etre ralentie ou bloquee par des checks d'outillage qui meritent peut-etre un job CI distinct.
- Recommended action: decision utilisateur: garder dans pytest backend, deplacer vers une suite qualite/ops, ou isoler par marqueurs.

## F-105 - Warnings deprecation `LLMNarrator`

- Severity: Low
- Confidence: High
- Category: deprecation-warning
- Domain: prediction tests
- Evidence: E-004
- Expected rule: une deprecation active dans une suite verte doit etre classee ou migree.
- Actual state: 7 tests de `tests/unit/prediction/test_llm_narrator.py` instancient `LLMNarrator`.
- Impact: dette faible a court terme, mais risque de suppression future sans garde de remplacement.
- Recommended action: migrer les tests vers `AIEngineAdapter.generate_horoscope_narration` ou documenter une compatibilite temporaire bornee.
