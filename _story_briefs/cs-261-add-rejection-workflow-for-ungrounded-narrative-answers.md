# CS-261 — Add Rejection Workflow For Ungrounded Narrative Answers

## Résumé

Définir le workflow de rejet et de stockage des réponses narratives non fondées.

## Contexte

Une réponse LLM contenant une affirmation sans preuve doit être rejetée, stockée et rendue analysable en admin. Le rejet ne doit pas supprimer la trace utile au diagnostic.

## Objectif

Spécifier les états, transitions, données conservées et comportements applicatifs en cas de réponse non fondée.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les conditions de passage à `rejected`.
2. Définir les données stockées pour analyse.
3. Définir la réponse contrôlée côté client.
4. Définir les logs et alertes internes.
5. Définir les règles minimales de confidentialité.
6. Définir que le client reçoit un message contrôlé, jamais la réponse IA brute.
7. Préciser que tout retry éventuel reste une décision de future story.

## Hors périmètre

- Implémenter le back-office de revue.
- Décider la durée RGPD finale.
- Modifier le provider LLM.
- Créer une file de retry.

## Critères d'acceptation

1. Le statut `rejected` est défini comme état terminal auditable.
2. La réponse rejetée est conservée pour analyse interne.
3. Le client ne reçoit pas la réponse non fondée.
4. Les raisons de rejet sont structurées.
5. Un log interne est produit lors du rejet.
6. Le retry n'est pas implémenté par cette story.
7. Le workflow reste séparé du debug calcul.

## Validation attendue

```powershell
rg -n "rejected|ungrounded|rejection_reason|réponse rejetée|message contrôlé|retry|audit" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-259 pour `narrative_answer_audit_v1`.
- CS-260 pour `evidence_refs`.

## Risques

Le risque principal est de masquer les erreurs IA sans les rendre exploitables. Le rejet doit protéger le client tout en conservant une preuve analysable.



