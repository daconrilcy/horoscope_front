from app.infra.llm.anonymizer import anonymize_text


def test_anonymize_text_redacts_direct_identifiers() -> None:
    text = (
        "email=user@example.com; phone=+33 6 12 34 56 78; "
        "name: Jean Dupont; adresse=10 rue de Paris; user_id=12345"
    )
    anonymized = anonymize_text(text)

    assert "user@example.com" not in anonymized
    assert "+33 6 12 34 56 78" not in anonymized
    assert "Jean Dupont" not in anonymized
    assert "10 rue de Paris" not in anonymized
    assert "12345" not in anonymized
    assert "[redacted_email_" in anonymized
    assert "[redacted_phone_" in anonymized
    assert "[redacted_name_" in anonymized
    assert "[redacted_address_" in anonymized
    assert "[redacted_id_" in anonymized


def test_anonymize_text_is_deterministic_for_same_input() -> None:
    text = "Mon email est deterministic@example.com"
    assert anonymize_text(text) == anonymize_text(text)


def test_anonymize_text_redacts_uuid_without_partial_leak() -> None:
    text = "uuid: 123e4567-e89b-12d3-a456-426614174000"
    anonymized = anonymize_text(text)

    assert "123e4567-e89b-12d3-a456-426614174000" not in anonymized
    assert "123e4567-e89b-12d3-a456" not in anonymized
    assert "[redacted_id_" in anonymized


def test_anonymize_text_redacts_generic_id_patterns() -> None:
    text = "id=12345; Mon identifiant interne est 998877"
    anonymized = anonymize_text(text)

    assert "12345" not in anonymized
    assert "998877" not in anonymized
    assert "[redacted_id_" in anonymized
