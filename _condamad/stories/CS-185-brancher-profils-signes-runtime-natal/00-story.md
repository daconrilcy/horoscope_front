# Story CS-185 brancher-profils-signes-runtime-natal: Brancher les profils de signes dans le runtime natal

Status: done

## 1. Objective

Faire de `astral_sign_profiles`, `astral_elements`, `astral_modalities` et
`astral_polarities` la source runtime effective des caracteristiques structurelles
des signes natals. Apres implementation, le flux natal expose des contrats types pour
les familles `element`, `modality` et `polarity`, ainsi que tout attribut enrichi deja
source par le schema actuel, afin d'alimenter les balances, signatures et
interpretations structurees sans constante locale ni fallback silencieux.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-18 sur les tables actuellement sous-exploitees.
- Reason for change: `astral_sign_profiles` est seedee et testee, mais le runtime natal ne consomme
  aujourd'hui que `element`, `modality` et `polarity` quand ces champs arrivent deja dans le payload
  `signs`; les profils DB canoniques et leurs taxonomies ne sont pas charges comme source de verite
  runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology`
- In scope:
  - Etendre le chargement infra du runtime astrology pour joindre `astral_sign_profiles` aux signes.
  - Etendre les contrats `SignReferenceData` et `SignRuntimeData` avec les attributs structurels
    disponibles et DB-backed.
  - Alimenter `ChartSignatureCalculator` avec les familles structurelles qui deviennent utiles
    pour balances et signatures.
  - Ajouter des tests repository, mapper, builder, signature et guard anti-retour.
- Out of scope:
  - Modifier le frontend.
  - Ajouter une nouvelle table DB ou une migration de schema.
  - Reecrire les textes editoriaux, prompts LLM ou profils planetaires.
  - Deplacer la logique de prediction quotidienne ou les poids produit.
- Explicit non-goals:
  - Ne pas recreer les listes `element`, `modality`, `polarity`, `seasonal quadrant`,
    `fertility`, `voice`, `humane/bestial` sous forme de constantes Python.
  - Ne pas modifier les libelles i18n de signes traites par `astral_sign_translations`.
  - Ne pas contourner `RG-093`, `RG-095`, `RG-107`, `RG-108`, `RG-112`, `RG-114`.
  - Ne pas introduire de fallback "unknown", "neutral" ou valeur par defaut silencieuse pour un profil manquant.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story enrichit un contrat runtime existant et doit preserver le calcul natal
  tout en changeant la source runtime observable des profils de signes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les themes avec DB complete peuvent exposer plus de donnees structurelles.
  - Les balances element/modality doivent rester coherentes avec les donnees seed existantes.
  - Un profil manquant ou incomplet doit produire une erreur d'integrite explicite, pas un fallback.
  - Aucun contrat HTTP public ne doit changer sans preuve OpenAPI et decision separee.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: les colonnes actuelles de `astral_sign_profiles` ne couvrent pas encore
  `seasonal quadrant`, `fertility`, `voice` ou `humane/bestial` et qu'une implementation exigerait
  une migration de schema ou une source canonique nouvelle.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La preuve doit venir du chargement DB runtime, pas d'un scan statique. |
| Baseline Snapshot | yes | Les balances et signatures doivent etre comparees avant/apres. |
| Ownership Routing | no | Les owners infra/domain existent deja et ne changent pas structurellement. |
| Allowlist Exception | no | Aucune exception ou fallback de profil n'est autorise. |
| Contract Shape | yes | Les dataclasses runtime de signes et signature sont enrichies. |
| Batch Migration | no | Une seule verticale runtime natal est visee. |
| Reintroduction Guard | yes | La story ajoute un guard de source DB-backed pour empecher le retour de mappings locaux. |
| Persistent Evidence | yes | Les snapshots et preuves de chargement doivent rester dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - Runtime artifact: SQLAlchemy `MetaData` et DB schema migre par Alembic pour
    `astral_sign_profiles`, `astral_elements`,
    `astral_modalities`, `astral_polarities` et `astral_signs`.
  - Seed applicatif pour les lignes canoniques de profils et taxonomies.
  - `AstrologyRuntimeReferenceRepository.load()` retourne `AstrologyRuntimeReference.signs`.
  - `AstrologyRuntimeReferenceMapper` convertit les rows infra en `SignReferenceData`.
- Secondary evidence:
  - Scans cibles sur `backend/app/domain/astrology` et `backend/app/services/natal`.
  - Tests unitaires mapper/builder/signature.
- Static scans alone are not sufficient for this story because:
  - Le risque principal est qu'un theme natal continue a fonctionner avec des signes partiels
    non profiled; seul le chargement runtime DB prouve la source effective.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-after.json`
- Expected invariant:
  - Les 12 signes restent charges dans le meme ordre.
  - Les champs deja publics du theme natal restent stables sauf ajout additif explicitement documente.
  - Les balances element/modality continuent a utiliser les poids de `SignRuntimeData`.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: la story conserve la frontiere existante infra charge, domain calcule, services orchestrent.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - Domain dataclasses runtime.
- Fields:
  - `SignReferenceData.element: str`
  - `SignReferenceData.modality: str`
  - `SignReferenceData.polarity: str`
  - `SignRuntimeData.element: str`
  - `SignRuntimeData.modality: str`
  - `SignRuntimeData.polarity: str`
- Candidate fields requiring an existing canonical DB source before implementation:
  - `seasonal_quadrant`
  - `fertility`
  - `voice`
  - `humanity`
- Required fields:
  - `element`, `modality`, `polarity` pour les 12 signes, lus depuis les FK de profil.
- Optional fields:
  - Aucun champ structurel supplementaire ne doit etre ajoute sans source DB canonique existante;
    si un champ candidat manque du schema actuel, bloquer et documenter la decision utilisateur requise.
- Status codes:
  - No HTTP status change expected.
- Serialization names:
  - Identiques aux noms runtime si projection publique additive approuvee; sinon non applicable.
- Frontend type impact:
  - Aucun type frontend ne doit changer dans cette story.
- Generated contract impact:
  - Produire une note OpenAPI confirmant que les schemas publics restent inchanges si aucune projection API n'est modifiee.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Runtime before | `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-before.json` | Before. |
| Runtime after | `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/sign-profile-runtime-after.json` | After. |
| OpenAPI impact | `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/openapi-impact.md` | API impact. |
| Guard evidence | `_condamad/stories/CS-185-brancher-profils-signes-runtime-natal/evidence/guard-evidence.md` | Guards. |

## 4i. Reintroduction Guard

- Reintroduction guard: required
- Reason: meme sans suppression de route ou de module legacy, cette story cree une dependance runtime
  durable envers les profils DB-backed et doit bloquer le retour de mappings locaux.
- Required source guard: ajouter ou etendre un test qui echoue si les profils de signes ne viennent
  plus de `astral_sign_profiles` et des FK `astral_elements`, `astral_modalities`, `astral_polarities`.
- Executable evidence:
  - `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`
  - `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`
  - `rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"`

## 4j. Source Finding Closure

For non-audit stories:

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/infra/db/models/reference.py` - `AstralSignProfileModel` existe avec
  FK vers `AstralElementModel`, `AstralModalityModel` et `AstralPolarityModel`.
- Evidence 2: `backend/app/services/prediction/reference_seed_service.py` - `_ensure_astral_sign_profiles`
  seed 12 profils et les taxonomies element/modality/polarity.
- Evidence 3: `backend/app/infra/db/repositories/reference_repository.py` - le payload `signs` contient
  actuellement `code` et `name`, sans jointure vers `astral_sign_profiles`.
- Evidence 4: `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - le mapper sait
  lire `element`, `modality`, `polarity` si elles sont deja dans le payload.
- Evidence 5: `backend/app/domain/astrology/builders/sign_runtime_builder.py` - `SignRuntimeData`
  recopie `element`, `modality`, `polarity` depuis `SignReferenceData`, mais pas les autres profils.
- Evidence 6: `backend/app/domain/astrology/interpretation/chart_signature.py` - les balances
  `elements` et `modalities` dependent des champs presents dans `SignRuntimeData`.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage,
  notamment `RG-093`, `RG-095`, `RG-107`, `RG-108`, `RG-112` et le nouvel invariant `RG-114`.

## 6. Target State

After implementation:

- `AstrologyRuntimeReferenceRepository.load()` charge les profils de signes DB et refuse une DB complete
  sans 12 profils exploitables.
- `SignReferenceData` et `SignRuntimeData` portent les attributs structurels disponibles sans valeur
  par defaut silencieuse.
- `build_sign_runtime_data()` conserve les profils des signes meme sans occupant planetaire.
- `ChartSignatureCalculator` peut produire ou preparer des balances structurelles depuis les profils
  runtime, sans recreer les taxonomies localement.
- Les tests prouvent que les donnees viennent des tables `astral_sign_profiles`,
  `astral_elements`, `astral_modalities`, `astral_polarities`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-093` - les signes astraux restent modelises par `astral_signs`, `astral_sign_profiles`
    et les taxonomies canoniques.
  - `RG-095` - `domain/astrology` ne doit pas importer prediction pour calculer les signatures.
  - `RG-107` - les payloads SQL/JSON libres restent confines a l'infra et convertis en contrats immutables.
  - `RG-108` - les vocabulaires DB-backed ne doivent pas etre recréés en constantes locales.
  - `RG-112` - les constantes metier astrologiques DB-backed ne doivent pas revenir.
  - `RG-114` - les profils structurels de signes doivent rester lus depuis `astral_sign_profiles`.
- Non-applicable invariants:
  - `RG-109` - la story ne traite pas les libelles localises des signes.
  - `RG-110` - la story ne modifie pas `backend/app/domain/prediction`.
- Required regression evidence:
  - Tests repository/mapper prouvant le chargement DB des profils.
  - Tests builder/signature prouvant l'usage runtime.
  - Scan negatif sur constantes locales de profils de signes dans `domain/astrology`.
- Allowed differences:
  - Ajout additif de champs runtime internes.
  - OpenAPI inchangé, sauf decision explicite documentee dans `openapi-impact.md`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Repository joint les 12 profils de signes. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC2 | Dataclasses runtime sans `dict` metier. | Evidence profile: `json_contract_shape`; `pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py`. |
| AC3 | Profil manquant bloque le chargement. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC4 | Signatures utilisent les profils runtime. | Evidence profile: `runtime_openapi_contract`; `pytest -q tests/unit/domain/astrology/test_chart_signature.py`. |
| AC5 | Champ non sourceable bloque sans fallback. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC6 | Guardrails DB-backed restent verts. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`. |
| AC7 | Evidence artifacts are produced. | Evidence profile: `persistent_evidence`; `pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'etat initial runtime (AC: AC1, AC7)
  - [ ] Generer `evidence/sign-profile-runtime-before.json` depuis `AstrologyRuntimeReferenceRepository.load("1.0.0")`.
  - [ ] Documenter les champs signes presents avant modification.

- [ ] Task 2 - Charger les profils DB dans l'infra (AC: AC1, AC3)
  - [ ] Etendre le repository ou la source payload pour joindre `AstralSignProfileModel`, `AstralElementModel`, `AstralModalityModel`, `AstralPolarityModel`.
  - [ ] Ajouter une validation bloquante: 12 profils, 12 `element`, 12 `modality`, 12 `polarity`, codes inconnus interdits.
  - [ ] Ajouter un test negatif pour profil manquant ou FK manquante.

- [ ] Task 3 - Etendre les contrats runtime de signe (AC: AC2, AC5)
  - [ ] Ajouter les champs structurels disponibles aux dataclasses runtime.
  - [ ] Refuser ou documenter explicitement tout attribut demande sans colonne/source canonique.
  - [ ] Mettre a jour les factories de tests sans recreer un referentiel concurrent.

- [ ] Task 4 - Brancher builder et signature (AC: AC2, AC4)
  - [ ] Faire transiter les profils enrichis via `build_sign_runtime_data()`.
  - [ ] Etendre `ChartSignatureCalculator` uniquement si le contrat de signature existant peut recevoir
    des balances additionnelles sans changement public non approuve.
  - [ ] Ajouter les tests de classement/tie-break necessaires.

- [ ] Task 5 - Ajouter guards et preuves finales (AC: AC6, AC7)
  - [ ] Etendre un guard DB-backed pour interdire les constantes locales de profils de signes.
  - [ ] Produire `evidence/sign-profile-runtime-after.json`, `openapi-impact.md` et `guard-evidence.md`.
  - [ ] Executer le plan de validation complet dans le venv.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstralSignProfileModel`, `AstralElementModel`, `AstralModalityModel`, `AstralPolarityModel`
    comme source DB.
  - `AstrologyRuntimeReferenceRepository` et `AstrologyRuntimeReferenceMapper` pour la frontiere infra.
  - `SignReferenceData`, `SignRuntimeData`, `build_sign_runtime_data()` et `ChartSignatureCalculator`.
  - `tests/factories/astrology_runtime_reference_factory.py` pour les fixtures runtime.
- Do not recreate:
  - mappings signe vers element/modalite/polarite;
  - listes locales `fire/earth/air/water`, `cardinal/fixed/mutable`, `yin/yang` hors assertion de test ciblee;
  - attributs de profil non presents dans une source canonique.
- Shared abstraction allowed only if:
  - elle evite une duplication entre repository et mapper;
  - elle reste dans la couche infra ou runtime appropriee;
  - elle ne devient pas une source de verite concurrente.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `SIGN_PROFILE_DATA` ou equivalent dans `backend/app/domain/astrology`
- `ELEMENT_BY_SIGN`, `MODALITY_BY_SIGN`, `POLARITY_BY_SIGN`
- valeur runtime `"unknown"` pour un champ de profil signe
- fallback local vers `fire`, `cardinal`, `yang`, `neutral` quand la DB ne fournit pas le profil
- nouvelle dependance Python
- nouveau `requirements.txt`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Profils structurels des signes | `astral_sign_profiles` + `astral_elements` + `astral_modalities` + `astral_polarities` | constantes dans `domain/astrology` ou `services/natal` |
| Mapping DB vers contrats runtime | `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | parsing dans `domain/astrology` |
| Calcul des signes natals | `backend/app/domain/astrology/builders/sign_runtime_builder.py` | services/API |
| Balance et signature | `backend/app/domain/astrology/interpretation/chart_signature.py` | serializers chart |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable unless implementation projects new fields through the API.
- Reason: no generated API, route manifest, schema, public contract, or generated client is intentionally affected.

Required generated-contract evidence if public projection changes:

- OpenAPI before/after note in `evidence/openapi-impact.md`.
- No frontend type change without a separate frontend/API contract story.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/sign_runtime_data.py`
- `backend/app/domain/astrology/builders/sign_runtime_builder.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/reference_repository.py` - inclure les profils signes dans le payload ou exposer un chargement dedie.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - valider les profils et erreurs d'integrite.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les attributs de profil vers `SignReferenceData`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - etendre `SignReferenceData`.
- `backend/app/domain/astrology/runtime/sign_runtime_data.py` - etendre `SignRuntimeData`.
- `backend/app/domain/astrology/builders/sign_runtime_builder.py` - propager les profils.
- `backend/app/domain/astrology/interpretation/chart_signature.py` - consommer les profils enrichis si le contrat le permet.
- `_condamad/stories/regression-guardrails.md` - invariant `RG-114` deja ajoute par cette story.

Likely tests:

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/tests/unit/domain/astrology/test_sign_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_chart_signature.py`
- `backend/tests/unit/domain/astrology/test_chart_signature_runtime_data.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/app/tests/unit/test_astrology_prediction_boundary.py`

Files not expected to change:

- `frontend/**` - aucun impact UI dans cette story.
- `backend/pyproject.toml` - aucune dependance nouvelle.
- `backend/migrations/versions/**` - aucune migration attendue sans decision utilisateur explicite.
- `backend/requirements.txt` - interdit par les regles du depot.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q tests/unit/domain/astrology/test_sign_runtime_builder.py tests/unit/domain/astrology/test_chart_signature.py
pytest -q tests/unit/domain/astrology/test_chart_signature_runtime_data.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
rg -n "ELEMENT_BY_SIGN|MODALITY_BY_SIGN|POLARITY_BY_SIGN|SIGN_PROFILE_DATA" app/domain/astrology app/services/natal -g "*.py"
rg -n "seasonal_quadrant|fertility|humane|bestial|voice" app/domain/astrology app/services/natal -g "*.py"
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```

Expected scan result:

- Aucun mapping local de profils signes sous `app/domain/astrology` ou `app/services/natal`.
- Les hits sur `seasonal_quadrant`, `fertility`, `voice`, `humane`, `bestial` doivent correspondre
  a un champ runtime source DB-backed ou a une preuve de blocage explicite, pas a une constante locale.

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-185-brancher-profils-signes-runtime-natal/00-story.md
```

## 22. Regression Risks

- Risk: les tests existants continuent a fournir des fixtures de signes sans profil et masquent la DB.
  - Guardrail: factory runtime mise a jour et test negatif repository.
- Risk: `ChartSignatureCalculator` change les scores historiques sans baseline.
  - Guardrail: snapshots avant/apres et tests de tie-break.
- Risk: les attributs demandes non presents en DB sont inventes en constantes.
  - Guardrail: AC5 bloque toute valeur non sourcee.
- Risk: une projection API additive modifie le contrat public sans suivi.
  - Guardrail: `openapi-impact.md` et story separee si schema public change.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create compatibility wrappers, aliases, shims, silent fallbacks or duplicate profile sources.
- Do not add a backend base folder.
- All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Keep the global French file comment and French docstrings on new or significantly modified Python files.

## 24. References

- `backend/app/infra/db/models/reference.py` - models SQLAlchemy des profils et taxonomies signes.
- `backend/app/services/prediction/reference_seed_service.py` - seed actuel des profils signes.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - chargement runtime DB.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapping infra vers dataclasses.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - contrat `SignReferenceData`.
- `backend/app/domain/astrology/runtime/sign_runtime_data.py` - contrat `SignRuntimeData`.
- `backend/app/domain/astrology/interpretation/chart_signature.py` - balances et signatures.
- `_condamad/stories/regression-guardrails.md` - invariants CONDAMAD applicables.
