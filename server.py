import socket
import json
import threading
from email.utils import formatdate  # For HTTP Date header

HOST = "0.0.0.0"
PORT = 8080

# In-memory database
DATA_STORE = []


# ============================
# HELPER FUNCTIONS
# ============================

def build_response(body, status="200 OK", content_type="text/plain"):
    """Build a proper HTTP/1.1 response including Date, Content-Type, and Content-Length."""

    # Auto convert Python dict/list → JSON
    if isinstance(body, (dict, list)):
        body = json.dumps(body, indent=2)
        content_type = "application/json"

    body_bytes = body.encode("utf-8")

    # RFC 1123 Date header
    date_header = formatdate(timeval=None, localtime=False, usegmt=True)

    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Date: {date_header}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "\r\n"
    ).encode("utf-8") + body_bytes

    return response


def send_json(data, status="200 OK"):
    """Helper function for JSON responses."""
    return build_response(data, status=status, content_type="application/json")


def parse_path_and_id(path: str):
    """Extract integer ID from paths like /data/3."""
    parts = path.split("/")
    if len(parts) == 3 and parts[2].isdigit():
        return int(parts[2])
    return None


# ============================
# CLIENT HANDLER (THREAD)
# ============================

def handle_client(client_socket, client_address):
    print("\n📣 New connection from:", client_address)

    raw_request = client_socket.recv(4096)
    if not raw_request:
        client_socket.close()
        return

    request_text = raw_request.decode("iso-8859-1")

    # Parse into header + body
    parts = request_text.split("\r\n\r\n", 1)
    header_section = parts[0]
    body_section = parts[1] if len(parts) > 1 else ""
    lines = header_section.split("\r\n")

    # Request line
    method, path, version = lines[0].split(" ", 2)

    # Parse headers
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.lower()] = value

    # ============================
    # ROUTING
    # ============================

    # ---------- GET ----------
    if method == "GET":

        # GET /
        if path == "/":
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Custom HTTP Server</title>
                <style>
                    body { font-family: Arial; padding: 20px; }
                    h1 { color: #2b7cff; }
                    code { background: #efefef; padding: 4px; border-radius: 4px; }
                </style>
            </head>
            <body>
                <h1>🚀 Welcome to My Custom HTTP Server</h1>
                <p>This server is built from scratch using Python sockets.</p>

                <h3>Available Endpoints:</h3>
                <ul>
                    <li><code>GET /</code> – Homepage</li>
                    <li><code>GET /echo?msg=hello</code></li>
                    <li><code>POST /data</code></li>
                    <li><code>GET /data</code></li>
                    <li><code>GET /data/&lt;id&gt;</code></li>
                    <li><code>DELETE /data/&lt;id&gt;</code></li>
                </ul>

                <p>Made by <strong>Manvi Gupta</strong></p>
            </body>
            </html>
            """
            response = build_response(html, content_type="text/html")

        # GET /echo
        elif path.startswith("/echo"):
            body = "No message given"
            if "?" in path:
                query = path.split("?", 1)[1]
                if "=" in query:
                    key, value = query.split("=", 1)
                    if key == "msg":
                        body = value
            response = build_response(body)

        # GET /data
        elif path == "/data":
            response = send_json(DATA_STORE)

        # GET /data/<id>
        elif path.startswith("/data/"):
            item_id = parse_path_and_id(path)
            if item_id is None or item_id >= len(DATA_STORE):
                response = send_json({"error": "Item not found"}, "404 Not Found")
            else:
                response = send_json(DATA_STORE[item_id])

        else:
            response = send_json({"error": "Route not found"}, "404 Not Found")

    # ---------- POST ----------
    elif method == "POST":

        # POST /data
        if path == "/data":
            content_length = int(headers.get("content-length", 0))
            content_type = headers.get("content-type", "")

            if content_type != "application/json":
                response = send_json(
                    {"error": "Content-Type must be application/json"},
                    "400 Bad Request"
                )
            else:
                raw_json = body_section[:content_length]
                try:
                    data = json.loads(raw_json)
                    DATA_STORE.append(data)
                    response = send_json({"message": "Data stored successfully"})
                except json.JSONDecodeError:
                    response = send_json({"error": "Invalid JSON"}, "400 Bad Request")

        else:
            response = send_json({"error": "Route not found"}, "404 Not Found")

    # ---------- DELETE ----------
    elif method == "DELETE":

        # DELETE /data/<id>
        if path.startswith("/data/"):
            item_id = parse_path_and_id(path)
            if item_id is None or item_id >= len(DATA_STORE):
                response = send_json({"error": "Item not found"}, "404 Not Found")
            else:
                DATA_STORE.pop(item_id)
                response = send_json({"message": "Item deleted"})
        else:
            response = send_json({"error": "Route not found"}, "404 Not Found")

    # ---------- Unsupported Method ----------
    else:
        response = send_json({"error": "Method not allowed"}, "405 Method Not Allowed")

    client_socket.sendall(response)
    client_socket.close()


# ============================
# MULTITHREADED SERVER
# ============================

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"🚀 Server running at http://localhost:{PORT}")
    print("🧵 Multithreading enabled (Phase 7 + Date Header)")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


if __name__ == "__main__":
    run_server()
