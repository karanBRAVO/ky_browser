from http.server import SimpleHTTPRequestHandler, HTTPServer


class LoggingHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("Received GET request")
        print("Headers:")
        for header, value in self.headers.items():
            print(f"{header}: {value}")
        super().do_GET()

    def do_POST(self):
        print("Received POST request")
        print("Headers:")
        for header, value in self.headers.items():
            print(f"{header}: {value}")
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print("Body:")
        print(body.decode('utf-8'))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST received")


if __name__ == '__main__':
    port = 8080
    server = HTTPServer(('', port), LoggingHTTPRequestHandler)
    print(f"Serving on port {port}")
    server.serve_forever()
