import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import random
import sys

# ---------------------------
# Configuration & Constants
# ---------------------------
JOKES_FILE = "jokes.txt"
FACTS_FILE = "facts.txt"
VOICE_RATE = 160
VOICE_ENABLED_DEFAULT = True

DEFAULT_JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the computer go to the doctor? Because it had a virus!",
    "What do you call fake spaghetti? An impasta!"
]
DEFAULT_FACTS = [
    "Honey never spoils. Archaeologists found edible honey in ancient Egyptian tombs.",
    "Bananas are berries, but strawberries aren't.",
    "Octopuses have three hearts."
]

CONVO_MAP = {
    "hello": "Hi!",
    "hi": "Hello!",
    "hey": "Hey there!",
    "how are you": "I'm fine, thanks! How can I help you today?",
    "what's up": "All good here — ready to chat!",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "See you later!",
    "thanks": "You're welcome!",
    "thank you": "Anytime!",
    "how are you doing?": "I’m doing well",
    "good morning": "A very wonderful morning to you and your family",
    "good afternoon": "Good afternoon User",
    "good evening": "Same to u🥰",
    "good night": "Good night... take care"
}

RIDDLES = [
    {"q": "I speak without a mouth and hear without ears. I have nobody, but I come alive with wind. What am I?",
     "a": "echo "},
    {"q": "I come from a mine and get surrounded by wood always. Everyone uses me. What am I?",
     "a": "pencil lead"},
    {"q": "What has keys but can't open locks?",
     "a": "piano"}
]

# Theme definitions: each theme is a dict of colors used in several widgets
THEMES = {
    "Dark": {
        "bg": "#0f172a",
        "top_bg": "#0b1220",
        "ctrl_bg": "#07102a",
        "chat_bg": "#091027",
        "chat_fg": "#dbeafe",
        "entry_bg": "#061026",
    },
    "Light": {
        "bg": "#f3f4f6",
        "top_bg": "#e6eef8",
        "ctrl_bg": "#e6eef8",
        "chat_bg": "#ffffff",
        "chat_fg": "#0b1220",
        "entry_bg": "#f8fafc",
    },
    "Blue": {
        "bg": "#e6f0ff",
        "top_bg": "#cfe4ff",
        "ctrl_bg": "#dbeeff",
        "chat_bg": "#f0f8ff",
        "chat_fg": "#05204a",
        "entry_bg": "#e9f3ff",
    }
}

DEFAULT_THEME = "Dark"

# ---------------------------
# File handling utilities
# ---------------------------
def safe_read_lines(filepath, default_list):
    try:
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(default_list))
            return list(default_list)
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(default_list))
            return list(default_list)
        return lines
    except Exception as e:
        print(f"[File read error] {filepath}: {e}", file=sys.stderr)
        return list(default_list)

def append_line_to_file(filepath, text):
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n" + text.strip())
    except Exception as e:
        print(f"[File write error] {filepath}: {e}", file=sys.stderr)

# ---------------------------
# Safe TTS wrapper (pyttsx3)
# ---------------------------
class SafeTTS:
    def __init__(self, enabled=True, rate=VOICE_RATE):
        self.enabled = enabled
        self.engine = None
        self.rate = rate
        if not enabled:
            return
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            try:
                self.engine.setProperty('rate', rate)
            except Exception:
                pass
        except Exception as e:
            print(f"[TTS init failed] pyttsx3 not available or error: {e}", file=sys.stderr)
            self.engine = None
            self.enabled = False

    def speak(self, text):
        if not self.enabled or not self.engine:
            return
        def _run():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[TTS error] {e}", file=sys.stderr)
        threading.Thread(target=_run, daemon=True).start()

# ---------------------------
# Chatbot core logic
# ---------------------------
class ChatbotCore:
    def __init__(self):
        self.jokes = safe_read_lines(JOKES_FILE, DEFAULT_JOKES)
        self.facts = safe_read_lines(FACTS_FILE, DEFAULT_FACTS)
        self.current_riddle = None
        self.riddle_active = True
        #self.riddle_active = False

    def get_reply(self, user_text):
        meta = {}
        text = user_text.strip().lower()

        if self.riddle_active and self.current_riddle:
            expected = self.current_riddle["a"].strip().lower()
            user_ans = " ".join(text.split())
            if expected == user_ans or expected in user_ans or user_ans in expected:
                reply = "Congrats! That's correct 🎉"
                meta['clear_riddle'] = True
                return reply, meta
            elif user_ans == "skip" or user_ans == "SKIP" or user_ans == "Skip":
                reply = "Riddle skipped...\n The correct answer is: " + expected
                meta['clear_riddle'] = True
                return reply, meta

            else:
                reply = "Not quite. Try again or type 'skip' to get the answer."
                return reply, meta

        if text in CONVO_MAP:
            reply = CONVO_MAP[text]
            if text in ("bye", "goodbye"):
                meta['clear_riddle'] = True
            return reply, meta

        if any(g in text for g in ["how are", "how's it going", "how are you doing"]):
            return CONVO_MAP.get("how are you"), meta

        if text in ("riddle", "riddles", "ask riddle", "give me a riddle", "RIDDLES", "RIDDLE", "please give me a riddle"):
            r = random.choice(RIDDLES)
            self.current_riddle = r
            self.riddle_active = True
            meta['riddle_question'] = True
            return r["q"], meta

        if text == "skip":
            if self.riddle_active and self.current_riddle:
                ans = self.current_riddle["a"]
                meta['clear_riddle'] = True
                return f"The answer is: {ans}", meta
            else:
                return "No active riddle to skip. Try 'Riddles' to get one.", meta

        if "joke" in text:
            return random.choice(self.jokes), meta

        if "fact" in text or "did you know" in text:
            return random.choice(self.facts), meta

        fallback = "I didn't get that. Try: 'hello', 'how are you', 'riddles', 'jokes', or 'facts'."
        return fallback, meta

    def get_random_joke(self):
        return random.choice(self.jokes) if self.jokes else DEFAULT_JOKES[0]

    def get_random_fact(self):
        return random.choice(self.facts) if self.facts else DEFAULT_FACTS[0]

    def stop_riddle(self):
        self.current_riddle = None
        self.riddle_active = False

# ---------------------------
# GUI
# ---------------------------
class ChatbotGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pythonChatbot")
        # start fullscreen
        self.attributes("-fullscreen", True)
        # store whether we're fullscreen for potential toggling
        self.fullscreen = True

        # default theme
        self.current_theme_name = DEFAULT_THEME
        self.theme = THEMES[self.current_theme_name]

        self.geometry("900x600")
        self.minsize(700, 500)

        self.font_title = ("Segoe UI", 18, "bold")
        self.font_text = ("Segoe UI", 11)
        self.font_small = ("Segoe UI", 9)

        # Core + TTS
        self.core = ChatbotCore()
        self.tts = SafeTTS(enabled=VOICE_ENABLED_DEFAULT)

        # Animation states
        self.cats_visible = False
        self.animation_running = False
        self.cat_btns = {}
        self.theme_visible = False
        self.theme_btns = {}

        # Build UI
        self._build_ui()
        self._bind_events()
        self.apply_theme(self.current_theme_name)

        # initial welcome
        self._insert_bot_message("Hello! I'm pythonChatbot. Type 'Riddles' for a riddle, or use Categories -> Jokes/Facts.")

    # -----------------------
    # UI Build
    # -----------------------
    def _build_ui(self):
        # Top bar
        self.top_frame = tk.Frame(self, bg=self.theme["top_bg"], height=70)
        self.top_frame.pack(fill="x")
        title = tk.Label(self.top_frame, text="pythonChatbot", font=self.font_title, fg="#e6eef8", bg=self.theme["top_bg"])
        title.pack(side="left", padx=16, pady=12)

        # Right side top controls (Exit, Fullscreen toggle, Voice)
        right_top = tk.Frame(self.top_frame, bg=self.theme["top_bg"])
        right_top.pack(side="right", padx=10)
        exit_btn = ttk.Button(right_top, text="Exit", command=self._on_exit)
        exit_btn.pack(side="right", padx=6)
        fs_btn = ttk.Button(right_top, text="Toggle Fullscreen", command=self._toggle_fullscreen)
        fs_btn.pack(side="right", padx=6)
        self.voice_var = tk.BooleanVar(value=self.tts.enabled)
        voice_chk = ttk.Checkbutton(right_top, text="Voice", variable=self.voice_var, command=self._toggle_voice)
        voice_chk.pack(side="right", padx=6)

        # Main frame
        self.main_frame = tk.Frame(self, bg=self.theme["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=(8,12))

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, font=self.font_text, state="disabled",
                                                      bg=self.theme["chat_bg"], fg=self.theme["chat_fg"], relief="flat", padx=10, pady=10)
        self.chat_display.pack(fill="both", expand=True, side="left")

        # Right control column
        self.ctrl_frame = tk.Frame(self.main_frame, width=240, bg=self.theme["ctrl_bg"])
        self.ctrl_frame.pack(fill="y", side="right", padx=(10,0))
        self.ctrl_frame.pack_propagate(False)

        # Button panel
        btn_frame = tk.Frame(self.ctrl_frame, bg=self.theme["ctrl_bg"])
        btn_frame.pack(pady=8)

        self.btn_categories = ttk.Button(btn_frame, text="Categories", command=self._toggle_categories)
        self.btn_categories.grid(row=0, column=0, pady=6, ipadx=6)

        self.riddles_btn = ttk.Button(btn_frame, text="Riddles", command=self._on_riddles_clicked)
        self.riddles_btn.grid(row=1, column=0, pady=6, ipadx=6)

        # Theme button
        self.theme_btn = ttk.Button(btn_frame, text="Theme", command=self._toggle_theme_options)
        self.theme_btn.grid(row=2, column=0, pady=6, ipadx=6)

        # Other controls
        ctrl2 = tk.Frame(self.ctrl_frame, bg=self.theme["ctrl_bg"])
        ctrl2.pack(padx=6, pady=10, fill="x")

        exit_btn2 = ttk.Button(ctrl2, text="Exit", command=self._on_exit)
        exit_btn2.pack(fill="x", pady=4)
        clear_btn = ttk.Button(ctrl2, text="Clear Screen", command=self._clear_chat)
        clear_btn.pack(fill="x", pady=4)
        manual_btn = ttk.Button(ctrl2, text="User Manual", command=self._show_manual)
        manual_btn.pack(fill="x", pady=4)

        # Category container (for animated Jokes/Facts)
        self.cat_container = tk.Frame(self.ctrl_frame, bg=self.theme["ctrl_bg"], height=110)
        self.cat_container.pack(fill="x", pady=6)

        jokes_btn = ttk.Button(self.cat_container, text="Jokes", command=self._on_jokes_clicked)
        facts_btn = ttk.Button(self.cat_container, text="Facts", command=self._on_facts_clicked)
        self.cat_btns['jokes'] = jokes_btn
        self.cat_btns['facts'] = facts_btn

        # Theme options container (animated theme buttons)
        self.theme_container = tk.Frame(self.ctrl_frame, bg=self.theme["ctrl_bg"], height=120)
        self.theme_container.pack(fill="x", pady=6)
        # create theme buttons but keep hidden
        light_btn = ttk.Button(self.theme_container, text="Light", command=lambda: self.apply_theme("Light"))
        dark_btn = ttk.Button(self.theme_container, text="Dark", command=lambda: self.apply_theme("Dark"))
        blue_btn = ttk.Button(self.theme_container, text="Blue", command=lambda: self.apply_theme("Blue"))
        self.theme_btns['Light'] = light_btn
        self.theme_btns['Dark'] = dark_btn
        self.theme_btns['Blue'] = blue_btn

        # Add content quick handlers
        add_frame = tk.LabelFrame(self.ctrl_frame, text="Add Content", bg=self.theme["ctrl_bg"], fg="#cbd5e1", font=self.font_small)
        add_frame.pack(fill="x", padx=8, pady=8)
        self.add_entry = ttk.Entry(add_frame)
        self.add_entry.pack(fill="x", padx=6, pady=6)
        add_joke_btn = ttk.Button(add_frame, text="Add as Joke", command=self._add_as_joke)
        add_fact_btn = ttk.Button(add_frame, text="Add as Fact", command=self._add_as_fact)
        add_joke_btn.pack(side="left", padx=6, pady=(0,8))
        add_fact_btn.pack(side="right", padx=6, pady=(0,8))

        # Bottom entry bar
        bottom_frame = tk.Frame(self, bg=self.theme["entry_bg"])
        bottom_frame.pack(fill="x", side="bottom")
        self.entry = ttk.Entry(bottom_frame, font=self.font_text)
        self.entry.pack(fill="x", padx=12, pady=8, side="left", expand=True)
        send_btn = ttk.Button(bottom_frame, text="Send", command=self._on_send)
        send_btn.pack(side="right", padx=12, pady=8)

    # -----------------------
    # Theme application
    # -----------------------
    def apply_theme(self, theme_name):
        if theme_name not in THEMES:
            return
        self.current_theme_name = theme_name
        self.theme = THEMES[theme_name]

        # Update backgrounds and chat colors
        try:
            self.configure(bg=self.theme["bg"])
            self.top_frame.configure(bg=self.theme["top_bg"])
            # update title label color (find by children)
            for child in self.top_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(bg=self.theme["top_bg"])
            self.main_frame.configure(bg=self.theme["bg"])
            self.ctrl_frame.configure(bg=self.theme["ctrl_bg"])
            self.cat_container.configure(bg=self.theme["ctrl_bg"])
            self.theme_container.configure(bg=self.theme["ctrl_bg"])
            self.chat_display.configure(bg=self.theme["chat_bg"], fg=self.theme["chat_fg"])
            # bottom entry background
            # Note: ttk.Entry doesn't accept bg reliably across platforms; use its master frame color
            # update entry container background
            # update the bottom frame background if present:
            # (we'll set the bottom_frame's bg if possible)
            for w in self.winfo_children():
                if isinstance(w, tk.Frame) or isinstance(w, tk.LabelFrame):
                    w.configure(bg=self.theme["bg"])
        except Exception:
            pass

        # update text colors on control buttons/labels if needed
        # For simplicity, force a small redraw by updating idletasks
        self.update_idletasks()

        # give a small feedback
        self._insert_bot_message(f"Theme changed to {theme_name}.")

    # -----------------------
    # UI helpers
    # -----------------------
    def _insert_bot_message(self, text):
        self._insert_message("Bot", text)

    def _insert_user_message(self, text):
        self._insert_message("You", text)

    def _insert_message(self, sender, text):
        stamp = time.strftime("%H:%M:%S")
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"{sender} [{stamp}]: {text}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    # -----------------------
    # Event binding and handlers
    # -----------------------
    def _bind_events(self):
        self.entry.bind("<Return>", lambda e: self._on_send())
        self.bind("<Configure>", lambda e: self._reposition_cat_buttons())
        # Allow pressing Escape to exit fullscreen (convenience)
        self.bind("<Escape>", lambda e: self._exit_fullscreen())
        # F11 toggles fullscreen
        self.bind("<F11>", lambda e: self._toggle_fullscreen())

    def _toggle_voice(self):
        enabled = self.voice_var.get()
        if enabled and not self.tts.enabled:
            self.tts = SafeTTS(enabled=True)
        else:
            self.tts.enabled = enabled

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def _exit_fullscreen(self):
        self.fullscreen = False
        self.attributes("-fullscreen", False)

    def _on_exit(self):
        # Attempt a graceful shutdown
        try:
            self.destroy()
        except Exception:
            os._exit(0)

    def _on_send(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self._insert_user_message(user_text)
        self.entry.delete(0, tk.END)
        threading.Thread(target=self._process_user_text, args=(user_text,), daemon=True).start()

    def _process_user_text(self, user_text):
        reply, meta = self.core.get_reply(user_text)
        self._insert_bot_message(reply)
        if self.tts.enabled:
            self.tts.speak(reply)
        if meta.get('riddle_question'):
            self._insert_bot_message("(Type your answer directly in the input box. Type 'skip' to see the answer.)")
        if meta.get('clear_riddle'):
            self.core.stop_riddle()

    # -----------------------
    # Categories animation (Jokes/Facts)
    # -----------------------
    def _toggle_categories(self):
        if self.animation_running:
            return
        if not self.cats_visible:
            self._show_category_buttons()
        else:
            self._hide_category_buttons()

    def _reposition_cat_buttons(self):
        if not self.cats_visible:
            return
        cont = self.cat_container
        cont.update_idletasks()
        w = cont.winfo_width()
        target_x = (w // 2) - 60
        if self.cats_visible and not self.animation_running:
            self.cat_btns['jokes'].place(x=target_x, y=10)
            self.cat_btns['facts'].place(x=target_x, y=52)

    def _show_category_buttons(self):
        cont = self.cat_container
        cont.update()
        w = cont.winfo_width() or cont.winfo_reqwidth() or 200
        start_x = -160
        target_x = (w // 2) - 60
        y_positions = {"jokes": 10, "facts": 52}
        for name, btn in self.cat_btns.items():
            btn.place(x=start_x, y=y_positions[name], width=120)
        self.cats_visible = True
        self.animation_running = True
        def animate(step=0):
            if step > 20:
                for name, btn in self.cat_btns.items():
                    btn.place(x=target_x, y=y_positions[name], width=120)
                self.animation_running = False
                return
            frac = step / 20.0
            cur_x = int(start_x + (target_x - start_x) * frac)
            for name, btn in self.cat_btns.items():
                btn.place(x=cur_x, y=y_positions[name])
            step += 1
            self.after(12, lambda: animate(step))
        animate(0)

    def _hide_category_buttons(self):
        if self.animation_running:
            return
        cont = self.cat_container
        cont.update()
        w = cont.winfo_width() or cont.winfo_reqwidth() or 200
        start_x = (w // 2) - 60
        target_x = -160
        y_positions = {"jokes": 10, "facts": 52}
        self.animation_running = True
        def animate(step=0):
            if step > 20:
                for name, btn in self.cat_btns.items():
                    btn.place_forget()
                self.cats_visible = False
                self.animation_running = False
                return
            frac = step / 20.0
            cur_x = int(start_x + (target_x - start_x) * frac)
            for name, btn in self.cat_btns.items():
                btn.place(x=cur_x, y=y_positions[name])
            step += 1
            self.after(12, lambda: animate(step))
        animate(0)

    def _on_jokes_clicked(self):
        joke = self.core.get_random_joke()
        self._insert_bot_message(joke)
        if self.tts.enabled:
            self.tts.speak(joke)

    def _on_facts_clicked(self):
        fact = self.core.get_random_fact()
        self._insert_bot_message(fact)
        if self.tts.enabled:
            self.tts.speak(fact)

    # -----------------------
    # Theme options animation & actions
    # -----------------------
    def _toggle_theme_options(self):
        if self.animation_running:
            return
        if not self.theme_visible:
            self._show_theme_buttons()
        else:
            self._hide_theme_buttons()

    def _show_theme_buttons(self):
        cont = self.theme_container
        cont.update()
        w = cont.winfo_width() or cont.winfo_reqwidth() or 200
        start_x = -160
        target_x = 12  # left aligned
        y_positions = {"Light": 8, "Dark": 40, "Blue": 72}
        for name, btn in self.theme_btns.items():
            btn.place(x=start_x, y=y_positions[name], width=100)
        self.theme_visible = True
        self.animation_running = True
        def animate(step=0):
            if step > 20:
                for name, btn in self.theme_btns.items():
                    btn.place(x=target_x, y=y_positions[name], width=100)
                self.animation_running = False
                return
            frac = step / 20.0
            cur_x = int(start_x + (target_x - start_x) * frac)
            for name, btn in self.theme_btns.items():
                btn.place(x=cur_x, y=y_positions[name])
            step += 1
            self.after(12, lambda: animate(step))
        animate(0)

    def _hide_theme_buttons(self):
        if self.animation_running:
            return
        cont = self.theme_container
        cont.update()
        w = cont.winfo_width() or cont.winfo_reqwidth() or 200
        start_x = 12
        target_x = -160
        y_positions = {"Light": 8, "Dark": 40, "Blue": 72}
        self.animation_running = True
        def animate(step=0):
            if step > 20:
                for name, btn in self.theme_btns.items():
                    btn.place_forget()
                self.theme_visible = False
                self.animation_running = False
                return
            frac = step / 20.0
            cur_x = int(start_x + (target_x - start_x) * frac)
            for name, btn in self.theme_btns.items():
                btn.place(x=cur_x, y=y_positions[name])
            step += 1
            self.after(12, lambda: animate(step))
        animate(0)

    # -----------------------
    # Riddle actions
    # -----------------------
    def _on_riddles_clicked(self):
        reply, meta = self.core.get_reply("riddles")
        self._insert_bot_message(reply)
        if self.tts.enabled:
            self.tts.speak(reply)
        if meta.get('riddle_question'):
            self._insert_bot_message("(Type your answer directly in the input box. Type 'skip' to get the answer.)")

    # -----------------------
    # Add content handlers
    # -----------------------
    def _add_as_joke(self):
        text = self.add_entry.get().strip()
        if not text:
            messagebox.showinfo("Add Joke", "Please enter text to add as a joke.")
            return
        append_line_to_file(JOKES_FILE, text)
        self.core.jokes.append(text)
        self.add_entry.delete(0, tk.END)
        messagebox.showinfo("Add Joke", "Added to jokes")

    def _add_as_fact(self):
        text = self.add_entry.get().strip()
        if not text:
            messagebox.showinfo("Add Fact", "Please enter text to add as a fact.")
            return
        append_line_to_file(FACTS_FILE, text)
        self.core.facts.append(text)
        self.add_entry.delete(0, tk.END)
        messagebox.showinfo("Add Fact", "Added to facts")

    # -----------------------
    # Clear screen & manual
    # -----------------------
    def _clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state="disabled")
        self._insert_bot_message("Screen cleared. Type anything to continue.")

    def _show_manual(self):
        manual_text = (
            "pythonChatbot - User Manual\n\n"
            "Basic usage:\n"
            "- Type common greetings like 'hello', 'how are you', 'bye'.\n"
            "- Type 'riddles' or press the 'Riddles' button to get a riddle.\n"
            "- Type your answer to the riddle directly into the input. Type 'skip' to see the answer.\n"
            "- Use 'Categories' -> reveal 'Jokes' and 'Facts' buttons.\n"
            "- Click 'Jokes' to get a random joke, 'Facts' to get a random fact.\n"
            "- Use 'Add Content' to append new entries for jokes and facts\n\n"
            "- Program opens fullscreen on start. Press Escape or 'Toggle Fullscreen' to exit fullscreen.\n"
            "- 'Exit' button closes the program.\n"
            "- 'Clear Screen' clears chat history.\n"
            "- 'Theme' button animates theme options (Light/Dark/Blue). Choose one to apply.\n"
            "- Voice: Toggle 'Voice' to enable/disable text-to-speech.\n\n"
            "- Have fun!"
        )
        # show in a popup Toplevel
        top = tk.Toplevel(self)
        top.title("User Manual")
        # size and center small
        top.geometry("600x420")
        txt = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=self.font_text)
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert(tk.END, manual_text)
        txt.configure(state="disabled")

    # -----------------------
    # Clear & Exit already defined
    # -----------------------

# ---------------------------
# Run the app
# ---------------------------
def main():
    app = ChatbotGUI()
    # Centering isn't necessary since fullscreen, but ensure window update for some platforms:
    app.update_idletasks()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
