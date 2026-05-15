WHITELIST_PATHS = {
    "/docs",
    "/openapi.json",
    "/api/v1/auth/login",
}


def is_whitelisted(path: str) -> bool:
    return path in WHITELIST_PATHS
