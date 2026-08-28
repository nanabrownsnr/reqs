from langchain_openai import ChatOpenAI

from reqs.config import settings


def get_llm():
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        model="openrouter/free",
        temperature=0,
    )

    return llm
