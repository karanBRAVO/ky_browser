import re


class CSSParser:
    """
    A CSS parser that extracts styles from inline and external stylesheets.
    """

    def __init__(self):
        self.styles = {}

    def extract_text_styles(self, styles: dict):
        text_styles = {
            "family": "Times New Roman",
            "size": 14,
            "weight": "normal",
            "slant": "roman",
            "underline": False,
        }
        if "font-style" in styles:
            font_style = styles["font-style"]
            if font_style == "italic":
                text_styles["slant"] = "italic"
        if "font-weight" in styles:
            font_weight = styles["font-weight"]
            if font_weight == "bold":
                text_styles["weight"] = "bold"
            elif font_weight == "normal":
                text_styles["weight"] = "normal"
            elif isinstance(font_weight, int) and int(font_weight) >= 600:
                text_styles["weight"] = "bold"
        if "font-family" in styles:
            text_styles["family"] = styles["font-family"]
        if "font-size" in styles:
            font_size = styles["font-size"]
            if font_size.endswith("px"):
                text_styles["size"] = int(font_size[:-2])
            elif font_size.endswith("pt"):
                text_styles["size"] = int(font_size[:-2]) * 0.75
        if "text-decoration" in styles:
            text_decoration = styles["text-decoration"]
            if text_decoration == "underline":
                text_styles["underline"] = True
        return text_styles

    def parse(self, external_styles: str = "", inline_styles: str = ""):
        if external_styles:
            self._parse_external_styles(external_styles)
        if inline_styles:  # override external styles
            self._parse_inline_styles(inline_styles)
        return self.styles

    def _parse_inline_styles(self, styles: str):
        styles = self.format_styles(styles)

        buffer = ""
        key = ""
        value = ""
        try:
            for char in styles:
                if char == ":":
                    key = buffer.strip()
                    buffer = ""
                elif char == ";":
                    value = buffer.strip()
                    if key and value:
                        self.styles[key] = value
                    buffer = ""
                else:
                    buffer += char
            if buffer:
                value = buffer.strip()
                if key and value:
                    self.styles[key] = value
        except Exception:
            print("Error parsing inline styles.")
            self.styles.clear()

    def _parse_external_styles(self, styles: str):
        styles = self.format_styles(styles)

        selector = ""
        buffer = ""
        key = ""
        value = ""
        try:
            for char in styles:
                if char == "{":
                    selector = buffer.strip()
                    buffer = ""
                elif char == ":":
                    key = buffer.strip()
                    buffer = ""
                    if selector and key:
                        self.styles.setdefault(selector, {})[key] = ""
                elif char == ";":
                    value = buffer.strip()
                    buffer = ""
                    if selector and key and value:
                        self.styles[selector][key] = value
                elif char == "}":
                    value = buffer.strip()
                    buffer = ""
                    if selector and key and value:
                        self.styles[selector][key] = value
                else:
                    if char == '"' or char == "'":
                        continue
                    buffer += char
            if buffer:
                value = buffer.strip()
                if selector and key and value:
                    self.styles[selector][key] = value
        except Exception:
            print("Error parsing external styles.")
            self.styles.clear()

    def format_styles(self, text: str):
        text = re.sub(r"\n(?=\S)", " ", text)
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
        text = re.sub(r"\s+", " ", text).strip()
        return text
