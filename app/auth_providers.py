"""OAuth2 providers (Google, Microsoft, GitHub) via Authlib. Providers without credentials are simply not shown."""
from .extensions import oauth


def register_providers(app):
    enabled = []
    creds = app.config["OAUTH"]
    cid, sec = creds["google"]
    if cid and sec:
        oauth.register("google", client_id=cid, client_secret=sec,
                       server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                       client_kwargs={"scope": "openid email profile"})
        enabled.append("google")
    cid, sec = creds["microsoft"]
    if cid and sec:
        oauth.register("microsoft", client_id=cid, client_secret=sec,
                       server_metadata_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
                       client_kwargs={"scope": "openid email profile"})
        enabled.append("microsoft")
    cid, sec = creds["github"]
    if cid and sec:
        oauth.register("github", client_id=cid, client_secret=sec,
                       access_token_url="https://github.com/login/oauth/access_token",
                       authorize_url="https://github.com/login/oauth/authorize",
                       api_base_url="https://api.github.com/",
                       client_kwargs={"scope": "read:user user:email"})
        enabled.append("github")
    app.config["ENABLED_PROVIDERS"] = enabled


def normalize_profile(provider, token):
    """Return {provider_id, email, username, avatar_url} from the provider response."""
    client = getattr(oauth, provider)
    if provider in ("google", "microsoft"):
        info = token.get("userinfo") or {}
        email = info.get("email") or info.get("preferred_username")
        return {"provider_id": str(info.get("sub") or info.get("oid")), "email": email,
                "username": info.get("name") or (email or "").split("@")[0] or "Traveller",
                "avatar_url": info.get("picture")}
    if provider == "github":
        me = client.get("user", token=token).json()
        email = me.get("email")
        if not email:
            try:
                for e in client.get("user/emails", token=token).json():
                    if e.get("primary") and e.get("verified"):
                        email = e.get("email")
                        break
            except Exception:
                email = None
        return {"provider_id": str(me["id"]), "email": email, "username": me.get("name") or me.get("login"),
                "avatar_url": me.get("avatar_url")}
    raise ValueError(provider)
