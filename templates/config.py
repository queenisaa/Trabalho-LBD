# config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key para sessões do Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")

    # URI de conexão com o MySQL (altere 'seu_usuario', 'sua_senha' e 'banco_db' para os seus valores)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:c%40tolic%40@localhost/banco_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
