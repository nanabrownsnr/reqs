from langgraph.checkpoint.postgres import PostgresSaver

from reqs.config import settings
from reqs.graph import build_graph
from reqs.telegram_bot import build_telegram_bot


def main():

    with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:

        checkpointer.setup()

        graph = build_graph(checkpointer)

        telegram_app = build_telegram_bot(
            token=settings.telegram_bot_token,
            graph=graph,
        )

        print("Telegram bot is running...")

        telegram_app.run_polling()


if __name__ == "__main__":
    main()
