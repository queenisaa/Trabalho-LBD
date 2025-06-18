import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:18887@localhost/banco_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
