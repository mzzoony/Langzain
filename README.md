# Langzain – LangChain + OpenAI Agent

Small experimental agent built with:

- Python
- LangChain / LangGraph-style agent loop
- OpenAI chat models & tools (weather + Wikipedia)
- CLI chat interface (and optional UI script)

> **Note:** You must provide your own OpenAI API key in a `.env` file – it is **not** committed to this repo.

## Project Structure

- `app.py` – simple console chatbot (`python app.py`)
- `agent_core.py` – agent logic & `run_agent` function
- `tools.py` – tool definitions (current weather + Wikipedia search)
- `ui_app.py` – optional UI (e.g. Streamlit, if you run it later)
- `.env` – **local only**, contains `OPENAI_API_KEY=...` (ignored by git)

## How to run (locally)

```bash
# 1. Create and activate venv (already done for you)
python -m venv .venv
.\.venv\Scripts\activate    # PowerShell

# 2. Install deps
pip install -r requirements.txt

# 3. Add your key to .env
#   OPENAI_API_KEY=sk-...

# 4. Run the CLI agent
python app.py
