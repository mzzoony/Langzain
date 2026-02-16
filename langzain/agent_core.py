# agent_core.py
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

try:
    from .tools import get_current_temperature, search_wikipedia
except ImportError:
    from langzain.tools import get_current_temperature, search_wikipedia
# Load .env so OPENAI_API_KEY is available
load_dotenv()

# 1. LLM
llm = ChatOpenAI(
    api_key= os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),  # e.g. "https://openrouter.ai/api/v1"
    model=os.getenv("OPENAI_MODULE","openai/gpt-4o-mini"),   # you can change to "gpt-4o-mini" if you have it
    temperature=0,
)

# 2. Tools – just pass the Python functions
tools = [get_current_temperature, search_wikipedia]

SYSTEM_PROMPT = (
    "You are a helpful but slightly sassy assistant. "
    "You can call tools when needed to answer questions. "
    "Use the Wikipedia tool for general knowledge questions. "
    "Use the weather tool when the user asks about the weather at some location."
)

# 3. Create the agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


def run_agent(messages):
    """
    Run the agent on the current conversation.

    messages: list of dicts like
        {'role': 'user'/'assistant'/'system', 'content': '...'}
    Returns: updated list of messages including the agent's latest reply.
    """
    result = agent.invoke({"messages": messages})

    # New LangChain agents usually return {'messages': [...]}.
    if isinstance(result, dict) and "messages" in result:
        return result["messages"]

    # If it directly returns a list of messages, just use that.
    if isinstance(result, list):
        return result

    # Fallback: append whatever came back as a single assistant message
    messages.append({"role": "assistant", "content": str(result)})
    return messages
