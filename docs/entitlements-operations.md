# Documentation opérationnelle des droits produit

Ce document décrit comment modifier une offre commerciale, où se trouve la vérité
canonique des droits produit et comment valider un changement sans dériver du
contrat frontend.

## Comment modifier une offre commerciale

La source de vérité métier est `backend/scripts/seed_product_entitlements.py`.

### Procédure

1. Modifier le binding cible dans `desired_bindings`:
   `is_enabled`, `access_mode`, `variant_code` et, si besoin, les quotas
   (`quota_key`, `quota_limit`, `period_unit`, `period_value`, `reset_mode`).
2. Réinstaller les dépendances backend dans le venv si nécessaire:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   pip install -e ".[dev]"
   ```

3. Rejouer le seed canonique:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   python .\scripts\seed_product_entitlements.py
   ```

4. Mettre à jour `docs/entitlements-validation-matrix.md` avec la nouvelle
   matrice.
5. Exécuter lint et tests ciblés avant toute livraison:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   ruff check .
   pytest -q app/tests/integration/test_entitlements_e2e_matrix.py
   ```

## Où se trouve la vérité des droits produit

| Niveau | Fichier | Rôle |
|---|---|---|
| Seed | `backend/scripts/seed_product_entitlements.py` | Source de vérité des plans B2C et de leurs bindings |
| Modèle DB | `backend/app/infra/db/models/product_entitlements.py` | Tables `PlanCatalogModel`, `FeatureCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel` et compteurs |
| Registry | `backend/app/services/feature_scope_registry.py` | Liste canonique des features reconnues |
| Resolver | `backend/app/services/effective_entitlement_resolver_service.py` | Source unique des droits effectifs au runtime |
| Endpoint | `backend/app/api/v1/routers/entitlements.py` | Expose `GET /v1/entitlements/me` au frontend |
| Contrat API | `backend/app/api/v1/schemas/entitlements.py` | Schémas Pydantic du payload frontend |
| Validation e2e | `backend/app/tests/integration/test_entitlements_e2e_matrix.py` | Verrouille la matrice métier et le contrat frontend |

## Comment valider un changement de plan

1. Exécuter la suite matricielle:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   pytest -q app/tests/integration/test_entitlements_e2e_matrix.py
   ```

2. Vérifier les tests liés aux gates métier concernés si le plan touche un
   produit existant:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   pytest -q app/tests/integration/test_entitlements_me.py
   pytest -q app/tests/integration/test_thematic_consultation_entitlement.py
   ```

3. Appeler `GET /v1/entitlements/me` avec un utilisateur représentatif et
   contrôler:
   `plan_code`, `billing_status`, `granted`, `reason_code`, `quota_limit`,
   `quota_remaining`, `variant_code`, `usage_states`.
4. Si une feature est à quota, vérifier que `quota_remaining` au top-level
   correspond bien à `usage_states[0].remaining`.
