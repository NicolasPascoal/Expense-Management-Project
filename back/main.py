import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")

    if debug_mode:
        # Modo desenvolvimento: servidor embutido do Flask com hot-reload
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # Modo produção no Windows: Waitress (WSGI server robusto)
        from waitress import serve
        port = int(os.getenv("PORT", 5000))
        print(f" * Servidor de produção iniciado em http://0.0.0.0:{port}")
        print(f" * Pressione CTRL+C para parar")
        serve(app, host='0.0.0.0', port=port, threads=8)
