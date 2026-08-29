from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from reqs.models import UserStory
from reqs.services import _save_user_stories_to_db, _get_user_stories_from_db


@tool
def save_user_stories(
    stories: list[UserStory],
    config: RunnableConfig,
):
    """
    Save user-confirmed user stories to the requirements database.

    Only call this tool after the user has explicitly confirmed
    that the proposed user stories should be saved.
    """
    tenant_id = config["configurable"]["tenant_id"]
    conversation_id = config["configurable"]["thread_id"]

    _save_user_stories_to_db(tenant_id, conversation_id, stories)

    return {
        "saved": True,
        "count": len(stories),
    }


@tool
def get_existing_user_stories(config: RunnableConfig):
    """
    Get previously saved user stories for all conversations.

    Use this when you need to review existing stories or check
    whether a similar story may already exist before proposing
    or saving a new one.
    """
    tenant_id = config["configurable"]["tenant_id"]

    return _get_user_stories_from_db(tenant_id)
