VALID_ROLES = {"user", "support", "ops", "enterprise_admin"}


def is_valid_role(role: str) -> bool:
    return role in VALID_ROLES
