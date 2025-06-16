from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import ENUM
from datetime import datetime, timezone

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    CPF = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tipo_usuario = db.Column(ENUM('Funcionario', 'Cliente'), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    otp_ativo = db.Column(db.String(6))
    otp_expiracao = db.Column(db.DateTime)

    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False, cascade="all, delete-orphan")
    funcionario = db.relationship('Funcionario', back_populates='usuario', uselist=False, cascade="all, delete-orphan")
    auditorias = db.relationship('Auditoria', back_populates='usuario')

class Funcionario(db.Model):
    __tablename__ = 'funcionario'
    id_funcionario = db.Column(db.Integer, primary_key=True)
    codigo_funcionario = db.Column(db.String(20), unique=True, nullable=False)
    cargo = db.Column(ENUM('Estagiario', 'Atendente', 'Gerente'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False, unique=True)
    id_supervisor = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'))
    usuario = db.relationship('Usuario', back_populates='funcionario')
    supervisor = db.relationship('Funcionario', remote_side=[id_funcionario], back_populates='subordinados')
    subordinados = db.relationship('Funcionario', back_populates='supervisor')
    relatorios = db.relationship('Relatorio', back_populates='funcionario')

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False, unique=True)
    score_credito = db.Column(db.Numeric(5, 2), default=0)
    usuario = db.relationship('Usuario', back_populates='cliente')
    contas = db.relationship('Conta', back_populates='cliente', cascade="all, delete-orphan")

class Endereco(db.Model):
    __tablename__ = 'endereco'
    id_endereco = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(9), nullable=False)
    local = db.Column(db.String(100), nullable=False)
    numero_casa = db.Column(db.Integer, nullable=False)
    bairro = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    complemento = db.Column(db.String(50))

class Agencia(db.Model):
    __tablename__ = 'agencia'
    id_agencia = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    codigo_agencia = db.Column(db.String(10), unique=True, nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey('endereco.id_endereco'), nullable=False)
    endereco = db.relationship('Endereco')
    contas = db.relationship('Conta', back_populates='agencia')

class Conta(db.Model):
    __tablename__ = 'conta'
    id_conta = db.Column(db.Integer, primary_key=True)
    numero_conta = db.Column(db.String(20), unique=True, nullable=False)
    saldo = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    tipo_conta = db.Column(ENUM('Poupanca', 'Corrente', 'Investimento'), nullable=False)
    data_abertura = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    status = db.Column(ENUM('Ativa', 'Encerrada', 'Bloqueada'), nullable=False, default='Ativa')
    id_agencia = db.Column(db.Integer, db.ForeignKey('agencia.id_agencia'), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    agencia = db.relationship('Agencia', back_populates='contas')
    cliente = db.relationship('Cliente', back_populates='contas')
    transacoes_origem = db.relationship('Transacao', foreign_keys='Transacao.id_conta_origem', back_populates='conta_origem')
    transacoes_destino = db.relationship('Transacao', foreign_keys='Transacao.id_conta_destino', back_populates='conta_destino')
    __mapper_args__ = {'polymorphic_on': tipo_conta}

class ContaPoupanca(Conta):
    __tablename__ = 'conta_poupanca'
    id_conta_poupanca = db.Column(db.Integer, primary_key=True)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'), nullable=False)
    taxa_rendimento = db.Column(db.Numeric(5, 2), nullable=False)
    ultimo_rendimento = db.Column(db.DateTime)
    __mapper_args__ = {'polymorphic_identity': 'Poupanca'}

class ContaCorrente(Conta):
    __tablename__ = 'conta_corrente'
    id_conta_corrente = db.Column(db.Integer, primary_key=True)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'), nullable=False)
    limite_cheque_especial = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    taxa_manutencao = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    __mapper_args__ = {'polymorphic_identity': 'Corrente'}

class ContaInvestimento(Conta):
    __tablename__ = 'conta_investimento'
    id_conta_investimento = db.Column(db.Integer, primary_key=True)
    id_conta = db.Column(db.Integer, db.ForeignKey('conta.id_conta'), nullable=False)
    perfil_risco = db.Column(ENUM('Baixo', 'Medio', 'Alto'), nullable=False)
    valor_minimo_deposito = db.Column(db.Numeric(15, 2), nullable=False)
    taxa_rendimento_base = db.Column(db.Numeric(5, 2), nullable=False)
    __mapper_args__ = {'polymorphic_identity': 'Investimento'}

class Transacao(db.Model):
    __tablename__ = 'transacao'
    id_transacao = db.Column(db.Integer, primary_key=True)
    tipo_transacao = db.Column(ENUM('Deposito', 'Saque', 'Transferencia', 'Pagamento', 'Rendimento'), nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    descricao = db.Column(db.String(100))
    id_conta_origem = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))
    id_conta_destino = db.Column(db.Integer, db.ForeignKey('conta.id_conta'))
    conta_origem = db.relationship('Conta', foreign_keys=[id_conta_origem], back_populates='transacoes_origem')
    conta_destino = db.relationship('Conta', foreign_keys=[id_conta_destino], back_populates='transacoes_destino')

class Auditoria(db.Model):
    __tablename__ = 'auditoria'
    id_auditoria = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    acao = db.Column(db.String(50), nullable=False)
    
    data_hora = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    detalhes = db.Column(db.Text)
    usuario = db.relationship('Usuario', back_populates='auditorias')

class Relatorio(db.Model):
    __tablename__ = 'relatorio'
    id_relatorio = db.Column(db.Integer, primary_key=True)
    id_funcionario = db.Column(db.Integer, db.ForeignKey('funcionario.id_funcionario'), nullable=False)
    tipo_relatorio = db.Column(db.String(50), nullable=False)
    data_geracao = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    conteudo = db.Column(db.Text, nullable=False)
    funcionario = db.relationship('Funcionario', back_populates='relatorios')
