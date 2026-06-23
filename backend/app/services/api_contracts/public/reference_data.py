"""Schemas Pydantic extraits du routeur API v1 correspondant."""

from __future__ import annotations

from pydantic import BaseModel


class ResponseMeta(BaseModel):
    """Contrat Pydantic exposé par l'API."""

    request_id: str


class LanguageData(BaseModel):
    """Langue disponible pour la localisation de l'interface."""

    code: str
    name: str


class LanguagesApiResponse(BaseModel):
    """Liste des langues supportées par le référentiel applicatif."""

    data: list[LanguageData]
    meta: ResponseMeta
