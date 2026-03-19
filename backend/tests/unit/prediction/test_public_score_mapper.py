from app.prediction.public_score_mapper import (
    PublicDomainScore,
    rank_domains,
    to_level,
    to_score_10,
)


def test_to_score_10():
    assert to_score_10(20.0) == 10.0
    assert to_score_10(0.0) == 0.0
    assert to_score_10(15.0) == 7.5
    assert to_score_10(10.0) == 5.0
    assert to_score_10(19.5) == 9.8

def test_to_level():
    assert to_level(9.0) == "très_favorable"
    assert to_level(10.0) == "très_favorable"
    assert to_level(7.5) == "favorable"
    assert to_level(8.9) == "favorable"
    assert to_level(6.0) == "stable"
    assert to_level(7.4) == "stable"
    assert to_level(4.5) == "mitigé"
    assert to_level(5.9) == "mitigé"
    assert to_level(4.4) == "exigeant"
    assert to_level(0.0) == "exigeant"

def test_rank_domains():
    def _d(key: str, label: str, score_10: float, note: float, order: int) -> PublicDomainScore:
        return PublicDomainScore(
            key=key, label=label, score_10=score_10, level="L", rank=0,
            note_20_internal=note, internal_codes=[], display_order=order,
        )
    domains = [
        _d("d1", "L1", 5.0, 10.0, 1),
        _d("d2", "L2", 8.0, 16.0, 2),
        _d("d3", "L3", 7.0, 14.0, 3),
    ]
    ranked = rank_domains(domains)
    
    assert ranked[0].key == "d2"
    assert ranked[0].rank == 1
    assert ranked[1].key == "d3"
    assert ranked[1].rank == 2
    assert ranked[2].key == "d1"
    assert ranked[2].rank == 3

def test_rank_domains_empty():
    assert rank_domains([]) == []
