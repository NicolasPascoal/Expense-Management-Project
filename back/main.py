import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Em desenvolvimento: python main.py (usa o servidor Flask embutido)
    # Em producao: gunicorn -w 4 -b 0.0.0.0:5000 main:app
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
