import socket
import json

HOST = "0.0.0.0"
PORT = 8080

DATA_STORE = []


# ============================
# HELPER FUNCTIONS
# ============================

def build_response(body, status="200 OK", content_type="text/plain"):
    """Builds a valid HTTP/1.1 response."""
    
    if isinstance(body, (dict, list)):  # Auto-convert dict/list to JSON
        body = json.dumps(body, indent=2)
        content_type = "application/json"
    
    body_bytes = body.encode("utf-8")
    
    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "\r\n"
    ).encode("utf-8") + body_bytes
    
    return response


def send_json(data, status="200 OK"):
    """Shortcut for sending JSON responses."""
    return build_response(data, status=status, content_type="application/json")


def parse_path_and_id(path):
    """Extract ID from paths like /data/3."""
    parts = path.split("/")
    if len(parts) == 3 and parts[2].isdigit():
        return int(parts[2])
    return None


# ============================
# SERVER START
# ============================

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server is running on http://localhost:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print("\n📣 New connection from:", client_address)

        raw_request = client_socket.recv(4096)

        if not raw_request:
            client_socket.close()
            continue

        request_text = raw_request.decode("iso-8859-1")

        # Parse request
        parts = request_text.split("\r\n\r\n", 1)
        header_section = parts[0]
        body_section = parts[1] if len(parts) > 1 else ""
        lines = header_section.split("\r\n")

        method, path, version = lines[0].split(" ", 2)

        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value

        # ============================
        # ROUTING (Cleaner Structure)
        # ============================

        # ---------- GET ROUTES ----------
        if method == "GET":

            # GET /
            if path == "/":
                response = build_response("Welcome to my improved HTTP server!")

            # GET /echo?msg=
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

        # ---------- POST ROUTES ----------
        elif method == "POST":

            # POST /data
            if path == "/data":
                content_length = int(headers.get("content-length", 0))
                content_type = headers.get("content-type", "")

                if content_type != "application/json":
                    response = send_json({"error": "Content-Type must be application/json"}, "400 Bad Request")
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

        # ---------- DELETE ROUTES ----------
        elif method == "DELETE":

            if path.startswith("/data/"):
                item_id = parse_path_and_id(path)
                if item_id is None or item_id >= len(DATA_STORE):
                    response = send_json({"error": "Item not found"}, "404 Not Found")
                else:
                    DATA_STORE.pop(item_id)
                    response = send_json({"message": "Item deleted"})
            else:
                response = send_json({"error": "Route not found"}, "404 Not Found")

        # ---------- UNSUPPORTED METHOD ----------
        else:
            response = send_json({"error": "Method not allowed"}, "405 Method Not Allowed")

        client_socket.sendall(response)
        client_socket.close()


# Run server
if __name__ == "__main__":
    run_server()
