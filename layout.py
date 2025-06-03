from nodes import Document, DocumentType, Element, Text, Comment
from tkinter.font import Font
from draw import DrawText, DrawRect


class LayoutNode:
    """
    Represents a node in the layout tree.
    Each node corresponds to an HTML element or text and contains its position,
    size, and children nodes.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        parent=None,
        name: str = "LayoutNode",
    ):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = []
        self.parent = parent
        self.node = None  # (Element or Text)

    def add_child(self, child):
        self.children.append(child)


class TextNode(LayoutNode):
    """
    Represents a text node in the layout tree.
    Each text node corresponds to a Text object and contains its position,
    size, and parent node.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        parent=None,
        name: str = "TextNode",
    ):
        super().__init__(x, y, width, height, parent, name)
        self.font = Font(
            family="Times New Roman",
            size=14,
            weight="normal",
            slant="roman",
        )


class Layout:
    """
    The `Layout` class is responsible for building the layout tree from an HTML document
    and providing methods to compute the display list for rendering the HTML source code
    and visualizing the layout tree.
    """

    HSTEP, VSTEP = 13, 18

    def __init__(self, window, screen_width: int, screen_height: int):
        self.window = window
        self.node = None
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.display_list = []
        self.cursor_x = self.HSTEP
        self.cursor_y = self.VSTEP

    def layout(self, node=None):
        """
        Builds the layout tree from the given `node`.
        """

        def recurse(node, prev=None):
            if node is None:
                return

            new_node = None

            if isinstance(node, Element):
                new_node = LayoutNode(
                    0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, None, node.tag
                )
                new_node.node = node
                if prev is not None:
                    ch = 0
                    for child in prev.children:
                        ch += child.height
                    prev.add_child(new_node)
                    new_node.parent = prev
                    new_node.x = prev.x
                    new_node.y = prev.y + ch
                    new_node.width = prev.width
                else:
                    self.node = new_node
            elif isinstance(node, Text):
                new_node = TextNode(
                    0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, None, node.text
                )
                new_node.node = node
                if prev is not None:
                    prev.add_child(new_node)
                    new_node.parent = prev
                    new_node.x = prev.x
                    new_node.y = prev.y
                    new_node.width = prev.width

                    # Calculate height based on text content
                    h = 0
                    text = ""
                    for word in node.text.split():
                        if text:
                            test_line = text + " " + word
                        else:
                            test_line = word
                        text_width = new_node.font.measure(test_line)
                        if text_width > self.SCREEN_WIDTH - self.HSTEP:
                            h += new_node.font.metrics()["linespace"]
                            text = word
                        else:
                            text = test_line
                    if text:
                        h += new_node.font.metrics()["linespace"]

                    new_node.height = h

            if isinstance(node, Document) or isinstance(node, Element):
                for child in node.children:
                    if isinstance(child, DocumentType):
                        continue
                    if isinstance(child, Element) and child.tag == "head":
                        continue
                    recurse(child, new_node)

            if isinstance(node, Element):
                if new_node is not None:
                    h = 0
                    for child in new_node.children:
                        h += child.height
                    new_node.height = h

        recurse(node)

    def _update_source_view_display_list(
        self, text: str, x: int, color: str, font: Font
    ):
        """
        Helper method to update the `display_list` for `source_view` method.
        """
        if not text:
            return

        self.cursor_x = x
        buffer = ""
        for i, char in enumerate(text):
            if char == "\n":
                self.cursor_x = x
                self.cursor_y += font.metrics()["linespace"] + self.VSTEP
            elif char == " ":
                if buffer:
                    self.display_list.append(
                        DrawText(self.cursor_x, self.cursor_y, buffer, font, color)
                    )
                    self.cursor_x += font.measure(buffer)
                    j = text.find(" ", i + 1)
                    if j != -1:
                        next_word = text[i + 1 : j]
                        next_word_width = font.measure(next_word)
                        if self.cursor_x + next_word_width > self.SCREEN_WIDTH:
                            self.cursor_x = x
                            self.cursor_y += font.metrics()["linespace"] + self.VSTEP
                    buffer = ""
                if i < 1 or text[i - 1] != " ":
                    self.cursor_x += font.measure(" ")
            else:
                buffer += char
        if buffer:
            self.display_list.append(
                DrawText(self.cursor_x, self.cursor_y, buffer, font, color)
            )

    def source_view(self, font: Font, root=None, indent=0):
        """
        Computes the `display_list` for viewing the `HTML` source code in a formatted way.
        """
        if root is None:
            return

        # DOCTYPE
        if isinstance(root, DocumentType):
            text = f"<!"
            prev_text = text
            self._update_source_view_display_list(text, indent, "white", font)
            text = "DOCTYPE "
            self._update_source_view_display_list(
                text, indent + font.measure(prev_text), "red", font
            )
            prev_text += text
            text = "HTML>"
            self._update_source_view_display_list(
                text, indent + font.measure(prev_text), "white", font
            )
            self.cursor_y += font.metrics()["linespace"] + self.VSTEP
        # opening tags
        elif isinstance(root, Element):
            text = f"<"
            prev_text = text
            self._update_source_view_display_list(text, indent, "white", font)
            text = f"{root.tag}"
            self._update_source_view_display_list(
                text, indent + font.measure(prev_text), "red", font
            )
            # attributes
            for name, value in root.attributes.items():
                prev_text += text
                text = f" {name}="
                self._update_source_view_display_list(
                    text, indent + font.measure(prev_text), "green", font
                )
                prev_text += text
                text = f'"{value}"'
                self._update_source_view_display_list(
                    text, indent + font.measure(prev_text), "yellow", font
                )
            prev_text += text
            text = f"{' /' if root.selfClosing else ''}>"
            self._update_source_view_display_list(
                text, indent + font.measure(prev_text), "white", font
            )
            self.cursor_y += font.metrics()["linespace"] + self.VSTEP
        # comments
        elif isinstance(root, Comment):
            text = f"<!-- {root.comment} -->"
            self._update_source_view_display_list(text, indent, "gray", font)
            self.cursor_y += font.metrics()["linespace"] + self.VSTEP

        # text
        if isinstance(root, Text):
            if root.parent and root.parent.tag == "title":
                text = root.text.strip()
                if text:
                    self.window.title(text)
            else:
                text = root.text
                self._update_source_view_display_list(text, indent, "white", font)
                self.cursor_y += font.metrics()["linespace"] + self.VSTEP

        # recurse children
        if isinstance(root, Document) or isinstance(root, Element):
            for child in root.children:
                self.source_view(font, child, indent + self.HSTEP)

        # closing tags
        if isinstance(root, Element):
            if not root.selfClosing:
                text = f"</"
                prev_text = text
                self._update_source_view_display_list(text, indent, "white", font)
                text = f"{root.tag}"
                self._update_source_view_display_list(
                    text, indent + font.measure(prev_text), "red", font
                )
                prev_text += text
                text = f">"
                self._update_source_view_display_list(
                    text, indent + font.measure(prev_text), "white", font
                )
                self.cursor_y += font.metrics()["linespace"] + self.VSTEP

    def file_view(self, text: str, font: Font):
        """
        Compute the `display_list` for viewing `file` content in a simple text format.
        """
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            if c == "\n":
                cursor_x = self.HSTEP
                cursor_y += self.VSTEP
            self.display_list.append(DrawText(cursor_x, cursor_y, c, font, "white"))
            cursor_x += self.HSTEP
            if cursor_x > self.SCREEN_WIDTH - self.HSTEP:
                cursor_x = self.HSTEP
                cursor_y += font.metrics()["linespace"] + self.VSTEP

    def render(self, root=None):
        """
        Use this method to display the layout tree visually.

        :param root: The root node of the layout tree. (generally represent the `HTML`)

        **Note:**
        Call the `layout` method to build the layout tree and then call this method to populate the display list.
        """
        if root.node is not None:
            if isinstance(root.node, Element):
                self.display_list.append(
                    DrawRect(
                        root.x,
                        root.y,
                        root.width,
                        root.height,
                        border="yellow",
                        backgound="black",
                    )
                )
            elif isinstance(root.node, Text):
                text = ""
                cursor_y = root.y
                for word in root.node.text.split():
                    if text:
                        test_line = text + " " + word
                    else:
                        test_line = word
                    text_width = root.font.measure(test_line)
                    if text_width > self.SCREEN_WIDTH - self.HSTEP:
                        self.display_list.append(
                            DrawText(
                                root.x,
                                cursor_y,
                                text,
                                root.font,
                                "white",
                            )
                        )
                        cursor_y += root.font.metrics()["linespace"]
                        text = word
                    else:
                        text = test_line
                if text:
                    self.display_list.append(
                        DrawText(
                            root.x,
                            cursor_y,
                            text,
                            root.font,
                            "white",
                        )
                    )

        for child in root.children:
            self.render(child)


def print_layout_tree(node=None, indent=0):
    """
    Prints the layout tree structure for debugging purposes.
    """
    if node is None:
        return

    print(
        " " * indent
        + f"'{node.name}' ({node.x}, {node.y}, {node.width}, {node.height})"
    )

    for child in node.children:
        print_layout_tree(child, indent + 2)
