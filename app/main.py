import socket
import threading
import os
import argparse

OK_STATUS = "HTTP/1.1 200 OK\r\n"
CREATED_STATUS = "HTTP/1.1 201 Created\r\n"
NOT_FOUND_STATUS = "HTTP/1.1 404 Not Found\r\n\r\n"
CRLF = "\r\n"

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--directory", help="Directory to serve files from", default="./tmp/")

args = arg_parser.parse_args()

FILE_DIRECTORY = args.directory

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
    Handle an HTTP request and generate an appropriate HTTP response based on the request path.
    """
    lines = request.split("\r\n")
    if len(lines) == 0:
        return NOT_FOUND_STATUS
    
    headers = parse_headers(request)

    method = request.split(" ")[0]
    path = request.split(" ")[1]
    if path == "/":
        return OK_STATUS + "\r\n"
    elif path.startswith("/echo"):
        echo = path.split("/echo/")[1] if "/echo/" in path else ""
        content_type = "Content-Type: text/plain\r\n"
        content_length = f"Content-Length: {len(path.split("/echo/")[1])}\r\n"

        return OK_STATUS + content_type + content_length + CRLF + echo
    elif path == "/user-agent":
        user_agent = headers.get("User-Agent", "")
        content_type = "Content-Type: text/plain\r\n"
        content_length = f"Content-Length: {len(user_agent)}\r\n"

        return OK_STATUS + content_type + content_length + CRLF + user_agent
    elif path.startswith("/files/"):
        file_name = path.split("/files/")[1] or ""
        file_path = os.path.join(FILE_DIRECTORY, file_name)

        if method == "POST":
            with open(file_path, "w") as file:
                file.write(request.split("\r\n\r\n")[1])

            return CREATED_STATUS
        
        if not os.path.exists(file_path):
            return NOT_FOUND_STATUS
        
        try: 
            with open(file_path) as file:
                file_content = file.read()
        except FileNotFoundError:
            return NOT_FOUND_STATUS
        
        content_length = f"Content-Length: {os.path.getsize(file_path)}\r\n"
        content_type = "Content-Type: application/octet-stream\r\n"

        return OK_STATUS + content_type + content_length + CRLF + file_content
    else:
        return NOT_FOUND_STATUS
    
def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")

    try:
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Received request: {request}")

        response = handle_request(request)

        client_socket.sendall(response.encode("utf-8"))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("Server is listening on port 4221")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
        client_thread.start()


if __name__ == "__main__":
    main()
