from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.schema.runnable import RunnableMap
from langchain.llms import OpenAI  # older completion-style model


# ---------------------------------------------------------------------------
# 1. Simple LCEL chain: prompt -> model -> parser
# ---------------------------------------------------------------------------


def build_joke_chain(temperature: float = 0.7) -> Any:
    """
    Build a simple LCEL chain that tells a short joke about a topic.

    Chain: ChatPromptTemplate -> ChatOpenAI -> StrOutputParser
    """
    prompt = ChatPromptTemplate.from_template(
        "Tell me a short joke about {topic}."
    )
    model = ChatOpenAI(temperature=temperature)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    return chain


def demo_single_joke(topic: str = "bears") -> str:
    """Return a single joke for the given topic."""
    chain = build_joke_chain()
    return chain.invoke({"topic": topic})


# ---------------------------------------------------------------------------
# 2. Retrieval-Augmented chain with RunnableMap
# ---------------------------------------------------------------------------


def build_tiny_retriever() -> Any:
    """
    Build the tiny vectorstore + retriever used in the course example.

    Documents:
      - "harrison worked at kensho"
      - "bears like to eat honey"
    """
    texts = ["harrison worked at kensho", "bears like to eat honey"]
    embeddings = OpenAIEmbeddings()
    vectorstore = DocArrayInMemorySearch.from_texts(texts, embedding=embeddings)
    return vectorstore.as_retriever()


def build_rag_chain() -> Any:
    """
    Build an LCEL chain that:
      1. Retrieves context for a question.
      2. Feeds {context, question} into a prompt.
      3. Uses ChatOpenAI + StrOutputParser to answer using ONLY that context.
    """
    retriever = build_tiny_retriever()

    template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI()
    output_parser = StrOutputParser()

    inputs = RunnableMap(
        {
            "context": lambda x: retriever.get_relevant_documents(x["question"]),
            "question": lambda x: x["question"],
        }
    )

    chain = inputs | prompt | model | output_parser
    return chain


def demo_rag(question: str) -> str:
    """Run the tiny RAG chain on a question."""
    chain = build_rag_chain()
    return chain.invoke({"question": question})


# ---------------------------------------------------------------------------
# 3. LCEL + bind(): function-calling style tools
# ---------------------------------------------------------------------------


def build_function_bound_model_single() -> Any:
    """
    Build a ChatOpenAI model bound with a single 'weather_search' function.
    """
    functions = [
        {
            "name": "weather_search",
            "description": "Search for weather given an airport code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "The airport code to get the weather for.",
                    },
                },
                "required": ["airport_code"],
            },
        }
    ]

    prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
    model = ChatOpenAI(temperature=0).bind(functions=functions)
    runnable = prompt | model
    return runnable


def build_function_bound_model_multi() -> Any:
    """
    Build a ChatOpenAI model bound with 'weather_search' AND 'sports_search'.
    """
    functions = [
        {
            "name": "weather_search",
            "description": "Search for weather given an airport code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": "The airport code to get the weather for.",
                    },
                },
                "required": ["airport_code"],
            },
        },
        {
            "name": "sports_search",
            "description": "Search for news of recent sport events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "team_name": {
                        "type": "string",
                        "description": "The sports team to search for.",
                    },
                },
                "required": ["team_name"],
            },
        },
    ]

    prompt = ChatPromptTemplate.from_messages([("human", "{input}")])
    base_model = ChatOpenAI(temperature=0)
    model = base_model.bind(functions=functions)
    runnable = prompt | model
    return runnable


def demo_weather_function_call() -> Dict[str, Any]:
    """
    Ask about weather; inspect the model's function-call decision.
    """
    runnable = build_function_bound_model_single()
    resp = runnable.invoke({"input": "what is the weather in sf"})
    # return as plain dict so callers can inspect tool calls
    return resp.dict() if hasattr(resp, "dict") else resp


def demo_sports_function_call() -> Dict[str, Any]:
    """
    Ask about sports; model has weather_search + sports_search bound.
    """
    runnable = build_function_bound_model_multi()
    resp = runnable.invoke({"input": "how did the patriots do yesterday?"})
    return resp.dict() if hasattr(resp, "dict") else resp


# ---------------------------------------------------------------------------
# 4. Fallback chains: older LLM + newer JSON-capable chat model
# ---------------------------------------------------------------------------


def build_fallback_chain() -> Any:
    """
    Build a chain that first tries an older completion model,
    then falls back to a ChatOpenAI-based chain if JSON parsing fails.

    This mirrors the 'fallbacks' section of the notebook.
    """
    challenge = (
        "write three poems in a json blob, where each poem is a json "
        "blob of a title, author, and first line"
    )

    # Primary chain: older completion-style model that often breaks JSON
    simple_model = OpenAI(
        temperature=0,
        max_tokens=1000,
        model="gpt-3.5-turbo-instruct",  # course replacement for text-davinci-001
    )
    simple_chain = simple_model | json.loads

    # Backup chain: newer ChatOpenAI + StrOutputParser + json.loads
    chat_model = ChatOpenAI(temperature=0)
    backup_chain = chat_model | StrOutputParser() | json.loads

    # Attach fallback
    final_chain = simple_chain.with_fallbacks([backup_chain])

    # Store the challenge on the chain for convenience (not strictly necessary)
    final_chain.challenge_prompt = challenge  # type: ignore[attr-defined]
    return final_chain


def demo_fallback() -> List[Dict[str, Any]]:
    """
    Run the fallback chain on its challenge prompt and return parsed poems.
    """
    chain = build_fallback_chain()
    challenge = getattr(
        chain,
        "challenge_prompt",
        "write three short poems as JSON with title, author, and first line.",
    )
    return chain.invoke(challenge)


# ---------------------------------------------------------------------------
# 5. Interface demos: invoke, batch, stream, ainvoke
# ---------------------------------------------------------------------------


def demo_interface_invoke(topic: str = "bears") -> str:
    chain = build_joke_chain()
    return chain.invoke({"topic": topic})


def demo_interface_batch(topics: List[str]) -> List[str]:
    chain = build_joke_chain()
    inputs = [{"topic": t} for t in topics]
    return chain.batch(inputs)


def demo_interface_stream(topic: str = "bears") -> List[str]:
    """
    Stream tokens for a joke. Returns the chunks as a list of strings.
    """
    chain = build_joke_chain()
    chunks: List[str] = []
    for t in chain.stream({"topic": topic}):
        # Each t is already a string because of StrOutputParser
        chunks.append(t)
    return chunks


async def demo_interface_ainvoke(topic: str = "bears") -> str:
    """
    Async version of invoke() – useful when you integrate into async apps.
    """
    chain = build_joke_chain()
    return await chain.ainvoke({"topic": topic})


def run_async_ainvoke_demo(topic: str = "bears") -> str:
    """
    Helper to run the async demo from a normal (sync) context.
    """
    return asyncio.run(demo_interface_ainvoke(topic))
