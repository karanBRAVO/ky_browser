from tkinter import Tk, Canvas, font
from url import URL
from html_parser import HTMLParser
from layout import Layout, print_layout_tree
from scrollbar import Scrollbar
import re
from css_parser import CSSParser


class Browser:
    WIDTH, HEIGHT = 800, 500
    MIN_WIDTH, MIN_HEIGHT = 400, 300
    HSTEP, VSTEP = 13, 18
    OS = "WINDOWS"  # or "LINUX", "MACOS"

    def __init__(self):
        self.window = Tk()
        self.window.title("Ky Browser")
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.resizable(True, True)
        self.window.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Create a canvas for drawing content
        self.canvas = Canvas(self.window, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack(fill="both", expand=True)

        # content
        self.url = ""
        self.content = ""
        self.mediaType = "text/plain"

        # layout
        self.display_list = []
        self.font = font.Font(
            family="Courier",
            size=14,
            weight="normal",
            slant="roman",
        )

        # scrollbar
        self.scroll_bar = Scrollbar(self.WIDTH, self.HEIGHT)

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

    def _configure(self, event):
        self.WIDTH = event.width
        self.HEIGHT = event.height
        self.scroll_bar.update_screen_dimensions(self.WIDTH, self.HEIGHT)
        self.parse()
        self.draw()

    def _mouse_wheel(self, event):
        if self.OS == "WINDOWS":
            scroll_direction = -(event.delta // 120)
            if scroll_direction > 0:
                self.scroll_bar.scroll_down(self.draw)
            else:
                self.scroll_bar.scroll_up(self.draw)

    def _left_key_press(self, event):
        self.scroll_bar.scroll_left(self.draw)

    def _right_key_press(self, event):
        self.scroll_bar.scroll_right(self.draw)

    def _down_key_press(self, event):
        self.scroll_bar.scroll_down(self.draw)

    def _up_key_press(self, event):
        self.scroll_bar.scroll_up(self.draw)

    def _button_4_press(self, event):
        self.scroll_bar.scroll_up(self.draw)

    def _button_5_press(self, event):
        self.scroll_bar.scroll_down(self.draw)

    def _button_1_press(self, event):
        self.scroll_bar.scrollbar_click(event.x, event.y, self.draw)

    def _b1_motion(self, event):
        self.scroll_bar.scrollbar_drag(event.x, event.y, self.draw)

    def _button_release_1(self, event):
        self.scroll_bar.scrollbar_release()

    def _motion(self, event):
        self.scroll_bar.scrollbar_hover(event.x, event.y, self.canvas)

    def _clear_canvas(self):
        self.canvas.delete("all")

    def change_canvas_background(self, color: str = "white"):
        self.canvas.config(background=color)

    def load(self, url):
        if url:
            self.url = url
            self.content, self.mediaType = URL(url).request()

    def extract_base_url(self, url: str):
        pattern = r"^(https?://[^/]+)"
        match = re.match(pattern, self.url)
        if match:
            base_url = match.group(1)
            return base_url
        return None

    def load_css(self, links: list[str]):
        base_url = self.extract_base_url(self.url)
        if not base_url:
            return

        # Initialize CSS parser
        css_parser = CSSParser()

        # load the default browser styles
        link = "file:///E:/ky_browser/browser.css"
        content, _ = URL(link).request()
        css_parser.parse(external_styles=content)

        for link in links:
            try:
                idx = link.find("http")
                if idx == -1:
                    link = f"{base_url}/{link.lstrip('/')}"
                else:
                    link = link[idx:]
                content, mediaType = URL(link).request()
                if "text/css" in mediaType:
                    css_parser.parse(external_styles=content)
            except Exception as e:
                print(f"Error loading CSS: {e}")
        return css_parser.styles

    def parse(self):
        self.display_list.clear()

        if not self.content or not self.url:
            return

        s = Layout(self.window, self.WIDTH, self.HEIGHT)

        if "text/html" in self.mediaType:
            html_parser = HTMLParser(self.content)
            root = html_parser.parse()

            if self.url.startswith("view-source:"):
                self.change_canvas_background("black")
                s.source_view(self.font, root)
            else:
                self.change_canvas_background("white")

                # Extract links from the HTML content
                html_parser.extract_links(root)
                styles = self.load_css(html_parser.links.get("css", []))

                # render the HTML content
                s.layout(root, styles=styles)
                s.render(s.node)
                # print_layout_tree(s.node)
        else:
            self.change_canvas_background("#1c1b22")
            s.file_view(self.content, self.font)

        # draw the display list
        self.display_list = s.display_list
        self.draw()

    def draw(self):
        self._clear_canvas()

        # calculate scroll limits
        self.scroll_bar.calc_max_scroll(self.display_list, self.font)

        # Calculate effective display area (excluding scrollbars)
        effective_width = self.WIDTH - (
            self.scroll_bar.SCROLLBAR_WIDTH if self.scroll_bar.MAX_V_SCROLL > 0 else 0
        )
        effective_height = self.HEIGHT - (
            self.scroll_bar.SCROLLBAR_WIDTH if self.scroll_bar.MAX_H_SCROLL > 0 else 0
        )

        for cmd in self.display_list:
            # Optimizations: Don't draw commands outside the visible area
            if (
                cmd.y > self.scroll_bar.v_scroll + effective_height
                or cmd.y + self.VSTEP < self.scroll_bar.v_scroll
            ):
                continue
            if (
                cmd.x > self.scroll_bar.h_scroll + effective_width
                or cmd.x < self.scroll_bar.h_scroll
            ):
                continue
            cmd.execute(self.canvas, self.scroll_bar.h_scroll, self.scroll_bar.v_scroll)

        # Draw scrollbars on top of content
        self.scroll_bar.draw_scrollbars(self.canvas)


if __name__ == "__main__":
    browser = Browser()
    browser.load("https://browser.engineering/styles.html")
    # browser.load("view-source:https://en.wikipedia.org/wiki/HTML")
    # browser.load("view-source:https://browser.engineering/html.html")
    # browser.load("view-source:http://localhost:5500/index.html")
    # browser.load("http://localhost:5500/index.html")
    # browser.load("file:///E:/ky_browser/html_parser.py")
    # browser.load("data:text/html,<h1>Hello World!</h1>")
    # browser.load("https://example.org/index.html")
    browser.window.mainloop()
