from langchain_openai import ChatOpenAI


def get_llm():
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        model="openrouter/free",
        temperature=0,
    )

    return llm
