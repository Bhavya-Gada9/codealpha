import tkinter as tk
import random

# ---------------- Word Lists and Hints ----------------
LEVEL_WORDS = {
    1: ["python", "developer", "computer", "hangman", "program","apple"],
    2: ["keyboard", "algorithm", "function", "variable", "internet",
        "syntax", "compiler", "software", "hardware", "database"],
    3: ["asynchronous", "polymorphism", "inheritance", "encapsulation",
        "abstraction", "multithreading", "concurrency", "optimization",
        "recursion", "serialization", "virtualization", "cryptography",
        "authentication", "authorization", "microservices"]
}
LEVEL_WORDS[1].extend(["table", "chair", "house", "train"])
LEVEL_WORDS[2].extend([
    "monitor", "printer", "package", "library", "storage", "network"
])


HINTS = {
    "PYTHON": "A popular programming language.",
    "APPLE": "A popular fruit that keeps the doctor away.",
    "DEVELOPER": "A person who writes code.",
    "COMPUTER": "Electronic device for processing data.",
    "HANGMAN": "The game you are playing!",
    "PROGRAM": "Set of instructions executed by a computer.",
    "KEYBOARD": "Input device with letters and keys.",
    "ALGORITHM": "Step-by-step problem-solving method.",
    "FUNCTION": "Reusable block of code in programming.",
    "VARIABLE": "Used to store data in programming.",
    "INTERNET": "Global network connecting computers.",
    "SYNTAX": "Rules for writing code.",
    "COMPILER": "Converts code into machine language.",
    "SOFTWARE": "Programs running on computers.",
    "HARDWARE": "Physical components of a computer.",
    "DATABASE": "Structured collection of data.",
    "ASYNCHRONOUS": "Execution not happening at the same time.",
    "POLYMORPHISM": "OOP concept: same interface, different forms.",
    "INHERITANCE": "OOP: child class gets features of parent.",
    "ENCAPSULATION": "OOP: keeping data safe inside class.",
    "ABSTRACTION": "OOP: showing only necessary details.",
    "MULTITHREADING": "Running multiple threads concurrently.",
    "CONCURRENCY": "Multiple tasks making progress at the same time.",
    "OPTIMIZATION": "Making code or process more efficient.",
    "RECURSION": "Function calls itself.",
    "SERIALIZATION": "Converting objects into data stream.",
    "VIRTUALIZATION": "Creating virtual versions of resources.",
    "CRYPTOGRAPHY": "Science of secure communication.",
    "AUTHENTICATION": "Verify identity of user.",
    "AUTHORIZATION": "Giving permissions to user.",
    "MICROSERVICES": "Small, independent services in an app.",
    "PRINTER": "Device used to print documents.",
    "PACKAGE": "Collection of modules or software components.",
    "LIBRARY": "Collection of code modules for reuse.",
    "STORAGE": "Place to save files or data.",
    "NETWORK": "Connected computers exchanging information."
}
HINTS.update({
    "APPLE": "A popular fruit that keeps the doctor away.",
    "TABLE": "Furniture used to place items on.",
    "CHAIR": "Something you sit on.",
    "HOUSE": "A place where people live.",
    "TRAIN": "A vehicle that runs on tracks."
})
# ---------------- Hangman Game Class ----------------
class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game 🎯")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#ADD8E6")

        # ---------------- UI Elements ----------------
        self.title_label = tk.Label(root, text="🎯 Hangman Game 🎯", font=("Comic Sans MS", 30, "bold"),
                                    bg="#ADD8E6", fg="#1A1A1A")
        self.title_label.pack(pady=30)

        self.level_label = tk.Label(root, text="Level: 1", font=("Arial", 20, "bold"),
                                    bg="#ADD8E6", fg="#000")
        self.level_label.pack(pady=5)

        self.word_label = tk.Label(root, text="", font=("Consolas", 32, "bold"),
                                   bg="#ADD8E6")
        self.word_label.pack(pady=20)

        self.message_label = tk.Label(root, text="", font=("Arial", 18),
                                      bg="#ADD8E6")
        self.message_label.pack(pady=10)

        self.buttons_frame = tk.Frame(root, bg="#ADD8E6")
        self.buttons_frame.pack(pady=10)

        self.control_frame = tk.Frame(root, bg="#ADD8E6")
        self.control_frame.pack(pady=30)

        # ---------------- Control Buttons ----------------
        self.reset_button = tk.Button(self.control_frame, text="🔄 Restart Game", font=("Arial", 16, "bold"),
                                      bg="#90EE90", width=15, command=self.reset_game)
        self.reset_button.grid(row=0, column=0, padx=10)

        self.exit_button = tk.Button(self.control_frame, text="❌ Exit Game", font=("Arial", 16, "bold"),
                                     bg="#FF6961", width=15, command=self.root.destroy)
        self.exit_button.grid(row=0, column=1, padx=10)

        self.manual_button = tk.Button(self.control_frame, text="📖 User Manual", font=("Arial", 16, "bold"),
                                       bg="#F39C12", width=15, command=self.show_manual)
        self.manual_button.grid(row=0, column=2, padx=10)

        self.hint_button = tk.Button(self.control_frame, text="💡 Hint", font=("Arial", 14, "bold"),
                                     bg="#F1C40F", width=12, command=self.show_hint)

        # ---------------- Game Variables ----------------
        self.level = 1
        self.correct_guess_counter = 0
        self.remaining_attempts = 6
        self.word = ""
        self.guessed = []
        self.guessed_letters = set()

        self.create_letter_buttons()
        self.start_game()

    # ---------------- Create Alphabet Buttons ----------------
    def create_letter_buttons(self):
        self.buttons = {}
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            button = tk.Button(self.buttons_frame, text=letter, font=("Arial", 14, "bold"),
                               width=4, height=2, bg="#FFD580",
                               command=lambda l=letter: self.guess_letter(l))
            row, col = divmod(i, 9)
            button.grid(row=row, column=col, padx=5, pady=5)
            self.buttons[letter] = button

    # ---------------- Start / Reset Game ----------------
    def start_game(self):
        self.word = random.choice(LEVEL_WORDS[self.level]).upper()
        self.guessed = ["_"] * len(self.word)
        self.guessed_letters.clear()
        self.remaining_attempts = 6
        self.update_ui()
        self.hide_extra_buttons()

        for btn in self.buttons.values():
            btn.config(state=tk.NORMAL, bg="#FFD580")

    def reset_game(self):
        self.level = 1
        self.correct_guess_counter = 0
        self.level_label.config(text=f"Level: {self.level}")
        self.start_game()

    # ---------------- Handle Guess ----------------
    def guess_letter(self, letter):
        if letter in self.guessed_letters:
            self.message_label.config(text=f"You already guessed '{letter}'!")
            return
        if self.remaining_attempts == 0:
            self.message_label.config(text="No attempts left! Click 'Next Word' to continue.")
            return

        self.guessed_letters.add(letter)

        if letter in self.word:
            for i, ch in enumerate(self.word):
                if ch == letter:
                    self.guessed[i] = letter
            self.word_label.config(text=" ".join(self.guessed))
            self.message_label.config(text=f"✅ '{letter}' is correct!")

            if "_" not in self.guessed:
                self.correct_guess_counter += 1
                self.check_level_up()
                for btn in self.buttons.values():
                    btn.config(state=tk.DISABLED)
                self.show_next_word_button(f"🎉 Congratulations! You guessed the word: {self.word}")
        else:
            if self.remaining_attempts > 0:
                self.remaining_attempts -= 1
            self.message_label.config(text=f"❌ Wrong guess! Attempts left: {self.remaining_attempts}")

            if self.remaining_attempts == 2:
                self.show_hint_button()

            if self.remaining_attempts == 0:
                for btn in self.buttons.values():
                    btn.config(state=tk.DISABLED)
                self.show_next_word_button(f"➡️ Word skipped! The word was: {self.word}")

        self.buttons[letter].config(state=tk.DISABLED, bg="#7F8C8D")

    # ---------------- Level Up Check ----------------
    def check_level_up(self):
        if self.correct_guess_counter >= 5 and self.level == 1:
            self.level = 2
            self.level_label.config(text=f"Level: {self.level}")
            self.message_label.config(text="🔥 Level Up! Welcome to Level 2")
        elif self.correct_guess_counter >= 15 and self.level == 2:
            self.level = 3
            self.level_label.config(text=f"Level: {self.level}")
            self.message_label.config(text="🚀 Level Up! Welcome to Level 3")

    # ---------------- Update UI ----------------
    def update_ui(self):
        self.word_label.config(text=" ".join(self.guessed))
        if "_" in self.guessed:
            self.message_label.config(text=f"Attempts left: {self.remaining_attempts}")

    # ---------------- Hint & Next Word Buttons ----------------
    def show_hint_button(self):
        self.hint_button.grid(row=0, column=3, padx=10)

    def hide_extra_buttons(self):
        self.hint_button.grid_forget()
        if hasattr(self, 'next_button') and self.next_button.winfo_exists():
            self.next_button.destroy()

    def show_hint(self):
        hint = HINTS.get(self.word, "No hint available")
        self.message_label.config(text=f"💡 Hint: {hint}")
        self.hint_button.grid_forget()

    def show_next_word_button(self, message):
        self.word_label.config(text=self.word)
        self.message_label.config(text=message)
        self.hide_extra_buttons()

        self.next_button = tk.Button(self.control_frame, text="▶️ Next Word", font=("Arial", 14, "bold"),
                                     bg="#3498DB", width=12, command=self.next_word)
        self.next_button.grid(row=0, column=4, padx=10)

    def next_word(self):
        if hasattr(self, 'next_button'):
            self.next_button.destroy()
        self.start_game()

    # ---------------- User Manual ----------------
    def show_manual(self):
        manual_window = tk.Toplevel(self.root)
        manual_window.title("User Manual")
        manual_window.geometry("600x500")
        manual_window.configure(bg="#FFEFD5")

        title = tk.Label(manual_window, text="🎯 Hangman Game - User Manual 🎯",
                         font=("Comic Sans MS", 20, "bold"), bg="#FFEFD5", fg="#000")
        title.pack(pady=20)

        instructions = (
            "1. The game starts at Level 1 with 5 words.\n"
            "2. Guess the word by clicking the letters.\n"
            "3. You have 6 attempts per word.\n"
            "4. If attempts reach 2, you can use the Hint button for a clue.\n"
            "5. If you cannot guess the word or want to skip, click the Next Word button.\n"
            "6. Correct guesses increase your score.\n"
            "7. After 5 correct words, you level up to Level 2.\n"
            "8. After 15 correct words, you level up to Level 3.\n"
            "9. Click 'Restart Game' to start over.\n"
            "10. Click 'Exit Game' to quit."
        )

        instruction_label = tk.Label(manual_window, text=instructions, font=("Arial", 14),
                                     bg="#FFEFD5", justify=tk.LEFT, wraplength=550)
        instruction_label.pack(padx=20, pady=10)

        close_button = tk.Button(manual_window, text="Close", font=("Arial", 14, "bold"),
                                 bg="#E74C3C", fg="white", width=10,
                                 command=manual_window.destroy)
        close_button.pack(pady=20)


# ---------------- Run App ----------------
if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()
