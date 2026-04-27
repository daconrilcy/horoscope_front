from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.api.dependencies.auth import (
    AuthenticatedUser,
    UserAuthenticationError,
    require_admin_user,
)
from app.api.errors import resolve_application_error_status

# We use a small app fixture-like helper to test the dependency in isolation.
admin_dependency_app = FastAPI()


@admin_dependency_app.exception_handler(UserAuthenticationError)
def handle_user_authentication_error(
    request: Request, error: UserAuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=resolve_application_error_status(error.code),
        content={
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            }
        },
    )


@admin_dependency_app.get("/admin-only")
def admin_only_endpoint(user: AuthenticatedUser = Depends(require_admin_user)):
    return {"message": "hello admin", "user_id": user.id}


client = TestClient(admin_dependency_app)


def test_require_admin_user_success():
    # Mock require_authenticated_user to return an admin user
    from datetime import datetime

    admin_user = AuthenticatedUser(
        id=1, role="admin", email="admin@test.com", created_at=datetime.now()
    )

    # We patch the dependency in the app
    admin_dependency_app.dependency_overrides[require_admin_user] = lambda: admin_user

    response = client.get("/admin-only")
    assert response.status_code == 200
    assert response.json() == {"message": "hello admin", "user_id": 1}

    admin_dependency_app.dependency_overrides = {}


def test_require_admin_user_forbidden():
    from datetime import datetime

    ops_user = AuthenticatedUser(id=2, role="ops", email="ops@test.com", created_at=datetime.now())

    # We need to test the actual logic of require_admin_user
    # So we override require_authenticated_user which is called by require_admin_user
    from app.api.dependencies import auth

    admin_dependency_app.dependency_overrides[auth.require_authenticated_user] = lambda: ops_user

    response = client.get("/admin-only")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "insufficient_role"
    assert response.json()["error"]["details"]["actual_role"] == "ops"

    admin_dependency_app.dependency_overrides = {}


def test_require_admin_user_unauthorized():
    # Mock require_authenticated_user to raise 401
    from app.api.dependencies import auth

    def mock_auth_error():
        raise UserAuthenticationError(
            code="missing_access_token", message="missing bearer access token", status_code=401
        )

    admin_dependency_app.dependency_overrides[auth.require_authenticated_user] = mock_auth_error

    response = client.get("/admin-only")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_access_token"

    admin_dependency_app.dependency_overrides = {}
