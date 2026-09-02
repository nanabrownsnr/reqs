from typing import Annotated, Sequence
from typing_extensions import TypedDict

from pydantic import BaseModel

from langgraph.graph.message import add_messages


# 1. Define the State of your graph
class AgentState(TypedDict):
    # add_messages appends new messages to the history instead of overwriting them
    messages: Annotated[Sequence[dict], add_messages]


class UserStory(BaseModel):
    title: str
    user_role: str
    goal: str
    benefit: str
    acceptance_criteria: list[str]


class TenantContext(BaseModel):
    tenant_id: str
    name: str
    telegram_token: str | None = None
    openrouter_api_key: str | None = None


class TenantRegistration(BaseModel):
    telegram_token: str
    openrouter_api_key: str


class TenantContext(BaseModel):
    tenant_id: str
    email: str
    name: str
    telegram_token: str
    openrouter_api_key: str
