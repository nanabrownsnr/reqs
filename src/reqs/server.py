from fastmcp import FastMCP

from starlette.requests import Request
from starlette.responses import JSONResponse

from reqs.telegram_service import handle_telegram_update, register_telegram_webhook
from reqs.services import _save_tenant


def build_server(graph):

    mcp = FastMCP("Requirements_Gathering")

    @mcp.custom_route("/health", methods=["GET"])
    async def health(request: Request):
        return JSONResponse({"status": "ok"})

    @mcp.custom_route("/telegram/{tenant_id}", methods=["POST"])
    async def telegram_webhook(request: Request):

        tenant_id = request.path_params["tenant_id"]
        payload = await request.json()
        await handle_telegram_update(
            tenant_id=tenant_id,
            payload=payload,
            graph=graph,
        )

        return JSONResponse({"ok": True})

    @mcp.custom_route("/tenants", methods=["POST"])
    async def register_tenant(request: Request):
        payload = await request.json()

        tenant = save_tenant(
            tenant_id=payload["tenant_id"],
            name=payload["name"],
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

    @mcp.tool
    def ping() -> str:
        """Check whether REQS is running."""

        return "REQS is running."

    return mcp
