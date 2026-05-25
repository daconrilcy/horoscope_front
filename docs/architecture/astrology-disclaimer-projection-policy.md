<!-- Commentaire global: ce document fixe la politique canonique de rattachement des disclaimers astrologiques aux projections B2C sans creer de surface runtime. -->

# Astrology Disclaimer Projection Policy

`policy_id`: `astrology_disclaimer_projection_policy`

## Decision

Les disclaimers astrologiques B2C sont application-controlled. Ils sont possedes
par le code applicatif, les builders de projection ou ce document de politique,
jamais par le LLM.

Le LLM does not create, does not rewrite and does not mutate disclaimer text. Il
peut rediger une interpretation depuis des faits prepares, mais il ne devient
pas proprietaire des limites produit, legales, medicales, financieres ou de
precision astrologique.

Cette politique documente le rattachement des disclaimers aux projections B2C
existantes; elle ne cree ni nouvelle route, ni schema OpenAPI, ni UI, ni
migration, ni prompt, ni nouvelle politique juridique.

## Inventory Scope

`inventory_scope`: backend, frontend, docs and story briefs.

Les scans bornes ont couvert:

- `backend/app`: registre statique, services LLM, builders de projection,
  contrats publics et messages de mode degrade.
- `frontend/src`: aucune source canonique de disclaimer B2C n'est autorisee.
- `docs/architecture`: contrats `beginner_summary_v1`,
  `client_interpretation_projection_v1`, entitlements B2C et primitives
  publiques.
- `_story_briefs`: briefs CS-257, CS-258, CS-283, CS-284 et CS-293 pour les
  limites produit.

## Existing Owners

| source_owner | usage_class | injection_owner | gap_status |
|---|---|---|---|
| `backend/app/services/resources/templates/disclaimer_registry.py` | natal, AI | `get_disclaimers(locale)` puis `InterpretationService` | covered |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | natal, degraded mode | service applicatif, apres sortie gateway et avant payload client | covered |
| `backend/app/domain/astrology/interpretation/beginner_summary_v1_builder.py` | natal, missing birth time, degraded mode | `BeginnerSummaryV1Builder` via `disclaimer_codes` | covered |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | natal, prediction, missing birth time, degraded mode, AI | `ClientInterpretationProjectionV1Builder` via `disclaimer_codes` | covered |
| `backend/app/services/llm_generation/guidance/guidance_service.py` | prediction, AI | guidance applicative; non proprietaire canonique des projections CS-257/CS-258 | product gap |
| `docs/architecture/beginner-summary-v1-contract.md` | missing birth time, degraded mode | contrat documentaire du message `BGS_DEGRADED_NO_TIME` | covered |
| `docs/architecture/client-interpretation-projection-v1-contract.md` | prediction, AI | contrat documentaire de profondeur par plan | covered |
| `docs/architecture/b2c-projection-entitlement-policy.md` | prediction | politique d'autorisation `free`, `basic`, `premium` | covered |

`next_action` pour le product gap guidance: si les guidances quotidiennes,
hebdomadaires ou contextuelles doivent devenir des projections B2C officielles,
Product + Architecture doivent ouvrir une story dediee qui remplace les textes
locaux par un rattachement explicite a cette politique ou a un registre
applicatif unique. Aucun changement de texte n'est effectue par CS-293.

## Projection Plan Mapping

| projection_id | projection_plan | applicability | disclaimer codes | injection_owner | llm_boundary |
|---|---|---|---|---|---|
| `beginner_summary_v1` | `free` | resume deterministe court | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` | `BeginnerSummaryV1Builder` | LLM absent; application code owns disclaimers |
| `beginner_summary_v1` | `basic` | resume deterministe complet debutant | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` | `BeginnerSummaryV1Builder` | LLM absent; application code owns disclaimers |
| `beginner_summary_v1` | `premium` | non cible premium; pas de profondeur supplementaire dans ce contrat | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` si reutilise comme sibling simple | `BeginnerSummaryV1Builder` | LLM absent; application code owns disclaimers |
| `client_interpretation_projection_v1` | `free` | profondeur `free_short`, sans prediction detaillee | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` | `ClientInterpretationProjectionV1Builder` | LLM redacteur eventuel, not disclaimer owner |
| `client_interpretation_projection_v1` | `basic` | narration plus complete et guidance simple | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` | `ClientInterpretationProjectionV1Builder` | LLM redacteur eventuel, not disclaimer owner |
| `client_interpretation_projection_v1` | `premium` | interpretation riche et fenetres de prediction controlees | `ASTROLOGY_GENERAL_LIMITATION`; ajoute `ASTROLOGY_MISSING_BIRTH_TIME` si `no_time` | `ClientInterpretationProjectionV1Builder` | LLM redacteur eventuel, not disclaimer owner |

## Degraded And Missing Birth Time Policy

`degraded mode` et `missing birth time` sont couverts pour les projections
B2C actuelles:

- `beginner_summary_v1` passe en `degraded` avec `degraded_reason: "no_time"`,
  `missing_data: ["no_time"]`, le message `BGS_DEGRADED_NO_TIME` et le code
  `ASTROLOGY_MISSING_BIRTH_TIME`.
- `client_interpretation_projection_v1` passe en `degraded` quand la source
  publique signale `no_time`; les sections sensibles a l'ascendant ou aux
  maisons recoivent un `display_hint: "degraded"` et le code
  `ASTROLOGY_MISSING_BIRTH_TIME`.
- Les services natals partages utilisent les modes applicatifs `no_time`,
  `no_location` et `no_location_no_time` pour eviter une certitude client sur
  l'ascendant ou les maisons quand les donnees manquent.

Les avertissements techniques admin, traces gateway, prompts, payloads provider,
raw runtime et erreurs internes restent exclus des payloads B2C.

## Text Delta Rule

`text_delta_justification`: none. CS-293 ne cree et ne modifie aucun texte de
disclaimer applicatif. Les textes existants restent ceux du registre statique,
des builders de projection ou des contrats documentaires deja presents.

Toute future creation ou mutation de texte devra citer un gap d'inventaire,
un owner produit, une validation juridique/produit si applicable, puis rattacher
le texte a un owner applicatif unique avant exposition client.

## Closure Evidence

`closure_evidence`:

- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/disclaimer-inventory.md`
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/source-checklist.md`
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/app-surface-status.txt`
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/evidence/validation.txt`
- `_condamad/stories/CS-284-astrology-disclaimer-projection-policy/generated/10-final-evidence.md`
