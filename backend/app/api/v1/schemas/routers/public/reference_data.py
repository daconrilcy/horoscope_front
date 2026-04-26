"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

# ruff: noqa: F401, F811, I001, UP035

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1/reference-data", tags=["reference-data"])


class ResponseMeta(BaseModel):
    request_id: str


class CloneReferenceVersionPayload(BaseModel):
    source_version: str
    new_version: str
