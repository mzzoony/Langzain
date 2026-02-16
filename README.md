# Langzain – OpenAI + LangChain Conversational Agent

Langzain is a small Python project that shows how to build a conversational AI agent using:

- **LangChain** for tools & routing
- **OpenAI** for the LLM (function calling)
- A simple **CLI chat** (`app.py`)
- An optional **Streamlit UI** (`ui_app.py`)

> ⚠️ You must provide your own OpenAI API key in a `.env` file.  
> The repo contains no keys for security reasons.



## Setup


git clone https://github.com/mzzoony/Langzain.git
cd Langzain

python -m venv .venv
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt