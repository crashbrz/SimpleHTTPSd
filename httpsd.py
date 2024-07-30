# Base taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# Generate certificate with the following commands:
# Generate the private key
#    openssl genpkey -algorithm RSA -out key.pem
# Generate the self-signed certificate
#    openssl req -new -x509 -key key.pem -out cert.pem -days 365
# Run as follows:
#    python httpsd.py -i ip -p port 
#    Or just: python httpsd.py to run it on localhost and 443 port.
# Type the password you have used to generate the certificate
# Then in your browser, visit:
#    https://<IP>:<PORT>

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import os
import argparse

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get the requested file path
        requested_path = self.path.strip("/")

        # If no specific file is requested, serve the index.html
        if not requested_path:
            requested_path = "index.html"

        # Ensure the requested path does not break out of the server's directory
        safe_path = os.path.join(os.getcwd(), os.path.normpath(requested_path))

        try:
            # Check if the requested file exists
            if os.path.isfile(safe_path):
                # Determine the content type
                if safe_path.endswith(".html"):
                    content_type = "text/html"
                elif safe_path.endswith(".css"):
                    content_type = "text/css"
                elif safe_path.endswith(".js"):
                    content_type = "application/javascript"
                elif safe_path.endswith(".png"):
                    content_type = "image/png"
                elif safe_path.endswith(".jpg") or safe_path.endswith(".jpeg"):
                    content_type = "image/jpeg"
                else:
                    content_type = "application/octet-stream"

                # Read and send the file content
                with open(safe_path, "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.end_headers()
                    self.wfile.write(file.read())
            else:
                # File not found
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"404 Not Found")
        except Exception as e:
            # Internal server error
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Internal Server Error: {e}".encode("utf-8"))

def run_server(ip_address, port):
    httpd = HTTPServer((ip_address, port), SimpleHTTPRequestHandler)
    
    # Use SSLContext for wrapping the socket
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving on https://{ip_address}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple HTTPS Server")
    parser.add_argument("-i", "--ip", type=str, default="127.0.0.1", help="IP address to bind the server")
    parser.add_argument("-p", "--port", type=int, default=443, help="Port to bind the server")
    args = parser.parse_args()
    
    run_server(args.ip, args.port)
