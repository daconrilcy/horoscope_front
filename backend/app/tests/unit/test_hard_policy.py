import pytest

from app.llm_orchestration.policies.hard_policy import get_hard_policy


def test_get_hard_policy_astrology():
    policy = get_hard_policy("astrology")
    assert "assistant d’interprétation astrologique et de tarot" in policy
    assert "tendances et de pistes" in policy


def test_get_hard_policy_support():
    policy = get_hard_policy("support")
    assert "contenu ésotérique" in policy
    assert "assistant de support client" in policy


def test_get_hard_policy_transactional():
    policy = get_hard_policy("transactional")
    assert "assistant transactionnel" in policy
    assert "exacte et vérifiable" in policy


def test_get_hard_policy_unknown():
    with pytest.raises(ValueError):
        get_hard_policy("unknown")
