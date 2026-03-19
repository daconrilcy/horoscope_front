from app.prediction.public_label_catalog import (
    CLIMATE_LABELS,
    REGIME_ACTION_HINTS,
    REGIME_LABELS,
    TP_FALLBACK_TITLES,
    WINDOW_ACTIONS,
    WINDOW_WHY_TEMPLATES,
    get_action_hint,
    get_best_window_why,
    get_climate_label,
    get_do_avoid,
    get_recommended_actions,
    get_turning_point_title,
)


def test_no_equilibre_in_dicts():
    # AC3: "équilibré" forbidden in labels except day_climate.summary
    for label in CLIMATE_LABELS.values():
        assert "équilibré" not in label.lower()

    for labels in REGIME_LABELS.values():
        for label in labels:
            assert "équilibré" not in label.lower()

    for hint in REGIME_ACTION_HINTS.values():
        assert "équilibré" not in hint.lower()


def test_regime_coverage():
    regimes = [
        "progression",
        "fluidité",
        "prudence",
        "pivot",
        "récupération",
        "retombée",
        "mise_en_route",
        "recentrage",
    ]
    for r in regimes:
        assert r in REGIME_LABELS
        assert r in REGIME_ACTION_HINTS
        assert get_action_hint(r) != "Suivez votre rythme", f"Missing action hint for regime {r}"


def test_change_type_coverage():
    change_types = ["emergence", "recomposition", "attenuation"]
    for ct in change_types:
        assert ct in TP_FALLBACK_TITLES
        assert get_turning_point_title(ct, None) != "Moment de bascule"


def test_public_domain_coverage():
    domains = [
        "pro_ambition",
        "relations_echanges",
        "energie_bienetre",
        "argent_ressources",
        "vie_personnelle",
    ]
    for d in domains:
        assert d in WINDOW_WHY_TEMPLATES
        assert d in WINDOW_ACTIONS
        assert get_best_window_why(d) != "Les conditions astrologiques convergent favorablement."
        assert len(get_recommended_actions(d)) == 3


def test_get_climate_label():
    assert get_climate_label("positive", 8.0) == "Journée de forte progression"
    assert get_climate_label("neutral", 5.0) == "Climat stable et fluide"
    assert get_climate_label("negative", 2.0) == "Petite réserve passagère"


def test_get_do_avoid_fallback():
    do, avoid = get_do_avoid("unknown_type", None)
    assert do == "Rester à l'écoute"
    assert avoid == "Agir avec précipitation"
