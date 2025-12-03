import socket

HOST = "0.0.0.0"
PORT = 8080

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

        # If nothing received, skip this client
        if not raw_request:
            client_socket.close()
            continue

        # Decode bytes -> string
        request_text = raw_request.decode("iso-8859-1")

        print("\n----- RAW HTTP REQUEST START -----")
        print(request_text)
        print("----- RAW HTTP REQUEST END -----\n")

        # STEP 1: Split headers and body
        parts = request_text.split("\r\n\r\n", 1)
        header_section = parts[0]

        # STEP 2: Split header section into lines
        lines = header_section.split("\r\n")

        # STEP 3: Parse request line (method, path, version)
        request_line = lines[0]
        method, path, version = request_line.split(" ", 2)

        print("Parsed Request Line:")
        print("  Method:", method)
        print("  Path:", path)
        print("  Version:", version)

        # STEP 4: Parse headers into dictionary
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value

        print("\nParsed Headers:")
        print(headers)

        # ============================
        # PHASE 3: ROUTING STARTS HERE
        # ============================

        # 1. Route: GET /
        if method == "GET" and path == "/":
            body = "Welcome to my custom HTTP server!"
            status_line = "HTTP/1.1 200 OK"

        # 2. Route: GET /echo?msg=...
        elif method == "GET" and path.startswith("/echo"):
            body = "No message provided."

            if "?" in path:
                query_string = path.split("?", 1)[1]   # msg=hello

                if "=" in query_string:
                    key, value = query_string.split("=", 1)
                    if key == "msg":
                        body = value

            status_line = "HTTP/1.1 200 OK"

        # 3. Route not found → 404
        else:
            body = "404 Not Found"
            status_line = "HTTP/1.1 404 Not Found"

        # Build HTTP response
        response = (
            f"{status_line}\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            f"{body}"
        )

        # Send response
        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()
        # ============================
        # PHASE 3: ROUTING ENDS HERE
        # ============================


if __name__ == "__main__":
    run_server()
