from langgraph.checkpoint.postgres import PostgresSaver

from reqs.config import settings
from reqs.graph import build_graph
from reqs.server import build_server


def main():

    with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:

        checkpointer.setup()

        graph = build_graph(checkpointer)

        mcp = build_server(graph)

        print("REQS is running......")

        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=8000,
        )


if __name__ == "__main__":
    main()
