import os
import random
from datetime import datetime, timedelta, timezone
from flask import (Blueprint, render_template, request, redirect, url_for, flash, session)
from werkzeug.security import check_password_hash, generate_password_hash


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
    
    print(f"\n--- [DEBUG] Tentativa de Login para CPF: {cpf_recebido} ---")
    
    usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()

    if not usuario:
        print("[DEBUG] ERRO: Usuário não encontrado no banco de dados.")
        flash('CPF, senha ou tipo de usuário inválidos.', 'danger')
        return redirect(url_for('auth.index'))

    print(f"[DEBUG] Senha recebida do formulário: '{senha_recebida}'")
    

    senha_correta = check_password_hash(usuario.senha_hash, senha_recebida)
    
    print(f"[DEBUG] Resultado da verificação da senha: {senha_correta}")

    if senha_correta:
        print("[DEBUG] SUCESSO: Senha correta. Prosseguindo para OTP.")
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
        print("[DEBUG] FALHA: Senha incorreta.")
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
            if usuario.senha_provisoria:
                flash('Por segurança, você precisa criar uma nova senha para o seu primeiro acesso.', 'info')
                return redirect(url_for('auth.mudar_senha'))
            if usuario.tipo_usuario == 'Cliente':
                return redirect(url_for('cliente.dashboard'))
            elif usuario.tipo_usuario == 'Funcionario':
                return redirect(url_for('funcionario.dashboard'))
        else:
            flash('Código OTP inválido ou expirado.', 'danger')
            return redirect(url_for('auth.index'))
    return render_template('auth/verify_otp.html')


@auth_bp.route('/mudar-senha', methods=['GET', 'POST'])
def mudar_senha():
    if 'user_id' not in session:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        if not nova_senha or len(nova_senha) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
        elif nova_senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
        else:
            user_id = session['user_id']
            usuario = Usuario.query.get(user_id)
            usuario.senha_hash = generate_password_hash(nova_senha)
            usuario.senha_provisoria = False
            db.session.commit()
            flash('Senha alterada com sucesso! Bem-vindo(a).', 'success')
            if usuario.tipo_usuario == 'Cliente':
                return redirect(url_for('cliente.dashboard'))
            elif usuario.tipo_usuario == 'Funcionario':
                return redirect(url_for('funcionario.dashboard'))
    return render_template('auth/mudar_senha.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    if os.path.exists('token.json'):
        os.remove('token.json')
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.index'))
