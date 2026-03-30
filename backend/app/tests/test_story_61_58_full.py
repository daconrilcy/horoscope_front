from sqlalchemy import select

from app.infra.db.models.product_entitlements import Audience, PlanCatalogModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.infra.db.models.user import UserModel
from app.infra.db.session import SessionLocal
from app.services.billing_service import BillingService
from app.services.effective_entitlement_resolver_service import EffectiveEntitlementResolverService


def test_full_reconciliation_chain():
    """
    Vérifie que la résolution des droits (entitlements) utilise bien
    le profil Stripe canonique en priorité.
    """
    with SessionLocal() as db:
        # 0. S'assurer que les plans existent (BillingService et PlanCatalog)
        BillingService.ensure_default_plans(db)

        # Vérifier que le plan canonique basic est présent dans PlanCatalog
        basic_catalog = db.scalar(
            select(PlanCatalogModel).where(PlanCatalogModel.plan_code == "basic")
        )
        if not basic_catalog:
            basic_catalog = PlanCatalogModel(
                plan_code="basic",
                plan_name="Basic Plan",
                audience=Audience.B2C,
                is_active=True,
            )
            db.add(basic_catalog)
            db.commit()

        # 1. Créer un utilisateur
        user = UserModel(email="test_full@example.com", password_hash="...", role="user")
        db.add(user)
        db.commit()
        db.refresh(user)

        # 2. Créer un profil Stripe actif (basic)
        profile = StripeBillingProfileModel(
            user_id=user.id,
            stripe_customer_id="cus_full",
            stripe_subscription_id="sub_full",
            subscription_status="trialing",  # Test avec trialing
            entitlement_plan="basic",
        )
        db.add(profile)
        db.commit()

        # 3. Résoudre le snapshot via EffectiveEntitlementResolverService
        snapshot = EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(
            db,
            app_user_id=user.id,
        )

        # Vérifications
        assert snapshot.plan_code == "basic"
        assert snapshot.billing_status == "trialing"

        # On vérifie qu'une feature B2C est accordée (ex: daily_horoscope)
        # Il faut s'assurer que FeatureCatalog et Bindings existent pour ce test,
        # mais ici on vérifie surtout les métadonnées du snapshot.

        print(
            "✅ Snapshot reconciled: "
            f"plan={snapshot.plan_code}, billing={snapshot.billing_status}"
        )

        # Cleanup
        db.delete(profile)
        db.delete(user)
        db.commit()

if __name__ == "__main__":
    test_full_reconciliation_chain()
