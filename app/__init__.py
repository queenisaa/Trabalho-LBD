# app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.models import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importa os blueprints
    from app.auth.routes import auth_bp
    from app.cliente.routes import cliente_bp
    from app.funcionario.routes import funcionario_bp # <-- 1. IMPORTAR O NOVO BLUEPRINT

    # Registra os blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    app.register_blueprint(funcionario_bp, url_prefix='/funcionario') # <-- 2. REGISTRAR O NOVO BLUEPRINT

    return app