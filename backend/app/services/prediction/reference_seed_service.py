"""Porte le seed canonique des references et rulesets de prediction."""

import json
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AspectProfileModel,
    AstralDignityTypeModel,
    AstralElementModel,
    AstralModalityModel,
    AstralPlanetSignDignityModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    PredictionRulesetModel,
    ReferenceVersionModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.infra.db.repositories import ReferenceRepository


class PredictionReferenceSeedAbortError(RuntimeError):
    """Erreur levee quand le seed de prediction doit s interrompre explicitement."""


EXPECTED_COUNTS = {
    "prediction_categories": 12,
    "planet_profiles": 10,
    "house_profiles": 12,
    "aspect_profiles": 5,
    "astro_points": 4,
    "astral_dignity_type": 4,
    "astral_elements": 4,
    "astral_modalities": 3,
    "astral_polarities": 2,
    "astral_planet_sign_dignities": 50,
    "astral_sign_profiles": 12,
    "planet_category_weights": 85,
    "house_category_weights": 24,
    "point_category_weights": 8,
    "ruleset_event_types": 16,  # 8 per ruleset (1.0.0 and 2.0.0)
    "ruleset_parameters": 16,  # 8 per ruleset (1.0.0 and 2.0.0)
}

SIGN_PROFILE_DATA = [
    ("aries", "fire", "cardinal", "yang"),
    ("taurus", "earth", "fixed", "yin"),
    ("gemini", "air", "mutable", "yang"),
    ("cancer", "water", "cardinal", "yin"),
    ("leo", "fire", "fixed", "yang"),
    ("virgo", "earth", "mutable", "yin"),
    ("libra", "air", "cardinal", "yang"),
    ("scorpio", "water", "fixed", "yin"),
    ("sagittarius", "fire", "mutable", "yang"),
    ("capricorn", "earth", "cardinal", "yin"),
    ("aquarius", "air", "fixed", "yang"),
    ("pisces", "water", "mutable", "yin"),
]
SIGN_CODE_BY_SOURCE_ID = {
    index: sign_code
    for index, (sign_code, _element, _modality, _polarity) in enumerate(SIGN_PROFILE_DATA, 1)
}
PLANET_CODE_BY_SOURCE_ID = {
    1: "sun",
    2: "moon",
    3: "mercury",
    4: "venus",
    5: "mars",
    6: "jupiter",
    7: "saturn",
    8: "uranus",
    9: "neptune",
    10: "pluto",
}


def _load_sign_keywords() -> dict[str, dict[str, list[str]]]:
    """Charge les mots-clés des signes depuis la source documentaire canonique."""
    repo_root = Path(__file__).resolve().parents[4]
    keywords_path = repo_root / "docs" / "recherches astro" / "signs_keywords.json"
    if not keywords_path.exists():
        keywords_path = (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "recherches astro"
            / "signs_keywords.json"
        )
    with keywords_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, dict):
        raise ValueError("signs keywords source must be an object")
    return raw


def _load_planet_sign_dignities() -> list[dict[str, object]]:
    """Charge les dignités planétaires depuis la source documentaire canonique."""
    repo_root = Path(__file__).resolve().parents[4]
    source_path = repo_root / "docs" / "recherches astro" / "planet_sign_diginities.json"
    if not source_path.exists():
        source_path = (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "recherches astro"
            / "planet_sign_diginities.json"
        )
    with source_path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if not isinstance(raw, list) or not raw:
        raise ValueError("planet sign dignities source must be a non-empty list")
    return raw


def _required_keyword_list(
    keywords_by_sign: dict[str, dict[str, list[str]]],
    sign_code: str,
    field_name: str,
) -> list[str]:
    """Valide la présence des listes de mots-clés attendues pour un signe."""
    sign_keywords = keywords_by_sign.get(sign_code)
    if sign_keywords is None:
        raise ValueError(f"missing keywords for sign {sign_code}")
    values = sign_keywords.get(field_name)
    if not isinstance(values, list) or not values:
        raise ValueError(f"missing {field_name} for sign {sign_code}")
    return [str(value) for value in values]


def _ensure_taxonomy(
    db: Session,
    model: type[
        AstralDignityTypeModel | AstralElementModel | AstralModalityModel | AstralPolarityModel
    ],
    rows: list[tuple[str, str]],
) -> dict[str, int]:
    """Insère les valeurs manquantes d'une taxonomie astrale stable."""
    for code, name in rows:
        if db.scalar(select(model.id).where(model.code == code)) is None:
            db.add(model(code=code, name=name))
    db.flush()
    return {row.code: row.id for row in db.scalars(select(model)).all()}


def _ensure_astral_dignity_types(db: Session) -> None:
    """Garantit le référentiel stable des types de dignités astrologiques."""
    _ensure_taxonomy(
        db,
        AstralDignityTypeModel,
        [
            ("domicile", "Domicile"),
            ("detriment", "Detriment"),
            ("exaltation", "Exaltation"),
            ("fall", "Fall"),
        ],
    )


def _ensure_astral_systems(db: Session) -> dict[str, int]:
    """Garantit le référentiel stable des systèmes astrologiques."""
    for name in ("traditional", "modern", "hellenistic", "medieval"):
        if db.scalar(select(AstralSystemModel.id).where(AstralSystemModel.name == name)) is None:
            db.add(AstralSystemModel(name=name))
    db.flush()
    return {row.name: row.id for row in db.scalars(select(AstralSystemModel)).all()}


def _ensure_astral_sign_profiles(db: Session) -> None:
    """Crée les profils structurels des douze signes à partir des taxonomies."""
    elements = _ensure_taxonomy(
        db,
        AstralElementModel,
        [("fire", "Fire"), ("earth", "Earth"), ("air", "Air"), ("water", "Water")],
    )
    modalities = _ensure_taxonomy(
        db,
        AstralModalityModel,
        [("cardinal", "Cardinal"), ("fixed", "Fixed"), ("mutable", "Mutable")],
    )
    polarities = _ensure_taxonomy(
        db,
        AstralPolarityModel,
        [("yang", "Yang"), ("yin", "Yin")],
    )
    signs = {sign.code: sign.id for sign in db.scalars(select(AstralSignModel)).all()}
    keywords_by_sign = _load_sign_keywords()

    for sign_code, element_code, modality_code, polarity_code in SIGN_PROFILE_DATA:
        keywords_json = json.dumps(
            _required_keyword_list(keywords_by_sign, sign_code, "keywords"),
            ensure_ascii=False,
        )
        shadow_keywords_json = json.dumps(
            _required_keyword_list(keywords_by_sign, sign_code, "shadow_keywords"),
            ensure_ascii=False,
        )
        profile = db.scalar(
            select(AstralSignProfileModel).where(
                AstralSignProfileModel.astral_sign_id == signs[sign_code]
            )
        )
        if profile is None:
            db.add(
                AstralSignProfileModel(
                    astral_sign_id=signs[sign_code],
                    astral_element_id=elements[element_code],
                    astral_modality_id=modalities[modality_code],
                    astral_polarity_id=polarities[polarity_code],
                    keywords_json=keywords_json,
                    shadow_keywords_json=shadow_keywords_json,
                )
            )
            continue
        profile.astral_element_id = elements[element_code]
        profile.astral_modality_id = modalities[modality_code]
        profile.astral_polarity_id = polarities[polarity_code]
        profile.keywords_json = keywords_json
        profile.shadow_keywords_json = shadow_keywords_json
    db.flush()


def _ensure_astral_planet_sign_dignities(db: Session) -> None:
    """Synchronise les dignités planétaires par signe depuis le JSON canonique."""
    _ensure_astral_dignity_types(db)
    systems = _ensure_astral_systems(db)
    dignity_types = {row.code: row.id for row in db.scalars(select(AstralDignityTypeModel)).all()}
    sign_ids = {row.code: row.id for row in db.scalars(select(AstralSignModel)).all()}
    planet_ids = {row.code: row.id for row in db.scalars(select(PlanetModel)).all()}
    expected_ids: set[int] = set()

    for source_row in _load_planet_sign_dignities():
        row_id = int(source_row["id"])
        source_sign_id = int(source_row["astral_sign_id"])
        source_planet_id = int(source_row["planet_id"])
        sign_code = SIGN_CODE_BY_SOURCE_ID.get(source_sign_id)
        planet_code = PLANET_CODE_BY_SOURCE_ID.get(source_planet_id)
        dignity_type = str(source_row["dignity_type"])
        system = str(source_row["system"])
        if sign_code not in sign_ids:
            raise ValueError(f"unknown astral_sign_id: {source_sign_id}")
        if planet_code not in planet_ids:
            raise ValueError(f"unknown astral_planet_id: {source_planet_id}")
        if dignity_type not in dignity_types:
            raise ValueError(f"unknown dignity_type: {dignity_type}")
        if system not in systems:
            raise ValueError(f"unknown astral system: {system}")
        expected_ids.add(row_id)
        dignity = db.get(AstralPlanetSignDignityModel, row_id)
        if dignity is None:
            db.add(
                AstralPlanetSignDignityModel(
                    id=row_id,
                    astral_sign_id=sign_ids[sign_code],
                    astral_planet_id=planet_ids[planet_code],
                    astral_dignity_type_id=dignity_types[dignity_type],
                    astral_system_id=systems[system],
                    weight=float(source_row["weight"]),
                    is_primary=bool(source_row["is_primary"]),
                )
            )
            continue
        dignity.astral_sign_id = sign_ids[sign_code]
        dignity.astral_planet_id = planet_ids[planet_code]
        dignity.astral_dignity_type_id = dignity_types[dignity_type]
        dignity.astral_system_id = systems[system]
        dignity.weight = float(source_row["weight"])
        dignity.is_primary = bool(source_row["is_primary"])

    db.execute(
        delete(AstralPlanetSignDignityModel).where(
            AstralPlanetSignDignityModel.id.not_in(expected_ids)
        )
    )
    db.flush()


def _check_counts(db: Session, reference_version_id: int) -> dict[str, int]:
    """Compte les artefacts attendus pour une version de référence donnée."""
    actual = {}
    actual["prediction_categories"] = db.scalar(
        select(func.count())
        .select_from(PredictionCategoryModel)
        .where(PredictionCategoryModel.reference_version_id == reference_version_id)
    )
    actual["planet_profiles"] = db.scalar(
        select(func.count())
        .select_from(PlanetProfileModel)
        .where(PlanetProfileModel.reference_version_id == reference_version_id)
    )
    actual["house_profiles"] = db.scalar(
        select(func.count())
        .select_from(HouseProfileModel)
        .where(HouseProfileModel.reference_version_id == reference_version_id)
    )
    actual["aspect_profiles"] = db.scalar(
        select(func.count())
        .select_from(AspectProfileModel)
        .where(AspectProfileModel.reference_version_id == reference_version_id)
    )
    actual["astro_points"] = db.scalar(select(func.count()).select_from(AstroPointModel))
    actual["astral_dignity_type"] = db.scalar(
        select(func.count()).select_from(AstralDignityTypeModel)
    )
    actual["astral_elements"] = db.scalar(select(func.count()).select_from(AstralElementModel))
    actual["astral_modalities"] = db.scalar(select(func.count()).select_from(AstralModalityModel))
    actual["astral_polarities"] = db.scalar(select(func.count()).select_from(AstralPolarityModel))
    actual["astral_planet_sign_dignities"] = db.scalar(
        select(func.count()).select_from(AstralPlanetSignDignityModel)
    )
    actual["astral_sign_profiles"] = db.scalar(
        select(func.count()).select_from(AstralSignProfileModel)
    )
    actual["planet_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PlanetCategoryWeightModel)
        .where(PlanetCategoryWeightModel.reference_version_id == reference_version_id)
    )
    actual["house_category_weights"] = db.scalar(
        select(func.count())
        .select_from(HouseCategoryWeightModel)
        .where(HouseCategoryWeightModel.reference_version_id == reference_version_id)
    )
    actual["point_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PointCategoryWeightModel)
        .where(PointCategoryWeightModel.reference_version_id == reference_version_id)
    )

    # Les rulesets sont rattachés à la version de référence ciblée.
    rulesets = db.scalars(
        select(PredictionRulesetModel).where(
            PredictionRulesetModel.reference_version_id == reference_version_id
        )
    ).all()

    actual["ruleset_event_types"] = 0
    actual["ruleset_parameters"] = 0

    for ruleset in rulesets:
        actual["ruleset_event_types"] += db.scalar(
            select(func.count())
            .select_from(RulesetEventTypeModel)
            .where(RulesetEventTypeModel.ruleset_id == ruleset.id)
        )
        actual["ruleset_parameters"] += db.scalar(
            select(func.count())
            .select_from(RulesetParameterModel)
            .where(RulesetParameterModel.ruleset_id == ruleset.id)
        )

    return actual


def _seed_ruleset_content(db: Session, ruleset_id: int):
    """Alimente les types d événements et paramètres d un ruleset donné."""
    # Types d événements : (code, groupe, priorité, poids de base).
    # Les priorités sont calibrées par rapport à
    # TurningPointDetector.PRIORITY_PIVOT_THRESHOLD = 65 :
    #   >= 65 : peut déclencher un pivot à haute priorité
    #   < 65 : enrichit seulement un pivot déjà existant
    event_types_data = [
        ("aspect_exact_to_angle", "aspect", 80, 2.0),  # above pivot threshold
        ("aspect_exact_to_luminary", "aspect", 75, 1.8),  # above pivot threshold
        ("aspect_exact_to_personal", "aspect", 68, 1.5),  # slightly above pivot threshold
        ("aspect_enter_orb", "aspect", 40, 1.0),  # below threshold — enriches only
        ("aspect_exit_orb", "aspect", 25, 0.5),  # below threshold
        ("moon_sign_ingress", "ingress", 72, 1.5),  # above pivot threshold
        ("asc_sign_change", "ingress", 78, 2.0),  # above pivot threshold — structurant
        ("planetary_hour_change", "timing", 20, 0.8),  # well below threshold
    ]
    for code, group, priority, weight in event_types_data:
        db.add(
            RulesetEventTypeModel(
                ruleset_id=ruleset_id,
                code=code,
                name=code.replace("_", " ").title(),
                event_group=group,
                priority=priority,
                base_weight=weight,
            )
        )

    # Paramètres runtime du ruleset.
    params_data = [
        ("orb_multiplier_applying", "float", "1.2"),
        ("orb_multiplier_exact", "float", "1.5"),
        ("orb_multiplier_separating", "float", "0.8"),
        ("turning_point_threshold", "float", "0.7"),
        ("score_clamp_min", "float", "0.0"),
        ("score_clamp_max", "float", "100.0"),
        ("top_turning_points_count", "int", "3"),
        ("normalization_method", "string", "percentile"),
    ]
    for key, dtype, val in params_data:
        db.add(
            RulesetParameterModel(
                ruleset_id=ruleset_id, param_key=key, param_value=val, data_type=dtype
            )
        )


def run_prediction_reference_seed(db: Session) -> None:
    """Crée ou répare le seed canonique de la référence 2.0.0 et de ses rulesets."""
    # 1. Vérification d idempotence.
    v2 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0"))
    if v2 is not None:
        _ensure_astral_dignity_types(db)
        _ensure_astral_systems(db)
        if db.scalar(select(func.count()).select_from(AstralSignModel)) > 0:
            _ensure_astral_sign_profiles(db)
            _ensure_astral_planet_sign_dignities(db)
        actual = _check_counts(db, v2.id)

        # On exige au minimum la présence du ruleset 2.0.0 pour considérer
        # l amorçage comme partiellement réalisé.
        ruleset_v2 = db.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "2.0.0",
            )
        )

        all_ok = (
            all(actual.get(k, 0) == v for k, v in EXPECTED_COUNTS.items())
            and ruleset_v2 is not None
        )

        if all_ok and v2.is_locked:
            print("2.0.0 already seeded and locked — skipping")
            return

        if not v2.is_locked:
            print("2.0.0 exists but is unlocked — proceeding with repair/seed")
            # Chemin de réparation : purge des données partielles avant reseed.
            db.execute(
                delete(RulesetEventTypeModel).where(
                    RulesetEventTypeModel.ruleset_id.in_(
                        select(PredictionRulesetModel.id).where(
                            PredictionRulesetModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(RulesetParameterModel).where(
                    RulesetParameterModel.ruleset_id.in_(
                        select(PredictionRulesetModel.id).where(
                            PredictionRulesetModel.reference_version_id == v2.id
                        )
                    )
                )
            )
            db.execute(
                delete(PredictionRulesetModel).where(
                    PredictionRulesetModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(PointCategoryWeightModel).where(
                    PointCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(HouseCategoryWeightModel).where(
                    HouseCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(PlanetCategoryWeightModel).where(
                    PlanetCategoryWeightModel.reference_version_id == v2.id
                )
            )
            db.execute(
                delete(HouseProfileModel).where(HouseProfileModel.reference_version_id == v2.id)
            )
            db.execute(
                delete(PlanetProfileModel).where(PlanetProfileModel.reference_version_id == v2.id)
            )
            db.execute(delete(AstralSignProfileModel))
            db.execute(
                delete(AspectProfileModel).where(AspectProfileModel.reference_version_id == v2.id)
            )
            db.execute(
                delete(PredictionCategoryModel).where(
                    PredictionCategoryModel.reference_version_id == v2.id
                )
            )

            # Les structures sont stables et globales. En réparation on vérifie
            # seulement que le vocabulaire de base existe.
            has_basic_data = db.scalar(select(func.count()).select_from(PlanetModel)) > 0
            if not has_basic_data:
                repo = ReferenceRepository(db)
                repo.seed_version_defaults()
            db.flush()
            _ensure_astral_sign_profiles(db)
            _ensure_astral_planet_sign_dignities(db)
        else:
            # État corrompu ou incomplet alors que la version est verrouillée.
            lines = [
                (
                    "ERROR: 2.0.0 exists and is LOCKED but is incomplete. "
                    "Manual investigation required."
                )
            ]
            for k, expected in EXPECTED_COUNTS.items():
                got = actual.get(k, 0)
                status = "OK" if got == expected else f"MISMATCH (expected {expected}, got {got})"
                lines.append(f"  {k}: {status}")
            lines.append(f"  ruleset_v2_exists: {ruleset_v2 is not None}")
            lines.append(f"  is_locked: {v2.is_locked}")
            raise PredictionReferenceSeedAbortError("\n".join(lines))
    else:
        # 2. Initialisation de V1 et V2.
        v1 = db.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0")
        )
        if not v1:
            raise PredictionReferenceSeedAbortError(
                "Reference version 1.0.0 not found. Seed failed."
            )

        print("Creating reference version 2.0.0...")
        repo = ReferenceRepository(db)
        v2 = repo.create_version(
            version="2.0.0",
            description="Moteur de prédiction quotidienne v1 — référentiel sémantique complet",
        )
        v2.is_locked = False
        db.flush()

        # 3. Les structures stables existent deja via la reference 1.0.0.
        if not repo.has_complete_version_data():
            print("Seeding stable astrology structures...")
            repo.seed_version_defaults()
        db.flush()
        _ensure_astral_dignity_types(db)
        _ensure_astral_systems(db)
        _ensure_astral_sign_profiles(db)
        _ensure_astral_planet_sign_dignities(db)

    # 4. Alimentation des catégories de prédiction.
    print("Seeding prediction categories...")
    categories_data = [
        ("energy", "Energy", "Énergie", 1),
        ("mood", "Mood", "Humeur", 2),
        ("health", "Health", "Santé", 3),
        ("work", "Work", "Travail", 4),
        ("career", "Career", "Carrière", 5),
        ("money", "Money", "Argent", 6),
        ("love", "Love", "Amour", 7),
        ("sex_intimacy", "Sex & Intimacy", "Intimité", 8),
        ("family_home", "Family & Home", "Famille & Foyer", 9),
        ("social_network", "Social Network", "Réseau social", 10),
        ("communication", "Communication", "Communication", 11),
        ("pleasure_creativity", "Pleasure & Creativity", "Plaisir & Créativité", 12),
    ]
    for code, name, display_name, order in categories_data:
        db.add(
            PredictionCategoryModel(
                reference_version_id=v2.id,
                code=code,
                name=name,
                display_name=display_name,
                sort_order=order,
                is_public=True,
                is_enabled=True,
            )
        )
    db.flush()

    # Résolution des identifiants utiles pour les étapes suivantes.
    categories = {
        c.code: c.id
        for c in db.scalars(
            select(PredictionCategoryModel).where(
                PredictionCategoryModel.reference_version_id == v2.id
            )
        ).all()
    }
    planets = {p.code: p.id for p in db.scalars(select(PlanetModel)).all()}

    # 5. Alimentation des profils planétaires.
    print("Seeding planet profiles...")
    planet_profiles_data = [
        (
            "sun",
            "luminary",
            1,
            "slow",
            0.6,
            1.0,
            "positive",
            5.0,
            1.5,
            ["identité", "vitalité", "volonté", "ego", "créativité"],
        ),
        (
            "moon",
            "luminary",
            0,
            "fast",
            1.0,
            0.8,
            "neutral",
            4.5,
            1.2,
            ["émotions", "instinct", "humeur", "inconscient", "réceptivité"],
        ),
        (
            "mercury",
            "personal",
            2,
            "fast",
            0.9,
            0.7,
            "neutral",
            3.0,
            1.0,
            ["pensée", "communication", "analyse", "adaptation", "arbitrage"],
        ),
        (
            "venus",
            "personal",
            3,
            "medium",
            0.7,
            0.8,
            "positive",
            3.0,
            1.0,
            ["amour", "beauté", "harmonie", "plaisir", "relation"],
        ),
        (
            "mars",
            "personal",
            4,
            "medium",
            0.8,
            0.9,
            "negative",
            3.0,
            1.0,
            ["action", "énergie", "désir", "conflits", "sexualité"],
        ),
        (
            "jupiter",
            "social",
            5,
            "slow",
            0.4,
            1.0,
            "positive",
            2.5,
            0.8,
            ["expansion", "chance", "philosophie", "sagesse", "optimisme"],
        ),
        (
            "saturn",
            "social",
            6,
            "slow",
            0.3,
            1.0,
            "negative",
            2.5,
            0.8,
            ["structure", "discipline", "limites", "responsabilité", "karma"],
        ),
        (
            "uranus",
            "transpersonal",
            7,
            "slow",
            0.1,
            0.5,
            "neutral",
            2.0,
            0.6,
            ["rupture", "originalité", "innovation", "liberté", "révolution"],
        ),
        (
            "neptune",
            "transpersonal",
            8,
            "slow",
            0.1,
            0.4,
            "neutral",
            2.0,
            0.6,
            ["dissolution", "spiritualité", "illusion", "idéal", "compassion"],
        ),
        (
            "pluto",
            "transpersonal",
            9,
            "slow",
            0.1,
            0.3,
            "neutral",
            2.0,
            0.6,
            ["transformation", "pouvoir", "mort-renaissance", "profondeur", "obsession"],
        ),
    ]
    for (
        code,
        class_code,
        rank,
        speed,
        w_intra,
        w_climate,
        pol,
        orb_active,
        orb_peak,
        kws,
    ) in planet_profiles_data:
        db.add(
            PlanetProfileModel(
                reference_version_id=v2.id,
                planet_id=planets[code],
                class_code=class_code,
                speed_rank=rank,
                speed_class=speed,
                weight_intraday=w_intra,
                weight_day_climate=w_climate,
                typical_polarity=pol,
                orb_active_deg=orb_active,
                orb_peak_deg=orb_peak,
                keywords_json=json.dumps(kws),
            )
        )

    # 6. Alimentation des profils de maisons.
    print("Seeding house profiles...")
    house_profiles_data = [
        # numéro, type, visibilité, priorité
        (1, "angular", 1.0, 10),
        (2, "succedent", 0.7, 6),
        (3, "cadent", 0.5, 4),
        (4, "angular", 0.9, 9),
        (5, "succedent", 0.7, 6),
        (6, "cadent", 0.6, 5),
        (7, "angular", 0.9, 9),
        (8, "succedent", 0.7, 7),
        (9, "cadent", 0.5, 4),
        (10, "angular", 1.0, 10),
        (11, "succedent", 0.6, 5),
        (12, "cadent", 0.4, 3),
    ]
    houses = {h.number: h.id for h in db.scalars(select(HouseModel)).all()}
    for num, kind, vis, prio in house_profiles_data:
        db.add(
            HouseProfileModel(
                reference_version_id=v2.id,
                house_id=houses[num],
                house_kind=kind,
                visibility_weight=vis,
                base_priority=prio,
            )
        )

    # 7. Alimentation des poids planète -> catégorie.
    print("Seeding planet category weights...")
    pcw_data = [
        ("sun", "energy", 0.8, "primary"),
        ("sun", "mood", 0.6, "secondary"),
        ("sun", "health", 0.5, "secondary"),
        ("sun", "work", 0.6, "secondary"),
        ("sun", "career", 0.8, "primary"),
        ("sun", "money", 0.5, "secondary"),
        ("sun", "love", 0.5, "secondary"),
        ("sun", "pleasure_creativity", 0.6, "primary"),
        ("moon", "energy", 0.4, "secondary"),
        ("moon", "mood", 0.9, "primary"),
        ("moon", "health", 0.6, "primary"),
        ("moon", "love", 0.7, "primary"),
        ("moon", "sex_intimacy", 0.4, "secondary"),
        ("moon", "family_home", 0.8, "primary"),
        ("moon", "social_network", 0.4, "secondary"),
        ("moon", "pleasure_creativity", 0.4, "secondary"),
        ("mercury", "energy", 0.3, "secondary"),
        ("mercury", "mood", 0.4, "secondary"),
        ("mercury", "work", 0.8, "primary"),
        ("mercury", "career", 0.5, "secondary"),
        ("mercury", "money", 0.3, "secondary"),
        ("mercury", "love", 0.3, "secondary"),
        ("mercury", "social_network", 0.7, "secondary"),
        ("mercury", "communication", 0.9, "primary"),
        ("mercury", "pleasure_creativity", 0.4, "secondary"),
        ("venus", "energy", 0.3, "secondary"),
        ("venus", "mood", 0.6, "secondary"),
        ("venus", "health", 0.4, "secondary"),
        ("venus", "money", 0.6, "secondary"),
        ("venus", "love", 0.9, "primary"),
        ("venus", "sex_intimacy", 0.7, "primary"),
        ("venus", "family_home", 0.5, "secondary"),
        ("venus", "social_network", 0.6, "secondary"),
        ("venus", "communication", 0.4, "secondary"),
        ("venus", "pleasure_creativity", 0.8, "primary"),
        ("mars", "energy", 0.9, "primary"),
        ("mars", "mood", 0.4, "secondary"),
        ("mars", "health", 0.6, "secondary"),
        ("mars", "work", 0.7, "secondary"),
        ("mars", "career", 0.5, "secondary"),
        ("mars", "money", 0.3, "secondary"),
        ("mars", "love", 0.4, "secondary"),
        ("mars", "sex_intimacy", 0.8, "primary"),
        ("mars", "pleasure_creativity", 0.4, "secondary"),
        ("jupiter", "energy", 0.5, "secondary"),
        ("jupiter", "mood", 0.6, "secondary"),
        ("jupiter", "health", 0.4, "secondary"),
        ("jupiter", "work", 0.5, "secondary"),
        ("jupiter", "career", 0.8, "primary"),
        ("jupiter", "money", 0.7, "primary"),
        ("jupiter", "love", 0.4, "secondary"),
        ("jupiter", "family_home", 0.4, "secondary"),
        ("jupiter", "social_network", 0.6, "secondary"),
        ("jupiter", "communication", 0.4, "secondary"),
        ("jupiter", "pleasure_creativity", 0.6, "secondary"),
        ("saturn", "energy", 0.3, "secondary"),
        ("saturn", "work", 0.7, "primary"),
        ("saturn", "career", 0.7, "primary"),
        ("saturn", "money", 0.5, "secondary"),
        ("saturn", "health", 0.5, "secondary"),
        ("saturn", "family_home", 0.4, "secondary"),
        ("uranus", "energy", 0.4, "secondary"),
        ("uranus", "mood", 0.3, "secondary"),
        ("uranus", "work", 0.4, "secondary"),
        ("uranus", "career", 0.4, "secondary"),
        ("uranus", "sex_intimacy", 0.3, "secondary"),
        ("uranus", "social_network", 0.5, "secondary"),
        ("uranus", "communication", 0.4, "secondary"),
        ("uranus", "pleasure_creativity", 0.5, "secondary"),
        ("neptune", "mood", 0.5, "secondary"),
        ("neptune", "health", 0.3, "secondary"),
        ("neptune", "love", 0.5, "secondary"),
        ("neptune", "sex_intimacy", 0.4, "secondary"),
        ("neptune", "family_home", 0.3, "secondary"),
        ("neptune", "social_network", 0.4, "secondary"),
        ("neptune", "pleasure_creativity", 0.5, "secondary"),
        ("pluto", "energy", 0.5, "secondary"),
        ("pluto", "mood", 0.3, "secondary"),
        ("pluto", "health", 0.4, "secondary"),
        ("pluto", "work", 0.4, "secondary"),
        ("pluto", "career", 0.5, "secondary"),
        ("pluto", "money", 0.5, "secondary"),
        ("pluto", "love", 0.4, "secondary"),
        ("pluto", "sex_intimacy", 0.6, "secondary"),
        ("pluto", "pleasure_creativity", 0.3, "secondary"),
    ]
    for p_code, c_code, weight, role in pcw_data:
        db.add(
            PlanetCategoryWeightModel(
                reference_version_id=v2.id,
                planet_id=planets[p_code],
                category_id=categories[c_code],
                weight=weight,
                influence_role=role,
            )
        )

    # 8. Alimentation des poids maison -> catégorie.
    print("Seeding house category weights...")
    hcw_data = [
        (1, "energy", 0.8, "primary"),
        (1, "mood", 0.6, "secondary"),
        (2, "money", 0.9, "primary"),
        (2, "work", 0.5, "secondary"),
        (3, "communication", 0.9, "primary"),
        (3, "social_network", 0.5, "secondary"),
        (4, "family_home", 0.9, "primary"),
        (4, "mood", 0.5, "secondary"),
        (5, "pleasure_creativity", 0.9, "primary"),
        (5, "love", 0.6, "secondary"),
        (6, "health", 0.9, "primary"),
        (6, "work", 0.7, "secondary"),
        (7, "love", 0.8, "primary"),
        (7, "social_network", 0.6, "secondary"),
        (8, "sex_intimacy", 0.8, "primary"),
        (8, "money", 0.6, "secondary"),
        (9, "pleasure_creativity", 0.5, "secondary"),
        (9, "career", 0.4, "secondary"),
        (10, "career", 0.9, "primary"),
        (10, "work", 0.6, "secondary"),
        (11, "social_network", 0.9, "primary"),
        (11, "pleasure_creativity", 0.5, "secondary"),
        (12, "mood", 0.5, "secondary"),
        (12, "health", 0.4, "secondary"),
    ]
    for house_num, c_code, weight, role in hcw_data:
        db.add(
            HouseCategoryWeightModel(
                reference_version_id=v2.id,
                house_id=houses[house_num],
                category_id=categories[c_code],
                weight=weight,
                routing_role=role,
            )
        )

    # 9. Alimentation des points astrologiques.
    print("Seeding astro points...")
    points_data = [
        ("asc", "Ascendant", "angle"),
        ("dsc", "Descendant", "angle"),
        ("mc", "Midheaven (MC)", "angle"),
        ("ic", "Imum Coeli (IC)", "angle"),
    ]
    for code, name, ptype in points_data:
        existing_point = db.scalar(select(AstroPointModel).where(AstroPointModel.code == code))
        if existing_point is None:
            db.add(AstroPointModel(code=code, name=name, point_type=ptype))
    db.flush()

    # Alimentation des poids point -> catégorie.
    points = {p.code: p.id for p in db.scalars(select(AstroPointModel)).all()}
    pcw_points_data = [
        ("asc", "energy", 0.8),
        ("asc", "mood", 0.7),
        ("mc", "career", 0.9),
        ("mc", "work", 0.6),
        ("dsc", "love", 0.7),
        ("dsc", "social_network", 0.6),
        ("ic", "family_home", 0.9),
        ("ic", "mood", 0.5),
    ]
    for p_code, c_code, weight in pcw_points_data:
        db.add(
            PointCategoryWeightModel(
                reference_version_id=v2.id,
                point_id=points[p_code],
                category_id=categories[c_code],
                weight=weight,
            )
        )

    # 10. Consolidation des dignités qui portent les maîtrises de signes.
    print("Seeding planet sign dignities...")
    _ensure_astral_planet_sign_dignities(db)

    # 11. Alimentation des profils d aspects.
    print("Seeding aspect profiles...")
    aspects_data = [
        # code, intensité, valence, multiplicateur d orbe, sensibilité à la phase
        ("conjunction", 1.5, "contextual", 1.0, False),
        ("sextile", 0.8, "favorable", 0.9, False),
        ("square", 1.2, "challenging", 1.0, False),
        ("trine", 1.0, "favorable", 1.0, False),
        ("opposition", 1.3, "polarizing", 1.0, True),
    ]
    aspects = {a.code: a.id for a in db.scalars(select(AspectModel)).all()}
    for code, intensity, valence, orb, phase in aspects_data:
        db.add(
            AspectProfileModel(
                reference_version_id=v2.id,
                aspect_id=aspects[code],
                intensity_weight=intensity,
                default_valence=valence,
                orb_multiplier=orb,
                phase_sensitive=phase,
            )
        )

    # 12. Alimentation du ruleset 1.0.0 (legacy).
    print("Seeding ruleset 1.0.0 (legacy)...")
    ruleset_v1 = PredictionRulesetModel(
        version="1.0.0",
        reference_version_id=v2.id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        description="Ruleset legacy (v1) rattaché à la référence 2.0.0",
        is_locked=False,
    )
    db.add(ruleset_v1)
    db.flush()
    _seed_ruleset_content(db, ruleset_v1.id)

    # 13. Alimentation du ruleset 2.0.0 (canonique).
    print("Seeding ruleset 2.0.0 (canonical)...")
    ruleset_v2 = PredictionRulesetModel(
        version="2.0.0",
        reference_version_id=v2.id,
        zodiac_type="tropical",
        coordinate_mode="geocentric",
        house_system="placidus",
        time_step_minutes=30,
        description="Ruleset canonique v2 rattaché à la référence 2.0.0",
        is_locked=False,
    )
    db.add(ruleset_v2)
    db.flush()
    _seed_ruleset_content(db, ruleset_v2.id)
    db.flush()

    # 14. Validation des comptages attendus.
    print("Validating counts...")
    actual = _check_counts(db, v2.id)
    for k, expected in EXPECTED_COUNTS.items():
        got = actual.get(k, 0)
        if got != expected:
            raise ValueError(f"Validation failed for {k}: expected {expected}, got {got}")

    # 16. Verrouillage final de V2.
    print("Locking reference version 2.0.0...")
    v2.is_locked = True
    db.flush()
    print("Seed 31.3 completed successfully.")


__all__ = [
    "PredictionReferenceSeedAbortError",
    "run_prediction_reference_seed",
]
