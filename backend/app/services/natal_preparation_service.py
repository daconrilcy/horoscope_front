from app.domain.astrology.natal_preparation import (
    BirthInput,
    BirthPreparedData,
    prepare_birth_data,
)


class NatalPreparationService:
    @staticmethod
    def prepare(payload: BirthInput) -> BirthPreparedData:
        return prepare_birth_data(payload)
