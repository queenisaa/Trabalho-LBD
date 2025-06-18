from functools import wraps
from decimal import Decimal
import io
from datetime import datetime, timedelta, timezone
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, send_file)
from sqlalchemy import or_, func
import pandas as pd
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from app.models import db, Cliente, Conta, Transacao, ContaCorrente, ContaPoupanca, ContaInvestimento

cliente_bp = Blueprint('cliente', __name__)

LIMITE_DIARIO_DEPOSITO = Decimal('10000.00')
TAXA_SAQUE_EXCESSIVO = Decimal('5.00')
LIMITE_SAQUES_GRATUITOS = 5

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


@cliente_bp.route('/dashboard')
@login_required(role='Cliente')
def dashboard():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    saldo_atual, ultimas_transacoes, detalhes_conta = 0.0, [], None
    if conta:
        saldo_atual = conta.saldo
        if isinstance(conta, ContaCorrente):
            detalhes_conta = {'limite_cheque_especial': conta.limite_cheque_especial}
        elif isinstance(conta, ContaPoupanca):
            detalhes_conta = {'taxa_rendimento': conta.taxa_rendimento}
        elif isinstance(conta, ContaInvestimento):
            detalhes_conta = {'perfil_risco': conta.perfil_risco, 'valor_minimo_deposito': conta.valor_minimo_deposito}
        ultimas_transacoes = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta)).order_by(Transacao.data_hora.desc()).limit(5).all()
    return render_template('cliente/dashboard_cliente.html',
                           nome_usuario=cliente.usuario.nome, saldo=saldo_atual, transacoes=ultimas_transacoes,
                           conta_id=conta.id_conta if conta else None, tipo_conta=conta.tipo_conta if conta else None,
                           detalhes_conta=detalhes_conta)


@cliente_bp.route('/deposito', methods=['GET', 'POST'])
@login_required(role='Cliente')
def deposito():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('cliente.dashboard'))
    if request.method == 'POST':
        try:
            valor = Decimal(request.form.get('valor').replace(',', '.'))
            if valor <= 0: raise ValueError("O valor do depósito deve ser positivo.")
            if isinstance(conta, ContaInvestimento) and valor < conta.valor_minimo_deposito:
                raise ValueError(f"O depósito mínimo é de R$ {conta.valor_minimo_deposito:.2f}.")
            
            inicio_janela_24h = datetime.now(timezone.utc) - timedelta(hours=24)
            
            depositos_recentes = db.session.query(func.sum(Transacao.valor)).filter(
                Transacao.id_conta_destino == conta.id_conta,
                Transacao.tipo_transacao == 'Deposito',
                Transacao.data_hora >= inicio_janela_24h
            ).scalar() or Decimal('0')

            if depositos_recentes + valor > LIMITE_DIARIO_DEPOSITO:
                raise ValueError(f"Limite de depósito de R$ {LIMITE_DIARIO_DEPOSITO:.2f} nas últimas 24 horas foi excedido.")

            conta.saldo += valor
            db.session.add(Transacao(tipo_transacao='Deposito', valor=valor, descricao="Depósito em conta", id_conta_destino=conta.id_conta))
            db.session.commit()
            flash('Depósito realizado com sucesso!', 'success')
            return redirect(url_for('cliente.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao processar o depósito.', 'danger')
    return render_template('cliente/deposito.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)


@cliente_bp.route('/saque', methods=['GET', 'POST'])
@login_required(role='Cliente')
def saque():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('cliente.dashboard'))
    if request.method == 'POST':
        try:
            valor = Decimal(request.form.get('valor').replace(',', '.'))
            if valor <= 0: raise ValueError("O valor do saque deve ser positivo.")
            
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
            descricao_saque = 'Saque da conta'
            if taxa_aplicada > 0:
                descricao_saque += f' (inclui taxa de R$ {taxa_aplicada:.2f})'
            db.session.add(Transacao(tipo_transacao='Saque', valor=valor, descricao=descricao_saque, id_conta_origem=conta.id_conta))
            db.session.commit()
            flash('Saque realizado com sucesso!', 'success')
            return redirect(url_for('cliente.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao processar o saque.', 'danger')
    return render_template('cliente/saque.html', nome_usuario=cliente.usuario.nome, saldo=conta.saldo)


@cliente_bp.route('/transferencia', methods=['GET', 'POST'])
@login_required(role='Cliente')
def transferencia():
    cliente_origem = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta_origem = cliente_origem.contas[0] if cliente_origem.contas else None
    if not conta_origem:
        flash('Nenhuma conta bancária encontrada.', 'danger')
        return redirect(url_for('cliente.dashboard'))
    if request.method == 'POST':
        try:
            numero_conta_destino = request.form.get('numero_conta_destino')
            valor = Decimal(request.form.get('valor').replace(',', '.'))
            if valor <= 0: raise ValueError("O valor da transferência deve ser positivo.")
            
            conta_destino = Conta.query.filter_by(numero_conta=numero_conta_destino).first()
            if not conta_destino: raise ValueError("Conta de destino não encontrada.")
            if conta_destino.id_conta == conta_origem.id_conta: raise ValueError("Você não pode transferir para a sua própria conta.")
            if conta_origem.saldo < valor: raise ValueError("Saldo insuficiente.")

            conta_origem.saldo -= valor
            conta_destino.saldo += valor
            db.session.add(Transacao(tipo_transacao='Transferencia', valor=valor, id_conta_origem=conta_origem.id_conta, id_conta_destino=conta_destino.id_conta))
            db.session.commit()
            flash('Transferência realizada com sucesso!', 'success')
            return redirect(url_for('cliente.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao processar a transferência.', 'danger')
    return render_template('cliente/transferencia.html', saldo=conta_origem.saldo, nome_usuario=cliente_origem.usuario.nome)


@cliente_bp.route('/limite')
@login_required(role='Cliente')
def limite():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    score = cliente.score_credito
    limite_atual = score * Decimal('1.5')
    fator_projecao = Decimal('1') + (score / Decimal('2000'))
    limite_projecao = limite_atual * fator_projecao
    return render_template('cliente/limite.html',
                           nome_usuario=cliente.usuario.nome,
                           limite_atual=limite_atual,
                           limite_projecao=limite_projecao,
                           score_credito=score)


@cliente_bp.route('/extrato')
@login_required(role='Cliente')
def extrato():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0] if cliente.contas else None
    if not conta: return redirect(url_for('cliente.dashboard'))
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str: query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str: query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    transacoes = query.order_by(Transacao.data_hora.desc()).all()
    return render_template('cliente/extrato.html', 
                           transacoes=transacoes, conta_id=conta.id_conta,
                           data_inicio=data_inicio_str, data_fim=data_fim_str)


@cliente_bp.route('/extrato/imprimir')
@login_required(role='Cliente')
def imprimir_extrato():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0]
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str: query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str: query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    transacoes = query.order_by(Transacao.data_hora.desc()).all()
    return render_template('cliente/extrato_pdf.html', transacoes=transacoes, conta=conta, cliente=cliente)


@cliente_bp.route('/extrato/excel')
@login_required(role='Cliente')
def exportar_excel():
    cliente = Cliente.query.filter_by(id_usuario=session['user_id']).first_or_404()
    conta = cliente.contas[0]
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    query = Transacao.query.filter(or_(Transacao.id_conta_origem == conta.id_conta, Transacao.id_conta_destino == conta.id_conta))
    if data_inicio_str: query = query.filter(Transacao.data_hora >= datetime.strptime(data_inicio_str, '%Y-%m-%d'))
    if data_fim_str: query = query.filter(Transacao.data_hora <= datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1))
    transacoes_db = query.order_by(Transacao.data_hora.desc()).all()

    dados = []
    for t in transacoes_db:
        valor = t.valor if t.id_conta_destino == conta.id_conta else -t.valor
        descricao = t.descricao or ''
        dados.append({
            'Data': t.data_hora.strftime('%d/%m/%Y %H:%M'),
            'Tipo': t.tipo_transacao,
            'Descrição': descricao,
            'Valor (R$)': valor
        })
    df = pd.DataFrame(dados)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Extrato')
        
        workbook = writer.book
        worksheet = writer.sheets['Extrato']

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        cell_alignment = Alignment(horizontal="left", vertical="center")
        
        for cell in worksheet["1:1"]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = cell_alignment

        worksheet.column_dimensions['A'].width = 20  
        worksheet.column_dimensions['B'].width = 15  
        worksheet.column_dimensions['C'].width = 50
        worksheet.column_dimensions['D'].width = 15

        for cell in worksheet['D'][1:]:
            cell.number_format = 'R$ #,##0.00'

    output.seek(0)
    
    return send_file(
        output,
        download_name='extrato.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )