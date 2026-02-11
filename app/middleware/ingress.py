"""Middleware for Home Assistant Ingress support.

When running as an HA add-on with Ingress enabled, all requests arrive through
the Supervisor proxy with an X-Ingress-Path header containing the base URL
prefix (e.g. /api/hassio_ingress/<token>/). This middleware rewrites absolute
paths in HTML responses so that fetch() calls, redirects, and links work
correctly behind the Ingress proxy.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
import re


class IngressMiddleware(BaseHTTPMiddleware):
    """Rewrite absolute paths in HTML responses for HA Ingress compatibility."""

    # Patterns to rewrite in HTML/JS content:
    #   fetch('/api/...')  ->  fetch('<ingress_path>/api/...')
    #   href="/setup"      ->  href="<ingress_path>/setup"
    #   url="/setup"       ->  url="<ingress_path>/setup"
    #   window.location.href = '/'  ->  window.location.href = '<ingress_path>/'
    PATH_PATTERN = re.compile(
        r"""(fetch\s*\(\s*[`'"])(/[^'"`]*)([`'"])"""
        r"""|"""
        r"""((?:href|action|url)\s*=\s*['"])(/[^'"]*)(["'])"""
        r"""|"""
        r"""((?:window\.location(?:\.href)?\s*=\s*|location\.href\s*=\s*)['"])(/[^'"]*)(["'])"""
        r"""|"""
        r"""(RedirectResponse\s*\(\s*url\s*=\s*['""])(/[^'"]*)(['"])"""
    )

    async def dispatch(self, request: Request, call_next):
        ingress_path = request.headers.get("X-Ingress-Path", "").rstrip("/")

        response = await call_next(request)

        # Only rewrite HTML responses when there's an ingress path
        if not ingress_path:
            return response

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response

        # Read the response body
        body_chunks = []
        async for chunk in response.body_iterator:
            if isinstance(chunk, bytes):
                body_chunks.append(chunk)
            else:
                body_chunks.append(chunk.encode("utf-8"))
        body = b"".join(body_chunks).decode("utf-8")

        # Inject a global JS variable with the base path, right after <head>
        base_script = f'<script>window.__ingress_path = "{ingress_path}";</script>'
        body = body.replace("<head>", f"<head>\n{base_script}", 1)

        # Rewrite fetch('/api/...') -> fetch('{ingress_path}/api/...')
        # and similar absolute path patterns
        def _rewrite(match):
            groups = match.groups()
            # Find which alternative matched (groups come in triples)
            for i in range(0, len(groups), 3):
                if groups[i] is not None:
                    prefix = groups[i]
                    path = groups[i + 1]
                    suffix = groups[i + 2]
                    return f"{prefix}{ingress_path}{path}{suffix}"
            return match.group(0)

        body = self.PATH_PATTERN.sub(_rewrite, body)

        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
