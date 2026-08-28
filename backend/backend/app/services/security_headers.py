"""Security middleware helpers."""
from starlette.middleware.base import BaseHTTPMiddleware

# The API responses (JSON) get a locked-down CSP. The frontend pages served
# from public/ use inline <script>/<style> and Google Fonts, so they need a
# CSP that actually permits those — "default-src 'self'" alone would block
# them from rendering at all (blank page, no console-visible HTML change).
_API_CSP = "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
_FRONTEND_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; "
    "img-src 'self' data:; "
    "media-src 'self'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        # Swagger UI and ReDoc load their assets from CDN.
        # Keep the normal API responses protected while allowing
        # FastAPI's documentation pages to load their required assets.
        path = request.url.path
        if path in {"/docs", "/redoc"}:
            pass
        elif path.startswith("/api") or path == "/health":
            response.headers["Content-Security-Policy"] = _API_CSP
        else:
            response.headers["Content-Security-Policy"] = _FRONTEND_CSP

        return response
