from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional

from .config import get_client, OpenAISettings


# ---- 1. Dummy backend function (your "tool") -------------------------------

def get_current_weather(location: str, unit: str = "fahrenheit") -> Dict[str, Any]:
    """
    Example backend function.

    In the course notebook it was hard-coded; in a real app this would call
    a real weather API (OpenWeather, WeatherAPI, etc.).
    """
    return {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }


# ---- 2. Tool / function schema for the LLM ---------------------------------

WEATHER_FUNCTION: Dict[str, Any] = {
    "name": "get_current_weather",
    "description": (
        "Look up the current weather for a given city. "
        "Use this when a user asks about temperature or forecast."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City and region, e.g. 'Boston, MA' or 'Fairfax, VA'.",
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit; default is fahrenheit.",
            },
        },
        "required": ["location"],
    },
}

WEATHER_FUNCTIONS: List[Dict[str, Any]] = [WEATHER_FUNCTION]


# ---- 3. Core helper to call the model with different function_call modes ----

FunctionCallMode = Literal["auto", "none", "force"]


def _call_weather_model(
    user_content: str,
    mode: FunctionCallMode = "auto",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call the OpenAI model with the weather tool available.

    mode:
        - "auto"  -> let the model decide whether to call the function
        - "none"  -> forbid function calls
        - "force" -> force calling get_current_weather
    """
    client = get_client()
    settings = OpenAISettings()
    model_name = model or settings.default_model

    messages = [{"role": "user", "content": user_content}]

    # Map our friendly "force" to the SDK's function_call payload
    if mode == "force":
        function_call = {"name": "get_current_weather"}
    elif mode == "none":
        function_call = "none"
    else:
        function_call = "auto"

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        functions=WEATHER_FUNCTIONS,
        function_call=function_call,
    )

    # Convert to plain dict for easier printing / testing
    return response.to_dict()


# ---- 4. High-level demos that match what the notebook showed ---------------

def demo_auto_weather_question() -> Dict[str, Any]:
    """User asks about weather; model should choose to call the function."""
    return _call_weather_model("What's the weather like in Boston?", mode="auto")


def demo_auto_smalltalk() -> Dict[str, Any]:
    """User just says hi; model should answer normally, no function call."""
    return _call_weather_model("hi!", mode="auto")


def demo_forbid_function_call() -> Dict[str, Any]:
    """User asks about weather but we forbid function calls (mode = none)."""
    return _call_weather_model("What's the weather in Boston?", mode="none")


def demo_force_function_on_smalltalk() -> Dict[str, Any]:
    """User says hi, but we force calling the function anyway (silly demo)."""
    return _call_weather_model("hi!", mode="force")


# ---- 5. Full round-trip: model chooses tool -> we call it -> model replies --

def demo_two_step_conversation(model: Optional[str] = None) -> Dict[str, Any]:
    """
    Demonstrate the classic 2-step pattern:

    1. Ask the model what tool to call.
    2. Actually call get_current_weather(...) in Python.
    3. Pass the tool result back to the model as a 'function' message.
    4. Get a final, natural-language answer.
    """
    client = get_client()
    settings = OpenAISettings()
    model_name = model or settings.default_model

    # Step 1: ask about the weather
    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": "What's the weather like in Boston?"}
    ]

    first = client.chat.completions.create(
        model=model_name,
        messages=messages,
        functions=WEATHER_FUNCTIONS,
        function_call={"name": "get_current_weather"},
    )

    first_msg = first.choices[0].message
    messages.append(first_msg.to_dict())

    # Parse arguments and call our backend function
    args = json.loads(first_msg.function_call.arguments)
    observation = get_current_weather(**args)

    # Step 2: pass function result back to the model
    messages.append(
        {
            "role": "function",
            "name": "get_current_weather",
            "content": json.dumps(observation),
        }
    )

    second = client.chat.completions.create(model=model_name, messages=messages)
    return second.to_dict()


if __name__ == "__main__":
    # Simple manual test when you run: python -m mzz_agents.openai_function_calling
    from pprint import pprint

    print("=== demo_auto_weather_question ===")
    pprint(demo_auto_weather_question())

    print("\n=== demo_two_step_conversation ===")
    pprint(demo_two_step_conversation())
