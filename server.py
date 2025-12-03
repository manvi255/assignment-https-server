import socket
import json

HOST = "0.0.0.0"
PORT = 8080

DATA_STORE = []


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

        print("\n----- RAW HTTP REQUEST START -----")
        print(request_text)
        print("----- RAW HTTP REQUEST END -----\n")

        # STEP 1: Split headers + body
        parts = request_text.split("\r\n\r\n", 1)
        header_section = parts[0]
        body_section = parts[1] if len(parts) > 1 else ""

        # STEP 2: Break header section into lines
        lines = header_section.split("\r\n")

        # STEP 3: Parse request line
        method, path, version = lines[0].split(" ", 2)

        print("Parsed Request Line:")
        print("  Method:", method)
        print("  Path:", path)
        print("  Version:", version)

        # STEP 4: Parse headers
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value

        print("\nParsed Headers:")
        print(headers)

        print("\nParsed Body Section:")
        print(body_section)

        # ============================
        # ROUTING START
        # ============================

        # 1. GET /
        if method == "GET" and path == "/":
            body = "Welcome to my custom HTTP server!"
            status_line = "HTTP/1.1 200 OK"

        # 2. GET /echo
        elif method == "GET" and path.startswith("/echo"):
            body = "No message provided."
            if "?" in path:
                query = path.split("?", 1)[1]
                if "=" in query:
                    key, value = query.split("=", 1)
                    if key == "msg":
                        body = value
            status_line = "HTTP/1.1 200 OK"

        # 3. POST /data
        elif method == "POST" and path == "/data":
            content_type = headers.get("content-type", "")
            content_length = int(headers.get("content-length", 0))

            if content_type != "application/json":
                body = "Unsupported Content-Type"
                status_line = "HTTP/1.1 400 Bad Request"
            else:
                json_body = body_section[:content_length]
                try:
                    data = json.loads(json_body)
                except json.JSONDecodeError:
                    body = "Invalid JSON"
                    status_line = "HTTP/1.1 400 Bad Request"
                else:
                    DATA_STORE.append(data)
                    body = "Data stored successfully!"
                    status_line = "HTTP/1.1 200 OK"

        # 4. 404 fallback
        else:
            body = "404 Not Found"
            status_line = "HTTP/1.1 404 Not Found"

        # Build final response
        response = (
            f"{status_line}\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            f"{body}"
        )

        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()

        # ============================
        # ROUTING END
        # ============================


if __name__ == "__main__":
    run_server()
