from flask import Flask
from flask_migrate import Migrate
from config import Config
from .models import db

migrate = Migrate()

def create_app():
    """
    Fábrica da aplicação: cria, configura e registra os componentes.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .auth.routes import auth_bp
    from .cliente.routes import cliente_bp
    
    app.register_blueprint(auth_bp)
    
    app.register_blueprint(cliente_bp, url_prefix='/cliente')

    return app
