# Text Adventure Game --- Game Module ---

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import sys
import builtins

# ---- ANSI/Colorama → Tk Text tagging bridge ---------------------------------
ANSI_ESC = "\x1b["
ANSI_END = "m"

ANSI_TO_TAG = {
    # We'll map bright + fore colors to tags; background white is default UI bg.
    ("1", "33"): "BOLD_YELLOW",   # Style.BRIGHT + Fore.YELLOW
    ("1", "36"): "BOLD_CYAN",     # Style.BRIGHT + Fore.CYAN
    ("1", "31"): "BOLD_RED",      # Style.BRIGHT + Fore.RED
    ("1", "35"): "BOLD_MAGENTA",  # Style.BRIGHT + Fore.MAGENTA
}

RESET_CODES = {"0"}  # Style.RESET_ALL

def configure_tags(text: ScrolledText):
    text.tag_configure("BOLD_YELLOW", foreground="#C5A100", font=("TkDefaultFont", 10, "bold"))
    text.tag_configure("BOLD_CYAN", foreground="#008B8B", font=("TkDefaultFont", 10, "bold"))
    text.tag_configure("BOLD_RED", foreground="#B00020", font=("TkDefaultFont", 10, "bold"))
    text.tag_configure("BOLD_MAGENTA", foreground="#8E24AA", font=("TkDefaultFont", 10, "bold"))

class TextRedirector:
    def __init__(self, text_widget: ScrolledText):
        self.text = text_widget
        self.current_tag = None
        self._buffer = ""

    def write(self, s: str):
        if not s:
            return
        # Buffer and schedule parsing on the Tk thread
        self._buffer += s
        self.text.after(0, self._drain)

    def _drain(self):
        s = self._buffer
        self._buffer = ""
        i = 0
        while i < len(s):
            esc = s.find(ANSI_ESC, i)
            if esc == -1:
                self._insert(s[i:], self.current_tag)
                break
            # Insert text up to the escape
            if esc > i:
                self._insert(s[i:esc], self.current_tag)
            # Parse escape sequence
            end = s.find(ANSI_END, esc)
            if end == -1:
                # malformed; just insert rest
                self._insert(s[esc:], self.current_tag)
                break
            seq = s[esc + len(ANSI_ESC):end]  # e.g., "1;33" or "0"
            codes = set(seq.split(";"))
            if codes & RESET_CODES:
                self.current_tag = None
            else:
                # Map a couple common combos we use
                if "1" in codes:  # bright
                    if "33" in codes:
                        self.current_tag = "BOLD_YELLOW"
                    elif "36" in codes:
                        self.current_tag = "BOLD_CYAN"
                    elif "31" in codes:
                        self.current_tag = "BOLD_RED"
                    elif "35" in codes:
                        self.current_tag = "BOLD_MAGENTA"
            i = end + 1

    def _insert(self, text, tag):
        self.text.insert(tk.END, text, tag)
        self.text.see(tk.END)

    def flush(self):
        pass

# ---- Terminal-style input hooked to Entry -----------------------------------
class TkInput:
    def __init__(self, text_widget: ScrolledText, entry: tk.Entry, send_button: tk.Button):
        self.text = text_widget
        self.entry = entry
        self.send_button = send_button
        self.queue = queue.Queue()
        self.entry.bind("<Return>", self._on_submit)
        self.send_button.config(command=self._on_submit)

    def _on_submit(self, event=None):
        value = self.entry.get()
        self.entry.delete(0, tk.END)
        self.queue.put(value)

    def input(self, prompt=""):
        if prompt:
            print(prompt, end="")
        value = self.queue.get()  # block until user hits Enter
        print(value + "\n")
        return value

# ---------------------- YOUR GAME, UPDATED WITH COLORAMA ----------------------
def game_main():
    from colorama import Fore, Back, Style  # ok to import here for constants

    score = 0  # local score tracked inside game_main

    def showScore():
        nonlocal score
        print(Fore.YELLOW + Back.WHITE + Style.BRIGHT + f"\t[Current Score: {score}]" + Style.RESET_ALL)
        print(Fore.CYAN + Back.WHITE + Style.BRIGHT + "" + Style.RESET_ALL)

    def endScore():
        nonlocal score
        print(Fore.YELLOW + Back.WHITE + Style.BRIGHT + f"\n    Your final score: \n\t{score} points" + Style.RESET_ALL)
        print(Fore.RED + Back.WHITE + Style.BRIGHT + "\n\tGame Over!!!" + Style.RESET_ALL)

    def continueToNext():
        print()
        input(Fore.CYAN + Back.WHITE + Style.BRIGHT + "\t<--- Tap Enter to Continue --->" + Style.RESET_ALL)
        print()

    def theBadEnd():
        print()
        print("Your choice had led you to a beast much greater than your skill, you could not win... Goodbye")
        print(Fore.RED + Back.WHITE + Style.BRIGHT + "\n\tYOU LOSE!!!" + Style.RESET_ALL)
        endScore()
        raise SystemExit

    def didNotAdventure():
        print()
        print("You chosen to not adventure to a new land, Your home was crushed by an astroid. You failed to survive!")
        print(Fore.RED + Back.WHITE + Style.BRIGHT + "\n\tYOU LOSE!!!" + Style.RESET_ALL)
        endScore()
        raise SystemExit

    def surviveAdventure():
        print()
        print("You have managed to survive in this new world. Enjoy your new Home!")
        print(Fore.RED + Back.WHITE + Style.BRIGHT + "\n\tYOU WIN!!!" + Style.RESET_ALL)
        endScore()
        raise SystemExit

    def getYesNo(question):
        while True:
            try:
                choice = input(question).strip().casefold()
                if choice in ("y", "n"):
                    return choice
                else:
                    print("Please enter 'y' or 'n'.")
            except Exception as e:
                print(f"Error: {e}. Try again.")

    def getOption(question, options):
        options_lower = [o.casefold() for o in options]
        while True:
            try:
                choice = input(question).strip().casefold()
                if choice in options_lower:
                    return choice
                else:
                    print(f"Please choose one of: {', '.join(options)}")
            except Exception as e:
                print(f"Error: {e}. Try again.")

    print(Fore.MAGENTA + Back.WHITE + Style.BRIGHT + "█▓▒░░ Welcome to: Reborn in a New World ░░▒▓█" + Style.RESET_ALL)
    continueToNext()

    print("The world fades to black and suddenly a bright light appears. Your eyes open and you awaken to a new world.")
    print("You have been Reborn! You are now in a world called Faefolk, a world of magic and must survive. You have some choice to make before you can start.")
    continueToNext()
    showScore()

    chooseAName = getYesNo("Do you want to pick a name? (y/n): ")

    if chooseAName == "n":
        print(" You ignored the naming process, a storm starts to brew outside...")
        print()
        didNotAdventure()
    elif chooseAName != "y":
        print()
        print("That doesn't make any sense but a storm has brewed outside...")
        didNotAdventure()
    else:
        print()
        print("You have chosen to select a name!")
        faeName = input("What shall your name be? : ").strip()
        if not faeName:
            faeName = "Nameless One"
        print()
        print(f"Welcome to Faefolk world of magic {str(faeName)}!")
        continueToNext()
        score += 10
        showScore()

        faeSkillChoice = getOption("Now you must choose your life skill.(Magic or Sword): ", ["magic", "sword"])
        if faeSkillChoice == "magic":
            print()
            print("You are have chosen the Magician class")
            continueToNext()
            score += 20
            showScore()
        elif faeSkillChoice == "sword":
            print()
            print("You have chosen the Warrior class")
            continueToNext()
            score += 20
            showScore()

    print(f"Now that you have chosen the name {str(faeName)} and the {str(faeSkillChoice)} class, it is time to set of on your Adventure to explore the world")
    continueToNext()
    showScore()

    print()
    print("You leave the house you were reborn into, there is a fork in the road going East and West.")
    print()

    chooseThePath = getOption("Will you travel East or West or Home?: ", ["east", "west", "Home"])

    if chooseThePath == "east":
        print("You have chosen to go East to the Forest.")
        continueToNext()
        score += 50
        showScore()
    elif chooseThePath == "west":
        print("You have chosen to go west into the dark cave")
        print()
        score -= 500
        showScore()
        theBadEnd()
    else:
        print()
        score -= 1000
        showScore()
        didNotAdventure()

    print(" You have made it to the forest where a small monster appears")
    fightToLive = getYesNo("Do you stay and fight? (y/n): ")

    if fightToLive == "n":
        print("You fleed and ended up in the dark cave...")
        score -= 500
        showScore()
        theBadEnd()
    elif fightToLive == "y":
        if faeSkillChoice == "magic":
            print()
            print(f"You have chosen to stay and fight! You use your {faeSkillChoice} and shoot a fireball")
            score += 200
            showScore()
            continueToNext()
        else:
            print()
            print(f"You have chosen to stay and fight! You use your {faeSkillChoice} and lunge with a big swing of your sword")
            continueToNext()
            score += 200
            showScore()

    print("You have made a direct hit and the monster is dead. You escape the forest and make it to the Village")
    continueToNext()
    score += 1000
    surviveAdventure()

# -------------------------- App wiring / UI -----------------------------------
def start_game():
    start_btn.config(state=tk.DISABLED)
    clear_btn.config(state=tk.DISABLED)

    def runner():
        try:
            game_main()
        except SystemExit:
            print("\n[Game ended]\n")
        except Exception as e:
            print(f"\n[Error] {e}\n")
        finally:
            root.after(0, lambda: (start_btn.config(state=tk.NORMAL), clear_btn.config(state=tk.NORMAL)))

    threading.Thread(target=runner, daemon=True).start()

def clear_terminal():
    terminal.config(state=tk.NORMAL)
    terminal.delete("1.0", tk.END)
    terminal.config(state=tk.NORMAL)

root = tk.Tk()
root.title("Reborn in a New World — Tk Terminal")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

terminal = ScrolledText(frame, wrap=tk.WORD, height=24, width=90)
terminal.pack(fill="both", expand=True)

configure_tags(terminal)

input_row = tk.Frame(frame)
input_row.pack(fill="x", pady=(8, 0))

entry = tk.Entry(input_row)
entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

send_btn = tk.Button(input_row, text="Enter")
send_btn.pack(side="right")

buttons = tk.Frame(frame)
buttons.pack(fill="x", pady=(8, 0))

start_btn = tk.Button(buttons, text="Start / Restart Game", command=start_game)
start_btn.pack(side="left")

clear_btn = tk.Button(buttons, text="Clear", command=clear_terminal)
clear_btn.pack(side="left", padx=8)

# Redirect stdout/stderr and patch input()
redir = TextRedirector(terminal)
sys.stdout = redir
sys.stderr = redir

tk_input = TkInput(terminal, entry, send_btn)
builtins.input = tk_input.input

entry.focus_set()
root.mainloop()
