from app.domain.llm.runtime.hard_policy import get_hard_policy


def test_get_hard_policy_astrology():
    policy = get_hard_policy("astrology")
    assert "assistant d'interprétation astrologique" in policy
    assert "Ne crée jamais de placements, aspects ou faits inexistants" in policy


def test_get_hard_policy_support():
    policy = get_hard_policy("support")
    assert "assistant de support client" in policy
    assert "d'interprétation astrologique" in policy
