from tkinter import Tk, Canvas, font
from url import URL


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
        self.content = ""
        self.font = font.Font(
            family="JetBrainsMonoNL NFP SemiBold", size=14, weight="normal", slant="roman"
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
        self.display_list = self.layout(self.content)
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
        body = URL(url).request()
        if url.startswith("view-source:"):
            self.content = body
        else:
            self.content = lex(body)
        self.display_list = self.layout(self.content)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, char in self.display_list:
            if y > self.scroll + self.HEIGHT or y + self.VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=char, font=self.font, anchor="nw")

    def layout(self, text: str):
        display_list = []
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            if c == "\n":
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += self.HSTEP
            if cursor_x > self.WIDTH - self.HSTEP:
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
        return display_list


def lex(body):
    text = ""
    in_tag = False
    for char in body:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            text += char
    return text


if __name__ == "__main__":
    browser = Browser()
    browser.load("view-source:https://example.org")
    browser.window.mainloop()
