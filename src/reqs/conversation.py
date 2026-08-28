from langchain_core.messages import HumanMessage


def chat(
    graph,
    conversation_id: str,
    message: str,
) -> str:

    config = {"configurable": {"thread_id": conversation_id}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    return result["messages"][-1].content
