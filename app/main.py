import socket

def handle_request(request):
    """
    A function that handles an HTTP request and generates an appropriate HTTP response based on the request path.
    This function takes the request as input and returns the corresponding HTTP response.
    """
    path = request.split(" ")[1]
    if path == "/":
        return "HTTP/1.1 200 OK\r\n\r\n"
    elif path.startswith("/echo"):
        (echo, ) = path.split("/echo/")[1:2] or ""
        status = "HTTP/1.1 200 OK\r\n"
        content_type = "Content-Type: text/plain\r\n"
        content_length = f"Content-Length: {len(path.split('/echo/')[1])}\r\n"

        return status + content_type + content_length + "\r\n" + echo
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\n"


def main():
    print("Logs from the program will appear here!")
  
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    
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
