from tab import Tab
from dialogue_box import DialogBox
from utils import load_json
from tkinter import Tk, Canvas, ttk
from bookmarks_manager import BookmarksManager


class Browser:
    """
    A web browser that can render HTML and CSS content.
    """

    WIDTH, HEIGHT = 800, 500
    MIN_WIDTH, MIN_HEIGHT = 400, 300
    OS = "WINDOWS"  # or "LINUX", "MACOS"

    def __init__(self):
        self.window = Tk()
        self.window.title("Ky Browser")
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.resizable(True, True)
        self.window.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # browser styles
        style = ttk.Style()
        style.theme_use("xpnative")
        style.configure("Browser.TButton", padding=2, width=3, relief="flat")
        style.configure(
            "ActiveTab.TButton",
            padding=(8, 4),
            relief="sunken",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Browser.TEntry",
            padding=5,
            relief="flat",
            font=("Segoe UI", 11),
            borderwidth=2,
        )
        # Style for close button
        style.configure(
            "CloseTab.TButton",
            padding=1,
            width=2,
            relief="flat",
            font=("Segoe UI", 8),
        )
        style.configure(
            "Overlay.TFrame", background="white", relief="raised", borderwidth=2
        )
        style.configure("OverlayTop.TFrame", background="white")

        # ui
        self._setup_ui()

        # tabs
        self.current_tab_pointer = 0  # pointer to the current tab
        self.tabs: list[Tab] = []
        self.tab_buttons: list[ttk.Button] = []
        self.tab_frames: list[ttk.Frame] = []
        self.close_buttons: list[ttk.Button] = []
        self._add_tab()  # add the first tab

        # bookmarks manager
        self.bookmark_manager = BookmarksManager()

        # bind events
        self.canvas.bind("<Configure>", self._configure)
        self.window.bind("<Left>", self._left_key_press)
        self.window.bind("<Right>", self._right_key_press)
        self.window.bind("<Down>", self._down_key_press)
        self.window.bind("<Up>", self._up_key_press)
        self.window.bind("<MouseWheel>", self._mouse_wheel)
        self.window.bind("<Button-4>", self._button_4_press)
        self.window.bind("<Button-5>", self._button_5_press)
        self.canvas.bind("<Button-1>", self._button_1_press)
        self.canvas.bind("<B1-Motion>", self._b1_motion)
        self.canvas.bind("<ButtonRelease-1>", self._button_release_1)
        self.canvas.bind("<Motion>", self._motion)

        self._browser_shortcuts()

    def _browser_shortcuts(self):
        self.window.bind("<Control-t>", lambda _: self._add_tab())
        self.window.bind(
            "<Control-w>", lambda _: self._close_tab(self.current_tab_pointer)
        )
        self.window.bind(
            "<Control-Tab>",
            lambda _: self._switch_tab((self.current_tab_pointer + 1) % len(self.tabs)),
        )
        self.window.bind(
            "<Control-Shift-Tab>",
            lambda _: self._switch_tab((self.current_tab_pointer - 1) % len(self.tabs)),
        )
        self.window.bind("<Control-l>", lambda _: self._focus_url_entry())
        self.window.bind("<Control-r>", lambda _: self.load())
        self.window.bind("<F5>", lambda _: self.load())
        self.window.bind("<Escape>", lambda _: self._hide_overlay())
        self.window.bind("<Control-b>", lambda _: self._open_bookmark_pane())
        self.window.bind("<Control-d>", lambda _: self._add_new_bookmark())
        self.window.bind("<Control-/>", lambda _: self._open_shortcuts_pane())

    def _open_shortcuts_pane(self):
        self._toggle_overlay()
        self.overlay_label.configure(text="Shortcuts")

        self._clear_overlay_content()

        canvas = Canvas(self.overlay, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overlay, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        shortcuts_frame = ttk.Frame(canvas)
        shortcuts_frame.pack(fill="both", expand=True)
        canvas.create_window((0, 0), window=shortcuts_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        shortcuts_frame.bind("<Configure>", on_frame_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        shortcuts = load_json("shortcuts.json")
        if shortcuts is None or not shortcuts:
            no_shortcuts_label = ttk.Label(
                shortcuts_frame, text="No shortcuts found.", font=("Lucida Console", 12)
            )
            no_shortcuts_label.pack(pady=20)
        else:
            for i, (key, desc) in enumerate(shortcuts.items()):
                desc_label = ttk.Label(
                    shortcuts_frame, text=desc, font=("Segoe UI", 10)
                )
                key_label = ttk.Label(
                    shortcuts_frame, text=key, font=("Lucida Console", 10, "bold")
                )

                desc_label.grid(row=i, column=0, sticky="w", padx=(10, 30), pady=2)
                key_label.grid(row=i, column=1, sticky="e", padx=(0, 10), pady=2)

    def _clear_overlay_content(self):
        for widget in self.overlay.winfo_children():
            if widget not in {
                self.overlay_top_frame,
                self.overlay_close_btn,
                self.overlay_label,
            }:
                widget.destroy()

    def _add_new_bookmark(self):
        def on_submit(name, url):
            if name and url:
                self.bookmark_manager.save_bookmark(name, url)

        curr_title = self._current_tab().title
        curr_url = self._current_tab().url

        DialogBox(
            self.window,
            "Add Bookmark",
            "Name",
            curr_title,
            "URL",
            curr_url,
            on_submit=on_submit,
        )

    def _open_bookmark_pane(self):
        self._toggle_overlay()
        self.overlay_label.configure(text="Bookmark Pane")

        self._clear_overlay_content()

        canvas = Canvas(self.overlay, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.overlay, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bFrame = ttk.Frame(canvas)
        bFrame.pack(fill="both", expand=True)
        canvas.create_window((0, 0), window=bFrame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        bFrame.bind("<Configure>", on_frame_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        bookmarks = self.bookmark_manager.load_bookmarks()

        if not bookmarks:
            no_bookmarks_label = ttk.Label(
                bFrame, text="No bookmarks found.", font=("Segoe UI", 12)
            )
            no_bookmarks_label.pack(pady=20)
        else:
            for name, url in bookmarks.items():
                bookmark_btn = ttk.Button(
                    bFrame,
                    text=name[:10] + "..." if len(name) > 10 else name,
                    command=lambda u=url: self.load(u),
                )
                bookmark_url_label = ttk.Label(
                    bFrame,
                    text=url[:100] if len(url) > 100 else url,
                    font=("Segoe UI", 8),
                    foreground="blue",
                )
                bookmark_btn.pack(anchor="w", padx=10, pady=2)
                bookmark_url_label.pack(anchor="w", padx=10, pady=2)

    def _toggle_overlay(self):
        if self.overlay_visible:
            self._hide_overlay()
        else:
            self._show_overlay()

    def _show_overlay(self):
        self.overlay.lift()
        self.overlay_visible = True

    def _hide_overlay(self):
        self.overlay.lower()
        self.overlay_visible = False

    def _create_overlay(self):
        self.overlay = ttk.Frame(self.window, style="Overlay.TFrame", padding=10)

        self.overlay_top_frame = ttk.Frame(
            self.overlay, padding=5, style="OverlayTop.TFrame"
        )

        self.overlay_label = ttk.Label(
            self.overlay_top_frame,
            text="Overlay Content",
            font=("Segoe UI", 12),
            background="white",
        )

        self.overlay_close_btn = ttk.Button(
            self.overlay_top_frame,
            text="×",
            style="CloseTab.TButton",
            command=self._hide_overlay,
        )

        self._hide_overlay()

        self.overlay.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=self.WIDTH - 50,
            height=self.HEIGHT - 50,
        )
        self.overlay_top_frame.pack(fill="x")
        self.overlay_label.pack(side="left", padx=2, anchor="nw")
        self.overlay_close_btn.pack(side="right", padx=2, anchor="ne")

    def _update_overlay_dimensions(self):
        self.overlay.place_configure(width=self.WIDTH - 50, height=self.HEIGHT - 50)

    def _configure(self, event):
        self.WIDTH = event.width
        self.HEIGHT = event.height
        for tab in self.tabs:
            tab._update_screen_dimensions(self.WIDTH, self.HEIGHT)
        self._update_canvas()
        self._update_overlay_dimensions()

    def _mouse_wheel(self, event):
        if self.OS == "WINDOWS":
            scroll_direction = -(event.delta // 120)
            if scroll_direction > 0:
                self._current_tab().scroll_bar.scroll_down()
            else:
                self._current_tab().scroll_bar.scroll_up()

    def _left_key_press(self, event):
        self._current_tab().scroll_bar.scroll_left()

    def _right_key_press(self, event):
        self._current_tab().scroll_bar.scroll_right()

    def _down_key_press(self, event):
        self._current_tab().scroll_bar.scroll_down()

    def _up_key_press(self, event):
        self._current_tab().scroll_bar.scroll_up()

    def _button_4_press(self, event):
        self._current_tab().scroll_bar.scroll_up()

    def _button_5_press(self, event):
        self._current_tab().scroll_bar.scroll_down()

    def _button_1_press(self, event):
        self._current_tab().scroll_bar.scrollbar_click(event.x, event.y)

    def _b1_motion(self, event):
        self._current_tab().scroll_bar.scrollbar_drag(event.x, event.y)

    def _button_release_1(self, event):
        self._current_tab().scroll_bar.scrollbar_release()

    def _motion(self, event):
        self._current_tab().scroll_bar.scrollbar_hover(event.x, event.y, self.canvas)

    def _update_canvas(self):
        self._current_tab().parse()
        self._current_tab().draw()

    def _update_url_entry(self):
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, self._current_tab().url)

    def _focus_url_entry(self):
        self.url_entry.focus_set()
        self.url_entry.select_range(0, "end")

    def _add_tab(self):
        tab = Tab(self.WIDTH, self.HEIGHT, self.canvas)
        self.tabs.append(tab)

        # Create tab frame to hold both title button and close button
        tab_frame = ttk.Frame(self.tabbar)
        self.tab_frames.append(tab_frame)

        tab_index = len(self.tabs) - 1

        # Create tab title button
        tab_button = ttk.Button(
            tab_frame,
            text=tab.title,
            style="Tab.TButton",
            command=lambda idx=tab_index: self._switch_tab(idx),
        )

        # Create close button
        close_button = ttk.Button(
            tab_frame,
            text="×",
            style="CloseTab.TButton",
            command=lambda idx=tab_index: self._close_tab(idx),
        )

        self.tab_buttons.append(tab_button)
        self.close_buttons.append(close_button)

        # Pack buttons within the frame
        tab_button.pack(side="left")
        close_button.pack(side="left")

        # Pack the frame
        tab_frame.pack(side="left", padx=(0, 2))

        self.current_tab_pointer = tab_index
        self._update_tab_styles()
        self._update_url_entry()
        self.canvas.delete("all")

    def _close_tab(self, tab_index: int):
        if len(self.tabs) <= 1:
            self._add_tab()

        if 0 <= tab_index < len(self.tabs):
            # Remove the tab and its UI elements
            self.tabs.pop(tab_index)
            self.tab_buttons.pop(tab_index)
            self.close_buttons.pop(tab_index)

            # Destroy the tab frame
            tab_frame = self.tab_frames.pop(tab_index)
            tab_frame.destroy()

            # Adjust current tab pointer
            if tab_index <= self.current_tab_pointer:
                if self.current_tab_pointer > 0:
                    self.current_tab_pointer -= 1
                else:
                    self.current_tab_pointer = 0

            # Update tab button commands with new indices
            self._update_tab_commands()

            # Update UI
            self._update_tab_styles()
            self._update_canvas()
            self._update_url_entry()

    def _update_tab_commands(self):
        for i, (tab_button, close_button) in enumerate(
            zip(self.tab_buttons, self.close_buttons)
        ):
            tab_button.configure(command=lambda idx=i: self._switch_tab(idx))
            close_button.configure(command=lambda idx=i: self._close_tab(idx))

    def _switch_tab(self, tab_index):
        if 0 <= tab_index < len(self.tabs):
            self.current_tab_pointer = tab_index
            self._update_tab_styles()
            self._update_canvas()
            self._update_url_entry()

    def _update_tab_styles(self):
        for i, button in enumerate(self.tab_buttons):
            if i == self.current_tab_pointer:
                button.configure(style="ActiveTab.TButton")
            else:
                button.configure(style="Tab.TButton")

    def _update_tab_title(self, title: str):
        if title and self.current_tab_pointer < len(self.tab_buttons):
            title = title[:10] + "..." if len(title) > 10 else title
            self.tab_buttons[self.current_tab_pointer].configure(text=title)

    def _current_tab(self):
        return self.tabs[self.current_tab_pointer]

    def _setup_ui(self):
        self._create_canvas()
        self._create_navbar()
        self._create_tabbar()
        self._create_overlay()

        # pack the ui elements
        self.navbar.pack(fill="x")
        self.back_btn.pack(side="left", padx=2)
        self.forward_btn.pack(side="left", padx=2)
        self.reload_btn.pack(side="left", padx=2)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=2)
        self.go_btn.pack(side="left", padx=2)

        self.tabbar.pack(fill="x")
        self.new_tab_button.pack(side="left", padx=2)

        self.canvas.pack(fill="both", expand=True)

    def _create_canvas(self):
        self.canvas = Canvas(self.window, width=self.WIDTH, height=self.HEIGHT)

    def _create_tabbar(self):
        self.tabbar = ttk.Frame(self.window, padding=5)

        self.new_tab_button = ttk.Button(
            self.tabbar,
            text="+",
            style="Browser.TButton",
            command=self._add_tab,
        )

    def _create_navbar(self):
        self.navbar = ttk.Frame(self.window, padding=5)

        self.back_btn = ttk.Button(
            self.navbar,
            text="←",
            style="Browser.TButton",
            command=lambda: print(f"Back Button Pressed"),
        )

        self.forward_btn = ttk.Button(
            self.navbar,
            text="→",
            style="Browser.TButton",
            command=self.load,
        )

        self.reload_btn = ttk.Button(
            self.navbar,
            text="⟳",
            style="Browser.TButton",
            command=self.load,
        )

        self.url_entry = ttk.Entry(self.navbar, style="Browser.TEntry")
        self.url_entry.bind("<Return>", lambda event: self.load())

        self.go_btn = ttk.Button(
            self.navbar,
            text="Go",
            style="Browser.TButton",
            command=self.load,
        )

    def load(self, url=None):
        url = url if url is not None else self.url_entry.get()
        if url:
            self._current_tab().load(url)
            self._update_tab_title(self._current_tab().title)
            self._update_url_entry()


if __name__ == "__main__":
    browser = Browser()
    # browser.load("https://browser.engineering/styles.html")
    # browser.load("view-source:https://en.wikipedia.org/wiki/HTML")
    # browser.load("view-source:https://browser.engineering/html.html")
    # browser.load("view-source:http://localhost:5500/index.html")
    # browser.load("http://localhost:5500/index.html")
    # browser.load("file:///E:/ky_browser/html_parser.py")
    # browser.load("data:text/html,<h1>Hello World!</h1>")
    # browser.load("https://example.org/index.html")
    browser.window.mainloop()
