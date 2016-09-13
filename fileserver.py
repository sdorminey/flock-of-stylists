from common import *
import os
import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

common = Common("Fileserver")
common.load()

port = int(common.fs_addr.split(":")[1])

class FileServingHandler(BaseHTTPRequestHandler):
    def _get_target_path(self):
        # Parse path.
        segments = self.path.split("/")
        category = segments[1]
        filename = segments[2]

        return os.path.join("/srv/flock/fs", category, filename)

    def do_GET(self):
        common.log("Received GET %s" % self.path)

        target = self._get_target_path()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")

        if not os.path.exists(target):
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("Not found.", "utf-8"))
            common.log("GET failed due to target %s missing." % target)
            return

        bytes_to_send = os.path.getsize(target)
        self.send_header("Content-Length", bytes_to_send)
        self.end_headers()
        
        with open(target, "rb") as f:
            while bytes_to_send > 0:
                chunk = f.read(min(bytes_to_send, 4096))
                if len(chunk) > 0:
                    self.wfile.write(chunk)
                else:
                    break
                bytes_to_send -= len(chunk)

        common.log("GET succeeded.")

    def do_POST(self):
        common.log("Received POST %s" % self.path)

        target = self._get_target_path()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("Ok.", "utf-8"))

        bytes_to_read = int(self.headers["Content-Length"])

        with open(target, "wb") as f:
            while bytes_to_read > 0:
                data = self.rfile.read(min(4096, bytes_to_read))
                if len(data) > 0:
                    f.write(data)
                else:
                    break
                bytes_to_read -= len(data)

        common.log("POST succeeded.")

server = socketserver.TCPServer(("", port), FileServingHandler)
common.log("FS started on port %d" % port)
server.serve_forever()
