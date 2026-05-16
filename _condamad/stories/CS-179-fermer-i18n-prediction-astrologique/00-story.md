# Story CS-179 fermer-i18n-prediction-astrologique: Fermer l'i18n astrologique du domaine prediction

Status: ready-to-dev

## 1. Objective

Supprimer les mappings francais actifs restants dans `backend/app/domain/prediction`
pour les libelles astrologiques publics et le contexte prompt quotidien. Apres
implementation, les signes, planetes, aspects et maisons affichables de
prediction doivent provenir d'un resolver canonique ou d'un contrat runtime
derive des sources de reference existantes, sans fallback FR local silencieux.

## 2. Trigger / Source

- Source type: code-review
- Source reference: demande utilisateur du 2026-05-16, point "Reste a
  surveiller" sur `public_astro_vocabulary.py` et `astrologer_prompt_builder.py`.
- Reason for change: CS-177 a ferme les surfaces natales principales mais a
  laisse des mappings FR dans `domain/prediction`; une i18n astrologique backend
  complete exige de traiter ce domaine ou de documenter une exception. Cette
  story choisit la fermeture complete.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/prediction`
- In scope:
  - Remplacer les labels FR locaux de `public_astro_vocabulary.py`.
  - Remplacer les labels FR locaux de `astrologer_prompt_builder.py`.
  - Adapter les consommateurs prediction de ces helpers.
  - Ajouter ou etendre une garde anti-retour ciblee prediction.
  - Persister un audit avant/apres des symboles interdits et des proprietaires.
- Out of scope:
  - Modifier les surfaces natales deja fermees par CS-177.
  - Modifier les calculs astrologiques purs sous `backend/app/domain/astrology`.
  - Modifier les bundles i18n frontend.
  - Ajouter une langue non seedee ou un nouveau modele de traduction.
  - Reecrire le contenu editorial long des prompts.
- Explicit non-goals:
  - Ne pas changer `RG-108`: les vocabulaires DB-backed ne sont pas recrees
    localement.
  - Ne pas changer `RG-109`: les labels de signes passent par le resolver
    canonique.
  - Ne pas introduire un resolver concurrent sous `domain/prediction`.
  - Ne pas conserver `PLANET_NAMES_FR`, `SIGN_NAMES_FR`, `SIGN_LABELS_FR`,
    `PLANET_CODE_LABELS` ou `ASPECT_LABELS` comme sources nominales actives.
  - Ne pas accepter une exception temporaire pour les deux fichiers cites.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story retire des constantes et helpers FR actifs devenus
  non canoniques depuis l'existence du resolver de traduction backend.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les libelles affichables peuvent changer uniquement pour respecter la langue
    effective resolue.
  - La structure des payloads publics prediction ne doit pas changer.
  - Les textes editoriaux longs et les cles techniques ne doivent pas etre
    traduits opportunistement.
- Deletion allowed: yes
- Replacement allowed: no
- Consumer adaptation constraints:
  - Les consommateurs prediction peuvent etre adaptes vers un contrat canonique
    injecte ou construit hors `domain/prediction`.
  - Les constantes, helpers, wrappers et alias FR interdits ne doivent pas etre
    remplaces par une surface locale equivalente sous un autre nom.
- User decision required if: un vocabulaire affiche par prediction n'a aucune
  source DB, runtime ou contrat canonique existant et ne peut pas etre derive
  sans decision produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les labels doivent pointer vers le schema DB de traduction ou un contrat runtime canonique. |
| Baseline Snapshot | yes | La story doit prouver les mappings FR avant/apres dans prediction. |
| Ownership Routing | yes | Le domaine prediction ne doit pas devenir proprietaire de vocabulaire astrologique DB-backed. |
| Allowlist Exception | yes | Le registre doit prouver qu'aucune ligne d'exception n'est ouverte. |
| Contract Shape | no | Aucun champ API, DTO, OpenAPI ou type frontend ne doit changer. |
| Batch Migration | no | Le perimetre est limite aux consommateurs prediction cites et directs. |
| Reintroduction Guard | yes | Les constantes FR interdites doivent echouer si elles reviennent. |
| Persistent Evidence | yes | L'audit avant/apres doit rester dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - Schema DB verifie par `inspect(engine)` ou `MetaData`: tables de traduction
    consommees par `AstrologyTranslationResolver`: `languages`,
    `astral_sign_translations`, `astral_planet_translations`,
    `astral_aspect_translations`, `astral_house_translations` quand le
    vocabulaire est DB-backed.
  - Contrats runtime astrology existants quand le libelle affiche n'est pas une
    traduction DB directe mais une projection derivee.
- Secondary evidence:
  - Scans `rg` des symboles FR interdits dans `backend/app/domain/prediction`.
  - Tests unitaires des projections et du prompt builder prediction.
- Static scans alone are not sufficient for this story because:
  - un symbole peut disparaitre tout en conservant un fallback FR local sous un
    autre nom; les tests doivent valider la langue effective et les payloads.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract
changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md`
- Expected invariant:
  - Les payloads prediction gardent les memes cles et les memes evenements; seuls
    les libelles affichables sont resolus par la source canonique.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Traduction des signes | `backend/app/services/reference_data/astrology_translation_resolver.py` | `backend/app/domain/prediction/**` |
| Traduction des planetes | `backend/app/services/reference_data/astrology_translation_resolver.py` | `backend/app/domain/prediction/**` |
| Traduction des aspects | `backend/app/services/reference_data/astrology_translation_resolver.py` | `backend/app/domain/prediction/**` |
| Traduction des maisons | `backend/app/services/reference_data/astrology_translation_resolver.py` | `backend/app/domain/prediction/**` |
| Projection publique prediction | `backend/app/domain/prediction/public_projection.py` | resolver de traduction concurrent local |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour les mappings FR prediction. | permanent zero-row policy |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Audit before | `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-before.md` | Inventorier mappings FR et consommateurs. |
| Audit after | `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md` | Prouver la disparition ou le remplacement canonique des mappings FR. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states

Required forbidden examples:

- `PLANET_NAMES_FR`
- `SIGN_NAMES_FR`
- `SIGN_LABELS_FR`
- `PLANET_CODE_LABELS`
- `ASPECT_LABELS`
- `HOUSE_SIGNIFICATIONS`
- `EFFECT_LABELS`
- `get_planet_name_fr`
- `get_sign_name_fr`
- `get_aspect_label`
- `get_effect_label`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q app/tests/unit/test_astrology_localization_guardrails.py` checks
  forbidden prediction symbols.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: demande utilisateur du 2026-05-16, point "Reste a surveiller"
  sur les mappings FR prediction.
- Closure proof required: audit before/after, garde anti-retour et scans
  zero-hit des symboles interdits dans `backend/app/domain/prediction`.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/prediction/public_astro_vocabulary.py` -
  contient `HOUSE_SIGNIFICATIONS`, `ASPECT_LABELS`, `EFFECT_LABELS`,
  `PLANET_NAMES_FR`, `SIGN_NAMES_FR` et des helpers `*_fr` avec fallback local.
- Evidence 2: `backend/app/domain/prediction/astrologer_prompt_builder.py` -
  contient `PLANET_CODE_LABELS` et `SIGN_LABELS_FR` pour construire le contexte
  quotidien.
- Evidence 3: `backend/app/domain/prediction/public_projection.py` et
  `backend/app/domain/prediction/public_astro_daily_events.py` consomment les
  helpers FR de `public_astro_vocabulary.py`.
- Evidence 4: `_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/00-story.md`
  a ferme les surfaces natales principales mais ne couvre pas `domain/prediction`.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants de
  regression consultes avant le cadrage de la story.

## 6. Target State

After implementation:

- `domain/prediction` ne contient plus de mapping FR actif pour signes,
  planetes, aspects ou maisons DB-backed.
- Les projections publiques prediction et le prompt builder quotidien resolvent
  les libelles via un contrat injecte ou construit hors `domain/prediction`
  depuis le resolver canonique.
- Les fallbacks de langue sont uniformes avec le resolver canonique.
- Les preuves avant/apres documentent tout vocabulaire restant non DB-backed avec
  owner exact ou decision bloquante.
- Une garde determinee bloque le retour des symboles FR interdits.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-035` - `domain/prediction` reste un domaine pur, sans dependance API,
    infra ou services opportuniste.
  - `RG-108` - les vocabulaires DB-backed ne doivent pas etre recrees localement.
  - `RG-109` - les labels de signes doivent passer par le resolver canonique.
  - `RG-110` - les labels astrologiques prediction ne doivent pas redevenir des
    mappings FR locaux.
- Non-applicable invariants:
  - `RG-107` - la story ne modifie pas le flux natal reference runtime.
  - `RG-095` - la story ne change pas la frontiere astrology vers prediction.
- Required regression evidence:
  - Tests unitaires prediction et garde localisation.
  - Scans zero-hit des symboles interdits dans `backend/app/domain/prediction`.
  - Audit before/after persiste.
- Allowed differences:
  - Les libelles affichables peuvent suivre la langue effective canonique; les
    structures de payload restent stables.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire des mappings FR prediction est complet avant modification. | Evidence profile: `baseline_snapshot`; `prediction-i18n-before.md` avec scans `rg`. |
| AC2 | Plus de source FR DB-backed dans `public_astro_vocabulary.py`. | Evidence: `pytest -q app/tests/unit/test_astrology_translation_resolver.py`; `rg` interdit. |
| AC3 | Plus de labels FR locaux dans `astrologer_prompt_builder.py`. | Evidence: `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py`; `rg` builder. |
| AC4 | Les projections prediction gardent leurs cles de payload. | Evidence: `pytest -q tests/unit/prediction/test_public_*.py`. |
| AC5 | Le retour de mappings FR prediction est bloque. | Evidence: `pytest -q app/tests/unit/test_astrology_localization_guardrails.py`. |
| AC6 | L'audit after prouve zero residu in-domain. | Evidence: `rg -n "Known residual in-domain work: none" prediction-i18n-after.md`; scans zero-hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'etat initial prediction i18n (AC: AC1)
  - [ ] Subtask 1.1 - Scanner les symboles FR et helpers `*_fr`.
  - [ ] Subtask 1.2 - Lister les consommateurs directs dans l'audit before.

- [ ] Task 2 - Converger le vocabulaire public prediction (AC: AC2, AC4)
  - [ ] Subtask 2.1 - Remplacer les mappings FR DB-backed par une resolution canonique.
  - [ ] Subtask 2.2 - Adapter `public_projection.py` et `public_astro_daily_events.py`.

- [ ] Task 3 - Converger le prompt builder quotidien (AC: AC3)
  - [ ] Subtask 3.1 - Supprimer `PLANET_CODE_LABELS` et `SIGN_LABELS_FR`.
  - [ ] Subtask 3.2 - Verifier que `lang` gouverne la langue effective.

- [ ] Task 4 - Ajouter les protections anti-retour (AC: AC5)
  - [ ] Subtask 4.1 - Etendre `test_astrology_localization_guardrails.py`.
  - [ ] Subtask 4.2 - Ajouter les symboles prediction interdits.

- [ ] Task 5 - Valider et persister l'apres (AC: AC6)
  - [ ] Subtask 5.1 - Executer tests, lint et scans.
  - [ ] Subtask 5.2 - Ecrire `prediction-i18n-after.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/reference_data/astrology_translation_resolver.py` pour
    les labels DB-backed.
  - Les contrats runtime astrology existants pour les faits non traduisibles
    directement par table.
  - Les tests de garde localisation existants pour eviter un second guard.
- Do not recreate:
  - mapping local de signes, planetes, aspects ou maisons;
  - fallback FR par consommateur;
  - resolver de traduction concurrent sous `domain/prediction`;
  - copie de seed data comme source runtime.
- Shared abstraction allowed only if:
  - elle remplace au moins deux consommateurs prediction actuels et delegue a la
    source canonique sans posseder le vocabulaire.

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

- `backend/app/domain/prediction/public_astro_vocabulary.py::PLANET_NAMES_FR`
- `backend/app/domain/prediction/public_astro_vocabulary.py::SIGN_NAMES_FR`
- `backend/app/domain/prediction/public_astro_vocabulary.py::ASPECT_LABELS`
- `backend/app/domain/prediction/public_astro_vocabulary.py::HOUSE_SIGNIFICATIONS`
- `backend/app/domain/prediction/public_astro_vocabulary.py::EFFECT_LABELS`
- `backend/app/domain/prediction/astrologer_prompt_builder.py::PLANET_CODE_LABELS`
- `backend/app/domain/prediction/astrologer_prompt_builder.py::SIGN_LABELS_FR`
- `get_planet_name_fr`, `get_sign_name_fr`, `get_aspect_label`, `get_effect_label`
  comme API nominale nouvelle ou conservee.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-before.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Labels astrologiques DB-backed | `AstrologyTranslationResolver` | mappings FR dans `domain/prediction` |
| Projection publique prediction | `backend/app/domain/prediction/public_projection.py` | ownership de vocabulaire astrologique |
| Prompt quotidien prediction | `backend/app/domain/prediction/astrologer_prompt_builder.py` | mappings FR locaux |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to a local compatibility helper;
- preserving a wrapper;
- adding a compatibility alias;
- keeping a deprecated mapping active;
- preserving the old helper name through re-export;
- replacing deletion with soft-disable behavior.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/astrologer_prompt_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/services/reference_data/astrology_translation_resolver.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/tests/unit/prediction/test_public_projection.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/prediction/public_astro_vocabulary.py` - supprimer ou
  convertir les helpers FR vers la source canonique.
- `backend/app/domain/prediction/astrologer_prompt_builder.py` - supprimer les
  mappings locaux et respecter la langue effective.
- `backend/app/domain/prediction/public_projection.py` - adapter les appels aux
  helpers de libelles.
- `backend/app/domain/prediction/public_astro_daily_events.py` - adapter les
  appels aux helpers de libelles.

Likely tests:

- `backend/app/tests/unit/test_astrology_localization_guardrails.py` - garde
  anti-retour des mappings FR prediction.
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py` - langue et
  libelles du prompt quotidien.
- `backend/tests/unit/prediction/test_public_projection.py` - payload stable et
  labels canoniques.
- `backend/tests/unit/prediction/test_public_astro_daily_events.py` - evenements
  quotidiens localises.

Files not expected to change:

- `frontend/**` - la story ne touche pas les bundles ou composants frontend.
- `backend/app/api/**` - aucun contrat HTTP n'est modifie.
- `backend/app/domain/astrology/**` - la story ne doit pas inverser la frontiere
  astrology vers prediction.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py
pytest -q tests/unit/prediction/test_public_projection.py tests/unit/prediction/test_public_astro_daily_events.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py
rg -n "PLANET_NAMES_FR|SIGN_NAMES_FR|SIGN_LABELS_FR|PLANET_CODE_LABELS" app/domain/prediction -g "*.py"
rg -n "ASPECT_LABELS|HOUSE_SIGNIFICATIONS|EFFECT_LABELS" app/domain/prediction -g "*.py"
rg -n "get_planet_name_fr|get_sign_name_fr|get_aspect_label|get_effect_label" app/domain/prediction -g "*.py"
rg -n "AstrologyTranslationResolver|astrology_translation_resolver|LanguageModel|from app\.services" app/domain/prediction -g "*.py"
rg -n "Known residual in-domain work: none" ../_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/prediction-i18n-after.md
```

Expected scan result:

- Le premier `rg` doit etre zero-hit hors preuves historiques `_condamad`.
- Le second `rg` doit etre classe dans `prediction-i18n-after.md`; toute
  dependance vers `services` depuis `domain/prediction` doit etre evitee ou
  bloquee par decision d'architecture.

## 21. Regression Risks

- Risk: introduire une dependance interdite de `domain/prediction` vers
  `services/reference_data`.
  - Guardrail: `RG-035` et scan des imports `from app.services`.
- Risk: remplacer les constantes nommees par des mappings FR anonymes.
  - Guardrail: audit after et scan des accents/libelles interdits cibles.
- Risk: modifier la forme des payloads publics prediction.
  - Guardrail: tests `test_public_projection.py` et `test_public_astro_daily_events.py`.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass convergence through wrapper, alias, fallback, re-export or local
  mapping renamed.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/00-story.md` -
  story precedente qui laisse explicitement `domain/prediction` hors fermeture.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-035`, `RG-108`, `RG-109` et nouvel invariant `RG-110`.
- `backend/app/domain/prediction/public_astro_vocabulary.py` - surface principale
  des mappings FR restants.
- `backend/app/domain/prediction/astrologer_prompt_builder.py` - surface prompt
  avec labels FR locaux.
