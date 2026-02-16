# run_langzain.py
# run_langzain_gui.py
"""
Entry point for the Langzain desktop GUI.

You can run this with:
    python run_langzain_gui.py
and PyInstaller will also use this as the main script.
"""

from langzain.gui_app import main  # <-- NOTE: gui_app, not LangzainGUI


if __name__ == "__main__":
    main()
