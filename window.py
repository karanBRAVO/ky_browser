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

        self.canvas = Canvas(self.window, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack(fill="both", expand=True)

        self.scroll = 0
        self.url = ""
        self.display_list = []
        self.cursor_y = self.VSTEP
        self.content = ""
        self.font = font.Font(
            family="JetBrainsMonoNL NFP SemiBold",
            size=14,
            weight="normal",
            slant="roman",
        )
        # print(font.families()) # all available fonts

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
            self.scroll += -(event.delta // 120) * self.SCROLL_STEP
        elif self.OS == "LINUX":
            self.scroll += -event.delta * self.SCROLL_STEP
        self.draw()

    def scrolldown(self, event):
        self.scroll += self.SCROLL_STEP
        self.draw()

    def scrollup(self, event):
        self.scroll -= self.SCROLL_STEP
        self.draw()

    def load(self, url):
        self.url = url
        self.content = URL(url).request()

    def parse(self):
        if not self.content or not self.url:
            return
        if self.url.startswith("view-source:"):
            self.layout(self.content)
        else:
            root = HTMLParser(self.content).parse()
            self.recurse(root)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, char in self.display_list:
            if y > self.scroll + self.HEIGHT or y + self.VSTEP < self.scroll:
                continue
            self.canvas.create_text(
                x, y - self.scroll, text=char, font=self.font, anchor="nw"
            )

    def layout(self, text: str):
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            if c == "\n":
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
            self.display_list.append((cursor_x, cursor_y, c))
            cursor_x += self.HSTEP
            if cursor_x > self.WIDTH - self.HSTEP:
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP

    def recurse(self, root=None):
        if root is None:
            return

        if isinstance(root, Text):
            text = root.text
            self.display_list.append((self.HSTEP, self.cursor_y, text))
            self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP
        elif isinstance(root, Comment):
            text = f"<!-- {root.comment} -->"
            self.display_list.append((self.HSTEP, self.cursor_y, text))
            self.cursor_y += self.font.metrics()["linespace"] + self.VSTEP

        if isinstance(root, Document) or isinstance(root, Element):
            for child in root.children:
                self.recurse(child)


if __name__ == "__main__":
    browser = Browser()
    # browser.load("https://browser.engineering/html.html")
    # browser.load("view-source:https://browser.engineering/html.html")
    browser.load("http://localhost:5500/index.html")
    # browser.load("https://example.org/index.html")
    browser.window.mainloop()
