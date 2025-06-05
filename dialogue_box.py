import tkinter as tk
from tkinter import ttk


class DialogBox:
    def __init__(
        self,
        parent,
        title="Input Dialog",
        label1="Name",
        value1="",
        label2="URL",
        value2="",
        on_submit=None,
    ):
        self.result = None
        self.on_submit = on_submit

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        ttk.Label(self.dialog, text=label1).grid(
            row=0, column=0, padx=10, pady=5, sticky="e"
        )
        ttk.Label(self.dialog, text=label2).grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )

        self.entry1 = ttk.Entry(self.dialog, width=40)
        self.entry1.insert(0, value1)
        self.entry2 = ttk.Entry(self.dialog, width=40)
        self.entry2.insert(0, value2)

        self.entry1.grid(row=0, column=1, padx=10, pady=5)
        self.entry2.grid(row=1, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ok_btn = ttk.Button(button_frame, text="OK", command=self._ok)
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        ok_btn.pack(side="left", padx=5)
        cancel_btn.pack(side="left", padx=5)

        self.entry1.focus()

    def _ok(self):
        name = self.entry1.get().strip()
        url = self.entry2.get().strip()
        if self.on_submit:
            self.on_submit(name, url)
        self.dialog.destroy()

    def _cancel(self):
        self.dialog.destroy()
