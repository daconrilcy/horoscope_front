from app.prediction.public_domain_taxonomy import (
    PUBLIC_DOMAINS,
    aggregate_public_domain_score,
    map_internal_to_public,
)


def test_map_internal_to_public():
    assert map_internal_to_public("work") == "pro_ambition"
    assert map_internal_to_public("career") == "pro_ambition"
    assert map_internal_to_public("love") == "relations_echanges"
    assert map_internal_to_public("communication") == "relations_echanges"
    assert map_internal_to_public("social_network") == "relations_echanges"
    assert map_internal_to_public("sex_intimacy") == "relations_echanges"
    assert map_internal_to_public("energy") == "energie_bienetre"
    assert map_internal_to_public("health") == "energie_bienetre"
    assert map_internal_to_public("mood") == "energie_bienetre"
    assert map_internal_to_public("money") == "argent_ressources"
    assert map_internal_to_public("pleasure_creativity") == "vie_personnelle"
    assert map_internal_to_public("family_home") == "vie_personnelle"
    assert map_internal_to_public("unknown") is None

def test_aggregate_public_domain_score():
    internal_scores = {
        "work": 14.0,
        "career": 18.0,
        "love": 12.0,
        "communication": 15.0,
        "energy": 10.0,
    }
    aggregated = aggregate_public_domain_score(internal_scores)
    
    assert aggregated["pro_ambition"] == 18.0
    assert aggregated["relations_echanges"] == 15.0
    assert aggregated["energie_bienetre"] == 10.0
    assert "argent_ressources" not in aggregated
    assert "vie_personnelle" not in aggregated

def test_public_domains_count():
    assert len(PUBLIC_DOMAINS) == 5
    expected_keys = {
        "pro_ambition",
        "relations_echanges",
        "energie_bienetre",
        "argent_ressources",
        "vie_personnelle"
    }
    assert set(PUBLIC_DOMAINS.keys()) == expected_keys
