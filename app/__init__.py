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

    from app.auth.routes import auth_bp
    from app.cliente.routes import cliente_bp
    from app.funcionario.routes import funcionario_bp 

    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    app.register_blueprint(funcionario_bp, url_prefix='/funcionario') 

    return app
