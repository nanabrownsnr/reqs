import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from reqs.conversation import chat


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text("Hi! Send me a message and we can chat.")


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None or update.message.text is None:
        return

    conversation_id = f"telegram-{update.effective_chat.id}"

    graph = context.application.bot_data["graph"]

    response = await asyncio.to_thread(
        chat,
        graph,
        conversation_id,
        update.message.text,
    )

    await update.message.reply_text(response)


def build_telegram_bot(
    token: str,
    graph,
):
    application = Application.builder().token(token).build()

    application.bot_data["graph"] = graph

    application.add_handler(
        CommandHandler(
            "start",
            start_command,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    return application
