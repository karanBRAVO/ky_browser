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

    def __init__(self):
        self.window = Tk()
        self.window.title("Ky Browser")
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        self.canvas = Canvas(
            self.window, width=self.WIDTH, height=self.HEIGHT, background="black"
        )
        self.canvas.pack(fill="both", expand=True)

        self.v_scroll = 0
        self.h_scroll = 0
        self.url = ""
        self.display_list = []
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        self.content = ""
        self.mediaType = "text/plain"
        self.font = font.Font(
            family="FiraCode Nerd Font Mono",
            size=14,
            weight="normal",
            slant="roman",
        )
        # print(font.families())  # all available fonts

        self.window.bind("<Left>", self.scrollleft)
        self.window.bind("<Right>", self.scrollright)
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)
        self.window.bind("<Button-4>", self.scrollup)
        self.window.bind("<Button-5>", self.scrolldown)
        self.canvas.bind("<Configure>", self.configure)

    def configure(self, event):
        self.WIDTH = event.width
        self.HEIGHT = event.height
        self.parse()
        self.draw()

    def mousewheel(self, event):
        if self.OS == "WINDOWS":
            self.v_scroll += -(event.delta // 120) * self.SCROLL_STEP
        elif self.OS == "LINUX":
            self.v_scroll += -event.delta * self.SCROLL_STEP
        self.draw()

    def scrollleft(self, event):
        self.h_scroll -= self.SCROLL_STEP
        self.draw()

    def scrollright(self, event):
        self.h_scroll += self.SCROLL_STEP
        self.draw()

    def scrolldown(self, event):
        self.v_scroll += self.SCROLL_STEP
        self.draw()

    def scrollup(self, event):
        self.v_scroll -= self.SCROLL_STEP
        self.draw()

    def load(self, url):
        self.url = url
        self.content, self.mediaType = URL(url).request()

    def parse(self):
        self.display_list.clear()
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP
        if not self.content or not self.url:
            return
        if self.mediaType == "text/html":
            root = HTMLParser(self.content).parse()
            if self.url.startswith("view-source:"):
                self.recurse(root, view_source=True)
            else:
                self.recurse(root, view_source=False, indent=self.HSTEP)
        else:
            self.layout(self.content)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, char, color in self.display_list:
            if y > self.v_scroll + self.HEIGHT or y + self.VSTEP < self.v_scroll:
                continue
            self.canvas.create_text(
                x - self.h_scroll,
                y - self.v_scroll,
                text=char,
                font=self.font,
                anchor="nw",
                fill=color,
            )

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

        if self.mediaType == "text/html" and view_source:
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
        if self.mediaType == "text/html" and view_source:
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
