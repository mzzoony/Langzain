# app.py
from .agent_core import run_agent
def extract_last_assistant_message(messages):
    """
    Given a list of messages (could be dicts or LangChain message objects),
    return the text of the last assistant message.
    """
    for m in reversed(messages):
        role = None
        content = None

        # Case 1: LangChain message objects (AIMessage, HumanMessage, SystemMessage)
        if hasattr(m, "content"):
            # New LangChain messages usually have .type = "ai" / "human" / "system"
            role = getattr(m, "type", None) or getattr(m, "role", None)
            content = getattr(m, "content", "")

        # Case 2: plain dicts: {"role": "...", "content": "..."}
        elif isinstance(m, dict):
            role = m.get("role")
            content = m.get("content", "")

        # If this is an assistant/AI message, extract the text
        if role in ("assistant", "ai"):
            # Sometimes content is a list of chunks instead of a plain string
            if isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        parts.append(part.get("text", ""))
                if parts:
                    return "".join(parts)
                return str(content)
            return str(content)

    return "[No assistant reply found]"


def main():
    print("AI Agent is ready. Type 'exit' to quit.\n")

    # This will hold the whole conversation for memory
    messages = []

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Bye!")
            break

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # Call the agent
        messages = run_agent(messages)

        # Extract last assistant reply
        bot_reply = extract_last_assistant_message(messages)
        print("Bot:", bot_reply)
        print()


if __name__ == "__main__":
    main()
