# LangzainGUI.py – ChatGPT-style desktop GUI with “3D” input bar,
# thinking indicator + emojis and bubble-style messages.

import tkinter as tk
from tkinter import ttk
from .agent_core import run_agent


class LangzainGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # ----- Window basics -----
        self.title("Langzain – Desktop Chat")
        self.minsize(900, 550)

        # state
        self.messages = []
        self.theme_var = tk.StringVar(value="light")
        self.font_size_var = tk.StringVar(value="medium")
        self.chat_font_family = "Segoe UI"
        self.emoji_font_family = "Segoe UI Emoji"

        # emojis
        self.user_emoji = "🧑‍💻"
        self.bot_emoji = "🤖"

        # references for 3D input bar
        self.input_outer = None
        self.input_shadow = None
        self.input_card = None

        # grid: 3 rows (header, chat, input)
        self.grid_rowconfigure(1, weight=1)   # chat area expands
        self.grid_columnconfigure(0, weight=1)

        self._create_styles()
        self._create_menubar()
        self._create_header()
        self._create_chat_area()
        self._create_input_bar()

        # apply theme + font size
        self.set_theme("light")
        self._apply_font_size()

        self._append_system_line(
            "LangZain: AI Agent is ready. Type your message below (or 'exit' to quit)."
        )

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------

    def _create_styles(self):
        style = ttk.Style()

        style.configure(
            "Header.TFrame",
            padding=(16, 10),
        )
        style.configure(
            "HeaderTitle.TLabel",
            font=("Segoe UI Semibold", 16),
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            font=("Segoe UI", 9),
        )

        # Padding for outer input area – extra bottom padding lifts bar up
        style.configure("InputBarOuter.TFrame", padding=(12, 8, 12, 26))

        style.configure(
            "ChatSend.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(24, 8),
        )

    def _create_menubar(self):
        menubar = tk.Menu(self)

        # Chat menu
        chat_menu = tk.Menu(menubar, tearoff=0)
        chat_menu.add_command(label="Clear chat", command=self.clear_chat)
        menubar.add_cascade(label="Chat", menu=chat_menu)

        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_radiobutton(
            label="Light",
            variable=self.theme_var,
            value="light",
            command=lambda: self.set_theme("light"),
        )
        theme_menu.add_radiobutton(
            label="Dark",
            variable=self.theme_var,
            value="dark",
            command=lambda: self.set_theme("dark"),
        )
        menubar.add_cascade(label="Theme", menu=theme_menu)

        # View menu – font size control
        view_menu = tk.Menu(menubar, tearoff=0)
        for label, value in [("Small", "small"), ("Medium", "medium"), ("Large", "large")]:
            view_menu.add_radiobutton(
                label=label,
                variable=self.font_size_var,
                value=value,
                command=self._apply_font_size,
            )
        menubar.add_cascade(label="View", menu=view_menu)

        self.config(menu=menubar)

    def _create_header(self):
        header = ttk.Frame(self, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")

        icon_lbl = ttk.Label(header, text="😎", font=("Segoe UI Emoji", 18))
        icon_lbl.grid(row=0, column=0, rowspan=2, sticky="w")

        title_lbl = ttk.Label(
            header,
            text="LangZain – Conversational Agent",
            style="HeaderTitle.TLabel",
        )
        title_lbl.grid(row=0, column=1, sticky="w", padx=(8, 0))

        subtitle_lbl = ttk.Label(
            header,
            text="A small local assistant using LangChain + OpenAI.",
            style="HeaderSubtitle.TLabel",
        )
        subtitle_lbl.grid(row=1, column=1, sticky="w", padx=(8, 0))

        header.grid_columnconfigure(1, weight=1)

    def _create_chat_area(self):
        chat_frame = ttk.Frame(self, padding=(10, 0, 10, 0))
        chat_frame.grid(row=1, column=0, sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_text = tk.Text(
            chat_frame,
            wrap="word",
            state="disabled",
            font=(self.chat_font_family, 12),
            padx=10,
            pady=10,
            relief="flat",
            borderwidth=0,
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            chat_frame, orient="vertical", command=self.chat_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_text.configure(yscrollcommand=scrollbar.set)

        # tags – colors & fonts will be updated in set_theme() / _apply_font_size()
        self.chat_text.tag_configure("system", spacing3=8)
        # user / bot tags: background gives “bubble”,
        # margins + spacing give separation between messages
        self.chat_text.tag_configure(
            "user",
            lmargin1=14,
            lmargin2=14,
            rmargin=14,
            spacing1=8,
            spacing3=14,
        )
        self.chat_text.tag_configure(
            "bot",
            lmargin1=14,
            lmargin2=14,
            rmargin=14,
            spacing1=8,
            spacing3=14,
        )
        self.chat_text.tag_configure(
            "thinking",
            lmargin1=18,
            lmargin2=18,
            rmargin=18,
            spacing1=4,
            spacing3=8,
            font=(self.emoji_font_family, 12, "italic"),
        )

    def _create_input_bar(self):
        """
        Create a “3D” style input bar:
        - outer frame (matches window bg)
        - a darker shadow rectangle
        - a slightly lifted card with entry + button
        """
        outer = ttk.Frame(self, style="InputBarOuter.TFrame")
        outer.grid(row=2, column=0, sticky="ew")
        outer.grid_columnconfigure(0, weight=1)
        self.input_outer = outer

        # Shadow frame (sits slightly lower – gives depth)
        shadow = tk.Frame(outer, bd=0)
        shadow.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 6))
        shadow.grid_columnconfigure(0, weight=1)

        # Card frame (slightly shifted up on top of shadow)
        card = tk.Frame(outer, bd=0)
        card.grid(row=0, column=0, sticky="ew", padx=20, pady=(6, 14))
        card.grid_columnconfigure(0, weight=1)

        self.input_shadow = shadow
        self.input_card = card

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            card,
            textvariable=self.entry_var,
            relief="flat",
            borderwidth=0,
            font=(self.chat_font_family, 12),
            insertwidth=2,
        )
        # ipady makes the entry itself taller
        self.entry.grid(row=0, column=0, sticky="ew", padx=(10, 14), pady=8, ipady=6)
        self.entry.bind("<Return>", self.on_send)

        send_btn = ttk.Button(card, text="Send", style="ChatSend.TButton")
        send_btn.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=8)
        send_btn.configure(command=lambda: self.on_send(None))

    # ------------------------------------------------------------------
    #  Theme + font handling
    # ------------------------------------------------------------------

    def set_theme(self, mode: str):
        """Switch between a light and dark palette (affects 3D bar & bubbles)."""
        self.theme_var.set(mode)

        if mode == "dark":
            # Dark theme
            bg_main = "#202123"        # window background
            bg_card = "#202123"        # chat area
            bg_input_card = "#343541"  # raised input bar
            bg_input_entry = "#40414f" # entry itself
            shadow_color = "#050509"   # bar shadow

            fg_text = "#e5e5e5"
            fg_system = "#a0a0a0"

            # chat “bubble” colors
            user_bubble_bg = "#818161"   # green-ish
            bot_bubble_bg = "#6e8959"    # blue-ish
        else:
            # Light theme
            bg_main = "#9a9ada"        # window background
            bg_card = "#c5bbbb"        # chat area
            bg_input_card = "#dedfe6"  # raised input bar (noticeably darker)
            bg_input_entry = "#f7f7fb" # entry itself
            shadow_color = "#797c89"   # soft gray shadow

            fg_text = "#222222"
            fg_system = "#666666"

            user_bubble_bg = "#818161"
            bot_bubble_bg = "#94a984"

        style = ttk.Style()

        # Window background
        self.configure(bg=bg_main)

        # Header
        style.configure("Header.TFrame", background=bg_main)
        style.configure(
            "HeaderTitle.TLabel",
            background=bg_main,
            foreground=fg_text,
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background=bg_main,
            foreground=fg_system,
        )

        # Chat area
        self.chat_text.configure(background=bg_card, foreground=fg_text)
        self.chat_text.tag_configure("system", foreground=fg_system)

        # Bubble tags – foreground / background set here so they react to theme
        self.chat_text.tag_configure(
            "user",
            foreground=fg_text,
            background=user_bubble_bg,
        )
        self.chat_text.tag_configure(
            "bot",
            foreground=fg_text,
            background=bot_bubble_bg,
        )
        self.chat_text.tag_configure(
            "thinking",
            foreground=fg_system,
            background=bot_bubble_bg if mode == "light" else "#3b3c4b",
        )

        # Outer input frame
        style.configure("InputBarOuter.TFrame", background=bg_main)

        # 3D bar colors
        if self.input_shadow is not None:
            self.input_shadow.configure(bg=shadow_color)
        if self.input_card is not None:
            self.input_card.configure(bg=bg_input_card)

        # Entry inside bar
        self.entry.configure(
            background=bg_input_entry,
            foreground=fg_text,
            insertbackground=fg_text,
        )

    def _apply_font_size(self):
        """Adjust chat + input font sizes based on the View → Font size menu."""
        size_map = {"small": 11, "medium": 13, "large": 15}
        size = size_map.get(self.font_size_var.get(), 13)

        self.chat_text.configure(font=(self.chat_font_family, size))
        self.entry.configure(font=(self.chat_font_family, size))

        # Make sure the bubbles (tags) also use the right font size.
        self.chat_text.tag_configure("system", font=(self.chat_font_family, size))
        self.chat_text.tag_configure("user", font=(self.emoji_font_family, size))
        self.chat_text.tag_configure("bot", font=(self.emoji_font_family, size))
        # thinking tag already has italic style; keep emoji font
        self.chat_text.tag_configure(
            "thinking",
            font=(self.emoji_font_family, size, "italic"),
        )

    # ------------------------------------------------------------------
    #  Chat logic
    # ------------------------------------------------------------------

    def clear_chat(self):
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")

    def _append_line(self, text: str, tag: str = None):
        """
        Insert a line into the chat and return the index where it starts.
        Returning the index lets us later delete the 'thinking...' line.

        Bubbles are implemented using tag backgrounds + margins, so each
        message is one “paragraph” with spacing around it.
        """
        self.chat_text.configure(state="normal")

        # start index of the new line (for thinking-removal logic)
        line_index = self.chat_text.index("end-1c linestart")

        if tag:
            self.chat_text.insert("end", text + "\n", tag)
        else:
            self.chat_text.insert("end", text + "\n")

        # extra newline for a bit more separation at the end
        self.chat_text.insert("end", "\n")

        self.chat_text.see("end")
        self.chat_text.configure(state="disabled")
        return line_index

    def _append_system_line(self, text: str):
        self._append_line(text, tag="system")

    def _append_user_line(self, text: str):
        # user emoji + bubble
        self._append_line(f"{self.user_emoji}  {text}", tag="user")

    def _append_bot_line(self, text: str):
        # assistant emoji + bubble
        self._append_line(f"{self.bot_emoji}  {text}", tag="bot")

    def _append_thinking_line(self):
        """Show a temporary 'thinking...' bubble and return its index."""
        idx = self._append_line(f"{self.bot_emoji}  thinking…", tag="thinking")
        # force UI refresh so it appears before the model finishes
        self.chat_text.update_idletasks()
        self.update_idletasks()
        return idx

    def _remove_thinking_line(self, index):
        """Delete the temporary thinking line at the given index."""
        self.chat_text.configure(state="normal")
        # delete that whole line including the extra newline we added
        self.chat_text.delete(index, f"{index} lineend+2c")
        self.chat_text.configure(state="disabled")

    def on_send(self, event):
        user_text = self.entry_var.get().strip()
        if not user_text:
            return

        if user_text.lower() in {"exit", "quit"}:
            self.destroy()
            return

        self._append_user_line(user_text)
        self.entry_var.set("")

        self.messages.append({"role": "user", "content": user_text})

        # show temporary thinking indicator
        thinking_index = self._append_thinking_line()

        # run the agent (blocking, but UI already shows 'thinking…')
        self.messages = run_agent(self.messages)

        bot_reply = self.extract_last_assistant_message(self.messages)

        # remove 'thinking…' and show final answer
        self._remove_thinking_line(thinking_index)
        self._append_bot_line(bot_reply)

    @staticmethod
    def extract_last_assistant_message(messages):
        for m in reversed(messages):
            role = None
            content = None

            if hasattr(m, "content"):
                role = getattr(m, "type", None) or getattr(m, "role", None)
                content = getattr(m, "content", "")
            elif isinstance(m, dict):
                role = m.get("role")
                content = m.get("content", "")

            if role in ("assistant", "ai"):
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
    app = LangzainGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
