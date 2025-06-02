from nodes import Document, DocumentType, Element, Text, Comment
import re


# HTML Parser Class
class HTMLParser:
    DOCTYPE_PATTERN = r"(?i)^\s*<!doctype\s+html\s*>"
    ATTRIBUTES_PATTERN = (
        r'([a-zA-Z][\w-]*)\s*(?:=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+)))?'
    )

    def __init__(self, html: str):
        self.html = html.strip()
        self.root = Document()

    def _handle_doctype(self, html: str, current_node):
        if re.match(self.DOCTYPE_PATTERN, html):
            current_node.add_child(DocumentType(current_node))
            html = re.sub(self.DOCTYPE_PATTERN, "", html, count=1).strip()
        return html

    def _handle_comment(self, content: str, html: str, i: int, j: int, current_node):
        if content.endswith("--"):
            comment_text = content[3:-2].strip()
        else:
            j = html.find("-->", j + 1)
            comment_text = html[i + 4 : j].strip()
            j += 2
        current_node.add_child(Comment(comment_text, current_node))
        return j

    def _handle_closing_tag(self, open_nodes: list[str], content: str, current_node):
        if len(open_nodes):
            closing_tag_name = content[1:].strip().lower()
            last_open_tag = open_nodes[-1].strip().lower() if open_nodes else None

            if last_open_tag != closing_tag_name:
                print(
                    f"Unmatched closing tag `{closing_tag_name}` for opening tag `{last_open_tag}`"
                )
            else:
                open_nodes.pop()
                current_node = current_node.parent
        return current_node, open_nodes

    def _handle_self_closing_tag(self, content: str, current_node):
        content = content[:-1].strip()
        attributes = []
        if content.find(" ") != -1:
            parts = content.strip().split(None, 1)
            tag_name = parts[0]
            if len(parts) > 1:
                attrs = parts[1]
                attributes = self._parse_attributes(attrs)
        else:
            tag_name = content
        new_element = Element(tag_name.strip().lower(), current_node, True)
        for name, value in attributes:
            new_element.set_attribute(name, value)
        current_node.add_child(new_element)
        return content, current_node

    def _parse_attributes(self, attr_string: str):
        attributes = []

        for match in re.finditer(self.ATTRIBUTES_PATTERN, attr_string):
            name = match.group(1).strip().lower()
            value = match.group(2) or match.group(3) or match.group(4) or ""
            attributes.append((name, value))

        return attributes

    def _handle_opening_tag(
        self, content: str, html: str, current_node, j: int, open_nodes: list
    ):
        # style tags
        if content.startswith("style"):
            j = html.find("</style>", j + 1)
            j += len("/style>")
        # script tags
        elif content.startswith("script"):
            j = html.find("</script>", j + 1)
            j += len("/script>")
        else:
            attributes = []
            if content.find(" ") != -1:
                parts = content.strip().split(None, 1)
                tag_name = parts[0]
                if len(parts) > 1:
                    attrs = parts[1]
                    attributes = self._parse_attributes(attrs)
            else:
                tag_name = content
            new_element = Element(tag_name.strip().lower(), current_node)
            current_node.add_child(new_element)
            open_nodes.append(tag_name.strip().lower())
            current_node = new_element
            for name, value in attributes:
                new_element.set_attribute(name, value)
        return current_node, j, open_nodes

    def parse(self):
        html = self.html
        if not html:
            print("No HTML content to parse.")
            return self.root

        current_node = self.root

        # DOCTYPE
        html = self._handle_doctype(html, current_node)

        open_nodes = []

        i = 0
        buffer = ""
        while i < len(html):
            char = html[i]

            if char == "<":
                if buffer:
                    text_content = buffer.strip()
                    if text_content:
                        new_element = Text(text_content, current_node)
                        current_node.add_child(new_element)
                buffer = ""

                j = html.find(">", i)
                if j == -1:
                    buffer += char
                    i += 1
                    continue

                _content = html[i + 1 : j].strip()

                # comments
                if _content.startswith("!--"):
                    j = self._handle_comment(_content, html, i, j, current_node)
                # closing tags
                elif _content.startswith("/"):
                    current_node, open_nodes = self._handle_closing_tag(
                        open_nodes, _content, current_node
                    )
                # self-closing tags
                elif _content.endswith("/"):
                    _content, current_node = self._handle_self_closing_tag(
                        _content, current_node
                    )
                # opening tags
                else:
                    current_node, j, open_nodes = self._handle_opening_tag(
                        _content, html, current_node, j, open_nodes
                    )

                i = j + 1
                continue

            i += 1
            buffer += char

        if buffer:
            text_content = buffer.strip()
            if text_content:
                new_element = Text(text_content, current_node)
                current_node.add_child(new_element)

        while len(open_nodes):
            open_nodes.pop()
            current_node = current_node.parent

        return self.root


def print_tree(start_node=None, indent=0):
    if start_node is None:
        return

    print(" " * indent, start_node)

    if isinstance(start_node, Document) or isinstance(start_node, Element):
        for child in start_node.children:
            print_tree(child, indent + 2)


if __name__ == "__main__":
    html_content = """
    <!DOCTYPE HTML>
    <html>
        <head>
            <title>Test Page</title>
            <style>body { font-family: Arial; }</style>
        </head>
        <body>
            <h1>Hello, World!</h1>
            <p>This is a test page.</p>
            <!-- This is a comment -->
        </body>
    </html>
    """

    parser = HTMLParser(html_content)
    root = parser.parse()
    print_tree(root)
