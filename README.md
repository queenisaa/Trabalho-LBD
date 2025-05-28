# 💰 BANCO MALVADER

Sistema bancário educacional desenvolvido para a disciplina **Laboratório de Banco de Dados** – Universidade Católica de Brasília.

## 📌 Objetivo

Criar uma aplicação bancária com interface gráfica e persistência em banco de dados MySQL, aplicando conceitos avançados de Programação Orientada a Objetos (POO), modelagem relacional e programação SQL. O projeto foca em segurança, desempenho, usabilidade e integridade dos dados.

## 🛠️ Tecnologias Utilizadas

- **Back-end**: Python + Flask
- **Banco de Dados**: MySQL 8.x
- **ORM/Conexão**: SQLAlchemy / PyMySQL (ou equivalente)
- **Front-end**: HTML/CSS/JS (via Flask) ou interface desktop opcional
- **Exportação**: PDF / Excel (via bibliotecas Python)
- **Segurança**: OTP (One-Time Password), hash MD5, triggers e validações no banco

## 🧱 Estrutura do Projeto

| Arquivo/Pasta      | Descrição                                          |
| ------------------ | -------------------------------------------------- |
| `app.py`           | Controlador principal (rotas Flask)                |
| `config.py`        | Configurações do banco de dados                    |
| `models.py`        | Modelos de dados (SQLAlchemy)                      |
| `templates/`       | Vistas (arquivos HTML Jinja2)                      |
| `templates/index.html`    |                                             |
| `templates/add_task.html` |                                             |
| `static/style.css` | Arquivos estáticos (CSS, JS, imagens)              |


## 🔐 Funcionalidades Principais

### 🧑‍💼 Funcionário
- Login com senha + OTP
- Abertura/encerramento de contas (CP, CC, CI)
- Cadastro e gerenciamento de clientes e funcionários
- Geração de relatórios financeiros (PDF/Excel)
- Controle hierárquico de permissões
- Consulta e alteração de dados com registro em auditoria

### 👤 Cliente
- Login com senha + OTP
- Consultar saldo, limite e extratos
- Realizar depósitos, saques e transferências
- Encerramento de sessão com log

## 🗃️ Banco de Dados

Estrutura relacional com:
- 12+ tabelas (cliente, conta, transação, funcionário, etc.)
- Gatilhos (validação de senha, saldo, limites)
- Procedures (gerar OTP, calcular score de crédito)
- Views (resumo de contas, movimentações recentes)
- Índices e constraints para garantir desempenho e integridade

## 👩🏻‍💻 Desenvolvedores

- Isabela Martins Bandeira
- Natália Ematné Kruchak
- Nathanael Magno
