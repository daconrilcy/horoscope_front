# Story 61.51 : Clôture du chantier entitlements canoniques (61.7–61.50)

Status: review

## Story

En tant que responsable produit ou tech lead,
je veux déclarer formellement la clôture du sous-chantier entitlements canoniques (stories 61.7 à 61.50),
afin d'acter que l'objectif du sous-chantier est atteint et de permettre à l'équipe de poursuivre l'epic 61 sur d'autres sujets, sans rester en mode "infrastructure entitlements".

---

## Contexte

L'epic 61 reste ouvert et accueillera d'autres sujets produit. Cependant, les stories 61.7 à 61.50 constituaient un sous-chantier cohérent avec un objectif propre : **migrer le système de droits produit d'un modèle couplé au legacy billing vers une plateforme canonique d'entitlements gouvernée, observable et validée de bout en bout**.

Cet objectif est atteint depuis la story 61.50 :
- Modèle canonique complet (`61.7–61.10`).
- Migration B2C et B2B vers le canonique (`61.11–61.26`).
- Garde-fous de cohérence à tous les niveaux critiques (`61.27–61.30`).
- Gouvernance des écritures, audit trail et ops SLA (`61.31–61.38`).
- Alerting ops persistant, retryable, triable et débruité par règles (`61.39–61.46`).
- Resolver runtime unique, contrat frontend stable, validation end-to-end (`61.47–61.50`).

Cette story ne livrera **aucune nouvelle brique runtime**. Elle se limite à deux actes de clôture du sous-chantier :
1. Créer `docs/entitlements-canonical-closure.md` : déclaration formelle d'objectif atteint, inventaire des livrables et cadrage des travaux post-clôture.
2. Pointer explicitement vers `docs/entitlements-legacy-remnants.md` comme liste de suivi de la dette technique post-clôture, sans traiter de reliquat dans cette story.

**L'epic 61 n'est PAS fermé** : il accueillera d'autres stories produit indépendantes de ce chantier.

---

## Acceptance Criteria

**AC1 — Document de clôture du sous-chantier créé**
Un fichier `docs/entitlements-canonical-closure.md` est créé avec :
- Section **"Objectif du sous-chantier"** : description de l'objectif des stories 61.7–61.50.
- Section **"État atteint"** : tableau des sept phases complétées (une ligne par phase).
- Section **"Travaux post-clôture prévus"** : les trois catégories de suivi post-clôture (suivi prod/alerting, corrections mineures isolées, dette technique sur les reliquats legacy inventoriés dans `docs/entitlements-legacy-remnants.md`).
- Section **"Ce qui n'est pas prévu"** : confirmation explicite qu'aucune nouvelle étape structurante du chantier entitlements n'est planifiée dans l'epic 61.

**AC2 — Aucune modification de code runtime**
Aucun fichier sous `backend/app/` ou `frontend/src/` n'est modifié. Aucune migration Alembic. Aucun nouvel endpoint. Cette story est strictement documentaire.

---

## Tasks / Subtasks

- [x] **Créer `docs/entitlements-canonical-closure.md`** (AC: 1)
  - [x] Rédiger la section "Objectif du sous-chantier"
  - [x] Rédiger le tableau "État atteint" (7 phases, une ligne par phase)
  - [x] Rédiger la section "Travaux post-clôture prévus" (3 catégories)
  - [x] Rédiger la section "Ce qui n'est pas prévu"

- [x] **Vérifier les fichiers docs de référence** (AC: 1)
  - [x] Confirmer que `docs/entitlements-legacy-remnants.md` existe (créé en 61.50)
  - [x] Confirmer que `docs/entitlements-operations.md` existe (créé en 61.50)
  - [x] Ne modifier ni l'un ni l'autre — pointer seulement depuis le nouveau fichier

---

## Dev Notes

### Périmètre strict

Cette story est **entièrement documentaire**. La seule modification autorisée est la suivante :
- Création de `docs/entitlements-canonical-closure.md` (nouveau fichier Markdown).

**Interdictions absolues :**
- Aucune modification de `backend/app/` ou `frontend/src/`.
- Aucune mise à jour de `sprint-status.yaml` — l'epic 61 reste `in-progress`.
- Aucune migration Alembic.
- Ne pas traiter les reliquats legacy de `docs/entitlements-legacy-remnants.md` ici.

### Structure attendue de `docs/entitlements-canonical-closure.md`

```markdown
# Clôture du chantier entitlements canoniques — Objectif atteint

## Objectif du sous-chantier

Migrer le système de droits produit d'un modèle couplé au legacy billing vers une
plateforme canonique d'entitlements gouvernée, observable et validée de bout en bout.
(Stories 61.7 à 61.50 de l'epic 61.)

## État atteint

| Phase | Stories | Livraison |
|---|---|---|
| Fondations canoniques | 61.7–61.10 | Modèle canonique, backfill, EntitlementService, moteur de quotas |
| Migration B2C | 61.11–61.17 | Gates B2C migrées, endpoint `GET /v1/entitlements/me`, décommission quota legacy |
| Migration B2B | 61.18–61.26 | Runtime B2B canonique, compteurs entreprise natifs, nettoyage admin_user_id |
| Garde-fous | 61.27–61.30 | Registre de scope, validation statique, enforcement CI, validation DB |
| Gouvernance écritures | 61.31–61.38 | Écriture centralisée, audit trail, review queue, SLA ops |
| Alerting ops | 61.39–61.46 | Alerting persistant, retry, triage, règles de suppression durables |
| Unification runtime | 61.47–61.50 | Resolver effectif, gates rebranchées, contrat frontend, validation e2e |

## Travaux post-clôture prévus

1. **Suivi production** : surveillance des alertes ops en conditions réelles,
   ajustements SLA si nécessaire.
2. **Corrections mineures isolées** : bugs ponctuels identifiés en production,
   traités au cas par cas sans rouvrir de chantier.
3. **Dette technique ciblée** : les reliquats legacy inventoriés dans
   `docs/entitlements-legacy-remnants.md` sont la liste de référence.
   Chaque suppression sera effectuée en story courte indépendante,
   uniquement si la régression est exclue par grep et tests existants.

## Ce qui n'est pas prévu

Aucune nouvelle étape structurante du chantier entitlements n'est planifiée dans
l'epic 61. Les prochaines stories de l'epic 61 porteront sur d'autres sujets produit.
```

### Fichiers de référence pour le contenu

- `_bmad-output/implementation-artifacts/61-7-a-61-50-synthese-entitlements-canoniques-et-ops.md` — synthèse complète des 44 stories (source principale pour le tableau "État atteint")
- `docs/entitlements-legacy-remnants.md` — inventaire des reliquats (pointer depuis "Travaux post-clôture")
- `docs/entitlements-operations.md` — documentation opérationnelle (ne pas modifier)

### Project Structure Notes

- Documentation : `docs/` (même dossier que `entitlements-operations.md`, `entitlements-legacy-remnants.md`)

### References

- `_bmad-output/implementation-artifacts/61-7-a-61-50-synthese-entitlements-canoniques-et-ops.md`
- `docs/entitlements-legacy-remnants.md`
- `docs/entitlements-operations.md`

---

## Hors périmètre explicite

- Fermeture de l'epic 61 (qui reste ouvert).
- Mise à jour de `sprint-status.yaml`.
- Traitement de tout reliquat legacy listé dans `docs/entitlements-legacy-remnants.md`.
- Modification de services, gates, resolver ou endpoint.

---

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Verified existence of `docs/entitlements-legacy-remnants.md` and `docs/entitlements-operations.md`.
- Created `docs/entitlements-canonical-closure.md` with requested content.

### Completion Notes List

- All documentation tasks completed.
- AC1 satisfied: Closure document created with all required sections.
- AC2 satisfied: No runtime code modified.

### File List

- `docs/entitlements-canonical-closure.md`
