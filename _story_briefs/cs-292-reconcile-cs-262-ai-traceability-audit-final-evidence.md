# CS-292 — Reconcile CS-262 AI Traceability Audit Final Evidence

## Résumé

Réconcilier CS-262 avec l'audit existant `_condamad/audits/ai-traceability/2026-05-24-1734` et produire la preuve finale CONDAMAD manquante.

## Contexte

Le rapport CS-256..CS-291 classe CS-262 comme `Not evidenced` parce que la capsule ne contient pas `generated/10-final-evidence.md` et que la ligne story reste `ready-to-dev`. Pourtant, un audit complet existe déjà avec les six fichiers attendus sous `_condamad/audits/ai-traceability/2026-05-24-1734`.

Depuis cet audit, CS-288 a ajouté la persistance `narrative_answer_audit_v1` sur `UserNatalInterpretationModel`. Il faut donc distinguer l'audit historique produit, la preuve finale absente, et les écarts maintenant résolus ou encore ouverts.

## Objectif

Clore proprement CS-262 au sens CONDAMAD sans créer de nouveau stockage parallèle, en rattachant l'audit existant à une preuve finale et en le réévaluant face au runtime actuel.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Lire l'audit `_condamad/audits/ai-traceability/2026-05-24-1734`.
2. Vérifier la présence et le contenu des six fichiers d'audit attendus.
3. Réévaluer les champs `answer_id`, `prompt_version`, `provider`, `model`, `full_prompt`, `prompt_ref` et `prompt_payload_snapshot` face au code actuel.
4. Comparer les conclusions historiques avec CS-288 et `narrative_answer_audit_v1`.
5. Produire `generated/10-final-evidence.md` dans la capsule CS-262.
6. Mettre à jour uniquement les artefacts CONDAMAD nécessaires si le statut doit passer en revue.

## Hors périmètre

- Ajouter un nouveau modèle, une migration, une route ou un service.
- Modifier les prompts ou le provider LLM.
- Implémenter une nouvelle politique de rétention des prompts complets.
- Fermer les décisions produit ou DPO non tranchées.

## Critères d'acceptation

1. CS-262 possède un `generated/10-final-evidence.md`.
2. La preuve finale cite l'audit existant et ses six fichiers.
3. Chaque champ de traçabilité est classé avec le runtime actuel.
4. Les écarts résolus par CS-288 sont séparés des écarts encore ouverts.
5. Aucun fichier applicatif backend, frontend ou migration n'est modifié par cette story.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from pathlib import Path; p=Path('_condamad/audits/ai-traceability/2026-05-24-1734'); assert all((p/name).exists() for name in ['00-audit-report.md','01-evidence-log.md','02-finding-register.md','03-story-candidates.md','04-risk-matrix.md','05-executive-summary.md'])"
rg -n "answer_id|prompt_version|provider|model|full_prompt|prompt_ref|prompt_payload_snapshot" _condamad\audits\ai-traceability\2026-05-24-1734 backend\app
git status --short -- backend/app backend/tests frontend/src backend/migrations
```

## Dépendances

- CS-259 pour le contrat cible `narrative_answer_audit_v1`.
- CS-262 pour la capsule à réconcilier.
- CS-288 pour la persistance maintenant disponible.

## Risques

Le risque principal est de confondre absence de preuve finale CONDAMAD et absence totale d'audit. La story doit préserver cette nuance et ne pas réimplémenter un audit déjà produit.
