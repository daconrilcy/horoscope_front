from enum import Enum


class ComputeMode(Enum):
    compute_if_missing = "compute_if_missing"
    force_recompute = "force_recompute"
    read_only = "read_only"


class DailyPredictionServiceError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")
