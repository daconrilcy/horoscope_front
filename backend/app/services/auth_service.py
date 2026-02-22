"""
Service d'authentification.

Ce module fournit les fonctionnalités d'authentification utilisateur :
inscription, connexion et rafraîchissement des tokens JWT.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.core.rbac import is_valid_role
from app.core.security import (
    SecurityError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.infra.db.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.infra.db.repositories.user_repository import UserRepository


class AuthServiceError(Exception):
    """Exception levée lors d'erreurs d'authentification."""

    def __init__(self, code: str, message: str, details: dict[str, str] | None = None) -> None:
        """
        Initialise une erreur d'authentification.

        Args:
            code: Code d'erreur unique identifiant le type d'erreur.
            message: Message descriptif de l'erreur.
            details: Dictionnaire optionnel contenant des détails supplémentaires.
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthTokens(BaseModel):
    """Modèle représentant la paire de tokens d'authentification."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUser(BaseModel):
    """Modèle représentant les informations utilisateur retournées après authentification."""

    id: int
    email: str
    role: str


class AuthResponse(BaseModel):
    """Réponse complète d'authentification incluant l'utilisateur et ses tokens."""

    user: AuthUser
    tokens: AuthTokens


def _normalize_email(email: str) -> str:
    """
    Normalise et valide une adresse email.

    Args:
        email: Adresse email brute à normaliser.

    Returns:
        Adresse email normalisée (minuscules, sans espaces).

    Raises:
        AuthServiceError: Si l'email est invalide.
    """
    normalized = email.strip().lower()
    try:
        validated = TypeAdapter(EmailStr).validate_python(normalized)
    except ValidationError as error:
        raise AuthServiceError(
            code="invalid_email",
            message="email is invalid",
            details={"field": "email"},
        ) from error
    return str(validated)


def _validate_password(password: str) -> None:
    """
    Valide la complexité du mot de passe.

    Args:
        password: Mot de passe à valider.

    Raises:
        AuthServiceError: Si le mot de passe ne respecte pas les critères de sécurité.
    """
    if len(password) < 8:
        raise AuthServiceError(
            code="invalid_password",
            message="password must be at least 8 characters",
            details={"field": "password"},
        )


class AuthService:
    """
    Service gérant l'authentification des utilisateurs.

    Fournit les méthodes pour l'inscription, la connexion et le
    rafraîchissement des tokens JWT.
    """

    @staticmethod
    def _extract_refresh_jti(refresh_token: str) -> str:
        """
        Extrait l'identifiant unique (JTI) d'un token de rafraîchissement.

        Args:
            refresh_token: Token de rafraîchissement JWT.

        Returns:
            Identifiant unique du token.

        Raises:
            AuthServiceError: Si le token est invalide ou mal formé.
        """
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except SecurityError as error:
            raise AuthServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error
        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            raise AuthServiceError(
                code="invalid_token",
                message="token is invalid",
                details={},
            )
        return jti.strip()

    @staticmethod
    def register(db: Session, email: str, password: str, role: str = "user") -> AuthResponse:
        """
        Inscrit un nouvel utilisateur.

        Args:
            db: Session de base de données.
            email: Adresse email de l'utilisateur.
            password: Mot de passe choisi.
            role: Rôle de l'utilisateur (par défaut "user").

        Returns:
            AuthResponse contenant l'utilisateur créé et ses tokens.

        Raises:
            AuthServiceError: Si l'email est déjà utilisé, invalide,
                ou si le mot de passe/rôle ne respecte pas les critères.
        """
        normalized_email = _normalize_email(email)
        _validate_password(password)
        if not is_valid_role(role):
            raise AuthServiceError(
                code="invalid_role",
                message="role is invalid",
                details={"field": "role"},
            )

        repo = UserRepository(db)
        if repo.get_by_email(normalized_email) is not None:
            raise AuthServiceError(
                code="email_already_registered",
                message="email is already registered",
                details={"email": normalized_email},
            )

        user = repo.create(
            email=normalized_email,
            password_hash=hash_password(password),
            role=role,
        )
        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        refresh_jti = AuthService._extract_refresh_jti(refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, refresh_jti)
        return AuthResponse(
            user=AuthUser(id=user.id, email=user.email, role=user.role),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        )

    @staticmethod
    def login(db: Session, email: str, password: str) -> AuthResponse:
        """
        Authentifie un utilisateur existant.

        Args:
            db: Session de base de données.
            email: Adresse email de l'utilisateur.
            password: Mot de passe de l'utilisateur.

        Returns:
            AuthResponse contenant l'utilisateur et ses nouveaux tokens.

        Raises:
            AuthServiceError: Si les identifiants sont invalides.
        """
        normalized_email = _normalize_email(email)
        repo = UserRepository(db)
        user = repo.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthServiceError(
                code="invalid_credentials",
                message="credentials are invalid",
                details={},
            )

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        refresh_jti = AuthService._extract_refresh_jti(refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, refresh_jti)
        return AuthResponse(
            user=AuthUser(id=user.id, email=user.email, role=user.role),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        )

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> AuthTokens:
        """
        Rafraîchit les tokens d'authentification.

        Valide le token de rafraîchissement fourni et génère une nouvelle
        paire de tokens (access + refresh). L'ancien refresh token est invalidé.

        Args:
            db: Session de base de données.
            refresh_token: Token de rafraîchissement actuel.

        Returns:
            AuthTokens contenant la nouvelle paire de tokens.

        Raises:
            AuthServiceError: Si le token est invalide, expiré ou révoqué.
        """
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except SecurityError as error:
            raise AuthServiceError(
                code=error.code,
                message=error.message,
                details=error.details,
            ) from error

        subject = payload.get("sub")
        role = payload.get("role")
        if not isinstance(subject, str) or not subject.isdigit():
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})
        if not isinstance(role, str) or not is_valid_role(role):
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})
        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti.strip():
            raise AuthServiceError(code="invalid_token", message="token is invalid", details={})

        user = UserRepository(db).get_by_id(int(subject))
        if user is None:
            raise AuthServiceError(
                code="invalid_token",
                message="token subject is invalid",
                details={},
            )
        refresh_state = UserRefreshTokenRepository(db).get_by_user_id(user.id)
        if refresh_state is None or refresh_state.current_jti != jti:
            raise AuthServiceError(
                code="invalid_token",
                message="token is invalid",
                details={},
            )

        new_refresh_token = create_refresh_token(subject=str(user.id), role=user.role)
        new_refresh_jti = AuthService._extract_refresh_jti(new_refresh_token)
        UserRefreshTokenRepository(db).upsert_current_jti(user.id, new_refresh_jti)
        return AuthTokens(
            access_token=create_access_token(subject=str(user.id), role=user.role),
            refresh_token=new_refresh_token,
        )
