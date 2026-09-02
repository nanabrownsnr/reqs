import uvicorn

from langgraph.checkpoint.postgres import PostgresSaver

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from reqs.config import settings
from reqs.graph import build_graph
from reqs.server import build_server


def main():

    with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:

        checkpointer.setup()

        graph = build_graph(checkpointer)

        mcp = build_server(graph)

        print("REQS is running......")

        match settings.ENVIRONMENT:
            case "development":
                origins = ["*"]
            case "staging":
                origins = [
                    "https://staging.twynity.ai",
                    "https://twynity-staging.mis.4th-ir.com",
                ]
            case "production":
                origins = ["https://twynity.ai", "https://twynity.mis.4th-ir.com"]
            case _:
                origins = ["*"]

        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    "mcp-protocol-version",
                    "mcp-session-id",
                    "Authorization",
                    "Content-Type",
                ],
                expose_headers=["mcp-session-id"],
            )
        ]

        app = mcp.http_app(middleware=middleware)
        uvicorn.run(app, host="0.0.0.0", port=8000)

        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=8000,
        )


if __name__ == "__main__":
    main()
