
import pytest
from sqlalchemy.orm import Session
from app.infra.db.models.user import UserModel
from app.infra.db.models.stripe_billing import StripeBillingProfileModel
from app.services.billing_service import BillingService
from app.infra.db.session import SessionLocal

def test_reproduce_stripe_first_bug():
    """
    Reproduit le bug où un utilisateur avec un profil Stripe actif
    mais sans UserSubscriptionModel legacy est considéré comme inactif.
    """
    with SessionLocal() as db:
        # 0. S'assurer que les plans existent
        BillingService.ensure_default_plans(db)
        
        # 1. Créer un utilisateur
        user = UserModel(email="test_bug@example.com", password_hash="...", role="user")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Créer un profil Stripe actif (basic)
        profile = StripeBillingProfileModel(
            user_id=user.id,
            stripe_customer_id="cus_123",
            stripe_subscription_id="sub_123",
            subscription_status="active",
            entitlement_plan="basic"
        )
        db.add(profile)
        db.commit()
        
        # 3. Récupérer le statut via BillingService
        status = BillingService.get_subscription_status_readonly(db, user_id=user.id)
        
        # On s'attend à ce que ce soit actif et sur le plan basic
        # MAIS actuellement ça devrait échouer (BUG)
        try:
            assert status.status == "active", f"Expected 'active', got '{status.status}'"
            assert status.plan is not None, "Expected plan to be not None"
            assert status.plan.code == "basic-entry", f"Expected plan 'basic-entry', got '{status.plan.code if status.plan else None}'"
            print("✅ Bug non reproduit (déjà corrigé ?)")
        except AssertionError as e:
            print(f"❌ Bug reproduit : {e}")
            # Ne pas faire échouer le test ici si on veut juste voir le résultat, 
            # mais pour un vrai test de reproduction on veut qu'il échoue tant que c'est pas corrigé.
            raise e
        finally:
            # Cleanup
            db.delete(profile)
            db.delete(user)
            db.commit()

if __name__ == "__main__":
    # Pour lancer manuellement si besoin
    test_reproduce_stripe_first_bug()
