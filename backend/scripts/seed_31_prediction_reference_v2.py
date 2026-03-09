import json
import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.db.models import (
    AspectModel,
    AspectProfileModel,
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
    SignModel,
    SignRulershipModel,
)
from app.infra.db.repositories import ReferenceRepository
from app.infra.db.session import SessionLocal


class SeedAbortError(RuntimeError):
    pass


EXPECTED_COUNTS = {
    "prediction_categories": 12,
    "planet_profiles": 10,
    "house_profiles": 12,
    "aspect_profiles": 5,
    "astro_points": 4,
    "sign_rulerships": 12,
    "planet_category_weights": 85,
    "house_category_weights": 24,
    "point_category_weights": 8,
    "ruleset_event_types": 16,  # 8 per ruleset (1.0.0 and 2.0.0)
    "ruleset_parameters": 16,   # 8 per ruleset (1.0.0 and 2.0.0)
}


def _check_counts(db: Session, reference_version_id: int) -> dict[str, int]:
    actual = {}
    actual["prediction_categories"] = db.scalar(
        select(func.count())
        .select_from(PredictionCategoryModel)
        .where(PredictionCategoryModel.reference_version_id == reference_version_id)
    )
    actual["planet_profiles"] = db.scalar(
        select(func.count())
        .select_from(PlanetProfileModel)
        .join(PlanetModel, PlanetProfileModel.planet_id == PlanetModel.id)
        .where(PlanetModel.reference_version_id == reference_version_id)
    )
    actual["house_profiles"] = db.scalar(
        select(func.count())
        .select_from(HouseProfileModel)
        .join(HouseModel, HouseProfileModel.house_id == HouseModel.id)
        .where(HouseModel.reference_version_id == reference_version_id)
    )
    actual["aspect_profiles"] = db.scalar(
        select(func.count())
        .select_from(AspectProfileModel)
        .join(AspectModel, AspectProfileModel.aspect_id == AspectModel.id)
        .where(AspectModel.reference_version_id == reference_version_id)
    )
    actual["astro_points"] = db.scalar(
        select(func.count())
        .select_from(AstroPointModel)
        .where(AstroPointModel.reference_version_id == reference_version_id)
    )
    actual["sign_rulerships"] = db.scalar(
        select(func.count())
        .select_from(SignRulershipModel)
        .where(SignRulershipModel.reference_version_id == reference_version_id)
    )
    actual["planet_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PlanetCategoryWeightModel)
        .join(PlanetModel, PlanetCategoryWeightModel.planet_id == PlanetModel.id)
        .where(PlanetModel.reference_version_id == reference_version_id)
    )
    actual["house_category_weights"] = db.scalar(
        select(func.count())
        .select_from(HouseCategoryWeightModel)
        .join(HouseModel, HouseCategoryWeightModel.house_id == HouseModel.id)
        .where(HouseModel.reference_version_id == reference_version_id)
    )
    actual["point_category_weights"] = db.scalar(
        select(func.count())
        .select_from(PointCategoryWeightModel)
        .join(AstroPointModel, PointCategoryWeightModel.point_id == AstroPointModel.id)
        .where(AstroPointModel.reference_version_id == reference_version_id)
    )

    # Rulesets are tied to reference_version_id
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
    """Seed event types and parameters for a specific ruleset."""
    # Seed event types — (code, group, priority, base_weight)
    # Priorities are calibrated against TurningPointDetector.PRIORITY_PIVOT_THRESHOLD = 65:
    #   >= 65: can trigger a high_priority_event pivot
    #   < 65:  enriches existing pivots only
    event_types_data = [
        ("aspect_exact_to_angle",    "aspect",  80, 2.0),  # above pivot threshold
        ("aspect_exact_to_luminary", "aspect",  75, 1.8),  # above pivot threshold
        ("aspect_exact_to_personal", "aspect",  68, 1.5),  # slightly above pivot threshold
        ("aspect_enter_orb",         "aspect",  40, 1.0),  # below threshold — enriches only
        ("aspect_exit_orb",          "aspect",  25, 0.5),  # below threshold
        ("moon_sign_ingress",        "ingress", 72, 1.5),  # above pivot threshold
        ("asc_sign_change",          "ingress", 78, 2.0),  # above pivot threshold — structurant
        ("planetary_hour_change",    "timing",  20, 0.8),  # well below threshold
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

    # Seed parameters
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


def run_seed(db: Session):
    # 1. Idempotence Check
    v2 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0"))
    if v2 is not None:
        actual = _check_counts(db, v2.id)
        
        # We check if at least version 2.0.0 ruleset exists to consider it partly done
        ruleset_v2 = db.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "2.0.0"
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
            # Repair path: clear existing partial data for v2 before re-seeding
            from sqlalchemy import delete
            db.execute(delete(RulesetEventTypeModel).where(RulesetEventTypeModel.ruleset_id.in_(
                select(PredictionRulesetModel.id).where(PredictionRulesetModel.reference_version_id == v2.id)
            )))
            db.execute(delete(RulesetParameterModel).where(RulesetParameterModel.ruleset_id.in_(
                select(PredictionRulesetModel.id).where(PredictionRulesetModel.reference_version_id == v2.id)
            )))
            db.execute(delete(PredictionRulesetModel).where(PredictionRulesetModel.reference_version_id == v2.id))
            db.execute(delete(PointCategoryWeightModel).where(PointCategoryWeightModel.point_id.in_(
                select(AstroPointModel.id).where(AstroPointModel.reference_version_id == v2.id)
            )))
            db.execute(delete(AstroPointModel).where(AstroPointModel.reference_version_id == v2.id))
            db.execute(delete(HouseCategoryWeightModel).where(HouseCategoryWeightModel.house_id.in_(
                select(HouseModel.id).where(HouseModel.reference_version_id == v2.id)
            )))
            db.execute(delete(PlanetCategoryWeightModel).where(PlanetCategoryWeightModel.planet_id.in_(
                select(PlanetModel.id).where(PlanetModel.reference_version_id == v2.id)
            )))
            db.execute(delete(HouseProfileModel).where(HouseProfileModel.house_id.in_(
                select(HouseModel.id).where(HouseModel.reference_version_id == v2.id)
            )))
            db.execute(delete(PlanetProfileModel).where(PlanetProfileModel.planet_id.in_(
                select(PlanetModel.id).where(PlanetModel.reference_version_id == v2.id)
            )))
            db.execute(delete(SignRulershipModel).where(SignRulershipModel.reference_version_id == v2.id))
            db.execute(delete(AspectProfileModel).where(AspectProfileModel.aspect_id.in_(
                select(AspectModel.id).where(AspectModel.reference_version_id == v2.id)
            )))
            db.execute(delete(PredictionCategoryModel).where(PredictionCategoryModel.reference_version_id == v2.id))
            
            # Step 3 must be re-run if we are repairing, as ReferenceRepository.clone_version_data 
            # might have been partially executed. However, clone_version_data itself is not 
            # easily "partially" undoable without deleting the ReferenceVersion itself.
            # For simplicity in this script, we assume if v2 exists, clone_version_data was called.
            # If we want to be 100% safe, we'd need to check if Planets/Houses exist in V2.
            has_basic_data = db.scalar(select(func.count()).select_from(PlanetModel).where(PlanetModel.reference_version_id == v2.id)) > 0
            if not has_basic_data:
                v1 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0"))
                if not v1:
                    raise SeedAbortError("Reference version 1.0.0 not found for cloning.")
                print("Cloning V1 data to V2...")
                repo = ReferenceRepository(db)
                repo.clone_version_data(v1.id, v2.id)
            db.flush()
        else:
            # State corrupted or incomplete AND locked
            lines = [
                "ERROR: 2.0.0 exists and is LOCKED but is incomplete. Manual investigation required."
            ]
            for k, expected in EXPECTED_COUNTS.items():
                got = actual.get(k, 0)
                status = "OK" if got == expected else f"MISMATCH (expected {expected}, got {got})"
                lines.append(f"  {k}: {status}")
            lines.append(f"  ruleset_v2_exists: {ruleset_v2 is not None}")
            lines.append(f"  is_locked: {v2.is_locked}")
            raise SeedAbortError("\n".join(lines))
    else:
        # 2. Setup V1 and V2
        v1 = db.scalar(select(ReferenceVersionModel).where(ReferenceVersionModel.version == "1.0.0"))
        if not v1:
            print("ERROR: Reference version 1.0.0 not found. Seed failed.")
            sys.exit(1)

        print("Creating reference version 2.0.0...")
        repo = ReferenceRepository(db)
        v2 = repo.create_version(
            version="2.0.0",
            description="Moteur de prédiction quotidienne v1 — référentiel sémantique complet",
        )
        v2.is_locked = False
        db.flush()

        # 3. Clone V1 to V2
        print("Cloning V1 data to V2...")
        repo.clone_version_data(v1.id, v2.id)
        db.flush()

    # 4. Seed prediction categories
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

    # Resolve IDs
    categories = {
        c.code: c.id
        for c in db.scalars(
            select(PredictionCategoryModel).where(
                PredictionCategoryModel.reference_version_id == v2.id
            )
        ).all()
    }
    planets = {
        p.code: p.id
        for p in db.scalars(
            select(PlanetModel).where(PlanetModel.reference_version_id == v2.id)
        ).all()
    }

    # 5. Seed planet profiles
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

    # 6. Seed house profiles
    print("Seeding house profiles...")
    house_profiles_data = [
        # number, kind, visibility, priority
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
    houses = {
        h.number: h.id
        for h in db.scalars(
            select(HouseModel).where(HouseModel.reference_version_id == v2.id)
        ).all()
    }
    for num, kind, vis, prio in house_profiles_data:
        db.add(
            HouseProfileModel(
                house_id=houses[num],
                house_kind=kind,
                visibility_weight=vis,
                base_priority=prio,
            )
        )

    # 7. Seed planet → category weights
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
                planet_id=planets[p_code],
                category_id=categories[c_code],
                weight=weight,
                influence_role=role,
            )
        )

    # 8. Seed house → category weights
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
                house_id=houses[house_num],
                category_id=categories[c_code],
                weight=weight,
                routing_role=role,
            )
        )

    # 9. Seed astro points
    print("Seeding astro points...")
    points_data = [
        ("asc", "Ascendant", "angle"),
        ("dsc", "Descendant", "angle"),
        ("mc", "Midheaven (MC)", "angle"),
        ("ic", "Imum Coeli (IC)", "angle"),
    ]
    for code, name, ptype in points_data:
        db.add(AstroPointModel(reference_version_id=v2.id, code=code, name=name, point_type=ptype))
    db.flush()

    # Seed point category weights
    points = {
        p.code: p.id
        for p in db.scalars(
            select(AstroPointModel).where(AstroPointModel.reference_version_id == v2.id)
        ).all()
    }
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
                point_id=points[p_code], category_id=categories[c_code], weight=weight
            )
        )

    # 10. Seed sign rulerships
    print("Seeding sign rulerships...")
    rulerships_data = [
        ("aries", "mars", True),
        ("taurus", "venus", True),
        ("gemini", "mercury", True),
        ("cancer", "moon", True),
        ("leo", "sun", True),
        ("virgo", "mercury", True),
        ("libra", "venus", True),
        ("scorpio", "mars", True),
        ("sagittarius", "jupiter", True),
        ("capricorn", "saturn", True),
        ("aquarius", "saturn", True),
        ("pisces", "jupiter", True),
    ]
    signs = {
        s.code: s.id
        for s in db.scalars(select(SignModel).where(SignModel.reference_version_id == v2.id)).all()
    }
    for s_code, p_code, is_pri in rulerships_data:
        db.add(
            SignRulershipModel(
                reference_version_id=v2.id,
                sign_id=signs[s_code],
                planet_id=planets[p_code],
                is_primary=is_pri,
                rulership_type="domicile",
            )
        )

    # 11. Seed aspect profiles
    print("Seeding aspect profiles...")
    aspects_data = [
        # code, intensity, valence, orb_mult, phase
        ("conjunction", 1.5, "contextual", 1.0, False),
        ("sextile", 0.8, "favorable", 0.9, False),
        ("square", 1.2, "challenging", 1.0, False),
        ("trine", 1.0, "favorable", 1.0, False),
        ("opposition", 1.3, "polarizing", 1.0, True),
    ]
    aspects = {
        a.code: a.id
        for a in db.scalars(
            select(AspectModel).where(AspectModel.reference_version_id == v2.id)
        ).all()
    }
    for code, intensity, valence, orb, phase in aspects_data:
        db.add(
            AspectProfileModel(
                aspect_id=aspects[code],
                intensity_weight=intensity,
                default_valence=valence,
                orb_multiplier=orb,
                phase_sensitive=phase,
            )
        )

    # 12. Seed ruleset 1.0.0 (legacy)
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

    # 13. Seed ruleset 2.0.0 (canonical)
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

    # 14. Validation counts
    print("Validating counts...")
    actual = _check_counts(db, v2.id)
    for k, expected in EXPECTED_COUNTS.items():
        got = actual.get(k, 0)
        if got != expected:
            raise ValueError(f"Validation failed for {k}: expected {expected}, got {got}")

    # 16. Lock V2
    print("Locking reference version 2.0.0...")
    v2.is_locked = True
    db.flush()
    print("Seed 31.3 completed successfully.")


def main():
    with SessionLocal() as db:
        try:
            with db.begin():
                run_seed(db)
        except SeedAbortError as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Seed failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
