from nodes import Document, DocumentType, Element, Attribute, Text, Comment
import re


# HTML Parser Class
class HTMLParser:
    DOCTYPE_PATTERN = r"(?i)^\s*<!doctype\s+html\s*>"

    def __init__(self, html: str):
        self.html = html.strip()
        self.root = Document()

    def parse(self):
        html = self.html
        if not html:
            print("No HTML content to parse.")
            return

        current_node = self.root

        if re.match(self.DOCTYPE_PATTERN, html):
            current_node.add_child(DocumentType(current_node))
            html = re.sub(self.DOCTYPE_PATTERN, "", html, count=1).strip()

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
                    break

                _content = html[i + 1 : j].strip()

                # comments
                if _content.startswith("!--"):
                    if _content.endswith("--"):
                        comment_text = _content[3:-2].strip()
                    else:
                        j = html.find("-->", j + 1)
                        if j == -1:
                            break
                        comment_text = html[i + 4 : j].strip()
                        j += 2
                    current_node.add_child(Comment(comment_text, current_node))
                # closing tags
                elif _content.startswith("/"):
                    if len(open_nodes):
                        open_nodes.pop()
                        current_node = current_node.parent
                # self-closing tags
                elif _content.endswith("/"):
                    tag_name = _content[:-1].strip()
                    new_element = Element(tag_name, current_node)
                    current_node.add_child(new_element)
                # opening tags
                else:
                    # style and script tags
                    if _content.startswith("style"):
                        j = html.find("</style>", j + 1)
                        if j == -1:
                            break
                        j += len("/style>")
                    elif _content.startswith("script"):
                        j = html.find("</script>", j + 1)
                        if j == -1:
                            break
                        j += len("/script>")
                    else:
                        tag_name = _content.strip()
                        # also parse attributes
                        new_element = Element(tag_name, current_node)
                        current_node.add_child(new_element)
                        open_nodes.append(tag_name)
                        current_node = new_element

                i = j + 1
                continue

            i += 1
            buffer += char

        print("Current Node:", current_node)
        print("Open Nodes:", open_nodes)

        if buffer:
            text_content = buffer.strip()
            if text_content:
                new_element = Text(text_content, current_node)
                current_node.add_child(new_element)

        while len(open_nodes):
            open_nodes.pop()
            current_node = current_node.parent

        # print the tree
        self.print_tree(self.root)

    def print_tree(self, start_node=None):
        if start_node is None:
            return

        print(start_node)

        if isinstance(start_node, Document) or isinstance(start_node, Element):
            for child in start_node.children:
                self.print_tree(child)
