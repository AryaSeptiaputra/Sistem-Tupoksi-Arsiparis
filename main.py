from app import create_app
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = create_app()

# Trust X-Forwarded-* headers from reverse proxy (IIS/Nginx)
# Aktifkan ini jika menggunakan reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,      # X-Forwarded-For
    x_proto=1,    # X-Forwarded-Proto  
    x_host=1,     # X-Forwarded-Host
    x_prefix=1    # X-Forwarded-Prefix
)

if __name__ == '__main__':
    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)