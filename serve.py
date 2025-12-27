from waitress import serve
from main import app
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger('waitress')

if __name__ == "__main__":
    # Bind ke localhost untuk keamanan (akses via reverse proxy)
    # Gunakan 0.0.0.0 hanya jika tidak menggunakan reverse proxy
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 8000))
    threads = int(os.environ.get('THREADS', 6))
    
    print(f"🚀 Server Production Berjalan di http://{host}:{port}")
    print("📌 Untuk akses via domain, gunakan reverse proxy (IIS/Nginx)")
    print("📄 Panduan: docs/REVERSE_PROXY_SETUP.md")
    
    serve(app, host=host, port=port, threads=threads)