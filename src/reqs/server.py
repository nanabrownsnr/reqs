import asyncio

from logging import getLogger

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware as MCPMiddleware, MiddlewareContext

from contextlib import asynccontextmanager

from starlette.requests import Request
from starlette.responses import JSONResponse

from reqs.telegram_service import handle_telegram_update, register_telegram_webhook
from reqs.services import (
    _save_tenant,
    _tenant_exists,
    _get_user_stories_from_db,
    _update_user_story_status,
)
from reqs.config import settings
from reqs.license import license_watcher
from reqs.auth import get_auth_provider, get_current_user
from reqs.usage import save_usage_report
from reqs.models import TenantRegistration

logger = getLogger(__name__)


def build_server(graph):

    @asynccontextmanager
    async def app_lifespan(server):
        task = asyncio.create_task(license_watcher())
        yield
        task.cancel()

    mcp = FastMCP(
        settings.app_title,
        auth=get_auth_provider(),
        lifespan=app_lifespan,
    )

    # APIs
    @mcp.custom_route("/api/v1/.well-known/mcp.json", methods=["GET"])
    async def manifest(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "name": "REQS",
                "base_url": f"{settings.public_url}/mcp",
                "version": "1.0.0",
                "external_connections": {
                    "project": {"name": "reqs_configuration"},
                },
            }
        )

    @mcp.custom_route("/api/v1/schema", methods=["GET"])
    async def configuration_schema(request: Request):
        return JSONResponse(
            {
                "name": "reqs_configuration",
                "endpoint": "/api/v1/configuration",
                "method": "POST",
                "schema": {
                    "telegram_token": "string",
                    "openrouter_api_key": "string",
                },
            }
        )

    @mcp.custom_route("/api/v1/configuration", methods=["POST"])
    async def create_configuration(request: Request):
        user = get_current_user()
        payload = await request.json()
        registration = TenantRegistration.model_validate(payload)
        await _save_tenant(
            tenant_id=user.id,
            email=user.email,
            name=user.username,
            telegram_token=registration.telegram_token,
            openrouter_api_key=registration.openrouter_api_key,
        )
        webhook = await register_telegram_webhook(tenant_id=user.id)
        return JSONResponse(
            {
                "configured": True,
                "telegram_webhook": webhook,
            }
        )

    @mcp.custom_route("/api/v1/external-connection/me")
    async def external_connection_me(request: Request):
        user = get_current_user()
        connected = await _tenant_exists(tenant_id=user.id)
        return JSONResponse({"connected": connected})

    @mcp.custom_route("/api/v1/health", methods=["GET"])
    async def health_status(request: Request) -> JSONResponse:
        headers = get_http_headers()
        return JSONResponse({"status": "ok"}, status_code=200)

    @mcp.custom_route("/api/v1/telegram/{tenant_id}", methods=["POST"])
    async def telegram_webhook(request: Request):
        tenant_id = request.path_params["tenant_id"]
        payload = await request.json()
        await handle_telegram_update(
            tenant_id=tenant_id,
            payload=payload,
            graph=graph,
        )
        return JSONResponse({"ok": True})

    @mcp.custom_route("/api/v1/tenants", methods=["POST"])
    async def register_tenant(request: Request):
        payload = await request.json()
        user = get_current_user()
        tenant = _save_tenant(
            tenant_id=user.id,
            name=user.username,
            email=user.email,
            telegram_token=payload["telegram_token"],
            openrouter_api_key=payload["openrouter_api_key"],
        )
        webhook_result = await register_telegram_webhook(tenant.tenant_id)
        return JSONResponse(
            {
                "tenant_id": tenant.tenant_id,
                "registered": True,
                "telegram_webhook": webhook_result,
            }
        )

    # MCPs
    @mcp.tool
    async def get_user_stories(status: str | None = None):
        """
        Get user stories for a tenant.

        Optionally filter by status, for example:
        draft, reviewed, rejected, added_to_board.
        """
        user = get_current_user()
        return await _get_user_stories_from_db(
            tenant_id=user.id,
            status=status,
        )

    @mcp.tool
    async def update_user_story_status(story_id: str, status: str):
        """
        Update the review/workflow status of a user story.

        Typical statuses:
        draft, reviewed, added_to_board, rejected.
        """
        user = get_current_user()
        return await _update_user_story_status(
            tenant_id=user.id,
            story_id=story_id,
            status=status,
        )

    class UsageTrackingMiddleware(MCPMiddleware):
        async def on_call_tool(self, context: MiddlewareContext, call_next):
            try:
                headers = get_http_headers()
                await save_usage_report(
                    method="TOOL_CALL",
                    endpoint=context.message.name,
                    auth_header=headers.get("authorization"),
                )
            except Exception:
                logger.exception(
                    "Usage tracking failed — continuing with tool call anyway"
                )
            return await call_next(context)

    mcp.add_middleware(UsageTrackingMiddleware())

    return mcp
