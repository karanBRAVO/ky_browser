from font import Font
from download import URL
from tkinter import Canvas
from console import Console
from scrollbar import Scrollbar
from css_parser import CSSParser
from url_parser import URLParser
from html_parser import HTMLParser, print_tree
from history_manager import HistoryManager
from js_context import JSContext
from layout import Layout, print_layout_tree


class Tab:
    """
    Represents a browser tab that can load and display content from a URL.
    """

    HSTEP, VSTEP = 13, 18
    BROWSER_DEFAULT_STYLESHEET = "file:///E:/ky_browser/browser.css"
    BROWSER_DEFAULT_JAVASCRIPT = "file:///E:/ky_browser/runtime.js"

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        canvas: Canvas,
        title: str = "New Tab",
    ):
        # canvas
        self.canvas = canvas

        # scrollbar
        self.scroll_bar = Scrollbar(screen_width, screen_height, self.draw)

        # title
        self.title = title

        # content
        self.url = ""
        self.content = ""
        self.mediaType = "text/plain"

        # dom tree root
        self.dom_root = None

        # layout
        self.display_list = []

        # history manager
        self.history_manager = HistoryManager()

        # JavaScript context
        self.js_ctx = JSContext()

        # console
        self.console = Console(self.js_ctx)

        # default font
        self.font = Font().get_font()

        # dimensions
        self.WIDTH = screen_width
        self.HEIGHT = screen_height

        data = [
            ("log", self.log),
            ("print_history", self.print_history),
            ("clear_history", self.clear_history),
            ("get_prev_history_url", self.print_prev_history_url),
            ("get_next_history_url", self.print_next_history_url),
            ("print_document_tree", self.print_dom_tree),
        ]
        self.js_ctx._register(data)

        self.load_defaults()

    def print_dom_tree(self):
        if self.dom_root is None:
            self.js_ctx.result = "null"
        else:
            self.js_ctx.result = print_tree(self.dom_root, 0, False)

    def log(self, *args):
        self.js_ctx.result = " ".join(str(arg) for arg in args)

    def print_prev_history_url(self):
        url = self.get_prev_history_url()
        if url is None:
            self.js_ctx.result = "null"
        else:
            self.js_ctx.result = url

    def print_next_history_url(self):
        url = self.get_next_history_url()
        if url is None:
            self.js_ctx.result = "null"
        else:
            self.js_ctx.result = url

    def print_history(self):
        self.js_ctx.result = self.history_manager.history

    def clear_history(self):
        self.history_manager.clear()
        self.js_ctx.result = "History cleared."

    def _update_screen_dimensions(self, screen_width: int, screen_height: int):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.scroll_bar.update_screen_dimensions(self.WIDTH, self.HEIGHT)

    def _change_canvas_background(self, color: str = "white"):
        self.canvas.config(background=color)

    def _clear_canvas(self):
        self.canvas.delete("all")

    def get_prev_history_url(self):
        try:
            url = self.history_manager.back()
            return url
        except IndexError:
            return None

    def get_next_history_url(self):
        try:
            url = self.history_manager.forward()
            return url
        except IndexError:
            return None

    def load(self, url: str, update_history: bool = True):
        if url:
            # download the content from the URL
            self.url = url
            self.content, self.mediaType = URL(url).request()
            if self.url and update_history:
                self.history_manager.add(self.url)
            # parse the loaded content
            self.parse()
            # draw the content on the canvas
            self.draw()

    def load_css(self, links: list[str]):
        base_url = URLParser().extract_base_url(self.url)

        # Initialize CSS parser
        css_parser = CSSParser()

        # load the default browser styles
        link = self.BROWSER_DEFAULT_STYLESHEET
        content, _ = URL(link).request()
        css_parser.parse(external_styles=content)

        # load external stylesheets
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
                self.console.add_message("", f"Error loading CSS from {link}: {e}")
        return css_parser.styles

    def load_defaults(self):
        # load the default browser scripts
        link = self.BROWSER_DEFAULT_JAVASCRIPT
        content, _ = URL(link).request()
        if content:
            self.js_ctx.run(link, content)

    def load_js(self, links: list[str]):
        base_url = URLParser().extract_base_url(self.url)

        for link in links:
            try:
                idx = link.find("http")
                if idx == -1:
                    link = f"{base_url}/{link.lstrip('/')}"
                else:
                    link = link[idx:]
                content, mediaType = URL(link).request()
                if (
                    "text/javascript" in mediaType
                    or "application/javascript" in mediaType
                ):
                    self.js_ctx.run(link, content)
            except Exception as e:
                self.console.add_message(
                    "", f"Error loading JavaScript from {link}: {e}"
                )

    def parse(self):
        self.display_list.clear()

        if not self.content or not self.url:
            return

        lTree = Layout(self.WIDTH, self.HEIGHT)

        if "text/html" in self.mediaType:
            html_parser = HTMLParser(self.content)
            self.dom_root = html_parser.parse()

            if self.url.startswith("view-source:"):
                self._change_canvas_background("black")
                self.title = self.url
                lTree.source_view(self.font, self.dom_root)
            else:
                self._change_canvas_background("white")
                if self.url.startswith("data:text/html"):
                    self.title = self.url
                else:
                    title = html_parser.extract_title(self.dom_root)
                    if title is None:
                        self.title = URLParser().extract_base_url(self.url)
                    else:
                        self.title = title

                # Extract links from the HTML content
                html_parser.extract_links(self.dom_root)
                styles = self.load_css(html_parser.links.get("css", []))

                # render the HTML content
                lTree.layout(self.dom_root, styles=styles)
                lTree.render(lTree.node)
                # print_layout_tree(lTree.node)

                # Load JavaScript files
                self.load_js(html_parser.links.get("js", []))
        else:
            self._change_canvas_background("#1c1b22")
            self.title = self.url
            lTree.file_view(self.content, self.font)

        # draw the display list
        self.display_list = lTree.display_list
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
