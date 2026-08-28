from langchain_core import messages
from langgraph.graph import StateGraph, START, END

from reqs.llm import get_llm
from reqs.models import AgentState

from langchain_core.messages import SystemMessage

SYSTEM_PROMPT = """
You are a requirements gathering agent.

Your job is to help stakeholders turn vague requests into clear, actionable user stories.

Rules:
- Ask focused clarifying questions when important details are missing.
- Do not invent requirements the stakeholder did not imply.
- When enough information is available, propose one or more user stories.
- Each user story should include:
  - title
  - user role
  - goal
  - benefit
  - acceptance criteria
- Present the proposed stories to the user before saving them.
- NEVER save a user story unless the user explicitly confirms that the proposed stories should be saved.
- If the user requests changes, revise the draft and ask for confirmation again.
- Keep the conversation natural and concise.
"""


# 2. Define a processing node
def llm_node(state: AgentState):
    print("\n--- Processing Node ---")

    llm = get_llm()
    messages = [SystemMessage(content=SystemMessage), *state["messages"]]
    resp = llm.invoke(messages)

    return {"messages": [resp]}


def build_graph(checkpointer):

    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)

    graph.add_edge(START, "llm")
    graph.add_edge("llm", END)

    return graph.compile(checkpointer=checkpointer)
