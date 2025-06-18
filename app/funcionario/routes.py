# app/funcionario/routes.py

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
import random
from functools import wraps
import re
import os

# Importa os modelos, 'db', e a função 'func' do SQLAlchemy
from app.models import (db, Usuario, Cliente, Funcionario, Conta, Agencia, Auditoria, 
                        HistoricoConta, ContaCorrente, ContaPoupanca, ContaInvestimento)
from sqlalchemy import func
from app.auth_services import enviar_email_otp

# Cria o Blueprint do funcionário
funcionario_bp = Blueprint('funcionario', __name__, template_folder='templates')

# --- DECORADOR DE AUTENTICAÇÃO E CONTEXTO ---
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('user_type') != 'Funcionario':
                flash('Acesso restrito a funcionários.', 'danger')
                return redirect(url_for('auth.index'))
            
            funcionario = Funcionario.query.filter_by(id_usuario=session['user_id']).first()
            if not funcionario:
                session.clear()
                flash('Funcionário não encontrado. Sessão encerrada.', 'danger')
                return redirect(url_for('auth.index'))
            
            session['cargo'] = funcionario.cargo

            # Se um cargo (role) específico é requerido, verifica a permissão
            if role and funcionario.cargo != role:
                flash('Você não tem permissão para esta ação.', 'danger')
                return redirect(url_for('funcionario.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@funcionario_bp.context_processor
def inject_user_info():
    """Injeta informações do funcionário em todos os templates deste blueprint."""
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
        base = random.randint(100000, 999999)
        check = (10 - luhn_checksum(base * 10)) % 10
        num = f"{base}-{check}"
        if not Conta.query.filter_by(numero_conta=num).first(): return num

def generate_employee_code():
    last_id = db.session.query(func.max(Funcionario.id_funcionario)).scalar() or 0
    return f"FUNC{last_id + 1:03d}"

# --- ROTAS DO FUNCIONÁRIO ---

@funcionario_bp.route('/dashboard')
@login_required()
def dashboard():
    return render_template('funcionario/dashboard_funcionario.html')

@funcionario_bp.route('/abertura-conta', methods=['GET', 'POST'])
@login_required()
def abertura_conta():
    if request.method == 'POST':
        try:
            data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date()
            if (date.today() - data_nascimento) < timedelta(days=16*365.25):
                raise ValueError("O cliente deve ter pelo menos 16 anos.")

            cpf_limpo = re.sub(r'\D', '', request.form.get('cpf'))
            if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                raise ValueError("CPF inválido. Deve conter 11 números.")
            if Usuario.query.filter_by(CPF=cpf_limpo).first():
                raise ValueError("Este CPF já está cadastrado.")

            novo_usuario = Usuario(nome=request.form.get('nome'), CPF=cpf_limpo, data_nascimento=data_nascimento, telefone=request.form.get('telefone'), email=request.form.get('email'), tipo_usuario='Cliente', senha_hash=generate_password_hash(request.form.get('senha')))
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
            db.session.flush()

            db.session.add(HistoricoConta(id_conta=nova_conta.id_conta, id_funcionario_responsavel=session['user_id'], acao='Abertura', motivo='Criação de nova conta.'))
            db.session.add(Auditoria(id_usuario=session.get('user_id'), acao='Abertura de Conta', detalhes=f'Conta {tipo_conta} nº {numero_conta_gerado} aberta para {novo_usuario.nome}.'))
            
            db.session.commit()
            flash(f'Conta {tipo_conta} aberta com sucesso! Número da conta: {numero_conta_gerado}', 'success')
            return redirect(url_for('funcionario.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao abrir a conta: {str(e)}', 'danger')
            
    max_dob = date.today().replace(year=date.today().year - 16)
    return render_template('funcionario/abertura_conta.html', max_dob=max_dob)

# --- ROTA DE CADASTRO DE FUNCIONÁRIO ADICIONADA ---
@funcionario_bp.route('/cadastro-funcionario', methods=['GET', 'POST'])
@login_required(role='Gerente') # Apenas Gerentes
def cadastro_funcionario():
    if request.method == 'POST':
        try:
            # Validações e lógica de criação de funcionário
            cpf_limpo = re.sub(r'\D', '', request.form.get('cpf'))
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

            codigo_gerado = generate_employee_code()
            novo_funcionario = Funcionario(
                id_usuario=novo_usuario.id_usuario,
                codigo_funcionario=codigo_gerado,
                cargo=request.form.get('cargo'),
                id_supervisor=session.get('user_id')
            )
            db.session.add(novo_funcionario)
            db.session.commit()
            flash(f'Funcionário {novo_usuario.nome} cadastrado com sucesso! Matrícula: {codigo_gerado}', 'success')
            return redirect(url_for('funcionario.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar funcionário: {str(e)}', 'danger')

    max_dob = date.today().replace(year=date.today().year - 16)
    return render_template('funcionario/cadastro_funcionario.html', max_dob=max_dob)
# ----------------------------------------------------

@funcionario_bp.route('/encerramento-conta', methods=['GET', 'POST'])
@login_required()
def encerramento_conta():
    if session.get('cargo') == 'Estagiario':
        flash('Estagiários não têm permissão para encerrar contas.', 'danger')
        return redirect(url_for('funcionario.dashboard'))
        
    conta_para_encerrar = None
    if request.method == 'POST':
        numero_conta = request.form.get('numero_conta')
        conta_para_encerrar = Conta.query.filter_by(numero_conta=numero_conta).first()
        if not conta_para_encerrar:
            flash('Conta não encontrada.', 'warning')
        elif conta_para_encerrar.status == 'Encerrada':
            flash('Esta conta já está encerrada.', 'info')
            conta_para_encerrar = None
    return render_template('funcionario/encerramento_conta.html', conta=conta_para_encerrar)


@funcionario_bp.route('/encerramento-conta/iniciar', methods=['POST'])
@login_required()
def iniciar_encerramento():
    id_conta = request.form.get('id_conta')
    motivo = request.form.get('motivo')
    conta = Conta.query.get_or_404(id_conta)
    funcionario_logado = Funcionario.query.filter_by(id_usuario=session['user_id']).first()

    try:
        if conta.saldo != 0:
            raise ValueError(f"A conta não pode ser encerrada. Saldo pendente de R$ {conta.saldo:.2f}.")
        
        if os.path.exists('token.json'):
            os.remove('token.json')

        otp = str(random.randint(100000, 999999))
        if enviar_email_otp(funcionario_logado.usuario.email, funcionario_logado.usuario.nome, otp):
            session['encerramento_otp'] = otp
            session['encerramento_conta_id'] = conta.id_conta
            session['encerramento_motivo'] = motivo
            session['encerramento_otp_expiracao'] = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
            
            flash('Um OTP foi enviado ao seu e-mail para confirmar a operação.', 'info')
            return redirect(url_for('funcionario.encerramento_confirmar'))
        else:
            raise Exception("Falha ao enviar e-mail de confirmação com OTP.")
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('funcionario.encerramento_conta'))

@funcionario_bp.route('/encerramento-conta/confirmar', methods=['GET', 'POST'])
@login_required()
def encerramento_confirmar():
    if 'encerramento_conta_id' not in session:
        return redirect(url_for('funcionario.encerramento_conta'))
    
    conta_id = session.get('encerramento_conta_id')
    conta = Conta.query.get(conta_id)

    if request.method == 'POST':
        try:
            senha_admin = request.form.get('senha_admin')
            otp_digitado = request.form.get('otp')
            
            funcionario_logado = Funcionario.query.filter_by(id_usuario=session['user_id']).first()
            expiracao_otp = datetime.fromisoformat(session.get('encerramento_otp_expiracao'))

            if not check_password_hash(funcionario_logado.usuario.senha_hash, senha_admin):
                raise ValueError("Sua senha de confirmação está incorreta.")
            if otp_digitado != session.get('encerramento_otp'):
                raise ValueError("O código OTP está incorreto.")
            if datetime.now(timezone.utc) > expiracao_otp:
                raise ValueError("O código OTP expirou. Por favor, inicie o processo novamente.")

            conta.status = 'Encerrada'
            log_historico = HistoricoConta(
                id_conta=conta.id_conta,
                id_funcionario_responsavel=funcionario_logado.id_usuario,
                acao='Encerramento',
                motivo=session.get('encerramento_motivo')
            )
            db.session.add(log_historico)
            db.session.commit()
            
            for key in ['encerramento_conta_id', 'encerramento_otp', 'encerramento_motivo', 'encerramento_otp_expiracao']:
                session.pop(key, None)
            
            flash(f'Conta {conta.numero_conta} encerrada com sucesso!', 'success')
            return redirect(url_for('funcionario.dashboard'))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception:
            flash('Um erro inesperado ocorreu. Tente novamente.', 'danger')
    
    return render_template('funcionario/encerramento_confirmar.html', conta=conta)
