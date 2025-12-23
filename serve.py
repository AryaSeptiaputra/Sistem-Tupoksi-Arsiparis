from waitress import serve
from main import app
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger('waitress')

if __name__ == "__main__":
    print("🚀 Server Production Berjalan di http://0.0.0.0:8080")
    serve(app, host='0.0.0.0', port=8080, threads=6)