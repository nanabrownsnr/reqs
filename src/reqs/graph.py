from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from reqs.llm import get_llm
from reqs.models import AgentState
from reqs.tools import save_user_stories, get_existing_user_stories
from reqs.system_prompt import _get_system_prompt
from reqs.services import _get_tenant


tools = [save_user_stories, get_existing_user_stories]


def llm_node(state: AgentState, config: RunnableConfig):
    print("\n--- Processing Node ---")

    tenant_id = config["configurable"]["tenant_id"]
    tenant = _get_tenant(tenant_id)

    llm = get_llm(tenant.openrouter_key).bind_tools(tools)

    messages = [SystemMessage(content=_get_system_prompt()), *state["messages"]]
    resp = llm.invoke(messages)

    return {"messages": [resp]}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


def build_graph(checkpointer):

    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "llm")
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "llm")

    return graph.compile(checkpointer=checkpointer)
