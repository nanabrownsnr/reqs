from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from reqs.config import settings


def get_auth_provider() -> JWTVerifier:
    """Builds the auth checker FastMCP will run on every incoming request."""
    jwks_url = (
        f"{settings.account_service_url.rstrip('/')}"
        f"/{settings.account_service_jwks_endpoint.lstrip('/')}"
    )
    return JWTVerifier(jwks_uri=jwks_url)


def get_current_user():
    token = get_access_token()

    if token is None:
        raise ValueError("User is not authenticated.")

    claims = token.claims

    return {
        "id": claims["id"],
        "email": claims["sub"],
        "username": claims["username"],
    }
