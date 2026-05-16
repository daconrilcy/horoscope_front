"""Tests du resolver canonique des libellés astrologiques localisés."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.infra.db.models.reference import (
    AspectModel,
    AstralAspectFamilyModel,
    AstralSignModel,
    HouseModel,
    LanguageModel,
    PlanetModel,
)
from app.infra.db.models.translation_reference import (
    AstralAspectTranslationModel,
    AstralHouseTranslationModel,
    AstralPlanetTranslationModel,
    AstralSignTranslationModel,
)
from app.infra.db.models.user import UserModel
from app.services.reference_data.astrology_translation_resolver import (
    AstrologyTranslationResolver,
)


def _seed_reference_rows(db: Session) -> None:
    """Insère les langues, signes et traductions minimales du resolver."""
    fr = LanguageModel(code="fr", name="Francais")
    en = LanguageModel(code="en", name="English")
    es = LanguageModel(code="es", name="Espanol")
    aries = AstralSignModel(code="aries", name="Aries")
    taurus = AstralSignModel(code="taurus", name="Taurus")
    sun = PlanetModel(code="sun", name="Sun", swe_id=0)
    house_one = HouseModel(number=1, name="House 1")
    family = AstralAspectFamilyModel(name="major")
    db.add_all([fr, en, es, aries, taurus, sun, house_one, family])
    db.flush()
    conjunction = AspectModel(code="conjunction", name="Conjunction", angle=0.0, family=family.id)
    db.add(conjunction)
    db.flush()
    db.add_all(
        [
            AstralSignTranslationModel(
                astral_sign_id=aries.id,
                language_id=fr.id,
                translated_name="Belier",
            ),
            AstralSignTranslationModel(
                astral_sign_id=taurus.id,
                language_id=fr.id,
                translated_name="Taureau",
            ),
            AstralSignTranslationModel(
                astral_sign_id=aries.id,
                language_id=en.id,
                translated_name="Aries",
            ),
            AstralSignTranslationModel(
                astral_sign_id=aries.id,
                language_id=es.id,
                translated_name="Aries ES",
            ),
            AstralPlanetTranslationModel(
                planet_id=sun.id,
                language_id=fr.id,
                translated_name="Soleil",
            ),
            AstralAspectTranslationModel(
                aspect_id=conjunction.id,
                language_id=fr.id,
                translated_name="conjonction",
            ),
            AstralHouseTranslationModel(
                house_id=house_one.id,
                language_id=fr.id,
                translated_name="Maison 1",
            ),
        ]
    )
    db.flush()


def test_resolver_prefers_explicit_language_over_user_default(db_session: Session) -> None:
    """La langue API explicite prime sur la préférence utilisateur."""
    _seed_reference_rows(db_session)
    en = db_session.query(LanguageModel).filter_by(code="en").one()
    db_session.add(
        UserModel(
            id=42,
            email="user@example.com",
            password_hash="hash",
            role="user",
            default_language_id=en.id,
        )
    )
    db_session.commit()

    labels = AstrologyTranslationResolver(db_session).resolve_labels(
        language_code="es-ES",
        user_id=42,
    )

    assert labels.effective_language_code == "es"
    assert labels.sign_label("aries") == "Aries ES"


def test_resolver_uses_user_default_then_system_fallback(db_session: Session) -> None:
    """Les traductions manquantes dans la langue utilisateur tombent sur le français."""
    _seed_reference_rows(db_session)
    en = db_session.query(LanguageModel).filter_by(code="en").one()
    db_session.add(
        UserModel(
            id=7,
            email="fallback@example.com",
            password_hash="hash",
            role="user",
            default_language_id=en.id,
        )
    )
    db_session.commit()

    labels = AstrologyTranslationResolver(db_session).resolve_labels(user_id=7)

    assert labels.effective_language_code == "en"
    assert labels.sign_label("aries") == "Aries"
    assert labels.sign_label("taurus") == "Taureau"


def test_resolver_falls_back_to_canonical_code(db_session: Session) -> None:
    """Le fallback technique final retourne le code canonique du signe."""
    _seed_reference_rows(db_session)

    labels = AstrologyTranslationResolver(db_session).resolve_labels(language_code="de")

    assert labels.effective_language_code == "fr"
    assert labels.sign_label("pisces") == "pisces"


def test_resolver_covers_planet_aspect_and_house_labels(db_session: Session) -> None:
    """Les familles de libellés DB ciblées sont exposées par le même contrat."""
    _seed_reference_rows(db_session)

    labels = AstrologyTranslationResolver(db_session).resolve_labels(language_code="fr")

    assert labels.planet_label("sun") == "Soleil"
    assert labels.aspect_label("conjunction") == "conjonction"
    assert labels.house_label(1) == "Maison 1"
    assert labels.planet_label("mars") == "mars"
