import socket
import ssl
import os
import gzip
from datetime import datetime, timedelta, timezone


class URL:
    SUPPORTED_SCHEMES = ("http", "https", "file", "data", "view-source", "about")

    def __init__(self, url: str):
        self.s = None  # socket
        self.cache = {}

        try:
            if (
                url.startswith("http")
                or url.startswith("https")
                or url.startswith("file")
            ):
                self.scheme, url = url.split("://", 1)
            else:
                self.scheme, url = url.split(":", 1)

            assert self.scheme in self.SUPPORTED_SCHEMES, "Invalid URL scheme"

            if self.scheme == "http" or self.scheme == "https":
                if self.scheme == "http":
                    self.port = 80
                elif self.scheme == "https":
                    self.port = 443

                if "/" not in url:
                    url += "/"
                self.host, url = url.split("/", 1)
                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)
                self.path = "/" + url
            elif self.scheme == "file":
                url = url.split("/", 1)[-1]
                assert os.path.exists(url), "File does not exist"
                self.path = url
            elif self.scheme == "data":
                self.mediaType, self.content = url.split(",", 1)
            elif self.scheme == "view-source":
                self.url = url
            elif self.scheme == "about":
                self.path = url
        except Exception as e:
            print(f"Error parsing URL: {e}")

    def request(self):
        try:
            if self.scheme == "http" or self.scheme == "https":
                url = f"{self.scheme}://{self.host}:{self.port}{self.path}"
                if url in self.cache:
                    cached = self.cache[url]
                    cacheMaxAge = int(cached.get("max-age", 0))
                    cacheDate = datetime.strptime(
                        cached.get("date", ""), "%a, %d %b %Y %H:%M:%S GMT"
                    )
                    cacheDate = cacheDate.replace(tzinfo=timezone.utc)

                    expirationTime = cacheDate + timedelta(seconds=cacheMaxAge)
                    now = datetime.now(timezone.utc)

                    if expirationTime > now:
                        return cached["content"]

                if self.s is None:
                    self.s = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
                    )
                    self.s.connect((self.host, self.port))

                    ctx = ssl.create_default_context()
                    if self.scheme == "https":
                        self.s = ctx.wrap_socket(self.s, server_hostname=self.host)

                requestHeaders = {
                    "Host": self.host,
                    "Connection": "keep-alive",  # close or keep-alive
                    "User-Agent": "Ky_Browser",
                    "Accept-Encoding": "gzip",
                }
                request = f"GET {self.path} HTTP/1.1\r\n"
                for name, value in requestHeaders.items():
                    request += f"{name}: {value}\r\n"
                request += "\r\n"  # End of headers

                self.s.send(request.encode("utf-8"))

                response = self.s.makefile("rb", encoding="utf-8", newline="\r\n")
                statusLine = response.readline().decode("utf-8").strip()
                version, status, reason = statusLine.split(" ", 2)  # HTTP/1.0 200 OK
                status = int(status)

                responseHeaders = {}
                while True:
                    line = response.readline().decode("utf-8")
                    if line == "\r\n":
                        break
                    name, value = line.split(":", 1)
                    responseHeaders[name.strip().casefold()] = value.strip()

                if "content-length" in responseHeaders:
                    contentLength = int(responseHeaders.get("content-length", 0))
                    content = response.read(contentLength)

                    if responseHeaders.get("content-encoding", "") == "gzip":
                        content = gzip.decompress(content).decode("utf-8")
                    else:
                        content = content.decode("utf-8")
                elif (
                    "transfer-encoding" in responseHeaders
                    and responseHeaders.get("transfer-encoding", "") == "chunked"
                ):
                    content = ""
                    while True:
                        chunk = response.readline().strip()
                        if not chunk or chunk == b"0":
                            break
                        chunkSize = int(chunk, 16)
                        if chunkSize == 0:
                            break
                        chunkData = response.read(chunkSize)
                        if responseHeaders.get("content-encoding", "") == "gzip":
                            chunkData = gzip.decompress(chunkData).decode("utf-8")
                        else:
                            chunkData = chunkData.decode("utf-8")
                        content += chunkData
                else:
                    content = ""

                # redirects
                if status >= 300 and status < 400:
                    location = responseHeaders.get("location")
                    if location:
                        if not location.startswith("http://"):
                            if not location.startswith("/"):
                                location = "/" + location
                            location = (
                                f"{self.scheme}://{self.host}:{self.port}{location}"
                            )
                        return URL(location).request()

                if requestHeaders.get("Connection", "").lower() == "close":
                    self.s = self.s.close()

                cacheControl = responseHeaders.get("cache-control", "")

                if cacheControl and cacheControl.find("max-age=") != -1:
                    maxAge = cacheControl.split("max-age=")[-1]
                    if maxAge.find(",") != -1:
                        maxAge = int(maxAge.split(",")[0])
                    self.cache[url] = {
                        "content": content,
                        "etag": responseHeaders.get("etag", ""),
                        "content-type": responseHeaders.get("content-type", ""),
                        "cache-control": cacheControl,
                        "date": responseHeaders.get("date", ""),
                        "max-age": maxAge,
                    }

                return content, responseHeaders.get("content-type", "")
            elif self.scheme == "file":
                try:
                    with open(self.path, "r", encoding="utf-8") as file:
                        return file.read(), "text/plain"
                except FileNotFoundError:
                    return "", "text/plain"
            elif self.scheme == "data":
                return self.content, self.mediaType
            elif self.scheme == "view-source":
                view_source_url = URL(self.url)
                return view_source_url.request()
            elif self.scheme == "about":
                if self.path == "blank":
                    return "<html><body></body></html>", "text/html"
                return "<html><body><h1>About Page</h1></body></html>", "text/html"
        except Exception as e:
            print(f"Error: {e}")
            return URL("about:blank").request()


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


def load(url: URL):
    content = url.request()
    print(content)


if __name__ == "__main__":
    # url = URL("https://example.org/index.html")
    # url = URL("https:/example.org/index.html") # invalid URL for testing
    # url = URL("https://browser.engineering/im/http-tls-2.gif")
    # url = URL("http://localhost:8080")
    # url = URL("file:///E:/ky_browser/html_parser.py")
    url = URL("data:text/html,<h1>Hello World!</h1>")
    # url = URL("view-source:http://example.org/")
    # url = URL("http://browser.engineering/redirect3")
    # url = URL("https://browser.engineering/html.html")
    load(url)
