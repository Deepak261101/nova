"""Social login (Google / GitHub) via Authlib.

Providers are registered only when their client credentials are configured, so the
app runs without any OAuth setup. Unconfigured providers return HTTP 501.
"""

from __future__ import annotations

import os
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.adapters.db.repositories import SqlUserRepository
from app.core.config import get_settings
from app.domain.models.user import AuthProvider
from app.services.auth import AuthService

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])

_oauth = OAuth()

if os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"):
    _oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if os.getenv("GITHUB_CLIENT_ID") and os.getenv("GITHUB_CLIENT_SECRET"):
    _oauth.register(
        name="github",
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user user:email"},
    )


def _client(provider: str):  # type: ignore[no-untyped-def]
    client = _oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=501, detail=f"{provider} OAuth is not configured")
    return client


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request) -> RedirectResponse:
    client = _client(provider)
    settings = get_settings()
    redirect_uri = f"{settings.oauth_redirect_base}/auth/oauth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request) -> RedirectResponse:
    client = _client(provider)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if provider == "google":
        info = token.get("userinfo") or await client.userinfo(token=token)
        email = info.get("email")
        name = info.get("name") or (email.split("@")[0] if email else "user")
        avatar = info.get("picture")
        auth_provider = AuthProvider.GOOGLE
    else:  # github
        resp = await client.get("user", token=token)
        profile = resp.json()
        email = profile.get("email")
        if not email:
            emails = (await client.get("user/emails", token=token)).json()
            primary = next((e for e in emails if e.get("primary")), None)
            email = primary["email"] if primary else None
        name = profile.get("name") or profile.get("login") or "user"
        avatar = profile.get("avatar_url")
        auth_provider = AuthProvider.GITHUB

    if not email:
        raise HTTPException(status_code=400, detail="Could not resolve email from provider")

    # Build the auth service manually (no request body dependency here).
    container = request.app.state.container
    tokens = None
    async for session in container.db.session():
        auth = AuthService(SqlUserRepository(session), container.settings)
        _user, tokens = await auth.upsert_oauth_user(
            email=email, display_name=name, provider=auth_provider, avatar_url=avatar
        )
        break
    assert tokens is not None

    frontend = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
    params = urlencode({"access_token": tokens.access_token, "refresh_token": tokens.refresh_token})
    return RedirectResponse(url=f"{frontend}/auth/callback?{params}")
