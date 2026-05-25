# CS-304 — Design Admin Audit And Replay Flows

## Résumé

Définir les écrans et flows admin pour consulter les réponses rejetées, les audits de réponse IA et les snapshots replay, uniquement sous garde admin interne.

## Contexte

Les surfaces backend existent pour le workflow de réponses rejetées, les logs d'accès admin et le replay snapshot v1. Il manque une phase UX/admin pour rendre ces fonctions opérables sans exposer de données sensibles ni créer une surface publique.

## Objectif

Produire un brief UX/API d'administration qui décrit les flows nécessaires avant implémentation frontend/admin :

- consultation des réponses rejetées ;
- lecture des détails d'audit autorisés ;
- consultation des métadonnées replay snapshot ;
- lancement d'une tentative replay contrôlée ;
- purge manuelle auditée.

## Condition obligatoire

Cette story ne doit passer à l'implémentation que si l'accès reste strictement admin/interne, avec AuthN/AuthZ existante, audit logs, masquage des données sensibles et aucune exposition B2C/public.

## Préalable obligatoire

Relire :

- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/api/v1/routers/admin/llm/observability.py`
- `backend/app/services/api_contracts/admin/audit.py`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/final-runtime-closure.md`

## Périmètre inclus

1. Cartographier les endpoints admin existants nécessaires.
2. Définir les écrans admin minimaux.
3. Définir les états autorisé/refusé/expiré/purgé/incomplet.
4. Définir les colonnes visibles et masquées.
5. Définir les actions auditables : lire, rejouer, purger, changer statut de revue.
6. Définir les preuves attendues pour absence de prompts bruts, secrets, birth data et payload provider.
7. Produire une checklist d'implémentation frontend/admin.

## Hors périmètre

- Implémenter directement l'UI.
- Ajouter une route publique.
- Ajouter un export massif.
- Afficher prompt brut, output brut provider, birth data brute, coordonnées exactes ou secrets.
- Étendre les rôles sans décision produit/sécurité.

## Critères d'acceptation

1. Les flows admin sont décrits sans ambiguïté.
2. Chaque action sensible indique son audit attendu.
3. Les champs sensibles interdits sont listés et exclus de l'UI.
4. Les endpoints backend consommés sont nommés.
5. Le document indique explicitement que l'implémentation frontend/admin est bloquée si l'accès ne reste pas admin interne.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -c "from app.main import app; paths=app.openapi()['paths']; assert all(path.startswith('/v1/admin/') for path in paths if 'replay' in path or 'audit' in path)"
```

## Dépendances

- CS-268 / CS-294.
- CS-290.
- CS-297 à CS-301.

## Risques

Le risque principal est de transformer un outil support/admin en fonctionnalité client ou support trop large. Le flow doit rester interne, minimal, audité et sans données brutes.
