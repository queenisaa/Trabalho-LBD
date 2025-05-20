Trabalho Programação Laboratorial de Banco de Dados BANCO MALVADER 

Objetivo do Trabalho 

Desenvolver uma aplicação bancária chamada "BANCO MALVADER" em Java (ou outra linguagem à escolha do grupo), com interface gráfica e persistência em um banco de dados MySQL. O sistema deve gerenciar contas bancárias com foco em Programação Orientada a Objetos (POO), implementando uma estrutura de banco de dados complexa e operações avançadas. Cada grupo deve demonstrar domínio em design de banco de dados relacional, consultas SQL avançadas, gatilhos, procedimentos armazenados e otimização. 

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

Documento de Requisitos do Sistema - Banco Malvader 

(SRS - Software Requirements Specification) 

Este documento será um complemento ao trabalho, detalhando os requisitos funcionais, não funcionais e as especificações do sistema para orientar os grupos no desenvolvimento.  

1. Introdução 

1.1 Objetivo 

Este documento descreve os requisitos para o desenvolvimento do sistema "Banco Malvader", uma aplicação bancária que gerencia contas, funcionários e clientes com persistência em um banco de dados MySQL. O sistema deve implementar funcionalidades avançadas de gerenciamento bancário, utilizando conceitos de Programação Orientada a Objetos (POO) e um banco de dados relacional. Este SRS será o guia para que seu grupo possa entender o escopo, as funcionalidades e os critérios de aceitação. 

1.2 Escopo 

O sistema "Banco Malvader" permitirá: 

Autenticação segura de usuários (funcionários e clientes) com senha e OTP (One-Time Password). 

Gerenciamento de contas bancárias (Poupança, Corrente e Investimento) com operações como abertura, encerramento, depósito, saque, transferência e consulta. 

Registro de funcionários com hierarquia e controle de permissões. 

Geração de relatórios financeiros detalhados com exportação para múltiplos formatos. 

Persistência de dados em um banco de dados MySQL com gatilhos, procedimentos armazenados, visões e auditoria. 

O front-end pode ser desenvolvido na linguagem de preferência do grupo (ex.: Java com Swing, JavaFX, Python com Tkinter, ou frameworks web como React), desde que se integre ao banco de dados MySQL. 

1.3 Definições, Acrônimos e Abreviações 

SRS: Software Requirements Specification (Especificação de Requisitos de Software). 

POO: Programação Orientada a Objetos. 

MySQL: Sistema de gerenciamento de banco de dados relacional. 

OTP: One-Time Password (Senha de Uso Único). 

DAO: Data Access Object (Objeto de Acesso a Dados). 

CPF: Cadastro de Pessoa Física. 

CC: Conta Corrente. 

CP: Conta Poupança. 

CI: Conta Investimento. 

1.4 Referências 

Documentação oficial do MySQL (https://dev.mysql.com/doc/). 

Padrões de design de banco de dados relacional e POO. 

2. Descrição Geral 

2.1 Perspectiva do Produto 

O "Banco Malvader" é um sistema bancário completo que simula operações reais de uma instituição financeira. Ele integra uma interface gráfica com um banco de dados MySQL, oferecendo funcionalidades para funcionários (gerenciamento de contas e relatórios) e clientes (operações financeiras).  

2.2 Funções do Produto 

Autenticação: Login seguro com senha e OTP gerado dinamicamente. 

Gerenciamento de Contas: Abertura, encerramento, consulta e alteração de contas (CP, CC, CI). 

Operações Financeiras: Depósito, saque, transferência e extrato. 

Relatórios: Geração de relatórios financeiros com exportação para Excel e PDF. 

Auditoria: Registro de todas as ações críticas no sistema. 

Segurança: Validação de senhas fortes, limites de transações e permissões hierárquicas. 

2.3 Características dos Usuários 

Funcionários: Usuários com conhecimento básico de sistemas bancários, responsáveis por gerenciar contas e relatórios. Incluem estagiários, atendentes e gerentes com diferentes níveis de permissão. 

Clientes: Usuários finais que realizam operações financeiras, com conhecimento mínimo de tecnologia. 

Desenvolvedores (Alunos): Estudantes de programação com domínio de POO da Universidade Católica de Brasília, SQL e integração com bancos de dados. 

2.4 Restrições 

O banco de dados deve ser implementado em MySQL. 

Todas as regras de negócio críticas (ex.: limites, validações) devem ser implementadas no banco de dados. 

O sistema deve suportar ao menos 100 contas e 1.000 transações sem degradação significativa de desempenho. 

2.5 Premissas e Dependências 

Premissa: Os alunos têm acesso a um ambiente MySQL configurado. 

Dependência: Uso do driver JDBC para conexão com MySQL (ou equivalente na linguagem escolhida). 

3. Requisitos Específicos 

3.1 Requisitos Funcionais 

RF1 - Autenticação 

RF1.1: O sistema deve exibir uma tela de login com opções "Funcionário", "Cliente" e "Sair". 

RF1.2: O login exige senha e OTP gerado pelo banco (válido por 5 minutos). 

RF1.3: Tentativas de login devem ser registradas na tabela auditoria com data, hora, usuário e resultado (sucesso/falha). 

Critério de Aceitação: Login bem-sucedido redireciona ao menu correspondente; falhas após 3 tentativas bloqueiam o usuário por 10 minutos. 

RF2 - Menu Funcionário 

RF2.1 - Abertura de Conta: 

Suporte a CP, CC e CI com campos específicos (ver estrutura do banco). 

Número da conta gerado automaticamente com dígito verificador. 

Gatilho registra a abertura em auditoria. 

RF2.2 - Encerramento de Conta: 

Requer senha de administrador e OTP. 

Bloqueia se saldo < 0 ou dívidas pendentes. 

Registra motivo em uma tabela de histórico. 

RF2.3 - Consulta de Dados: 

Submenu com visões para Conta, Funcionário e Cliente. 

Exibe dados calculados (ex.: score de crédito, projeção de rendimentos). 

RF2.4 - Alteração de Dados: 

Alterações em Conta, Funcionário e Cliente com senha de administrador. 

Registro de alterações em auditoria com valores antigos/novos. 

RF2.5 - Cadastro de Funcionários: 

Requer permissão de gerente. 

Código único gerado pelo banco. 

Gatilho verifica limite de funcionários por agência (máximo 20). 

RF2.6 - Geração de Relatórios: 

Relatórios de movimentações, inadimplência e desempenho de funcionários. 

Exportação para Excel e PDF via front-end. 

Dados obtidos de uma view específica. 

RF3 - Menu Cliente 

RF3.1 - Operações de Conta: 

Saldo: Exibe saldo e projeção de rendimentos (CP/CI) com senha e OTP. 

Depósito: Limite diário de R$10.000 via trigger. 

Saque: Verifica saldo + limite; aplica taxa para saques excessivos (>5/mês). 

Transferência: Entre contas ou terceiros com validação e taxa. 

Extrato: Últimas 50 transações ou por período, exportável. 

Consultar Limite: Mostra limite atual e projeção. 

RF3.2 - Encerrar Sessão: Logout registrado em auditoria. 

3.2 Requisitos Não Funcionais 

RNF1 - Desempenho: Consultas devem retornar em < 2 segundos com 1.000 transações. 

RNF2 - Escalabilidade: Suporte a 100 contas e 10.000 transações com índices adequados. 

RNF3 - Segurança: Senhas criptografadas (MD5 ou superior), OTP e auditoria de ações. 

RNF4 - Usabilidade: Interface gráfica intuitiva, com mensagens claras de erro/sucesso. 

RNF5 - Portabilidade: Banco de dados MySQL compatível com versões 8.x; front-end independente de plataforma. 

3.3 Requisitos de Interface 

RI1: Tela de login com campos para senha e OTP. 

RI2: Menus com botões para cada funcionalidade (Funcionário e Cliente). 

RI3: Formulários para cadastro e alteração com validação de entrada. 

RI4: Exibição de relatórios e extratos em formato tabular, com opção de exportação. 

3.4 Requisitos de Banco de Dados 

RBD1: Estrutura conforme seção 4, com tabelas, gatilhos, procedures e visões. 

RBD2: Índices em campos de busca frequente (ex.: numero_conta, data_hora). 

RBD3: Transações SQL para operações críticas (ex.: transferências). 

RBD4: Validações no banco (ex.: limite de depósito, senha forte). 

4. Estrutura do Banco de Dados 

4.1 Tabelas 

usuario: id_usuario (PK), nome, cpf (UNIQUE), data_nascimento, telefone, tipo_usuario, senha_hash, otp_ativo, otp_expiracao. 

funcionario: id_funcionario (PK), id_usuario (FK), codigo_funcionario (UNIQUE), cargo, id_supervisor (FK). 

cliente: id_cliente (PK), id_usuario (FK), score_credito. 

endereco: id_endereco (PK), id_usuario (FK), cep, local, numero_casa, bairro, cidade, estado, complemento. 

agencia: id_agencia (PK), nome, codigo_agencia (UNIQUE), endereco_id (FK). 

conta: id_conta (PK), numero_conta (UNIQUE), id_agencia (FK), saldo, tipo_conta, id_cliente (FK), data_abertura, status. 

conta_poupanca: id_conta_poupanca (PK), id_conta (FK, UNIQUE), taxa_rendimento, ultimo_rendimento. 

conta_corrente: id_conta_corrente (PK), id_conta (FK, UNIQUE), limite, data_vencimento, taxa_manutencao. 

conta_investimento: id_conta_investimento (PK), id_conta (FK, UNIQUE), perfil_risco, valor_minimo, taxa_rendimento_base. 

transacao: id_transacao (PK), id_conta_origem (FK), id_conta_destino (FK), tipo_transacao, valor, data_hora, descricao. 

auditoria: id_auditoria (PK), id_usuario (FK), acao, data_hora, detalhes. 

relatorio: id_relatorio (PK), id_funcionario (FK), tipo_relatorio, data_geracao, conteudo. 

4.2 Gatilhos 

Atualização de saldo após transações. 

Validação de senha forte em usuario. 

Limite de depósito diário em transacao. 

4.3 Procedimentos Armazenados 

gerar_otp(id_usuario): Gera OTP de 6 dígitos. 

calcular_score_credito(id_cliente): Atualiza score com base em transações. 

4.4 Visões 

vw_resumo_contas: Resumo de contas por cliente. 

vw_movimentacoes_recentes: Movimentações dos últimos 90 dias. 

5. Requisitos de Design 

Arquitetura: MVC (Model-View-Controller) ou equivalente. 

Pacotes: 

dao: Acesso ao banco de dados. 

model: Representação das tabelas. 

view: Interface gráfica (livre escolha). 

controller: Lógica de negócios. 

util: Conexão e utilitários. 

Conexão: Driver JDBC ou similar, com pool de conexões recomendado. 

6. Critérios de Aceitação 

Todas as funcionalidades listadas em RF2 e RF3 implementadas e testadas. 

Banco de dados configurado com todas as tabelas, gatilhos, procedures e visões funcionando. 

Interface gráfica funcional, com validação de entrada e exportação de relatórios. 

Documentação com diagrama ER e descrição das regras de negócio. 

7. Entrega 

Código: Organizado em pacotes, com comentários detalhando lógica e SQL. 

Documentação: Diagrama ER, instruções de instalação e descrição do sistema. 

Apresentação: Demonstração prática (5-10 minutos) mostrando autenticação, operações e relatórios. 

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

Revisão dos requisitos técnicos 

Acesso ao Programa 

Autenticação Inicial: 

Tela de login com autenticação multifator: senha e um código temporário gerado pelo banco de dados (OTP - One-Time Password). 

Menu principal com opções: "Funcionário", "Cliente" e "Sair". 

Registro de tentativas de login (com data, hora e resultado) em uma tabela de auditoria. 

Menu Funcionário 

Abertura de Conta: 

Suporte a múltiplos tipos de conta: Conta Poupança (CP), Conta Corrente (CC) e Conta Investimento (CI). 

Dados obrigatórios: 

CP: agência, número da conta, nome, CPF, data de nascimento, telefone, endereço completo, senha, taxa de rendimento personalizada. 

CC: mesma base + limite dinâmico (calculado com base no histórico de transações do cliente), data de vencimento e taxa de manutenção. 

CI: mesma base + perfil de risco (baixo, médio, alto) e valor mínimo de investimento. 

Validação no banco: CPF único, número de conta gerado automaticamente com dígito verificador (ex.: algoritmo de Luhn). 

Gatilho para registrar a abertura em uma tabela de log. 

Encerramento de Conta: 

Requer senha de administrador e OTP. 

Verificar saldo pendente e bloquear encerramento se houver dívidas. 

Registrar motivo do encerramento (ex.: solicitação do cliente, inadimplência) em uma tabela de histórico. 

Atualizar status da conta para "Encerrada" via procedure. 

Consulta de Dados: 

Submenu: 

Conta: Tipo, nome, CPF, saldo atual, limite disponível, data de vencimento, histórico de transações (últimos 90 dias) e projeção de rendimentos (para CP e CI). 

Funcionário: Código, cargo, nome, CPF, data de nascimento, telefone, endereço, número de contas abertas por ele e desempenho (média de valores movimentados). 

Cliente: Nome, CPF, data de nascimento, telefone, endereço, score de crédito (calculado via procedure), e lista de contas ativas/inativas. 

Consultas devem usar visões (views) para otimizar e proteger dados sensíveis. 

Alteração de Dados: 

Submenu: 

Conta: Alterar limite (com validação de score de crédito), data de vencimento e taxa de rendimento/manutenção. 

Funcionário: Alterar cargo (com restrição de nível hierárquico), telefone e endereço. 

Cliente: Alterar telefone, endereço e senha (com validação de força da senha via trigger). 

Todas as alterações registradas em uma tabela de auditoria com data, usuário responsável e valores antigos/novos. 

Cadastro de Funcionários: 

Dados: código único (gerado pelo banco), cargo (hierarquia: estagiário, atendente, gerente), nome, CPF, data de nascimento, telefone, endereço, senha criptografada (ex.: hash MD5 no banco). 

Requer permissão de administrador (nível gerente ou superior). 

Gatilho para verificar limite de funcionários por agência. 

Geração de Relatórios: 

Relatórios avançados: 

Movimentações por período (filtro por data, tipo de transação e agência). 

Clientes inadimplentes (saldo negativo ou limite excedido). 

Desempenho de funcionários (contas abertas, valores movimentados). 

Exportação para Excel e PDF via front-end, com dados obtidos de uma view específica. 

Procedure para calcular métricas (ex.: total movimentado, média de transações por cliente). 

Sair: Retorna ao menu principal. 

 

Menu Cliente 

Operações de Conta: 

Submenu: 

Saldo: Exibir saldo atual e projeção de rendimentos (CP e CI), com senha e OTP. 

Depósito: Permitir depósitos com validação de valor máximo diário (ex.: R$10.000) via trigger. 

Saque: Verificar saldo + limite (CC) ou saldo disponível (CP/CI), com registro de taxa para saques excessivos. 

Transferência: Entre contas do mesmo cliente ou para terceiros (com validação de conta destino e taxa). 

Extrato: Últimas 50 transações ou por período, exportável para Excel/PDF. 

Consultar Limite: Limite atual e projeção de aumento com base no score de crédito. 

Todas as operações registradas em uma tabela de transações com gatilho para atualizar o saldo. 

Encerrar Programa: Finaliza a sessão do cliente com logout registrado no banco. 

 

Estrutura do Banco de Dados 

Tabelas 

usuario 

id_usuario (PK, INT, AUTO_INCREMENT) 

nome (VARCHAR(100), NOT NULL) 

cpf (VARCHAR(11), UNIQUE, NOT NULL) 

data_nascimento (DATE, NOT NULL) 

telefone (VARCHAR(15), NOT NULL) 

tipo_usuario (ENUM('FUNCIONARIO', 'CLIENTE'), NOT NULL) 

senha_hash (VARCHAR(32), NOT NULL) - Armazena hash MD5 da senha 

otp_ativo (VARCHAR(6)) - Código OTP temporário 

otp_expiracao (DATETIME) - Data/hora de expiração do OTP 

funcionario 

id_funcionario (PK, INT, AUTO_INCREMENT) 

id_usuario (FK, INT, REFERENCES usuario(id_usuario)) 

codigo_funcionario (VARCHAR(20), UNIQUE, NOT NULL) - Gerado automaticamente 

cargo (ENUM('ESTAGIARIO', 'ATENDENTE', 'GERENTE'), NOT NULL) 

id_supervisor (FK, INT, REFERENCES funcionario(id_funcionario)) - Hierarquia 

cliente 

id_cliente (PK, INT, AUTO_INCREMENT) 

id_usuario (FK, INT, REFERENCES usuario(id_usuario)) 

score_credito (DECIMAL(5,2), DEFAULT 0) - Calculado dinamicamente 

endereco 

id_endereco (PK, INT, AUTO_INCREMENT) 

id_usuario (FK, INT, REFERENCES usuario(id_usuario)) 

cep (VARCHAR(10), NOT NULL) 

local (VARCHAR(100), NOT NULL) 

numero_casa (INT, NOT NULL) 

bairro (VARCHAR(50), NOT NULL) 

cidade (VARCHAR(50), NOT NULL) 

estado (CHAR(2), NOT NULL) 

complemento (VARCHAR(50)) - Opcional 

Índice em cep para buscas rápidas 

agencia 

id_agencia (PK, INT, AUTO_INCREMENT) 

nome (VARCHAR(50), NOT NULL) 

codigo_agencia (VARCHAR(10), UNIQUE, NOT NULL) 

endereco_id (FK, INT, REFERENCES endereco(id_endereco)) 

conta 

id_conta (PK, INT, AUTO_INCREMENT) 

numero_conta (VARCHAR(20), UNIQUE, NOT NULL) - Inclui dígito verificador 

id_agencia (FK, INT, REFERENCES agencia(id_agencia)) 

saldo (DECIMAL(15,2), NOT NULL DEFAULT 0) 

tipo_conta (ENUM('POUPANCA', 'CORRENTE', 'INVESTIMENTO'), NOT NULL) 

id_cliente (FK, INT, REFERENCES cliente(id_cliente)) 

data_abertura (DATETIME, NOT NULL DEFAULT CURRENT_TIMESTAMP) 

status (ENUM('ATIVA', 'ENCERRADA', 'BLOQUEADA'), NOT NULL DEFAULT 'ATIVA') 

Índice em numero_conta 

conta_poupanca 

id_conta_poupanca (PK, INT, AUTO_INCREMENT) 

id_conta (FK, INT, REFERENCES conta(id_conta), UNIQUE) 

taxa_rendimento (DECIMAL(5,2), NOT NULL) - Personalizada por conta 

ultimo_rendimento (DATETIME) - Última aplicação do rendimento 

conta_corrente 

id_conta_corrente (PK, INT, AUTO_INCREMENT) 

id_conta (FK, INT, REFERENCES conta(id_conta), UNIQUE) 

limite (DECIMAL(15,2), NOT NULL DEFAULT 0) 

data_vencimento (DATE, NOT NULL) 

taxa_manutencao (DECIMAL(5,2), NOT NULL DEFAULT 0) 

conta_investimento 

id_conta_investimento (PK, INT, AUTO_INCREMENT) 

id_conta (FK, INT, REFERENCES conta(id_conta), UNIQUE) 

perfil_risco (ENUM('BAIXO', 'MEDIO', 'ALTO'), NOT NULL) 

valor_minimo (DECIMAL(15,2), NOT NULL) 

taxa_rendimento_base (DECIMAL(5,2), NOT NULL) 

transacao 

id_transacao (PK, INT, AUTO_INCREMENT) 

id_conta_origem (FK, INT, REFERENCES conta(id_conta)) 

id_conta_destino (FK, INT, REFERENCES conta(id_conta)) - Para transferências 

tipo_transacao (ENUM('DEPOSITO', 'SAQUE', 'TRANSFERENCIA', 'TAXA', 'RENDIMENTO'), NOT NULL) 

valor (DECIMAL(15,2), NOT NULL) 

data_hora (TIMESTAMP, NOT NULL DEFAULT CURRENT_TIMESTAMP) 

descricao (VARCHAR(100)) - Detalhe da transação 

Índice em data_hora 

auditoria 

id_auditoria (PK, INT, AUTO_INCREMENT) 

id_usuario (FK, INT, REFERENCES usuario(id_usuario)) 

acao (VARCHAR(50), NOT NULL) - Ex.: "LOGIN", "ALTERACAO", "ENCERRAMENTO" 

data_hora (TIMESTAMP, NOT NULL DEFAULT CURRENT_TIMESTAMP) 

detalhes (TEXT) - JSON ou texto com valores antigos/novos 

relatorio 

id_relatorio (PK, INT, AUTO_INCREMENT) 

id_funcionario (FK, INT, REFERENCES funcionario(id_funcionario)) 

tipo_relatorio (VARCHAR(50), NOT NULL) 

data_geracao (TIMESTAMP, NOT NULL DEFAULT CURRENT_TIMESTAMP) 

conteudo (TEXT, NOT NULL) - Dados em formato JSON ou CSV 

Gatilhos (Triggers) 

Atualização de Saldo: Após cada transação (INSERT em transacao), atualizar o saldo da conta correspondente. 

sql 

DELIMITER $$ 

CREATE TRIGGER atualizar_saldo AFTER INSERT ON transacao 

FOR EACH ROW 

BEGIN 

    IF NEW.tipo_transacao = 'DEPOSITO' THEN 

        UPDATE conta SET saldo = saldo + NEW.valor WHERE id_conta = NEW.id_conta_origem; 

    ELSEIF NEW.tipo_transacao IN ('SAQUE', 'TAXA') THEN 

        UPDATE conta SET saldo = saldo - NEW.valor WHERE id_conta = NEW.id_conta_origem; 

    ELSEIF NEW.tipo_transacao = 'TRANSFERENCIA' THEN 

        UPDATE conta SET saldo = saldo - NEW.valor WHERE id_conta = NEW.id_conta_origem; 

        UPDATE conta SET saldo = saldo + NEW.valor WHERE id_conta = NEW.id_conta_destino; 

    END IF; 

END $$ 

DELIMITER ; 

Validação de Senha Forte: Antes de atualizar senha_hash em usuario, verificar se a senha tem pelo menos 8 caracteres, 1 letra maiúscula, 1 número e 1 caractere especial. 

sql 

DELIMITER $$ 

CREATE TRIGGER validar_senha BEFORE UPDATE ON usuario 

FOR EACH ROW 

BEGIN 

    IF NEW.senha_hash REGEXP '^[0-9a-f]{32}$' THEN -- Assume MD5 

        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Senha deve ser atualizada via procedure com validação'; 

    END IF; 

END $$ 

DELIMITER ; 

Limite de Depósito Diário: Bloquear depósitos acima de R$10.000 por dia por cliente. 

sql 

DELIMITER $$ 

CREATE TRIGGER limite_deposito BEFORE INSERT ON transacao 

FOR EACH ROW 
