# CS-269 — Add Rejected Answer Review Workflow

## Résumé

Ajouter un workflow de revue admin des réponses narratives rejetées.

## Contexte

Les réponses rejetées sont stockées pour analyse. Il faut permettre à l'admin de comprendre la cause, trier les rejets et préparer des corrections de prompt, contrat ou validation.

## Objectif

Définir puis implémenter un workflow minimal de revue des réponses rejetées.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Lister les réponses rejetées.
2. Consulter `rejection_reason`, preuves manquantes et contexte de version.
3. Ajouter des statuts de revue internes.
4. Journaliser les consultations et actions.
5. Documenter les limites de correction manuelle.

## Hors périmètre

- Réinjecter manuellement une réponse rejetée au client.
- Modifier automatiquement les prompts.
- Implémenter un outil d'annotation avancé.
- Ajouter un replay complet.

## Critères d'acceptation

1. Les réponses rejetées sont consultables par admin autorisé.
2. Les raisons de rejet sont visibles et structurées.
3. Les actions de revue sont journalisées.
4. Aucune réponse rejetée n'est livrée au client.
5. Le workflow reste séparé du support client public.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-261 pour le rejet.
- CS-267 pour l'API admin.
- CS-268 pour les logs d'accès.
- CS-288 pour la persistance d'audit.
- CS-289 pour la validation des preuves.
- CS-290 pour le rejet applicatif réel.

## Risques

Le risque principal est de transformer la revue admin en contournement qualité. Elle doit diagnostiquer, pas publier.



