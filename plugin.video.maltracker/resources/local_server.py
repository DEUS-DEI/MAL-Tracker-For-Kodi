import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import xbmcgui

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Autenticacion exitosa!</h1><p>Puedes cerrar esta ventana.</p></body></html>')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Error</h1><p>No se recibio codigo.</p></body></html>')
    
    def log_message(self, format, *args):
        pass  # Silenciar logs

def start_callback_server():
    CallbackHandler.auth_code = None
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.timeout = 60  # 60 segundos timeout
    server.handle_request()  # Solo una request
    return getattr(CallbackHandler, 'auth_code', None)