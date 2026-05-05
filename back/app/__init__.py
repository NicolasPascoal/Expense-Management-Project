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
    from app.routes.projeto_routes import projeto_bp
    from app.routes.servicos_routes import servicos_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.usuarios_routes import usuarios_bp
    from app.routes.requisicao_routes import requisicao_bp
    
    app.register_blueprint(lancamentos_bp, url_prefix='/api')
    app.register_blueprint(projeto_bp, url_prefix='/api')
    app.register_blueprint(servicos_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(requisicao_bp, url_prefix='/api')
    
    return app
