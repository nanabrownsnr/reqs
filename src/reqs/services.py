from uuid import uuid4
import json
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from reqs.config import settings
from reqs.models import UserStory, TenantContext
from reqs.encryption import encrypt_data, decrypt_data


async def _save_user_stories_to_db(
    tenant_id: str, conversation_id: str, stories: list[UserStory]
):
    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        for story in stories:
            await conn.execute(
                """
                INSERT INTO user_stories (
                    story_id,
                    tenant_id,
                    conversation_id,
                    title,
                    user_role,
                    goal,
                    benefit,
                    acceptance_criteria,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid4()),
                    tenant_id,
                    conversation_id,
                    story.title,
                    story.user_role,
                    story.goal,
                    story.benefit,
                    Jsonb(story.acceptance_criteria),
                    "draft",
                ),
            )

        await conn.commit()


async def _get_user_stories_from_db(tenant_id: str, status: str | None = None):
    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        if status:
            cursor = await conn.execute(
                """
                SELECT
                    story_id,
                    title,
                    user_role,
                    goal,
                    benefit,
                    acceptance_criteria,
                    status,
                    created_at
                FROM user_stories
                WHERE tenant_id = %s
                AND status = %s
                ORDER BY created_at DESC
                """,
                (
                    tenant_id,
                    status,
                ),
            )
        else:
            cursor = await conn.execute(
                """
                SELECT
                    story_id,
                    title,
                    user_role,
                    goal,
                    benefit,
                    acceptance_criteria,
                    status,
                    created_at
                FROM user_stories
                WHERE tenant_id = %s
                ORDER BY created_at DESC
                """,
                (tenant_id,),
            )

        rows = await cursor.fetchall()

    return [
        {
            "story_id": str(row[0]),
            "title": row[1],
            "user_role": row[2],
            "goal": row[3],
            "benefit": row[4],
            "acceptance_criteria": row[5],
            "status": row[6],
            "created_at": row[7].isoformat(),
        }
        for row in rows
    ]


async def _update_user_story_status(tenant_id: str, story_id: str, status: str):
    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        cursor = await conn.execute(
            """
            UPDATE user_stories
            SET status = %s
            WHERE story_id = %s
            AND tenant_id = %s
            RETURNING story_id, status
            """,
            (
                status,
                story_id,
                tenant_id,
            ),
        )

        result = await cursor.fetchone()

        await conn.commit()

    if result is None:
        raise ValueError(f"User story {story_id} not found.")

    return {
        "story_id": str(result[0]),
        "status": result[1],
    }


async def _get_tenant(tenant_id: str) -> TenantContext:

    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        cursor = await conn.execute(
            """
            SELECT
                tenant_id,
                email,
                name,
                telegram_token,
                openrouter_api_key
            FROM tenant_integrations
            WHERE tenant_id = %s
            """,
            (tenant_id,),
        )

        row = await cursor.fetchone()

    if row is None:
        raise ValueError(f"Tenant {tenant_id} is not registered.")

    return TenantContext(
        tenant_id=row[0],
        email=row[1],
        name=row[2],
        telegram_token=decrypt_data(bytes(row[3])).decode("utf-8"),
        openrouter_api_key=decrypt_data(bytes(row[4])).decode("utf-8"),
    )


async def _save_tenant(
    tenant_id: str, email: str, name: str, telegram_token: str, openrouter_api_key: str
):
    encrypted_telegram_token = encrypt_data(telegram_token.encode("utf-8"))

    encrypted_openrouter_key = encrypt_data(openrouter_api_key.encode("utf-8"))

    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        await conn.execute(
            """
            INSERT INTO tenant_integrations (
                tenant_id,
                email,
                name,
                telegram_token,
                openrouter_api_key
            )
            VALUES (%s, %s, %s, %s, %s)

            ON CONFLICT (tenant_id)
            DO UPDATE SET
                email = EXCLUDED.email,
                name = EXCLUDED.name,
                telegram_token = EXCLUDED.telegram_token,
                openrouter_api_key = EXCLUDED.openrouter_api_key,
                updated_at = NOW()
            """,
            (
                tenant_id,
                email,
                name,
                encrypted_telegram_token,
                encrypted_openrouter_key,
            ),
        )

        await conn.commit()


async def _tenant_exists(tenant_id: str) -> bool:

    async with await psycopg.AsyncConnection.connect(settings.database_url) as conn:

        cursor = await conn.execute(
            """
            SELECT 1
            FROM tenant_integrations
            WHERE tenant_id = %s
            LIMIT 1
            """,
            (tenant_id,),
        )

        row = await cursor.fetchone()

    return row is not None
