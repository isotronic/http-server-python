import socket
import threading
import os
import argparse
import gzip
import logging

# Constants
OK_STATUS = "HTTP/1.1 200 OK\r\n"
CREATED_STATUS = "HTTP/1.1 201 Created\r\n\r\n"
NOT_FOUND_STATUS = "HTTP/1.1 404 Not Found\r\n\r\n"
ERROR_STATUS = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
CRLF = "\r\n"

# Setup Argument Parser
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--directory", help="Directory to serve files from", default="./files/")
arg_parser.add_argument("--port", help="Port to listen on", default=4221)
args = arg_parser.parse_args()
FILE_DIRECTORY = args.directory
PORT = args.port

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

def build_response(status, headers, body):
    """
    Builds an HTTP response based on the provided status, headers, and body.

    Args:
        status (str): The HTTP status code of the response.
        headers (list): A list of HTTP headers to include in the response.
        body (str or bytes): The content of the response.

    Returns:
        The HTTP response as a byte string or string.
    """
    response_headers = "".join(headers)
    if isinstance(body, str):
        body = body.encode("utf-8")
    response = (status + response_headers + CRLF).encode("utf-8") + body
    return response

def handle_request(request):
    """
    Handle an HTTP request and generate an appropriate HTTP response based on the request path.
    """
    try:
        lines = request.split(CRLF)
        if len(lines) == 0:
            return build_response(NOT_FOUND_STATUS, [], "")
        
        request_headers = parse_headers(request)

        method = request.split(" ")[0]
        path = request.split(" ")[1]
        if path == "/":
            return (OK_STATUS + "\r\n").encode("utf-8")
        
        elif path.startswith("/echo"):
            echo = path.split("/echo/")[1] if "/echo/" in path else ""
            headers = ["Content-Type: text/plain\r\n"]
            if "gzip" in request_headers.get("Accept-Encoding", "").lower():
                headers.append("Content-Encoding: gzip\r\n")
                body = gzip.compress(echo.encode("utf-8"))
            else:
                body = echo
            headers.append(f"Content-Length: {len(body)}\r\n")
            return build_response(OK_STATUS, headers, body)
        
        elif path == "/user-agent":
            user_agent = request_headers.get("User-Agent", "")
            headers = [
                "Content-Type: text/plain\r\n",
                f"Content-Length: {len(user_agent)}\r\n"
            ]
            return build_response(OK_STATUS, headers, user_agent)
        
        elif path.startswith("/files"):
            file_name = path.split("/files/")[1] or ""
            file_path = os.path.join(FILE_DIRECTORY, file_name)

            if method == "POST":
                with open(file_path, "w") as file:
                    file.write(request.split(CRLF + CRLF)[1])
                return build_response(CREATED_STATUS, [], "")
            
            if not os.path.exists(file_path):
                return build_response(NOT_FOUND_STATUS, [], "")
            
            try: 
                with open(file_path) as file:
                    file_content = file.read()
            except FileNotFoundError:
                return build_response(NOT_FOUND_STATUS, [], "")
            
            headers = [
                "Content-Type: application/octet-stream\r\n",
                f"Content-Length: {os.path.getsize(file_path)}\r\n"
            ]
            return build_response(OK_STATUS, headers, file_content)
        
        else:
            return build_response(NOT_FOUND_STATUS, [], "")

    except Exception as e:
        logging.error(f"Error handling request: {e}")
        return build_response(ERROR_STATUS, [], str(e))
    
def handle_client(client_socket, client_address):
    """
    Handle a client connection by receiving and processing an HTTP request.
    
    Args:
        client_socket (socket.socket): The socket object representing the client connection.
        client_address (tuple): A tuple containing the client's IP address and port number.
    """
    logging.info(f"Accepted connection from {client_address}")
    try:
        request = client_socket.recv(1024).decode("utf-8")
        logging.info(f"Received request: {request}")
        response = handle_request(request)
        client_socket.sendall(response)
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()


def main():
    """
    Creates a server socket and listens for incoming client connections.
    """
    server_socket = socket.create_server(("localhost", PORT), reuse_port=False)
    logging.info(f"Server is listening on port {PORT}")
    
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address), daemon=True)
            client_thread.start()
        except Exception as e:
            logging.error(f"Error accepting connection: {e}")



if __name__ == "__main__":
    main()
