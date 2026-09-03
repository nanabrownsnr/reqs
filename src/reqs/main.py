import asyncio
import os

import uvicorn

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from reqs.config import settings
from reqs.graph import build_graph
from reqs.server import build_server


async def main():

    async with AsyncPostgresSaver.from_conn_string(
        settings.database_url
    ) as checkpointer:

        await checkpointer.setup()

        graph = build_graph(checkpointer)

        mcp = build_server(graph)

        print("REQS is running......")

        match settings.environment:

            case "development":
                origins = ["*"]

            case "staging":
                origins = [
                    "https://staging.twynity.ai",
                    "https://twynity-staging.mis.4th-ir.com",
                ]

            case "production":
                origins = [
                    "https://twynity.ai",
                    "https://twynity.mis.4th-ir.com",
                ]

            case _:
                origins = ["*"]

        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["mcp-session-id"],
            )
        ]

        app = mcp.http_app(middleware=middleware)

        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
        )

        server = uvicorn.Server(config)

        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
