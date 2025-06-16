import os
import random
from datetime import datetime, timedelta, timezone
from flask import (Blueprint, render_template, request, redirect, url_for, flash, session)
from werkzeug.security import check_password_hash

from app.models import db, Usuario, Auditoria
from app.auth_services import enviar_email_otp

auth_bp = Blueprint('auth', __name__)

TENTATIVAS_MAXIMAS = 3
TEMPO_BLOQUEIO_MINUTOS = 10

@auth_bp.route('/')
def index():
    return render_template('auth/index.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    if os.path.exists('token.json'):
        os.remove('token.json')
        
    cpf_recebido = request.form.get('cpf', '').strip()
    senha_recebida = request.form.get('senha', '').strip()
    tipo_recebido = request.form.get('tipo', '').strip()
    
    usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()

    if not usuario:
        flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
        return redirect(url_for('auth.index'))

    ultimo_sucesso = Auditoria.query.filter_by(id_usuario=usuario.id_usuario, acao='Login', detalhes='Sucesso').order_by(Auditoria.data_hora.desc()).first()
    query_falhas = Auditoria.query.filter(Auditoria.id_usuario == usuario.id_usuario, Auditoria.acao == 'Login', Auditoria.detalhes.like('Falha%'))
    if ultimo_sucesso:
        query_falhas = query_falhas.filter(Auditoria.data_hora > ultimo_sucesso.data_hora)
    falhas_recentes = query_falhas.order_by(Auditoria.data_hora.desc()).limit(TENTATIVAS_MAXIMAS).all()

    if len(falhas_recentes) >= TENTATIVAS_MAXIMAS:
        ultima_falha_time = falhas_recentes[0].data_hora
        if ultima_falha_time.tzinfo is None:
            ultima_falha_time = ultima_falha_time.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < ultima_falha_time + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS):
            minutos_restantes = ((ultima_falha_time + timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)) - datetime.now(timezone.utc)).seconds // 60 + 1
            flash(f'Usuário bloqueado. Tente novamente em {minutos_restantes} minuto(s).', 'danger')
            return redirect(url_for('auth.index'))

    if check_password_hash(usuario.senha_hash, senha_recebida):
        db.session.add(Auditoria(id_usuario=usuario.id_usuario, acao='Login', detalhes='Sucesso'))
        db.session.commit()
        otp = str(random.randint(100000, 999999))
        if enviar_email_otp(usuario.email, usuario.nome, otp):
            usuario.otp_ativo = otp
            usuario.otp_expiracao = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.session.commit()
            session['id_usuario_para_verificar'] = usuario.id_usuario
            flash('Um código de verificação foi enviado para o seu e-mail.', 'info')
            return redirect(url_for('auth.verify_otp'))
        else:
            return redirect(url_for('auth.index'))
    else:
        db.session.add(Auditoria(id_usuario=usuario.id_usuario, acao='Login', detalhes=f'Falha na autenticação (Tentativa {len(falhas_recentes) + 1})'))
        db.session.commit()
        if len(falhas_recentes) + 1 >= TENTATIVAS_MAXIMAS:
            flash(f'Usuário bloqueado por {TEMPO_BLOQUEIO_MINUTOS} minutos.', 'danger')
        else:
            flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
        return redirect(url_for('auth.index'))

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'id_usuario_para_verificar' not in session:
        return redirect(url_for('auth.index'))
    user_id = session['id_usuario_para_verificar']
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return redirect(url_for('auth.index'))
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
            return redirect(url_for('cliente.dashboard'))
        else:
            flash('Código OTP inválido ou expirado.', 'danger')
            return redirect(url_for('auth.index'))
    return render_template('auth/verify_otp.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    if os.path.exists('token.json'):
        os.remove('token.json')
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.index'))
