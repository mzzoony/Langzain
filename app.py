# app.py
from agent_core import run_agent


def extract_last_assistant_message(messages):
    """
    Given a list of messages (could be dicts or LangChain message objects),
    return the text of the last assistant message.
    """
    for m in reversed(messages):
        # Get role
        role = getattr(m, "role", None) or m.get("role", None)
        content = getattr(m, "content", None) or m.get("content", "")

        if role in ("assistant", "ai"):
            # LangChain sometimes stores content as a list of chunks
            if isinstance(content, list):
                # Try to join any 'text' chunks
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
