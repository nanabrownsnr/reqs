import asyncio

from telegram import Bot, Update

from reqs.conversation import chat
from reqs.services import _get_tenant
from reqs.config import settings


async def register_telegram_webhook(
    tenant_id: str,
):

    tenant = _get_tenant(tenant_id)

    bot = Bot(token=tenant.telegram_token)

    webhook_url = f"{settings.public_url}" f"/telegram/{tenant_id}"

    await bot.set_webhook(url=webhook_url)

    return {
        "tenant_id": tenant_id,
        "webhook_url": webhook_url,
    }


async def handle_telegram_update(
    tenant_id: str,
    payload: dict,
    graph,
):

    # Which tenant owns the bot?
    tenant = _get_tenant(tenant_id)

    # Use that tenant's Telegram bot.
    bot = Bot(token=tenant.telegram_token)

    # Convert Telegram's JSON into an Update.
    update = Update.de_json(payload, bot)

    if update.message is None or update.message.text is None:
        return

    telegram_chat_id = update.effective_chat.id

    conversation_id = f"{tenant_id}:telegram:{telegram_chat_id}"

    response = await asyncio.to_thread(
        chat,
        graph,
        tenant_id,
        conversation_id,
        update.message.text,
    )

    await bot.send_message(
        chat_id=telegram_chat_id,
        text=response,
    )
