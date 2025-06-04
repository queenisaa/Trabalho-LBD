# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import ENUM

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    CPF = db.Column(db.String(100), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    tipo_usuario = db.Column(ENUM('Funcionario', 'Cliente'), nullable=False)
    senha_hash = db.Column(db.String(32), nullable=False)
    otp_ativo = db.Column(db.String(6))
    oto_expiracao = db.Column(db.DateTime)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    score_credito = db.Column(db.Numeric(5, 2), default=0)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Funcionario(db.Model):
    __tablename__ = 'funcionario'
    id_funcionario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_funcionario = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(ENUM('Estagiario', 'Atendente', 'Gerente'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))
    id_supervisor = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'))

class Endereco(db.Model):
    __tablename__ = 'endereco'
    id_endereco = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cep = db.Column(db.String(100), nullable=False)
    local = db.Column(db.String(100), nullable=False)
    numero_casa = db.Column(db.Integer, nullable=False)
    bairro = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    complemento = db.Column(db.String(50))

class Agencia(db.Model):
    __tablename__ = 'agencia'
    id_agencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    codigo_agencia = db.Column(db.String(10), unique=True, nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey('endereco.id_endereco'))

class Conta(db.Model):
    __tablename__ = 'conta'
    id_conta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_conta = db.Column(db.String(20), unique=True, nullable=False)
    saldo = db.Column(db.Numeric(15, 2), default=0)
    tipo_conta = db.Column(ENUM('Poupanca', 'Corrente', 'Investimento'), nullable=False)
    data_abertura = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    status = db.Column(ENUM('Ativa', 'Encerrada', 'Bloqueada'), default='Ativa')
    id_agencia = db.Column(db.Integer, db.ForeignKey('agencia.id_agencia'))
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'))

class ContaPoupanca(db.Model):
    __tablename__ = 'conta_poupanca'
    id_conta_poupanca = db.Column(db.Integer, primary_key=True, autoincrement=True)
    taxa_rendimento = db.Column(db.Numeric(5, 2), nullable=False)
    ultimo_rendimento = db.Column(db.DateTime)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))

class ContaCorrente(db.Model):
    __tablename__ = 'conta_corrente'
    id_conta_corrente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    limite = db.Column(db.Numeric(5, 2), default=0)
    data_vencimento = db.Column(db.Date, nullable=False)
    taxa_manutencao = db.Column(db.Numeric(5, 2), default=0)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))

class ContaInvestimento(db.Model):
    __tablename__ = 'conta_investimento'
    id_conta_investimento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    perfil_risco = db.Column(ENUM('Baixo', 'Medio', 'Alta'), nullable=False)
    valor_minimo = db.Column(db.Numeric(15, 2), nullable=False)
    taxa_rendimento_base = db.Column(db.Numeric(5, 2), nullable=False)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))

class Transacao(db.Model):
    __tablename__ = 'transacao'
    id_transacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_transacao = db.Column(ENUM('Deposito', 'Saque', 'Transferencia', 'Taxa', 'Rendimento'), nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    data_hora = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    descricao = db.Column(db.String(100))
    id_conta_origem = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))
    id_conta_destino = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id_auditoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    acao = db.Column(db.String(50), nullable=False)
    data_hora = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    detalhes = db.Column(db.Text)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class Relatorio(db.Model):
    __tablename__ = 'relatorio'
    id_relatorio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_relatorio = db.Column(db.String(50), nullable=False)
    data_geracao = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    conteudo = db.Column(db.Text, nullable=False)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'))
