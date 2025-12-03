import socket

HOST = "0.0.0.0"  # Your server will listen on all network interfaces
PORT = 8080       # Default port for your HTTP server

def run_server():
    # 1. Create the socket (a communication endpoint)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2. Allow immediate restart without waiting for the port to free
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 3. Bind socket to host and port
    server_socket.bind((HOST, PORT))

    # 4. Start listening for connections
    server_socket.listen(5)
    print(f"Server is running on http://localhost:{PORT}")

    while True:
        # 5. Accept a client's connection
        client_socket, client_address = server_socket.accept()
        print("\n📣 New connection from:", client_address)

        # 6. Receive request data (raw bytes)
        raw_request = client_socket.recv(4096)

        print("\n----- RAW HTTP REQUEST START -----")
        print(raw_request.decode("iso-8859-1"))
        print("----- RAW HTTP REQUEST END -----\n")

        # 7. Send back an HTTP response
        body = "Hello from my server!"
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            f"{body}"
        )

        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()

if __name__ == "__main__":
    run_server()
