# Validation des preuves requises avant exposition publique des transits.
"""Vérifie les preuves CS-280 et CS-281 avant toute projection transit client."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TransitProjectionProofResult:
    """Résultat de proof gate exploitable par le service de projection."""

    is_valid: bool
    public_refs: tuple[str, ...]
    missing_paths: tuple[str, ...] = ()
    invalid_paths: tuple[str, ...] = ()


class TransitProjectionProofGateUnavailable(Exception):
    """Signale une preuve attendue présente mais impossible à lire."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code


class TransitProjectionProofGate:
    """Contrôle les preuves persistées des dépendances transit obligatoires."""

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = repo_root or Path(__file__).resolve().parents[4]

    def validate(self) -> TransitProjectionProofResult:
        """Retourne un blocage explicite si une preuve attendue est absente ou invalide."""
        required_proofs = (
            (
                self._repo_root
                / (
                    "_condamad/stories/CS-280-internal-transit-runtime/"
                    "generated/10-final-evidence.md"
                ),
                "Validation outcome: PASS",
            ),
            (
                self._repo_root
                / "_condamad/stories/CS-280-internal-transit-runtime/evidence/validation.txt",
                "PASS:",
            ),
            (
                self._repo_root
                / (
                    "_condamad/stories/CS-281-transit-client-projection-by-plan/"
                    "generated/10-final-evidence.md"
                ),
                "Validation outcome: PASS",
            ),
            (
                self._repo_root
                / (
                    "_condamad/stories/CS-281-transit-client-projection-by-plan/"
                    "evidence/validation.txt"
                ),
                "Result: PASS",
            ),
            (
                self._repo_root / "docs/architecture/transit-client-projection-v1-contract.md",
                "transit_client_projection_v1",
            ),
        )
        missing = tuple(
            str(path.relative_to(self._repo_root))
            for path, _marker in required_proofs
            if not path.exists()
        )
        invalid_paths: list[str] = []
        for path, marker in required_proofs:
            if not path.exists():
                continue
            relative_path = str(path.relative_to(self._repo_root))
            try:
                proof_content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise TransitProjectionProofGateUnavailable(
                    f"proof_evidence_unavailable:{relative_path}"
                ) from exc
            if marker not in proof_content:
                invalid_paths.append(relative_path)
        invalid = tuple(invalid_paths)
        if missing or invalid:
            return TransitProjectionProofResult(
                is_valid=False,
                public_refs=(),
                missing_paths=missing,
                invalid_paths=invalid,
            )
        return TransitProjectionProofResult(
            is_valid=True,
            public_refs=(
                "CS-280:final-evidence",
                "CS-280:validation",
                "CS-281:final-evidence",
                "CS-281:validation",
                "transit-client-projection-v1-contract",
            ),
        )
