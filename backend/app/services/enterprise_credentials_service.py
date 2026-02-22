"""
Service de gestion des credentials API entreprise.

Ce module gère la création, la rotation et l'authentification des clés API
pour les comptes entreprise B2B.
"""

from __future__ import annotations

import hmac
from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe

from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models.enterprise_account import EnterpriseAccountModel
from app.infra.db.models.enterprise_api_credential import EnterpriseApiCredentialModel


def utc_now() -> datetime:
    """Retourne l'instant actuel en UTC."""
    return datetime.now(timezone.utc)


class EnterpriseCredentialsServiceError(Exception):
    """Exception levée lors d'erreurs de gestion des credentials."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur de credentials.

        Args:
            code: Code d'erreur unique.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel de détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class EnterpriseCredentialMetadataData(BaseModel):
    """Métadonnées d'un credential API (sans le secret)."""

    credential_id: int
    key_prefix: str
    status: str
    created_at: datetime
    revoked_at: datetime | None


class EnterpriseCredentialListData(BaseModel):
    """Liste des credentials d'un compte entreprise."""

    account_id: int
    company_name: str
    status: str
    has_active_credential: bool
    credentials: list[EnterpriseCredentialMetadataData]


class EnterpriseCredentialSecretData(BaseModel):
    """Données d'un credential incluant la clé API en clair."""

    credential_id: int
    key_prefix: str
    api_key: str
    status: str
    created_at: datetime


class EnterpriseApiKeyAuthData(BaseModel):
    """Résultat d'authentification par clé API."""

    account_id: int
    credential_id: int
    key_prefix: str
    credential_status: str
    account_status: str


class EnterpriseCredentialsService:
    """
    Service de gestion des credentials API B2B.

    Gère la création, la rotation et l'authentification des clés API
    avec hachage sécurisé et support de rotation des clés secrètes.
    """
    @staticmethod
    def _hash_secret(secret: str, key: str) -> str:
        """Calcule le hash HMAC-SHA256 d'un secret avec une clé."""
        digest = hmac.new(
            key.encode(),
            secret.encode(),
            sha256,
        ).hexdigest()
        return digest

    @staticmethod
    def _candidate_hashes(secret: str) -> set[str]:
        """Génère les hashes candidats avec toutes les clés actives et précédentes."""
        keys = [settings.api_credentials_secret_key, *settings.api_credentials_previous_secret_keys]
        return {EnterpriseCredentialsService._hash_secret(secret, key) for key in keys}

    @staticmethod
    def _to_metadata(model: EnterpriseApiCredentialModel) -> EnterpriseCredentialMetadataData:
        """Convertit un modèle de credential en DTO de métadonnées."""
        return EnterpriseCredentialMetadataData(
            credential_id=model.id,
            key_prefix=model.key_prefix,
            status=model.status,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def authenticate_api_key(
        db: Session,
        *,
        api_key: str,
    ) -> EnterpriseApiKeyAuthData:
        """
        Authentifie une clé API et retourne les informations du compte.

        Args:
            db: Session de base de données.
            api_key: Clé API brute à authentifier.

        Returns:
            Informations d'authentification du compte et credential.

        Raises:
            EnterpriseCredentialsServiceError: Si la clé est invalide ou révoquée.
        """
        normalized = api_key.strip()
        if not normalized:
            raise EnterpriseCredentialsServiceError(
                code="missing_api_key",
                message="api key is required",
                details={},
            )
        if not normalized.startswith("b2b_"):
            raise EnterpriseCredentialsServiceError(
                code="invalid_api_key",
                message="api key is invalid",
                details={},
            )

        key_prefix = normalized[:16]
        candidates = db.scalars(
            select(EnterpriseApiCredentialModel)
            .where(EnterpriseApiCredentialModel.key_prefix == key_prefix)
            .order_by(
                desc(EnterpriseApiCredentialModel.created_at),
                desc(EnterpriseApiCredentialModel.id),
            )
            .limit(10)
        ).all()
        if not candidates:
            raise EnterpriseCredentialsServiceError(
                code="invalid_api_key",
                message="api key is invalid",
                details={},
            )

        candidate_hashes = EnterpriseCredentialsService._candidate_hashes(normalized)
        matched = next((item for item in candidates if item.secret_hash in candidate_hashes), None)
        if matched is None:
            raise EnterpriseCredentialsServiceError(
                code="invalid_api_key",
                message="api key is invalid",
                details={},
            )

        account = db.scalar(
            select(EnterpriseAccountModel)
            .where(EnterpriseAccountModel.id == matched.enterprise_account_id)
            .limit(1)
        )
        if account is None:
            raise EnterpriseCredentialsServiceError(
                code="enterprise_account_not_found",
                message="enterprise account was not found",
                details={},
            )
        if account.status != "active":
            raise EnterpriseCredentialsServiceError(
                code="enterprise_account_inactive",
                message="enterprise account is inactive",
                details={"status": account.status},
            )
        if matched.status != "active":
            raise EnterpriseCredentialsServiceError(
                code="revoked_api_key",
                message="api key is revoked",
                details={},
            )

        return EnterpriseApiKeyAuthData(
            account_id=account.id,
            credential_id=matched.id,
            key_prefix=matched.key_prefix,
            credential_status=matched.status,
            account_status=account.status,
        )

    @staticmethod
    def _get_active_enterprise_account(
        db: Session,
        *,
        admin_user_id: int,
    ) -> EnterpriseAccountModel:
        """Récupère le compte entreprise actif de l'administrateur."""
        account = db.scalar(
            select(EnterpriseAccountModel)
            .where(EnterpriseAccountModel.admin_user_id == admin_user_id)
            .limit(1)
        )
        if account is None:
            raise EnterpriseCredentialsServiceError(
                code="enterprise_account_not_found",
                message="enterprise account was not found",
                details={},
            )
        if account.status != "active":
            raise EnterpriseCredentialsServiceError(
                code="enterprise_account_inactive",
                message="enterprise account is inactive",
                details={"status": account.status},
            )
        return account

    @staticmethod
    def _get_active_credential(
        db: Session,
        *,
        account_id: int,
    ) -> EnterpriseApiCredentialModel | None:
        """Récupère le credential actif d'un compte avec verrou."""
        return db.scalar(
            select(EnterpriseApiCredentialModel)
            .where(
                EnterpriseApiCredentialModel.enterprise_account_id == account_id,
                EnterpriseApiCredentialModel.status == "active",
            )
            .order_by(
                desc(EnterpriseApiCredentialModel.created_at),
                desc(EnterpriseApiCredentialModel.id),
            )
            .limit(1)
            .with_for_update()
        )

    @staticmethod
    def list_credentials(
        db: Session,
        *,
        admin_user_id: int,
    ) -> EnterpriseCredentialListData:
        """
        Liste tous les credentials d'un compte entreprise.

        Args:
            db: Session de base de données.
            admin_user_id: Identifiant de l'administrateur du compte.

        Returns:
            Liste des credentials avec métadonnées.
        """
        account = EnterpriseCredentialsService._get_active_enterprise_account(
            db, admin_user_id=admin_user_id
        )
        credentials = db.scalars(
            select(EnterpriseApiCredentialModel)
            .where(EnterpriseApiCredentialModel.enterprise_account_id == account.id)
            .order_by(
                desc(EnterpriseApiCredentialModel.created_at),
                desc(EnterpriseApiCredentialModel.id),
            )
        ).all()

        return EnterpriseCredentialListData(
            account_id=account.id,
            company_name=account.company_name,
            status=account.status,
            has_active_credential=any(item.status == "active" for item in credentials),
            credentials=[EnterpriseCredentialsService._to_metadata(item) for item in credentials],
        )

    @staticmethod
    def create_credential(
        db: Session,
        *,
        admin_user_id: int,
    ) -> EnterpriseCredentialSecretData:
        """
        Crée un nouveau credential API pour un compte.

        Args:
            db: Session de base de données.
            admin_user_id: Identifiant de l'administrateur.

        Returns:
            Nouveau credential avec la clé API en clair (à sauvegarder).

        Raises:
            EnterpriseCredentialsServiceError: Si un credential actif existe déjà.
        """
        account = EnterpriseCredentialsService._get_active_enterprise_account(
            db, admin_user_id=admin_user_id
        )
        active = EnterpriseCredentialsService._get_active_credential(db, account_id=account.id)
        if active is not None:
            raise EnterpriseCredentialsServiceError(
                code="credential_already_exists",
                message="active credential already exists",
                details={"action": "rotate_credential"},
            )

        raw_secret = f"b2b_{token_urlsafe(32)}"
        key_prefix = raw_secret[:16]
        model = EnterpriseApiCredentialModel(
            enterprise_account_id=account.id,
            key_prefix=key_prefix,
            secret_hash=EnterpriseCredentialsService._hash_secret(
                raw_secret, settings.api_credentials_secret_key
            ),
            status="active",
            created_by_user_id=admin_user_id,
            revoked_at=None,
        )
        db.add(model)
        try:
            db.flush()
        except IntegrityError as error:
            raise EnterpriseCredentialsServiceError(
                code="credential_already_exists",
                message="active credential already exists",
                details={"action": "rotate_credential"},
            ) from error
        return EnterpriseCredentialSecretData(
            credential_id=model.id,
            key_prefix=model.key_prefix,
            api_key=raw_secret,
            status=model.status,
            created_at=model.created_at,
        )

    @staticmethod
    def rotate_credential(
        db: Session,
        *,
        admin_user_id: int,
    ) -> EnterpriseCredentialSecretData:
        """
        Fait la rotation du credential actif (révoque et en crée un nouveau).

        Args:
            db: Session de base de données.
            admin_user_id: Identifiant de l'administrateur.

        Returns:
            Nouveau credential avec la clé API en clair.

        Raises:
            EnterpriseCredentialsServiceError: Si aucun credential actif n'existe.
        """
        account = EnterpriseCredentialsService._get_active_enterprise_account(
            db, admin_user_id=admin_user_id
        )
        active = EnterpriseCredentialsService._get_active_credential(db, account_id=account.id)
        if active is None:
            raise EnterpriseCredentialsServiceError(
                code="credential_not_found",
                message="active credential was not found",
                details={},
            )

        active.status = "revoked"
        active.revoked_at = utc_now()
        db.flush()

        raw_secret = f"b2b_{token_urlsafe(32)}"
        key_prefix = raw_secret[:16]
        replacement = EnterpriseApiCredentialModel(
            enterprise_account_id=account.id,
            key_prefix=key_prefix,
            secret_hash=EnterpriseCredentialsService._hash_secret(
                raw_secret, settings.api_credentials_secret_key
            ),
            status="active",
            created_by_user_id=admin_user_id,
            revoked_at=None,
        )
        db.add(replacement)
        try:
            db.flush()
        except IntegrityError as error:
            raise EnterpriseCredentialsServiceError(
                code="credential_already_exists",
                message="active credential already exists",
                details={"action": "rotate_credential"},
            ) from error

        return EnterpriseCredentialSecretData(
            credential_id=replacement.id,
            key_prefix=replacement.key_prefix,
            api_key=raw_secret,
            status=replacement.status,
            created_at=replacement.created_at,
        )
