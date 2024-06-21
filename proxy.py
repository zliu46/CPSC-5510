"""
@Purpose: This program implements small web proxy server that is able to cache web pages.
          It is a very simple proxy server that only understands simple GET requests of html files.
          
@Author: Zhou Liu
@Course: CPSC5510
@4/17/2024
@version 1.0
"""
import sys
from socket import *
from urllib.parse import urlparse
from pathlib import Path

def main():
    """
    Initializes the proxy server and handles client connections continuously.
    Accepts port number as a command-line argument.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 proxy.py PORT")
        return
    port = int(sys.argv[1])
    server_socket = socket(AF_INET6, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('::', port))
    server_socket.listen(1)
    print("\n******************** Ready to serve ********************")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Received a client connection from {addr}")
            handle_client(client_socket)
            print("\n******************** Ready to serve ********************")
    except KeyboardInterrupt:
        print("Server shutdown.")
        server_socket.close()

def handle_client(client_socket):
    """
    Receives a client request, processes it, and sends back the appropriate HTTP response.
    Handles GET requests and caching mechanism.
    """
    try:
        request = client_socket.recv(1024).decode()
        print(f"Received a message from this client: {request.encode()}")
        lines = request.split('\r\n')
        first_line = lines[0]
        method, full_url, version = first_line.split()
        
        if method != 'GET':
            client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_socket.close()
            return
        
        url_parsed = urlparse(full_url)
        hostname = url_parsed.hostname
        port = url_parsed.port if url_parsed.port else 80
        path = url_parsed.path
        
        if url_parsed.query or url_parsed.fragment:
            raise ValueError("URL with parameters or fragment not supported")
        
        cache_path = Path(f'cache/{hostname}{path}')
        if cache_path.exists():
            print("Yay! The requested file is in the cache...")
            send_cached_response(client_socket, cache_path, version)
        else:
            print("Oops! No cache hit! Requesting origin server for the file...")
            fetch_and_cache_response(client_socket, hostname, port, path, cache_path, version)
    except Exception as e:
        print(e)
        client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
    finally:
        print("All done! Closing socket...\n")
        client_socket.close()

def send_cached_response(client_socket, cache_path, version):
    """
    Sends a cached response to the client.
    """
    with open(cache_path, 'rb') as file:
        content = file.read()
        headers = f"{version} 200 OK\r\n"
        headers += "Cache-Hit: 1\r\n"
        client_socket.sendall(headers.encode() + content)

def fetch_and_cache_response(client_socket, hostname, port, path, cache_path, version):
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.connect((hostname, port))
        request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
        server_socket.sendall(request.encode())
        print(f"Sending the following message from proxy to server:\n{request}")

        response = bytearray()
        while True:
            chunk = server_socket.recv(1024)
            if not chunk:
                break
            response.extend(chunk)
        
        response_content = response.split(b'\r\n\r\n', 1)
        headers, body = response_content[0], response_content[1] if len(response_content) > 1 else (b'', b'')
        status_line = headers.split(b'\r\n')[0]
        status_code = status_line.split(b' ')[1]
        print(f"Response received from server, and status code is not 200!")
        if status_code == b'200':
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'wb') as file:
                file.write(body)  # Cache only the body to avoid caching response headers
            print("Write to cache, save time next time...")
            client_socket.sendall(headers + b'\r\n\r\n' + body)
        elif status_code == b'404':
            client_socket.sendall(headers + b'\r\nCache-Hit: 0\r\n\r\n' + body)
        else:
            error_message = f"{version} 500 Internal Server Error\r\nCache-Hit: 0\r\n\r\n"
            client_socket.sendall(error_message.encode())
            print("An error occurred, responding with 500 Internal Server Error...")

    except Exception as e:
        print(f"Failed to connect or send to the server: {e}")
        error_message = f"{version} 500 Internal Server Error\r\nCache-Hit: 0\r\n\r\n"
        client_socket.sendall(error_message.encode())
    finally:
        print("Now responding to the client...")
        server_socket.close()

if __name__ == "__main__":
    main()

