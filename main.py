from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)