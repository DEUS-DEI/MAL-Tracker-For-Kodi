import threading
import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import xbmcgui

class CallbackHandler(BaseHTTPRequestHandler):
    auth_code = None
    server_should_stop = False
    
    def do_GET(self):
        import xbmc
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        xbmc.log(f'MAL Callback: Received request to {self.path}', xbmc.LOGDEBUG)
        
        # Manejar favicon y otros requests
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return
            
        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            CallbackHandler.server_should_stop = True
            xbmc.log('MAL Callback: Authorization code received successfully', xbmc.LOGINFO)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            success_page = '''<!DOCTYPE html>
<html><head><title>MAL Tracker - Autenticacion Exitosa</title>
<style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#f0f0f0}
.success{color:#28a745;font-size:24px;margin-bottom:20px}</style></head>
<body><div class="success">✓ Autenticacion Exitosa</div>
<p>Ya puedes cerrar esta ventana y volver a Kodi.</p>
<script>setTimeout(()=>window.close(),3000)</script></body></html>'''
            self.wfile.write(success_page.encode('utf-8'))
            
        elif 'error' in params:
            error = params.get('error', ['unknown'])[0]
            error_desc = params.get('error_description', [''])[0]
            CallbackHandler.server_should_stop = True
            xbmc.log(f'MAL Callback: OAuth error - {error}: {error_desc}', xbmc.LOGERROR)
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            error_page = f'''<!DOCTYPE html>
<html><head><title>MAL Tracker - Error</title>
<style>body{{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#f0f0f0}}
.error{{color:#dc3545;font-size:24px;margin-bottom:20px}}</style></head>
<body><div class="error">✗ Error de Autenticacion</div>
<p>Error: {error}</p><p>{error_desc}</p><p>Cierra esta ventana e intentalo de nuevo.</p></body></html>'''
            self.wfile.write(error_page.encode('utf-8'))
            
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            waiting_page = '''<!DOCTYPE html>
<html><head><title>MAL Tracker - Esperando</title>
<style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#f0f0f0}</style></head>
<body><h2>Esperando autorizacion...</h2><p>Autoriza la aplicacion en MyAnimeList</p></body></html>'''
            self.wfile.write(waiting_page.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Silenciar logs

def start_callback_server():
    import xbmc
    CallbackHandler.auth_code = None
    CallbackHandler.server_should_stop = False
    
    try:
        # Verificar si el puerto está disponible
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        
        if result == 0:
            xbmc.log('MAL Callback: Port 8080 already in use', xbmc.LOGWARNING)
            return None
            
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        server.timeout = 2  # Timeout corto para permitir múltiples requests
        xbmc.log('MAL Callback: Server started on port 8080', xbmc.LOGINFO)
        
        # Manejar múltiples requests hasta obtener el código
        start_time = time.time()
        while not CallbackHandler.server_should_stop and (time.time() - start_time) < 120:
            try:
                server.handle_request()
            except socket.timeout:
                continue
            except Exception as e:
                xbmc.log(f'MAL Callback: Request handling error - {str(e)}', xbmc.LOGDEBUG)
                continue
                
        server.server_close()
        auth_code = CallbackHandler.auth_code
        
        if auth_code:
            xbmc.log('MAL Callback: Authorization code captured successfully', xbmc.LOGINFO)
        else:
            xbmc.log('MAL Callback: No authorization code received within timeout', xbmc.LOGWARNING)
            
        return auth_code
        
    except Exception as e:
        xbmc.log(f'MAL Callback: Server error - {str(e)}', xbmc.LOGERROR)
        return None