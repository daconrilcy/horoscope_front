<!-- Commentaire global: ce document fixe la frontiere entre le contrat OpenAPI public et les surfaces internes protegees. -->

# Frontiere OpenAPI publique et surfaces internes

`/openapi.json` expose le contrat public derive de `app.openapi()`. Ce document
ne doit pas publier de schema client pour les payloads de diagnostic, runtime,
trace, replay, debug ou projection technique interne.

Les familles `admin/ops/b2b/internal` appartiennent aux surfaces protegees:

- `/v1/admin/**` reste reserve aux utilisateurs admin authentifies;
- `/v1/ops/**` reste reserve aux utilisateurs ops authentifies;
- `/v1/b2b/**` reste reserve aux clients ou administrateurs B2B authentifies;
- `/v1/internal/**` reste non public et ne doit pas etre monte sans garde
  explicite.

Les tokens suivants sont interdits dans le contrat OpenAPI public:
`ChartObjectRuntimeData`, `chart_objects`, `CalculationGraph`,
`execution_trace`, `replay_snapshot`, `llm_input`,
`expert_technical_projection`, `astrology_full_data` et
`admin_chart_diagnostics`.

Toute future publication de projection doit passer par une story de contrat API
dediee, avec tests `app.openapi()`, inventaire `app.routes`, snapshot avant/apres
et refus explicite des acces non authentifies pour les familles protegees.
