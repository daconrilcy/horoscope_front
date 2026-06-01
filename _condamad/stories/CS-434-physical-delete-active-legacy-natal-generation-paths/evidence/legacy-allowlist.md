# Legacy Allowlist CS-434

<!-- Commentaire global: cette allowlist est fermee par CS-440 et renvoie vers l'audit zero-hit durable. -->

Status: CLOSED_BY_CS_440

Les anciens symboles natals ne sont plus autorises ici comme allowlist runtime active.
Les residus acceptes sont maintenant portes par:

- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/evidence/legacy-natal-zero-hit-audit.md`;
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`;
- `RG-174` dans `_condamad/stories/regression-guardrails.md`.

| Scope | Decision | Proof |
|---|---|---|
| Runtime public generation | closed | `POST /v1/natal/interpretation` est `410 Gone`; `theme_natal` est le seul chemin public de generation. |
| Runtime readonly/admin classified hits | moved-to-CS-440-audit | Hits limites a readonly historique, admin-only metadata ou garde de rejet. |
| Backend/frontend tests | extinction-only-or-rejection | Noms anti-retour et guards CS-440. |
| `_condamad` historical evidence | proof-only | Documents conserves sans valeur runtime. |
