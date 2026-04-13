from pathlib import Path

import pytest

from app.llm_orchestration.services.doc_conformity_validator import DocConformityValidator


def test_doc_conformity_validator_taxonomy():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)
    content = root / "docs" / "llm-prompt-generation-by-feature.md"
    if not content.exists():
        pytest.skip("Doc file not found")

    doc_content = content.read_text(encoding="utf-8")
    errors = validator.validate_taxonomy(doc_content)
    assert not errors, f"Taxonomy errors in doc: {errors}"


def test_doc_conformity_validator_providers():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)
    content = root / "docs" / "llm-prompt-generation-by-feature.md"
    if not content.exists():
        pytest.skip("Doc file not found")

    doc_content = content.read_text(encoding="utf-8")
    errors = validator.validate_providers(doc_content)
    assert not errors, f"Provider errors in doc: {errors}"


def test_doc_conformity_validator_fallbacks():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)
    content = root / "docs" / "llm-prompt-generation-by-feature.md"
    if not content.exists():
        pytest.skip("Doc file not found")

    doc_content = content.read_text(encoding="utf-8")
    errors = validator.validate_fallbacks(doc_content)
    assert not errors, f"Fallback errors in doc: {errors}"


def test_doc_conformity_validator_obs_snapshot_classification():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)
    content = root / "docs" / "llm-prompt-generation-by-feature.md"
    if not content.exists():
        pytest.skip("Doc file not found")

    doc_content = content.read_text(encoding="utf-8")
    errors = validator.validate_obs_snapshot_classification(doc_content)
    assert not errors, f"ObsSnapshot errors in doc: {errors}"


def test_doc_conformity_is_update_required():
    validator = DocConformityValidator(Path("/tmp"))

    assert validator.is_update_required(["backend/app/llm_orchestration/gateway.py"])
    assert validator.is_update_required(["docs/llm-prompt-generation-by-feature.md"])
    assert not validator.is_update_required(["backend/app/main.py"])
    assert not validator.is_update_required(["frontend/src/App.tsx"])


def test_doc_conformity_check_verification_reference_updated():
    validator = DocConformityValidator(Path("/tmp"))

    old_content = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
    """

    new_content_same = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
    """

    new_content_updated_date = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-13`
- **Référence stable (Commit SHA)** : `abcdef1`
Si le code diverge
    """

    new_content_updated_ref = """
Dernière vérification manuelle contre le pipeline réel du gateway :
- **Date** : `2026-04-10`
- **Référence stable (Commit SHA)** : `f123154`
Si le code diverge
    """

    assert not validator.check_verification_reference_updated(old_content, new_content_same)
    assert validator.check_verification_reference_updated(old_content, new_content_updated_date)
    assert validator.check_verification_reference_updated(old_content, new_content_updated_ref)


def test_taxonomy_mismatch_fails_validation():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)

    # Fake content with missing family
    fake_content = (
        "| `chat` | ... | `nominal_canonical` |\n"  # guidance, natal, horoscope_daily missing
    )
    errors = validator.validate_taxonomy(fake_content)
    assert len(errors) >= 3
    assert any("guidance" in e for e in errors)
    assert any("natal" in e for e in errors)
    assert any("horoscope_daily" in e for e in errors)


def test_provider_mismatch_fails_validation():
    root = Path(__file__).resolve().parents[3]
    validator = DocConformityValidator(root)

    # Fake content with wrong provider
    fake_content = "nominalement uniquement par `anthropic`"
    errors = validator.validate_providers(fake_content)
    assert len(errors) == 1
    assert "openai" in errors[0]
