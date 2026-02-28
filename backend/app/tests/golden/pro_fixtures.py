from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GoldenProSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engine: str
    ephe: str
    frame: str
    zodiac: str
    house_system: str


class GoldenProExpected(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sun: float
    moon: float
    mercury: float
    asc: float
    mc: float
    cusp_1: float
    cusp_10: float


class GoldenProDateTime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: str
    birth_time: str
    birth_timezone: str
    expected_jd_ut: float


class GoldenProPlaceResolved(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    lat: float
    lon: float
    altitude_m: float


class GoldenProCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    datetime: GoldenProDateTime
    place_resolved: GoldenProPlaceResolved
    settings: GoldenProSettings
    expected: GoldenProExpected


class GoldenProDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str
    description: str
    generated_on: str
    case_count: int = Field(ge=50, le=200)
    tolerances: dict[str, float]
    cases: list[GoldenProCase]

    @model_validator(mode="after")
    def _validate_case_count(self) -> "GoldenProDataset":
        if len(self.cases) != self.case_count:
            raise ValueError(
                f"case_count ({self.case_count}) does not match cases length ({len(self.cases)})"
            )
        return self


@lru_cache(maxsize=1)
def load_golden_pro_dataset() -> GoldenProDataset:
    dataset_path = Path(__file__).with_name("pro_dataset_v1.json")
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    return GoldenProDataset.model_validate(payload)
