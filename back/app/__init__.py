from flask import Flask
from flask_cors import CORS
from app.database.db import init_db

def create_app():
    app = Flask(__name__)
    
    # Habilita CORS para permitir que o frontend acesse os endpoints
    CORS(app)
    
    # Inicializa o banco de dados (cria o arquivo database.db e a tabela se não existirem)
    init_db()
    
    # Importar e registrar os blueprints (rotas)
    from app.routes.lancamentos_routes import lancamentos_bp
    
    app.register_blueprint(lancamentos_bp, url_prefix='/api')
    
    return app
