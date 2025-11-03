# Issue: FE-7 — Account (RGPD)

## Objectif

Implémenter la fonctionnalité Account (RGPD) permettant aux utilisateurs d'exporter leurs données au format ZIP et de supprimer leur compte avec confirmation double saisie.

## Tâches

### 7.1 — AccountService

**Objectif**: mapper export + delete.

- **Tâches**:
  - `exportZip()` (réponse binaire ZIP), `deleteAccount()` (DELETE).

**AC**:
  - Téléchargement ZIP, toast de succès.
  - Content-Type guard (ZIP/octet-stream uniquement).
  - Filename depuis `Content-Disposition` ou fallback daté.
  - URL blob révoquée après téléchargement.
  - Timeout 60s avec support AbortController.

**Refs**: `GET /v1/account/export`, `DELETE /v1/account`.

### 7.2 — Page /app/account

**Objectif**: UI self-service.

- **Tâches**:
  - Section Export (bouton), section Delete (confirm modal double saisie).

**AC**:
  - Delete → redirection `/` + logout + purge complète (stores, localStorage, caches).
  - Export → fichier valide.
  - Modal avec double saisie case-sensitive ("SUPPRIMER").
  - Gestion erreurs: 409 → toast métier (pas de logout), 401 → flux standard.
  - Accessibilité complète (focus trap, aria-*, Escape).

## Labels

`feature`, `account`, `rgpd`, `milestone-fe-7`
