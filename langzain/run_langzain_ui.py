# run_langzain_ui.py
import os
import sys
import subprocess


def main() -> None:
    """
    Launch the Langzain Streamlit UI as if it were a normal desktop app.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(base_dir, "langzain", "ui_app.py")

    # Use the current Python and run "python -m streamlit run langzain/ui_app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", ui_path, "--server.headless=false"]

    # Optional: open in a new browser tab
    # cmd += ["--browser.serverAddress=localhost"]

    subprocess.run(cmd)


if __name__ == "__main__":
    main()