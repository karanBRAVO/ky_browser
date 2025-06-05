import re


class URLParser:
    """
    A class to parse and handle URLs.
    """

    def __init__(self):
        pass

    def extract_base_url(self, url: str):
        pattern = r"^(https?://[^/]+)"
        match = re.match(pattern, url)
        if match:
            base_url = match.group(1)
            return base_url
        return None
