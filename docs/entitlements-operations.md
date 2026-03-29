# Documentation opérationnelle des droits produit (Entitlements)

Ce document décrit comment gérer et valider les offres commerciales du point de vue technique.

## 1. Comment modifier une offre commerciale

La source de vérité des droits produit est le script de seed : `backend/scripts/seed_product_entitlements.py`.

### Procédure de modification :
1. **Modifier `backend/scripts/seed_product_entitlements.py`** : Mettez à jour le dictionnaire `desired_bindings` avec les nouvelles limites de quota ou les changements de mode d'accès (`UNLIMITED`, `QUOTA`, `DISABLED`).
2. **Exécuter le seed en local** (environnement de développement) :
   ```bash
   python backend/scripts/seed_product_entitlements.py
   ```
3. **Mettre à jour la documentation métier** : Reportez les changements dans `docs/entitlements-validation-matrix.md`.
4. **Valider les changements avec les tests** :
   ```bash
   pytest backend/app/tests/integration/test_entitlements_e2e_matrix.py
   ```

## 2. Cartographie des fichiers sources (Vérité des droits)

| Niveau | Fichier | Rôle |
|---|---|---|
| **Seed** | `backend/scripts/seed_product_entitlements.py` | Source de vérité des offres commerciales. |
| **Modèles DB** | `backend/app/infra/db/models/product_entitlements.py` | Tables `PlanCatalogModel`, `FeatureCatalogModel`, `PlanFeatureBindingModel`, `PlanFeatureQuotaModel`. |
| **Registre** | `backend/app/services/feature_scope_registry.py` | Liste canonique des features reconnues par le système. |
| **Resolver** | `backend/app/services/effective_entitlement_resolver_service.py` | Source unique de vérité au runtime pour les droits effectifs. |
| **Endpoint** | `backend/app/api/v1/routers/entitlements.py` | Exposition du snapshot d'entitlements via `GET /v1/entitlements/me`. |

## 3. Comment valider un changement de plan

Lorsqu'une nouvelle offre est créée ou modifiée, suivez ces étapes :

1. **Appeler l'API de diagnostic** :
   Utilisez l'endpoint `GET /v1/entitlements/me` avec un token utilisateur pour vérifier les droits résolus par le moteur canonique.
2. **Exécuter la suite de tests matriciels** :
   ```bash
   pytest backend/app/tests/integration/test_entitlements_e2e_matrix.py
   ```
3. **Vérifier les compteurs de consommation** (si quota) :
   Vérifiez que le champ `usage_states` dans la réponse de l'API reflète bien la consommation réelle stockée dans la table `feature_usage_counters`.
