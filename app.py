# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from models import db, Usuario, Cliente, Funcionario
import hashlib

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa o SQLAlchemy com o app
    db.init_app(app)

    # ================== ROTAS ==================

    @app.route('/', methods=['GET'])
    def index():
        # Tela de login principal
        return render_template('index.html')

    @app.route('/login', methods=['POST'])
    def login():
        """
        Lê os campos:
          - tipo: “Cliente” ou “Funcionario”
          - cpf: string
          - senha: string (texto simples)
        Verifica no banco:
          1) Busca Usuario com CPF e tipo_usuario iguais aos informados.
          2) Se existir, gera MD5 da senha informada e compara com senha_hash armazenado.
          3) Se bater, grava na sessão e redireciona para dashboard correspondente.
          4) Senão, exibe mensagem de erro via flash e retorna para index.
        """
        cpf_recebido = request.form.get('cpf', '').strip()
        senha_recebida = request.form.get('senha', '').strip()
        tipo_recebido = request.form.get('tipo', '').strip()  # “Cliente” ou “Funcionario”

        # 1) Busca no model Usuario
        usuario = Usuario.query.filter_by(CPF=cpf_recebido, tipo_usuario=tipo_recebido).first()
        if not usuario:
            flash('Usuário não encontrado ou tipo incorreto.', 'danger')
            return redirect(url_for('index'))

        # 2) Gera MD5 da senha digitada e compara
        md5_da_senha = hashlib.md5(senha_recebida.encode('utf-8')).hexdigest()
        if md5_da_senha != usuario.senha_hash:
            flash('Senha incorreta.', 'danger')
            return redirect(url_for('index'))

        # 3) Login válido: grava na sessão
        session.clear()
        session['id_usuario'] = usuario.id_usuario
        session['tipo_usuario'] = usuario.tipo_usuario

        if tipo_recebido == 'Cliente':
            cliente = Cliente.query.filter_by(id_usuario=usuario.id_usuario).first()
            if cliente:
                session['id_cliente'] = cliente.id_cliente
            return redirect(url_for('dashboard_cliente'))

        if tipo_recebido == 'Funcionario':
            funcionario = Funcionario.query.filter_by(id_usuario=usuario.id_usuario).first()
            if funcionario:
                session['id_funcionario'] = funcionario.id_funcionario
            return redirect(url_for('dashboard_funcionario'))

        flash('Tipo de usuário inválido.', 'danger')
        return redirect(url_for('index'))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/dashboard_cliente')
    def dashboard_cliente():
        """
        Apenas acessível quando session['tipo_usuario'] == 'Cliente'.
        Exibe nome do Usuário e score_credito.
        """
        if 'id_usuario' not in session or session.get('tipo_usuario') != 'Cliente':
            flash('Acesso negado.', 'danger')
            return redirect(url_for('index'))

        cliente = Cliente.query.filter_by(id_usuario=session['id_usuario']).first()
        usuario = Usuario.query.get(session['id_usuario'])
        return render_template('dashboard_cliente.html',
                               nome_usuario=usuario.nome,
                               score_credito=cliente.score_credito)

    @app.route('/dashboard_funcionario')
    def dashboard_funcionario():
        """
        Apenas acessível quando session['tipo_usuario'] == 'Funcionario'.
        Exibe nome do Usuário e cargo do Funcionário.
        """
        if 'id_usuario' not in session or session.get('tipo_usuario') != 'Funcionario':
            flash('Acesso negado.', 'danger')
            return redirect(url_for('index'))

        funcionario = Funcionario.query.filter_by(id_usuario=session['id_usuario']).first()
        usuario = Usuario.query.get(session['id_usuario'])
        return render_template('dashboard_funcionario.html',
                               nome_usuario=usuario.nome,
                               cargo=funcionario.cargo)

    return app

# ================== EXECUÇÃO ==================
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
