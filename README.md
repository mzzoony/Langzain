# Langzain – OpenAI + LangChain Conversational Agent

Langzain is a small Python project where I teach a language model to behave like a tiny agent.  
It can chat, remember what you said earlier in the session, and call a couple of tools (weather + Wikipedia) when it needs extra info.

## Features

- ⚙️ **LangChain** for routing and tool calling  
- 🤖 **OpenAI-compatible LLM** for the actual conversation  
- 💻 **CLI chat** (`app.py`) so you can talk to it from the terminal  
- 🌐 **Streamlit UI** (`ui_app.py`) for a lightweight “ChatGPT-style” web interface  

> 🔐 You must bring your own API key (OpenAI or an OpenAI-compatible provider such as OpenRouter).
> Add it to a `.env` file – the repo never includes any keys.

---

## Setup

git clone https://github.com/mzzoony/Langzain.git
cd Langzain

python -m venv .venv

# Windows:
.venv\Scripts\activate

pip install -r requirements.txt


## Install & Run

### Option 1 – Clone the repo (recommended)

This is the best way if you want both the terminal chat and the Streamlit UI.


git clone https://github.com/mzzoony/Langzain.git
cd Langzain

# Create and activate a virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the langzain package in editable mode
pip install -e .

-Before you run anything, create a .env file in the project root and add your key:
  OPENAI_API_KEY=sk-...

-Run the terminal chat:
  python -m langzain.app

-Run the Streamlit UI:
  Run the Streamlit UI



#Screenshots:
![Streamlit UI](screenshots/streamlit-screenshot.png)
![Terminal demo](screenshots/terminal-main.png)
