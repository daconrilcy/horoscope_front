# CS-348 - Architecture Cartographie Generation Prompt LLM

<!-- Commentaire global: ce brief cadre la synthese architecture des audits de generation des prompts LLM. -->

## Resume

Utiliser le skill `condamad-product-architecture` pour synthetiser les audits CS-343 a CS-347 en architecture produit et technique de la generation des prompts LLM.

Le nom de ce brief contient `architecture` pour declencher le skill specialise.

## Contexte

Les audits precedents doivent produire une base factuelle. Cette story ne refait pas les audits: elle transforme leurs preuves en decisions d'architecture, matrices, registres canoniques et roadmap eventuelle.

## Objectif

Produire une architecture de reference qui explique:

- les owners de chaque etape de prompt generation;
- les registres canoniques;
- les frontieres prompt-visible, runtime-only, validation-only, audit-only;
- les surfaces nominales et non nominales;
- les decisions de versioning, trace, cache, replay et invalidation;
- les blockers ou contradictions.

## Perimetre inclus

1. Charger le skill `condamad-product-architecture`.
2. Ingerer les audits CS-343 a CS-347 comme sources primaires.
3. Produire une capability matrix.
4. Produire une surface matrix.
5. Produire des registry decisions.
6. Produire les object/entity decisions.
7. Produire les operational rules.
8. Produire une roadmap ordonnee si des gaps restent.

## Hors perimetre

- Relire tout le code pour refaire un audit complet.
- Modifier le code.
- Produire le rapport de livraison final.
- Produire la documentation Mermaid finale, qui releve de CS-350.

## Sources obligatoires

- `_condamad/audits/prompt-generation-cartography/**/01-surface-inventory-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/02-configuration-assembly-placeholder-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/05-output-validation-persistence-audit.md`
- `.agents/skills/condamad-product-architecture/SKILL.md`

## Livrable attendu

Creer:

```text
_condamad/architecture/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/architecture-prompt-generation-llm.md
```

Le document doit suivre le contrat du skill:

1. Executive architecture decision summary.
2. Audit source map.
3. Capability matrix.
4. Surface matrix.
5. Canonical registry decisions.
6. Entity/object decisions.
7. Operational rules: versioning, trace, cache, replay, invalidation.
8. Blockers and decision owners.
9. Ordered implementation roadmap.
10. Open questions and validation plan.

## Criteres d'acceptation

1. Chaque decision majeure cite une source d'audit ou une assumption.
2. Les frontieres prompt/audit/validation/runtime sont explicites.
3. Les registres canoniques ont owner, versioning, compatibilite, trace et deprecation posture.
4. Les contradictions restent visibles comme blockers.
5. La roadmap ne cree pas d'architecture non supportee par les audits.

## Validation attendue

```powershell
rg -n "Executive architecture|Capability|Surface|Canonical registry|Operational rules|Blockers" _condamad/architecture/prompt-generation-cartography
rg -n "architecture-prompt-generation-llm" _condamad
```

## Risques

Le risque principal est de glisser vers un nouvel audit ou une implementation. La story doit rester une synthese d'evidence.

