from tkinter import Tk, Canvas, font
from url import URL, lex
from html_parser import HTMLParser
from nodes import Document, DocumentType, Element, Text, Comment


class Browser:
    WIDTH = 800
    HEIGHT = 500
    SCROLL_STEP = 100
    HSTEP, VSTEP = 13, 18
    OS = "WINDOWS"  # or "LINUX", "MACOS"

    # Scrollbar settings
    MIN_V_SCROLL, MIN_H_SCROLL = 0, 0
    SCROLLBAR_WIDTH = 15
    SCROLLBAR_COLOR = "#444444"
    SCROLLBAR_THUMB_COLOR = "#888888"
    SCROLLBAR_THUMB_HOVER_COLOR = "#AAAAAA"

    def __init__(self):
        self.window = Tk()
        self.window.title("Ky Browser")
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.canvas = Canvas(
            self.window, width=self.WIDTH, height=self.HEIGHT, background="black"
        )
        self.canvas.pack(fill="both", expand=True)

        # scrollbar
        self.v_scroll = 0
        self.h_scroll = 0
        self.MAX_V_SCROLL = 0
        self.MAX_H_SCROLL = 0

        # content
        self.url = ""
        self.content = ""
        self.mediaType = "text/plain"

        # layout
        self.display_list = []
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        self.font = font.Font(
            family="FiraCode Nerd Font Mono",
            size=14,
            weight="normal",
            slant="roman",
        )

        # Scrollbar dragging state
        self.dragging_v_scrollbar = False
        self.dragging_h_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_x = 0
        self.drag_start_scroll = 0

        self.window.bind("<Left>", self.scroll_left)
        self.window.bind("<Right>", self.scroll_right)
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("<MouseWheel>", self.mouse_wheel)
        self.window.bind("<Button-4>", self.scroll_up)
        self.window.bind("<Button-5>", self.scroll_down)
        self.canvas.bind("<Configure>", self.configure)

        # Mouse events for scrollbar interaction
        self.canvas.bind("<Button-1>", self.on_scrollbar_click)
        self.canvas.bind("<B1-Motion>", self.on_scrollbar_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_scrollbar_release)
        self.canvas.bind("<Motion>", self.on_scrollbar_hover)

    def configure(self, event):
        self.WIDTH = event.width
        self.HEIGHT = event.height
        self.parse()
        self.draw()

    def mouse_wheel(self, event):
        if self.OS == "WINDOWS":
            scroll_direction = -(event.delta // 120)
            scroll_step = scroll_direction * self.SCROLL_STEP
            if scroll_direction > 0:
                if self.v_scroll + scroll_step > self.MAX_V_SCROLL:
                    self.v_scroll = self.MAX_V_SCROLL
                else:
                    self.v_scroll += scroll_step
            else:
                if self.v_scroll + scroll_step < self.MIN_V_SCROLL:
                    self.v_scroll = self.MIN_V_SCROLL
                else:
                    self.v_scroll += scroll_step
        self.draw()

    def scroll_left(self, event):
        if self.h_scroll - self.SCROLL_STEP < self.MIN_H_SCROLL:
            self.h_scroll = self.MIN_H_SCROLL
        else:
            self.h_scroll -= self.SCROLL_STEP
        self.draw()

    def scroll_right(self, event):
        if self.h_scroll + self.SCROLL_STEP > self.MAX_H_SCROLL:
            self.h_scroll = self.MAX_H_SCROLL
        else:
            self.h_scroll += self.SCROLL_STEP
        self.draw()

    def scroll_down(self, event):
        if self.v_scroll + self.SCROLL_STEP > self.MAX_V_SCROLL:
            self.v_scroll = self.MAX_V_SCROLL
        else:
            self.v_scroll += self.SCROLL_STEP
        self.draw()

    def scroll_up(self, event):
        if self.v_scroll - self.SCROLL_STEP < self.MIN_V_SCROLL:
            self.v_scroll = self.MIN_V_SCROLL
        else:
            self.v_scroll -= self.SCROLL_STEP
        self.draw()

    def get_v_scrollbar_bounds(self):
        if self.MAX_V_SCROLL <= 0:
            return None

        # Scrollbar track area
        track_x = self.WIDTH - self.SCROLLBAR_WIDTH
        track_y = 0
        track_width = self.SCROLLBAR_WIDTH
        track_height = self.HEIGHT - (
            self.SCROLLBAR_WIDTH if self.MAX_H_SCROLL > 0 else 0
        )

        # Scrollbar thumb (the draggable part)
        content_height = self.MAX_V_SCROLL + self.HEIGHT
        thumb_height = max(20, int((self.HEIGHT / content_height) * track_height))
        thumb_y = (
            int((self.v_scroll / self.MAX_V_SCROLL) * (track_height - thumb_height))
            if self.MAX_V_SCROLL > 0
            else 0
        )

        return {
            "track": (track_x, track_y, track_width, track_height),
            "thumb": (track_x, thumb_y, track_width, thumb_height),
        }

    def get_h_scrollbar_bounds(self):
        if self.MAX_H_SCROLL <= 0:
            return None

        # Scrollbar track area
        track_x = 0
        track_y = self.HEIGHT - self.SCROLLBAR_WIDTH
        track_width = self.WIDTH - (
            self.SCROLLBAR_WIDTH if self.MAX_V_SCROLL > 0 else 0
        )
        track_height = self.SCROLLBAR_WIDTH

        # Scrollbar thumb (the draggable part)
        content_width = self.MAX_H_SCROLL + self.WIDTH
        thumb_width = max(20, int((self.WIDTH / content_width) * track_width))
        thumb_x = (
            int((self.h_scroll / self.MAX_H_SCROLL) * (track_width - thumb_width))
            if self.MAX_H_SCROLL > 0
            else 0
        )

        return {
            "track": (track_x, track_y, track_width, track_height),
            "thumb": (thumb_x, track_y, thumb_width, track_height),
        }

    def is_point_in_rect(self, x, y, rect_x, rect_y, rect_width, rect_height):
        return (
            rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height
        )

    def on_scrollbar_click(self, event):
        # Check vertical scrollbar
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]
            if self.is_point_in_rect(
                event.x, event.y, thumb_x, thumb_y, thumb_width, thumb_height
            ):
                self.dragging_v_scrollbar = True
                self.drag_start_y = event.y
                self.drag_start_scroll = self.v_scroll
                return

            # Click on track (but not thumb) - jump to position
            track_x, track_y, track_width, track_height = v_bounds["track"]
            if self.is_point_in_rect(
                event.x, event.y, track_x, track_y, track_width, track_height
            ):
                # Calculate new scroll position based on click position
                relative_y = event.y - track_y
                scroll_ratio = relative_y / track_height
                new_scroll = int(scroll_ratio * self.MAX_V_SCROLL)
                self.v_scroll = max(
                    self.MIN_V_SCROLL, min(self.MAX_V_SCROLL, new_scroll)
                )
                self.draw()
                return

        # Check horizontal scrollbar
        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]
            if self.is_point_in_rect(
                event.x, event.y, thumb_x, thumb_y, thumb_width, thumb_height
            ):
                self.dragging_h_scrollbar = True
                self.drag_start_x = event.x
                self.drag_start_scroll = self.h_scroll
                return

            # Click on track (but not thumb) - jump to position
            track_x, track_y, track_width, track_height = h_bounds["track"]
            if self.is_point_in_rect(
                event.x, event.y, track_x, track_y, track_width, track_height
            ):
                # Calculate new scroll position based on click position
                relative_x = event.x - track_x
                scroll_ratio = relative_x / track_width
                new_scroll = int(scroll_ratio * self.MAX_H_SCROLL)
                self.h_scroll = max(
                    self.MIN_H_SCROLL, min(self.MAX_H_SCROLL, new_scroll)
                )
                self.draw()
                return

    def on_scrollbar_drag(self, event):
        if self.dragging_v_scrollbar:
            v_bounds = self.get_v_scrollbar_bounds()
            if v_bounds:
                track_x, track_y, track_width, track_height = v_bounds["track"]
                thumb_height = v_bounds["thumb"][3]

                # Calculate how much the mouse moved
                delta_y = event.y - self.drag_start_y

                # Convert mouse movement to scroll movement
                usable_track_height = track_height - thumb_height
                if usable_track_height > 0:
                    scroll_delta = (delta_y / usable_track_height) * self.MAX_V_SCROLL
                    new_scroll = self.drag_start_scroll + scroll_delta
                    self.v_scroll = max(
                        self.MIN_V_SCROLL, min(self.MAX_V_SCROLL, int(new_scroll))
                    )
                    self.draw()

        elif self.dragging_h_scrollbar:
            h_bounds = self.get_h_scrollbar_bounds()
            if h_bounds:
                track_x, track_y, track_width, track_height = h_bounds["track"]
                thumb_width = h_bounds["thumb"][2]

                # Calculate how much the mouse moved
                delta_x = event.x - self.drag_start_x

                # Convert mouse movement to scroll movement
                usable_track_width = track_width - thumb_width
                if usable_track_width > 0:
                    scroll_delta = (delta_x / usable_track_width) * self.MAX_H_SCROLL
                    new_scroll = self.drag_start_scroll + scroll_delta
                    self.h_scroll = max(
                        self.MIN_H_SCROLL, min(self.MAX_H_SCROLL, int(new_scroll))
                    )
                    self.draw()

    def on_scrollbar_release(self, event):
        self.dragging_v_scrollbar = False
        self.dragging_h_scrollbar = False

    def on_scrollbar_hover(self, event):
        cursor = "arrow"

        # Check if hovering over scrollbars
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]
            track_x, track_y, track_width, track_height = v_bounds["track"]
            if self.is_point_in_rect(
                event.x, event.y, thumb_x, thumb_y, thumb_width, thumb_height
            ) or self.is_point_in_rect(
                event.x, event.y, track_x, track_y, track_width, track_height
            ):
                cursor = "hand2"

        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]
            track_x, track_y, track_width, track_height = h_bounds["track"]
            if self.is_point_in_rect(
                event.x, event.y, thumb_x, thumb_y, thumb_width, thumb_height
            ) or self.is_point_in_rect(
                event.x, event.y, track_x, track_y, track_width, track_height
            ):
                cursor = "hand2"

        self.canvas.config(cursor=cursor)

    def draw_scrollbars(self):
        # Draw vertical scrollbar
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            track_x, track_y, track_width, track_height = v_bounds["track"]
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]

            # Draw track
            self.canvas.create_rectangle(
                track_x,
                track_y,
                track_x + track_width,
                track_y + track_height,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )

            # Draw thumb
            self.canvas.create_rectangle(
                thumb_x,
                thumb_y,
                thumb_x + thumb_width,
                thumb_y + thumb_height,
                fill=self.SCROLLBAR_THUMB_COLOR,
                outline=self.SCROLLBAR_THUMB_COLOR,
            )

        # Draw horizontal scrollbar
        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            track_x, track_y, track_width, track_height = h_bounds["track"]
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]

            # Draw track
            self.canvas.create_rectangle(
                track_x,
                track_y,
                track_x + track_width,
                track_y + track_height,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )

            # Draw thumb
            self.canvas.create_rectangle(
                thumb_x,
                thumb_y,
                thumb_x + thumb_width,
                thumb_y + thumb_height,
                fill=self.SCROLLBAR_THUMB_COLOR,
                outline=self.SCROLLBAR_THUMB_COLOR,
            )

        # Draw corner piece if both scrollbars are present
        if v_bounds and h_bounds:
            corner_x = self.WIDTH - self.SCROLLBAR_WIDTH
            corner_y = self.HEIGHT - self.SCROLLBAR_WIDTH
            self.canvas.create_rectangle(
                corner_x,
                corner_y,
                corner_x + self.SCROLLBAR_WIDTH,
                corner_y + self.SCROLLBAR_WIDTH,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )

    def load(self, url):
        self.url = url
        self.content, self.mediaType = URL(url).request()

    def parse(self):
        self.display_list.clear()
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        if not self.content or not self.url:
            return
        if "text/html" in self.mediaType:
            root = HTMLParser(self.content).parse()
            if self.url.startswith("view-source:"):
                self.recurse(root, view_source=True)
            else:
                self.recurse(root, view_source=False, indent=self.HSTEP)
        else:
            self.layout(self.content)
        self._calc_max_scroll()
        self.draw()

    def _calc_max_scroll(self):
        effective_height = self.HEIGHT - (
            self.SCROLLBAR_WIDTH if self.MAX_H_SCROLL > 0 else 0
        )
        effective_width = self.WIDTH - (
            self.SCROLLBAR_WIDTH if self.MAX_V_SCROLL > 0 else 0
        )

        self.MAX_V_SCROLL = max(
            0,
            (
                self.display_list[-1][1]
                - effective_height
                + self.font.metrics()["linespace"]
                if self.display_list
                else 0
            ),
        )
        self.MAX_H_SCROLL = max(
            0,
            (
                max([x for x, _, _, _ in self.display_list]) - effective_width
                if self.display_list
                else 0
            ),
        )

    def draw(self):
        self.canvas.delete("all")

        # Calculate effective display area (excluding scrollbars)
        effective_width = self.WIDTH - (
            self.SCROLLBAR_WIDTH if self.MAX_V_SCROLL > 0 else 0
        )
        effective_height = self.HEIGHT - (
            self.SCROLLBAR_WIDTH if self.MAX_H_SCROLL > 0 else 0
        )

        for x, y, char, color in self.display_list:
            if y > self.v_scroll + effective_height or y + self.VSTEP < self.v_scroll:
                continue
            if x > self.h_scroll + effective_width or x < self.h_scroll:
                continue
            self.canvas.create_text(
                x - self.h_scroll,
                y - self.v_scroll,
                text=char,
                font=self.font,
                anchor="nw",
                fill=color,
            )

        # Draw scrollbars on top of content
        self.draw_scrollbars()

    def layout(self, text: str):
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            if c == "\n":
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
            self.display_list.append((cursor_x, cursor_y, c, "white"))
            cursor_x += self.HSTEP
            if cursor_x > self.WIDTH - self.HSTEP:
                cursor_x = self.HSTEP
                cursor_y += self.font.metrics()["linespace"] + self.VSTEP

    def _update_display_list(self, text: str, x: int, color: str):
        if not text:
            return

        self.cursor_x = x
        buffer = ""
        for i, char in enumerate(text):
            if char == "\n":
                self.cursor_x = x
                self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP
            elif char == " ":
                if buffer:
                    self.display_list.append(
                        (self.cursor_x, self.cursor_y, buffer, color)
                    )
                    self.cursor_x += self.font.measure(buffer)
                    j = text.find(" ", i + 1)
                    if j != -1:
                        next_word = text[i + 1 : j]
                        next_word_width = self.font.measure(next_word)
                        if self.cursor_x + next_word_width > self.WIDTH:
                            self.cursor_x = x
                            self.cursor_y += (
                                self.font.metrics()["linespace"] + self.VSTEP
                            )
                    buffer = ""
                if i < 1 or text[i - 1] != " ":
                    self.cursor_x += self.font.measure(" ")
            else:
                buffer += char
        if buffer:
            self.display_list.append((self.cursor_x, self.cursor_y, buffer, color))

    def recurse(self, root=None, view_source=False, indent=0):
        if root is None:
            return

        if "text/html" in self.mediaType and view_source:
            # DOCTYPE
            if isinstance(root, DocumentType):
                text = f"<!"
                prev_text = text
                self._update_display_list(text, indent, "white")
                text = "DOCTYPE "
                self._update_display_list(
                    text, indent + self.font.measure(prev_text), "red"
                )
                prev_text += text
                text = "HTML>"
                self._update_display_list(
                    text, indent + self.font.measure(prev_text), "white"
                )
                self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP
            # opening tags
            elif isinstance(root, Element):
                text = f"<"
                prev_text = text
                self._update_display_list(text, indent, "white")
                text = f"{root.tag}"
                self._update_display_list(
                    text, indent + self.font.measure(prev_text), "red"
                )
                # attributes
                for name, value in root.attributes.items():
                    prev_text += text
                    text = f" {name}="
                    self._update_display_list(
                        text,
                        indent + self.font.measure(prev_text),
                        "green",
                    )
                    prev_text += text
                    text = f'"{value}"'
                    self._update_display_list(
                        text,
                        indent + self.font.measure(prev_text),
                        "yellow",
                    )
                prev_text += text
                text = f"{' /' if root.selfClosing else ''}>"
                self._update_display_list(
                    text, indent + self.font.measure(prev_text), "white"
                )
                self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP
            # comments
            elif isinstance(root, Comment):
                text = f"<!-- {root.comment} -->"
                self._update_display_list(text, indent, "gray")
                self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP

        # text
        if isinstance(root, Text):
            text = root.text
            self._update_display_list(text, indent, "white")
            self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP

        # recurse children
        if isinstance(root, Document) or isinstance(root, Element):
            for child in root.children:
                self.recurse(
                    child, view_source, indent + self.HSTEP if view_source else indent
                )

        # closing tags
        if "text/html" in self.mediaType and view_source:
            if isinstance(root, Element):
                if not root.selfClosing:
                    text = f"</"
                    prev_text = text
                    self._update_display_list(text, indent, "white")
                    text = f"{root.tag}"
                    self._update_display_list(
                        text,
                        indent + self.font.measure(prev_text),
                        "red",
                    )
                    prev_text += text
                    text = f">"
                    self._update_display_list(
                        text,
                        indent + self.font.measure(prev_text),
                        "white",
                    )
                    self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP


if __name__ == "__main__":
    browser = Browser()
    # browser.load("https://browser.engineering/html.html")
    # browser.load("view-source:https://browser.engineering/html.html")
    # browser.load("view-source:http://localhost:5500/index.html")
    # browser.load("http://localhost:5500/index.html")
    browser.load("file:///E:/ky_browser/html_parser.py")
    # browser.load("data:text/html,<h1>Hello World!</h1>")
    # browser.load("https://example.org/index.html")
    browser.window.mainloop()
