from langchain_openai import ChatOpenAI

from reqs.config import settings


def get_llm(api_key: str):
    llm = ChatOpenAI(
        base_url=settings.openrouter_url,
        api_key=api_key,
        model=settings.openrouter_model,
        temperature=0,
    )

    return llm
