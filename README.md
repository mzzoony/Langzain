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

```bash
git clone https://github.com/mzzoony/Langzain.git
cd Langzain

python -m venv .venv

# Windows:
.venv\Scripts\activate

pip install -r requirements.txt


## How to run

Terminal chat:
  python app.py
Terminal chat:
 streamlit run ui_app.py




#Screenshots:
![Streamlit UI](screenshots/streamlit-screenshot.png)
![Terminal demo](screenshots/terminal-main.png)
