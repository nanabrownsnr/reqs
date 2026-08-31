from uuid import uuid4
import json
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


from reqs.config import settings
from reqs.models import UserStory, TenantContext

# USERS_FILE_PATH = "src\\reqs\\users.json"
USERS_FILE_PATH = Path(settings.users_file_path)


def _save_user_stories_to_db(
    tenant_id: str, conversation_id: str, stories: list[UserStory]
):
    with psycopg.connect(settings.database_url) as conn:

        for story in stories:
            conn.execute(
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

        conn.commit()


def _get_user_stories_from_db(
    tenant_id: str,
    status: str | None = None,
):
    with psycopg.connect(settings.database_url) as conn:

        if status:
            rows = conn.execute(
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
            ).fetchall()

        else:
            rows = conn.execute(
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
            ).fetchall()

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


def _get_tenant(tenant_id: str) -> TenantContext:

    if not USERS_FILE_PATH.exists():
        raise ValueError("No tenants have been registered.")

    with USERS_FILE_PATH.open("r", encoding="utf-8") as f:
        users = json.load(f)

    if tenant_id not in users:
        raise ValueError(f"Tenant {tenant_id} not found.")

    return TenantContext.model_validate(users[tenant_id])


def _save_tenant(
    tenant_id: str,
    name: str,
    telegram_token: str,
    openrouter_api_key: str,
) -> TenantContext:

    tenant = TenantContext(
        tenant_id=tenant_id,
        name=name,
        telegram_token=telegram_token,
        openrouter_api_key=openrouter_api_key,
    )

    USERS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if USERS_FILE_PATH.exists():
        with USERS_FILE_PATH.open("r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = {}

    users[tenant_id] = tenant.model_dump()

    with USERS_FILE_PATH.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

    return tenant


def _update_user_story_status(
    tenant_id: str,
    story_id: str,
    status: str,
):
    with psycopg.connect(settings.database_url) as conn:
        result = conn.execute(
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
        ).fetchone()

        conn.commit()

    if result is None:
        raise ValueError(f"User story {story_id} not found.")

    return {
        "story_id": str(result[0]),
        "status": result[1],
    }
