from typing import List, Tuple
import tkinter as tk
from tkinter import Toplevel, ttk, Text, Entry, Scrollbar


class Console:
    """
    A class to represent a console for displaying messages and errors.
    """

    def __init__(self, js_ctx=None):
        self.js_ctx = js_ctx
        self.messages: List[Tuple[str, str]] = [
            ("Console initialized.", "Ready to accept commands.")
        ]

    def open(self, parent, title="Console"):
        parent = parent
        self.dialog = Toplevel(parent)
        self.dialog.title(title[:30] + "..." if len(title) > 30 else title)
        self.dialog.geometry("600x400")
        self.dialog.minsize(400, 300)
        self.dialog.resizable(True, True)

        self.draw()

    def draw(self):
        self.frame = ttk.Frame(self.dialog, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.entry = Entry(self.frame)
        self.entry.pack(fill="x", pady=5, padx=2)
        self.entry.bind("<Return>", self.handle_command)
        self.entry.focus()

        self.text_area = Text(
            self.frame, wrap="word", yscrollcommand=self.scrollbar.set, state="disabled"
        )
        self.text_area.pack(fill="both", expand=True, padx=2, pady=2)
        self.scrollbar.configure(command=self.text_area.yview)

        for cmd, output in self.messages:
            self._write(cmd, output)

    def _write(self, message: str, output: str):
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.insert(tk.END, output + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def handle_command(self, event):
        cmd = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not cmd:
            return

        output = None

        if cmd.startswith("clear"):
            if cmd != "clear()":
                output = "Invalid command. Use 'clear()' to clear the console."
            else:
                self.messages.clear()
                self.text_area.configure(state="normal")
                self.text_area.delete("1.0", tk.END)
                self.text_area.config(state="disabled")

        elif self.js_ctx is not None:
            try:
                self.js_ctx.run("", cmd)
                if self.js_ctx.result is None:
                    output = "undefined"
                else:
                    output = self.js_ctx.result
            except Exception as e:
                output = f"Unknown command: {cmd}\nError: {e}"
        else:
            output = "JavaScript context not available."

        if output is not None:
            self._write(f"> {cmd}", str(output))
