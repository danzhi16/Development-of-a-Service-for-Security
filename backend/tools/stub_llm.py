"""OpenAI-compatible stub that always returns the same vulnerable code. For tests and demos only."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ANSWER = "```python\nimport os\n\n\ndef run():\n    os.system(input())\n```"
REPLY = {"choices": [{"message": {"content": ANSWER}, "finish_reason": "stop"}]}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("content-length", 0)))
        found = self.path == "/v1/chat/completions"
        body = json.dumps(REPLY if found else {"error": "not found"}).encode()
        self.send_response(200 if found else 404)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
