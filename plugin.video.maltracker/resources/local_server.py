import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import xbmcgui

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        import xbmc
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        xbmc.log(f'MAL Callback: Received request to {self.path}', xbmc.LOGDEBUG)
        
        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            xbmc.log('MAL Callback: Authorization code received successfully', xbmc.LOGINFO)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Página de éxito estilo MALSync
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
            xbmc.log(f'MAL Callback: OAuth error - {error}', xbmc.LOGERROR)
            
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            error_page = f'''<!DOCTYPE html>
<html><head><title>MAL Tracker - Error</title>
<style>body{{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#f0f0f0}}
.error{{color:#dc3545;font-size:24px;margin-bottom:20px}}</style></head>
<body><div class="error">✗ Error de Autenticacion</div>
<p>Error: {error}</p><p>Cierra esta ventana e intentalo de nuevo.</p></body></html>'''
            self.wfile.write(error_page.encode('utf-8'))
            
        else:
            xbmc.log('MAL Callback: No authorization code received', xbmc.LOGWARNING)
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            error_page = '''<!DOCTYPE html>
<html><head><title>MAL Tracker - Error</title>
<style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#f0f0f0}
.error{color:#dc3545;font-size:24px;margin-bottom:20px}</style></head>
<body><div class="error">✗ Error</div>
<p>No se recibio codigo de autorizacion.</p></body></html>'''
            self.wfile.write(error_page.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Silenciar logs

def start_callback_server():
    import xbmc
    CallbackHandler.auth_code = None
    
    try:
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        server.timeout = 60
        xbmc.log('MAL Callback: Server started on port 8080', xbmc.LOGINFO)
        
        server.handle_request()
        auth_code = getattr(CallbackHandler, 'auth_code', None)
        
        if auth_code:
            xbmc.log('MAL Callback: Authorization code captured successfully', xbmc.LOGINFO)
        else:
            xbmc.log('MAL Callback: No authorization code received', xbmc.LOGWARNING)
            
        return auth_code
        
    except Exception as e:
        xbmc.log(f'MAL Callback: Server error - {str(e)}', xbmc.LOGERROR)
        return None