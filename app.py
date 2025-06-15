# ================== IMPORTAÇÕES ==================
import os
import random
from datetime import datetime, timedelta, timezone
from functools import wraps
from decimal import Decimal
import io

# Flask e extensões
from flask import (Flask, Blueprint, render_template, request, redirect,
                   url_for, flash, session, send_file)
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from sqlalchemy import or_, func

# Módulos locais
from config import Config
from models import db, Usuario, Cliente, Conta, Transacao, ContaCorrente, ContaPoupanca
from auth_services import enviar_email_otp
import pandas as pd

# ================== CONFIGURAÇÃO DO BLUEPRINT E CONSTANTES ==================
main_bp = Blueprint('main', __name__)
LIMITE_DIARIO_DEPOSITO = Decimal('10000.00')
TAXA_SAQUE_EXCESSIVO = Decimal('5.00')
LIMITE_SAQUES_GRATUITOS = 5

# ================== DECORADOR DE AUTENTICAÇÃO ==================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Você precisa fazer login para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            if role and session.get('user_type') != role:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ================== ROTAS ==================

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['POST'])
def login():
    if os.path.exists('token.json'):
        os.remove('token.json')
    cpf_recebido = request.form.get('cpf', '').strip()
    senha_recebida = request.form.get('senha', '').strip()
    tipo_recebido = request.form.get('tipo', '').strip()
    usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()
    if usuario and check_password_hash(usuario.senha_hash, senha_recebida):
        otp = str(random.randint(100000, 999999))
        if enviar_email_otp(usuario.email, usuario.nome, otp):
            usuario.otp_ativo = otp
            usuario.otp_expiracao = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.session.commit()
            session['id_usuario_para_verificar'] = usuario.id_usuario
            flash('Um código de verificação foi enviado para o seu e-mail.', 'info')
            return redirect(url_for('main.verify_otp'))
        else:
            return redirect(url_for('main.index'))
    else:
        flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'id_usuario_para_verificar' not in session:
        return redirect(url_for('main.index'))
    user_id = session['id_usuario_para_verificar']
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        submitted_otp = request.form.get('otp')
        expiracao = usuario.otp_expiracao
        if expiracao and expiracao.tzinfo is None:
            expiracao = expiracao.replace(tzinfo=timezone.utc)
        if usuario.otp_ativo == submitted_otp and expiracao and datetime.now(timezone.utc) < expiracao:
            usuario.otp_ativo = None
            usuario.otp_expiracao = None
            db.session.commit()
            session.pop('id_usuario_para_verificar', None)
            session['user_id'] = usuario.id_usuario
            session['user_type'] = usuario.tipo_usuario
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        else:
            flash('Código OTP inválido ou expirado.', 'danger')
            return redirect(url_for('main.index'))
    return render_template('verify_otp.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    if os.path.exists('token.json'):
        os.remove('token.json')
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard_cliente')
@login_required(role='Cliente')
def dashboard_cliente():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    saldo_atual = 0.0
    ultimas_transacoes = []
    detalhes_conta = None
    if conta:
        saldo_atual = conta.saldo
        if isinstance(conta, ContaCorrente):
            detalhes_conta = {'limite_cheque_especial': conta.limite_cheque_especial}
        elif isinstance(conta, ContaPoupanca):
            detalhes_conta = {'taxa_rendimento': conta.taxa_rendimento}
        ultimas_transacoes = Transacao.query.filter(
            or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta)
        ).order_by(Transacao.data_hora.desc()).limit(5).all()
    return render_template('dashboard_cliente.html',
                           nome_usuario=cliente.usuario.nome,
                           saldo=saldo_atual,
                           transacoes=ultimas_transacoes,
                           conta_id=conta.id_conta if conta else None,
                           tipo_conta=conta.tipo_conta if conta else None,
                           detalhes_conta=detalhes_conta)

@main_bp.route('/deposito', methods=['GET', 'POST'])
@login_required(role='Cliente')
def deposito():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        valor_str = request.form.get('valor')
        try:
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                raise ValueError("O valor do depósito deve ser positivo.")
            hoje_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            depositos_hoje = db.session.query(func.sum(Transacao.valor)).filter(
                Transacao.id_conta_destino == conta.id_conta,
                Transacao.tipo_transacao == 'Deposito',
                Transacao.data_hora >= hoje_inicio
            ).scalar() or Decimal('0')
            if depositos_hoje + valor > LIMITE_DIARIO_DEPOSITO:
                raise ValueError(f"Limite de depósito diário (R$ {LIMITE_DIARIO_DEPOSITO:.2f}) excedido.")
            conta.saldo += valor
            nova_transacao = Transacao(tipo_transacao='Deposito', valor=valor, descricao='Depósito em conta', id_conta_destino=conta.id_conta)
            db.session.add(nova_transacao)
            db.session.commit()
            flash(f'Depósito de R$ {valor:.2f} realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('deposito.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao processar o depósito.', 'danger')
            return render_template('deposito.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)
    return render_template('deposito.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)

@main_bp.route('/saque', methods=['GET', 'POST'])
@login_required(role='Cliente')
def saque():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        valor_str = request.form.get('valor')
        try:
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                raise ValueError("O valor do saque deve ser positivo.")
            saldo_disponivel = conta.saldo
            if isinstance(conta, ContaCorrente):
                saldo_disponivel += conta.limite_cheque_especial
            if saldo_disponivel < valor:
                raise ValueError("Saldo insuficiente para realizar o saque.")
            mes_inicio = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            saques_mes = db.session.query(Transacao).filter(Transacao.id_conta_origem == conta.id_conta, Transacao.tipo_transacao == 'Saque', Transacao.data_hora >= mes_inicio).count()
            taxa_aplicada = Decimal('0.00')
            if saques_mes >= LIMITE_SAQUES_GRATUITOS:
                taxa_aplicada = TAXA_SAQUE_EXCESSIVO
                if saldo_disponivel < valor + taxa_aplicada:
                    raise ValueError("Saldo insuficiente para cobrir o saque e a taxa de serviço.")
                flash(f'Taxa de R$ {taxa_aplicada:.2f} aplicada por exceder o limite de saques mensais.', 'warning')
            conta.saldo -= (valor + taxa_aplicada)
            descricao_saque = f'Saque da conta'
            if taxa_aplicada > 0:
                descricao_saque += f' (inclui taxa de R$ {taxa_aplicada:.2f})'
            nova_transacao = Transacao(tipo_transacao='Saque', valor=valor, descricao=descricao_saque, id_conta_origem=conta.id_conta)
            db.session.add(nova_transacao)
            db.session.commit()
            flash(f'Saque de R$ {valor:.2f} realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('saque.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)
        except Exception:
            db.session.rollback()
            flash('Ocorreu um erro ao processar o saque.', 'danger')
            return render_template('saque.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)
    return render_template('saque.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)

@main_bp.route('/transferencia', methods=['GET', 'POST'])
@login_required(role='Cliente')
def transferencia():
    cliente_origem = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta_origem = cliente_origem.contas[0] if cliente_origem.contas else None
    if not conta_origem:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    if request.method == 'POST':
        try:
            numero_conta_destino = request.form.get('numero_conta_destino')
            valor_str = request.form.get('valor')
            valor = Decimal(valor_str.replace(',', '.'))
            if valor <= 0:
                raise ValueError('O valor da transferência deve ser positivo.')
            conta_destino = Conta.query.filter_by(numero_conta=numero_conta_destino).first()
            if not conta_destino:
                raise ValueError('A conta de destino não foi encontrada.')
            if conta_destino.id_conta == conta_origem.id_conta:
                raise ValueError('Você não pode transferir para a sua própria conta.')
            if conta_origem.saldo < valor:
                raise ValueError('Saldo insuficiente para realizar a transferência.')
            conta_origem.saldo -= valor
            conta_destino.saldo += valor
            nova_transacao = Transacao(tipo_transacao='Transferencia', valor=valor, descricao=f'Transferência para {conta_destino.numero_conta}', id_conta_origem=conta_origem.id_conta, id_conta_destino=conta_destino.id_conta)
            db.session.add(nova_transacao)
            db.session.commit()
            flash(f'Transferência de R$ {valor:.2f} realizada com sucesso!', 'success')
            return redirect(url_for('main.dashboard_cliente'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao processar a transferência. Tente novamente.', 'danger')
        return render_template('transferencia.html', saldo=conta_origem.saldo, nome_usuario=cliente_origem.usuario.nome)
    return render_template('transferencia.html', saldo=conta_origem.saldo, nome_usuario=cliente_origem.usuario.nome)

@main_bp.route('/limite')
@login_required(role='Cliente')
def limite():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    score = cliente.score_credito
    limite_atual = score * Decimal('1.5')
    fator_projecao = Decimal('1') + (score / Decimal('2000'))
    limite_projecao = limite_atual * fator_projecao
    return render_template('limite.html',
                           nome_usuario=cliente.usuario.nome,
                           limite_atual=limite_atual,
                           limite_projecao=limite_projecao,
                           score_credito=score)

@main_bp.route('/extrato')
@login_required(role='Cliente')
def extrato():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('main.dashboard_cliente'))
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str:
        query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str:
        query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    if not data_inicio_str and not data_fim_str:
        transacoes = query.order_by(Transacao.data_hora.desc()).limit(50).all()
    else:
        transacoes = query.order_by(Transacao.data_hora.desc()).all()
    return render_template('extrato.html', 
                           transacoes=transacoes, 
                           conta_id=conta.id_conta,
                           data_inicio=data_inicio_str,
                           data_fim=data_fim_str)

@main_bp.route('/extrato/imprimir')
@login_required(role='Cliente')
def imprimir_extrato():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0]
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str:
        query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str:
        query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    transacoes = query.order_by(Transacao.data_hora.desc()).all()
    return render_template('extrato_pdf.html', transacoes=transacoes, conta=conta, cliente=cliente)

@main_bp.route('/extrato/excel')
@login_required(role='Cliente')
def exportar_excel():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0]
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str:
        query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str:
        query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    transacoes_db = query.order_by(Transacao.data_hora.desc()).all()
    dados = []
    for t in transacoes_db:
        valor = t.valor if t.id_conta_destino == conta.id_conta else -t.valor
        dados.append({'Data': t.data_hora.strftime('%d/%m/%Y %H:%M'), 'Tipo': t.tipo_transacao, 'Descrição': t.descricao, 'Valor (R$)': f'{valor:.2f}'})
    df = pd.DataFrame(dados)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Extrato')
    output.seek(0)
    return send_file(output, download_name='extrato.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ================== FÁBRICA DE APLICAÇÃO E EXECUÇÃO ==================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(main_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
