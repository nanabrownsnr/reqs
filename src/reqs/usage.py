from datetime import datetime, timezone
from logging import getLogger
import httpx
from reqs.config import settings

logger = getLogger(__name__)


async def save_usage_report(
    method: str, endpoint: str, auth_header: str | None
) -> None:
    """Fire-and-forget usage report. Skips calls with no Authorization header."""
    if auth_header is None:
        return
    try:
        data = {
            "service": settings.service_id,
            "method": method,
            "endpoint": endpoint,
            "timestamp": datetime.now(timezone).timestamp(),
        }
        headers = {"Authorization": auth_header}
        async with httpx.AsyncClient() as client:
            await client.post(
                settings.usage_report_endpoint, json=data, headers=headers
            )
    except Exception as e:
        logger.error(f"Usage report failed: {e}")
