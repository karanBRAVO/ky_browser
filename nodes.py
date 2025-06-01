# Root Node
class Document:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return f"<ROOT>"


# <!DOCTYPE HTML>
class DocumentType:
    def __init__(self, parent=None):
        self.parent = parent

    def __str__(self):
        return f"<!DOCTYPE HTML>"


# Element Node
class Element:
    def __init__(self, tag: str, parent=None):
        self.tag = tag
        self.children = []
        self.parent = parent
        self.attributes = {}

    def set_attribute(self, name: str, value: str):
        self.attributes[name] = value

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return f"<{self.tag}> Attributes: {self.attributes} Childrens: {len(self.children)}"


# Text Node
class Text:
    def __init__(self, text: str, parent=None):
        self.text = text
        self.parent = parent

    def __str__(self):
        return f"{self.text}"


# Comment Node
class Comment:
    def __init__(self, comment: str, parent=None):
        self.comment = comment
        self.parent = parent

    def __str__(self):
        return f"<!-- {self.comment} -->"
