import sys
import os

# Activa el entorno virtual
activate_this = '/home/u6-ws4csemxvlh3/www/lodorol3.sg-host.com/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Configuración de rutas
sys.path.insert(0, "/home/u6-ws4csemxvlh3/www/lodorol3.sg-host.com")
os.chdir("/home/u6-ws4csemxvlh3/www/lodorol3.sg-host.com")

# Variables de entorno
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lodoro_analytics.settings")

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    # Escribir el error en un archivo para depuración
    with open('/home/u6-ws4csemxvlh3/www/lodorol3.sg-host.com/error_django.log', 'w') as f:
        f.write(f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}")
    def application(environ, start_response):
        status = '500 Internal Server Error'
        error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        output = error_msg.encode('utf-8')
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output] 