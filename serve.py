from waitress import serve
from main import app
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger('waitress')

if __name__ == "__main__":
    # Bind ke 0.0.0.0 agar bisa diakses dari device lain
    # Gunakan 127.0.0.1 jika hanya ingin akses lokal
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 6001))
    # Increase default threads to reduce waitress queue depth warnings under light bursts
    threads = int(os.environ.get('THREADS', 12))
    
    print("[SERVER] Production running at http://{}:{}".format(host, port))
    print("[INFO] Akses dari device lain: http://<IP-Komputer-Ini>:{}".format(port))
    print("[INFO] For domain access, use reverse proxy (IIS/Nginx)")
    print("[DOCS] Guide: docs/REVERSE_PROXY_SETUP.md")
    
    serve(app, host=host, port=port, threads=threads)