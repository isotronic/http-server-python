import socket

OK_STATUS = "HTTP/1.1 200 OK\r\n"
NOT_FOUND_STATUS = "HTTP/1.1 404 Not Found\r\n\r\n"

def parse_headers(request):
    """
    Parse the headers of an HTTP request.
    """
    headers = {}
    lines = request.split("\r\n")
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(": ", 1)
            headers[key] = value
    
    return headers

def handle_request(request):
    """
    Handle an HTTP request and generates an appropriate HTTP response based on the request path.
    """
    path = request.split(" ")[1]
    if path == "/":
        return OK_STATUS + "\r\n"
    elif path.startswith("/echo"):
        (echo, ) = path.split("/echo/")[1:2] or ""
        content_type = "Content-Type: text/plain\r\n"
        content_length = f"Content-Length: {len(path.split("/echo/")[1])}\r\n"

        return OK_STATUS + content_type + content_length + "\r\n" + echo
    elif path == "/user-agent":
        user_agent = parse_headers(request)["User-Agent"]
        content_type = "Content-Type: text/plain\r\n"
        content_length = f"Content-Length: {len(user_agent)}\r\n"

        return OK_STATUS + content_type + content_length + "\r\n" + user_agent
    else:
        return NOT_FOUND_STATUS


def main():
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
