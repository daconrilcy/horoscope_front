# CS-290 — Implement Rejected Narrative Answer Workflow

## Résumé

Implémenter le workflow de rejet des réponses narratives non fondées.

## Contexte

CS-261 définit le rejet. Une réponse non fondée ne doit pas être livrée au client, mais elle doit être stockée avec une raison exploitable en admin.

## Objectif

Ajouter le comportement applicatif de rejet, stockage et réponse client contrôlée.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Réutiliser la persistance d'audit existante.
2. Marquer les réponses non fondées en `rejected`.
3. Stocker `rejection_reason` et contexte de validation.
4. Retourner un message client contrôlé sans réponse IA brute.
5. Ajouter les logs internes et tests associés.

## Hors périmètre

- Implémenter un retry automatique.
- Publier manuellement une réponse rejetée.
- Créer une UI complète de revue.
- Modifier le provider LLM.

## Critères d'acceptation

1. Une réponse non fondée est rejetée et stockée.
2. Le client reçoit un message contrôlé, jamais la réponse IA brute.
3. Un log interne est produit.
4. Le retry reste hors scope sauf décision future.
5. Les tests couvrent rejet, stockage et réponse client.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-261 pour le workflow contractuel.
- CS-288 pour la persistance d'audit.
- CS-289 pour la validation des preuves.

## Risques

Le risque principal est de masquer le rejet côté backend tout en laissant la réponse brute transiter côté client. Le comportement client doit être testé.



