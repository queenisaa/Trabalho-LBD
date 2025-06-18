# app/funcionario/routes.py

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from werkzeug.security import generate_password_hash
from datetime import datetime
from decimal import Decimal
import random
from functools import wraps
import re

# Importa os modelos, 'db', e a função 'func' do SQLAlchemy
from app.models import db, Usuario, Cliente, Funcionario, Conta, Agencia, Auditoria, \
                       ContaCorrente, ContaPoupanca, ContaInvestimento
from sqlalchemy import func

# Cria o Blueprint do funcionário
funcionario_bp = Blueprint('funcionario', __name__, template_folder='templates')

# --- DECORADOR DE AUTENTICAÇÃO ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Você precisa fazer login para acessar esta página.', 'danger')
                return redirect(url_for('auth.index'))
            if role and session.get('user_type') != role:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('auth.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- PROCESSADOR DE CONTEXTO ---
@funcionario_bp.context_processor
def inject_user_info():
    if 'user_id' in session and session.get('user_type') == 'Funcionario':
        funcionario = Funcionario.query.filter_by(id_usuario=session['user_id']).first()
        if funcionario:
            return dict(nome_usuario=funcionario.usuario.nome, cargo=funcionario.cargo)
    return dict(nome_usuario=None, cargo=None)

# --- FUNÇÕES HELPER ---

def luhn_checksum(card_number):
    def digits_of(n): return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits, even_digits = digits[-1::-2], digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def generate_account_number():
    while True:
        base_number = random.randint(100000, 999999)
        check_digit = (10 - luhn_checksum(base_number * 10)) % 10
        account_number = f"{base_number}-{check_digit}"
        if not Conta.query.filter_by(numero_conta=account_number).first():
            return account_number

def generate_employee_code():
    """Gera um código de funcionário único no formato FUNCXXX."""
    # Encontra o último ID de funcionário para criar o próximo
    last_id = db.session.query(func.max(Funcionario.id_funcionario)).scalar() or 0
    next_id = last_id + 1
    # Formata o código com zeros à esquerda, ex: FUNC001, FUNC010, FUNC123
    new_code = f"FUNC{next_id:03d}"
    return new_code

# --- ROTAS DO FUNCIONÁRIO ---

@funcionario_bp.route('/dashboard')
@login_required(role='Funcionario')
def dashboard():
    return render_template('funcionario/dashboard_funcionario.html')

@funcionario_bp.route('/abertura-conta', methods=['GET', 'POST'])
@login_required(role='Funcionario')
def abertura_conta():
    # ... (código da função de abertura de conta continua o mesmo) ...
    if request.method == 'POST':
        try:
            cpf = request.form.get('cpf')
            telefone = request.form.get('telefone')
            
            cpf_limpo = re.sub(r'\D', '', cpf)
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit(): raise ValueError("CPF inválido.")
            if Usuario.query.filter_by(CPF=cpf_limpo).first(): raise ValueError("Este CPF já está cadastrado.")

            telefone_limpo = re.sub(r'\D', '', telefone)
            if not (10 <= len(telefone_limpo) <= 11) or not telefone_limpo.isdigit(): raise ValueError("Telefone inválido.")

            novo_usuario = Usuario(
                nome=request.form.get('nome'), CPF=cpf_limpo,
                data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date(),
                telefone=telefone_limpo, email=request.form.get('email'),
                tipo_usuario='Cliente', senha_hash=generate_password_hash(request.form.get('senha'))
            )
            db.session.add(novo_usuario)
            db.session.flush()

            novo_cliente = Cliente(id_usuario=novo_usuario.id_usuario, score_credito=500)
            db.session.add(novo_cliente)
            db.session.flush()

            tipo_conta = request.form.get('tipo_conta')
            numero_conta_gerado = generate_account_number()
            agencia_padrao = Agencia.query.first()
            if not agencia_padrao: raise Exception("Nenhuma agência cadastrada.")
            
            conta_base_args = {'numero_conta': numero_conta_gerado, 'id_agencia': agencia_padrao.id_agencia, 'id_cliente': novo_cliente.id_cliente, 'saldo': Decimal(request.form.get('saldo_inicial', '0.0'))}

            if tipo_conta == 'Corrente': nova_conta = ContaCorrente(**conta_base_args, limite_cheque_especial=Decimal(request.form.get('limite_cheque_especial')), taxa_manutencao=Decimal(request.form.get('taxa_manutencao')))
            elif tipo_conta == 'Poupanca': nova_conta = ContaPoupanca(**conta_base_args, taxa_rendimento=Decimal(request.form.get('taxa_rendimento')))
            elif tipo_conta == 'Investimento': nova_conta = ContaInvestimento(**conta_base_args, perfil_risco=request.form.get('perfil_risco'), valor_minimo_deposito=Decimal(request.form.get('valor_minimo_deposito')), taxa_rendimento_base=Decimal(request.form.get('taxa_rendimento_base')))
            else: raise ValueError("Tipo de conta inválido.")

            db.session.add(nova_conta)
            log_auditoria = Auditoria(id_usuario=session.get('user_id'), acao='Abertura de Conta', detalhes=f'Conta {tipo_conta} nº {numero_conta_gerado} aberta para o cliente {novo_usuario.nome}.')
            db.session.add(log_auditoria)
            db.session.commit()
            flash(f'Conta {tipo_conta} aberta com sucesso! Número da conta: {numero_conta_gerado}', 'success')
            return redirect(url_for('funcionario.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao abrir a conta: {str(e)}', 'danger')
    
    return render_template('funcionario/abertura_conta.html')


@funcionario_bp.route('/cadastro-funcionario', methods=['GET', 'POST'])
@login_required(role='Funcionario')
def cadastro_funcionario():
    funcionario_logado = Funcionario.query.filter_by(id_usuario=session['user_id']).first()
    if not funcionario_logado or funcionario_logado.cargo != 'Gerente':
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('funcionario.dashboard'))

    if request.method == 'POST':
        try:
            cpf = request.form.get('cpf')
            cpf_limpo = re.sub(r'\D', '', cpf)
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit(): raise ValueError("CPF inválido.")
            if Usuario.query.filter_by(CPF=cpf_limpo).first(): raise ValueError("Este CPF já está cadastrado.")
            
            novo_usuario = Usuario(
                nome=request.form.get('nome'), CPF=cpf_limpo,
                data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date(),
                telefone=re.sub(r'\D', '', request.form.get('telefone')),
                email=request.form.get('email'), tipo_usuario='Funcionario',
                senha_hash=generate_password_hash(request.form.get('senha'))
            )
            db.session.add(novo_usuario)
            db.session.flush()

            # --- CORREÇÃO APLICADA AQUI ---
            # O código do funcionário agora é gerado automaticamente
            codigo_gerado = generate_employee_code()

            novo_funcionario = Funcionario(
                id_usuario=novo_usuario.id_usuario,
                codigo_funcionario=codigo_gerado,
                cargo=request.form.get('cargo'),
                id_supervisor=funcionario_logado.id_funcionario
            )
            db.session.add(novo_funcionario)
            db.session.commit()
            flash(f'Funcionário {novo_usuario.nome} cadastrado com sucesso! Matrícula: {codigo_gerado}', 'success')
            return redirect(url_for('funcionario.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar funcionário: {str(e)}', 'danger')

    return render_template('funcionario/cadastro_funcionario.html')
