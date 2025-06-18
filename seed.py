from app import create_app, db
from app.models import (Usuario, Cliente, Funcionario, Agencia, Conta, Endereco, 
                        ContaCorrente, ContaPoupanca, ContaInvestimento, HistoricoConta)
from werkzeug.security import generate_password_hash
from datetime import date
from decimal import Decimal

app = create_app()

def seed_data():
    with app.app_context():
        print("Limpando dados antigos...")
        db.session.query(HistoricoConta).delete()
        db.session.query(ContaInvestimento).delete()
        db.session.query(ContaCorrente).delete()
        db.session.query(ContaPoupanca).delete()
        db.session.query(Conta).delete()
        db.session.query(Funcionario).delete()
        db.session.query(Cliente).delete()
        db.session.query(Agencia).delete()
        db.session.query(Endereco).delete()
        db.session.query(Usuario).delete()
        db.session.commit()
        
        print("Criando agência de teste...")
        endereco_agencia = Endereco(cep='01001-000', local='Praça da Sé', numero_casa=1, bairro='Sé', estado='SP')
        db.session.add(endereco_agencia)
        db.session.commit()
        
        agencia_central = Agencia(nome='Agência Central Imperial', codigo_agencia='0001', id_endereco=endereco_agencia.id_endereco)
        db.session.add(agencia_central)
        db.session.commit()
        print(" -> Agência '0001' criada.")

        # --- USUÁRIO 1: CONTA POUPANÇA (CLIENTE) ---
        print("\nCriando usuário Cliente de teste...")
        usuario_cliente = Usuario(
            nome='Nathanael Cliente', 
            CPF='111111', # CPF ajustado
            data_nascimento=date(1990, 1, 1), 
            telefone='(11) 91111-1111', 
            email='nathanaelvictor000@gmail.com', 
            tipo_usuario='Cliente', 
            senha_hash=generate_password_hash('cliente123')
        )
        db.session.add(usuario_cliente)
        db.session.commit()

        cliente = Cliente(id_usuario=usuario_cliente.id_usuario, score_credito=800.00)
        db.session.add(cliente)
        db.session.commit()

        conta_poupanca = ContaPoupanca(
            numero_conta='11223-3',
            saldo=7500.00,
            status='Ativa',
            id_agencia=agencia_central.id_agencia,
            id_cliente=cliente.id_cliente,
            taxa_rendimento=Decimal('0.05')
        )
        db.session.add(conta_poupanca)
        print(" -> Usuário 'Nathanael Cliente' e Conta Poupança '11223-3' criados.")

        # --- USUÁRIO 2: FUNCIONÁRIO (GERENTE) ---
        print("\nCriando usuário Funcionário (Gerente)...")
        usuario_funcionario = Usuario(
            nome='Nathanael Funcionário', 
            CPF='222222', # CPF ajustado
            data_nascimento=date(1992, 2, 2), 
            telefone='(11) 92222-2222', 
            email='nathanaelmagno000@gmail.com', 
            tipo_usuario='Funcionario', 
            senha_hash=generate_password_hash('func123')
        )
        db.session.add(usuario_funcionario)
        db.session.commit()

        gerente = Funcionario(
            id_usuario=usuario_funcionario.id_usuario,
            codigo_funcionario='FUNC001',
            cargo='Gerente'
        )
        db.session.add(gerente)
        db.session.commit()
        print(" -> Usuário 'Nathanael Funcionário' criado.")

        db.session.commit()
        print("\nBanco de dados populado com sucesso!")

if __name__ == '__main__':
    seed_data()
