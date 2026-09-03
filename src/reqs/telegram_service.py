from telegram import Bot, Update

from reqs.conversation import chat
from reqs.services import _get_tenant
from reqs.config import settings


async def register_telegram_webhook(
    tenant_id: str,
):
    tenant = await _get_tenant(tenant_id)

    bot = Bot(token=tenant.telegram_token)

    webhook_url = f"{settings.public_url}" f"/api/v1/telegram/{tenant_id}"

    print("REGISTERING TELEGRAM WEBHOOK:", webhook_url)

    result = await bot.set_webhook(url=webhook_url)

    print("TELEGRAM SET WEBHOOK RESULT:", result)

    info = await bot.get_webhook_info()

    print("TELEGRAM CURRENT WEBHOOK:", info.url)

    return {"tenant_id": tenant_id, "webhook_url": info.url}


async def handle_telegram_update(
    tenant_id: str,
    payload: dict,
    graph,
):

    # Which tenant owns the bot?
    tenant = await _get_tenant(tenant_id)

    # Use that tenant's Telegram bot.
    bot = Bot(token=tenant.telegram_token)

    # Convert Telegram's JSON into an Update.
    update = Update.de_json(payload, bot)

    if update.message is None or update.message.text is None:
        return

    telegram_chat_id = update.effective_chat.id

    conversation_id = f"{tenant_id}:telegram:{telegram_chat_id}"

    response = await chat(
        graph,
        tenant_id,
        conversation_id,
        update.message.text,
    )

    await bot.send_message(
        chat_id=telegram_chat_id,
        text=response,
    )


# from telegram import Bot
# import asyncio


# async def check_webhook():
#     bot = Bot(token="8226888448:AAGk7jBgDIEGGjZWoK5W-n6H9_9-F0wMs6s")

#     info = await bot.get_webhook_info()

#     print("Current webhook:", info.url)
#     print("Pending updates:", info.pending_update_count)
#     print("Last error:", info.last_error_message)


# asyncio.run(check_webhook())
