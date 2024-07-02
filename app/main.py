import socket

def handle_request(request):
    path = request.split(" ")[1]
    if path == "/":
        return "HTTP/1.1 200 OK\r\n\r\n"
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\n"


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
  
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        request = client_socket.recv(1024).decode("utf-8")
        print(f"Received request: {request}")

        response = handle_request(request)

        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()


if __name__ == "__main__":
    main()
