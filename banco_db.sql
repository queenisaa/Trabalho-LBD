#Atalhos
create database banco_db;
use banco_db;

#Tabelas 
create table usuario(
id_usuario int primary key auto_increment,
nome VARCHAR(100) NOT NULL,
CPF VARCHAR(100) UNIQUE NOT NULL,
data_nascimento date not null,
telefone VARCHAR(15) not null,
tipo_usuario ENUM('Funcionario', 'Cliente') not null,
senha_hash VARCHAR(32) NOT NULL, 
otp_ativo VARCHAR(6),  
oto_expiracao DATETIME
);

create table funcionario(
id_funcionario int primary key auto_increment,
codigo_funcionario VARCHAR(20) unique not null,
cargo ENUM('Estagiario', 'Atendente', 'Gerente') not null,
CONSTRAINT id_supervisor foreign key (id_funcionario) references funcionario(id_funcionario),
CONSTRAINT id_usuario foreign key (id_usuario) references cliente(id_cliente)
);

create table cliente(
id_cliente int primary key auto_increment,
score_credito decimal (5,2) default 0,
CONSTRAINT id_usuario foreign key (id_usuario) references usuario(id_usuario)
);

create table endereco(
id_endereco int auto_increment,
cep VARCHAR(100) not null,
local varchar(100) not null,
numero_casa int not null,
bairro varchar(50) not null,
estado char(2) not null,
complemento varchar(50)
# Indice no cep
);

create table agencia(
id_agencia int primary key auto_increment,
nome VARCHAR(50) not null,
codigo_agencia varchar(10) unique not null,
CONSTRAINT id_endereco foreign key (id_endereco) references endereco (id_endereco) 
);

create table conta(
id_conta int primary key auto_increment,
numero_conta VARCHAR(20) unique not null,
saldo decimal(15,2) not null default 0,
tipo_conta ENUM('Poupanca', 'Corrente', 'Investimento') not null,
data_abertura datetime not null default current_timestamp,
status enum('Ativa', 'Encerrada', 'Bloqueada') not null default 'Ativa',
CONSTrAINT id_agencia foreign key (id_agencia) references agencia(id_agencia),
CONSTRAINT id_cliente foreign key (id_cliente) references cliente(id_cliente)
#Indice numero_conta
);

create table conta_poupanca(
id_conta_poupanca int primary key auto_increment,
taxa_rendimento decimal (5,2) not null,
ultimo_rendimento datetime,
constraint id_conta foreign key (id_conta) references conta(id_conta)  
);

create table conta_corrente(
id_conta_corrente int primary key auto_increment,
limite decimal(5,2) not null default 0,
data_vencimento date not null,
taxa_manutencao decimal (5,2) not null default 0,
constraint id_conta foreign key (id_conta) references conta(id_conta)
);

create table conta_investimento(
id_conta_investimento int primary key auto_increment,
perfil_risco enum('Baixo', 'Medio', 'Alta') not null,
valor_minimo decimal (15,2) not null,
taxa_rendimento_base decimal (5,2) not null,
constraint id_conta foreign key (id_conta) references conta(id_conta)
);

create table transacao(
id_transacao int primary key auto_increment,
tipo_transacao enum('Deposito', 'Saque', 'Transferencia', 'Taxa', 'Rendimento') not null,
valor decimal (15,2) not null,
data_hora timestamp not null default current_timestamp,
descricao VARCHAR(100),
constraint id_conta_origem foreign key (id_conta) references conta(id_conta),
constraint id_conta_destino foreign key (id_conta) references conta(id_conta)
#Indice em data_hora
);

create table auditoria(
id_auditoria int not null auto_increment,
acao varchar(50) not null,
data_hora timestamp not null default current_timestamp,
detalhes text, 
constraint id_usuario foreign key (id_usuario) references usuario(id_usuario)
);

create table relatorio(
id_relatorio int primary key auto_increment,
tipo_relatorio varchar(50) not null,
data_geracao timestamp not null default current_timestamp,
conteudo text not null,
constraint id_funcionario foreign key (id_funcionario) references funcionario(id_funcionario) 
);

#Triggers
#Trigger de atulização de saldo apos transferencia
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

#Trigger pra validação de senha forte 
DELIMITER $$ 

CREATE TRIGGER validar_senha BEFORE UPDATE ON usuario 

FOR EACH ROW 

BEGIN 

    IF NEW.senha_hash REGEXP '^[0-9a-f]{32}$' THEN -- Assume MD5 

        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Senha deve ser atualizada via procedure com validação'; 

    END IF; 

END $$ 

DELIMITER ;

#Trigger para limitar depositos diarios, bloqueia depositos acima de 10.000 por dia
DELIMITER $$ 

CREATE TRIGGER limite_deposito BEFORE INSERT ON transacao 

FOR EACH ROW 

BEGIN 

    DECLARE total_dia DECIMAL(15,2); 

    SELECT SUM(valor) INTO total_dia 

    FROM transacao 

    WHERE id_conta_origem = NEW.id_conta_origem 

      AND tipo_transacao = 'DEPOSITO' 

      AND DATE(data_hora) = DATE(NEW.data_hora); 

    IF (total_dia + NEW.valor) > 10000 THEN 

        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite diário de depósito excedido'; 

    END IF; 

END $$ 

DELIMITER ; 

#Procedures
#Procedure para gerar OTP(One-Time-Password) cria um codigo temporario de 6 digitos por 5 MINUTOS
DELIMITER $$ 

CREATE PROCEDURE gerar_otp(IN id_usuario INT) 

BEGIN 

    DECLARE novo_otp VARCHAR(6); 

    SET novo_otp = LPAD(FLOOR(RAND() * 1000000), 6, '0'); 

    UPDATE usuario SET otp_ativo = novo_otp, otp_expiracao = NOW() + INTERVAL 5 MINUTE 

    WHERE id_usuario = id_usuario; 

    SELECT novo_otp; 

END $$ 

DELIMITER ; 

#Procedure para calcular score de credito, atualiza o score do com cliente com base no historico de transações 
DELIMITER $$ 

CREATE PROCEDURE calcular_score_credito(IN id_cliente INT) 

BEGIN 

    DECLARE total_trans DECIMAL(15,2); 

    DECLARE media_trans DECIMAL(15,2); 

    SELECT SUM(valor), AVG(valor) INTO total_trans, media_trans 

    FROM transacao t 

    JOIN conta c ON t.id_conta_origem = c.id_conta 

    WHERE c.id_cliente = id_cliente AND t.tipo_transacao IN ('DEPOSITO', 'SAQUE'); 

    UPDATE cliente SET score_credito = LEAST(100, (total_trans / 1000) + (media_trans / 100)) 

    WHERE id_cliente = id_cliente; 

END $$ 

DELIMITER ; 

#Views
#Views para resumo das contas por cliente
CREATE VIEW vw_resumo_contas AS 

SELECT c.id_cliente, u.nome, COUNT(co.id_conta) AS total_contas, SUM(co.saldo) AS saldo_total 

FROM cliente c 

JOIN usuario u ON c.id_usuario = u.id_usuario 

JOIN conta co ON c.id_cliente = co.id_cliente 

GROUP BY c.id_cliente, u.nome; 

#View para movimentações recentes
CREATE VIEW vw_movimentacoes_recentes AS 

SELECT t.*, c.numero_conta, u.nome AS cliente 

FROM transacao t 

JOIN conta c ON t.id_conta_origem = c.id_conta 

JOIN cliente cl ON c.id_cliente = cl.id_cliente 

JOIN usuario u ON cl.id_usuario = u.id_usuario 

WHERE t.data_hora >= NOW() - INTERVAL 90 DAY; 

# Permissoes

#Criando um role
CREATE role 'gerente';

GRANT ROLE TO 'carlos'@'localhost';
#Dando permissão a um gerente
GRANT privilegios ON banco_db.tabela_funcionario TO 'carlos'@'localhost';
FLUSH PRIVILEGES;

#Recarrega todas as tabelas internas de privilegios dentro o mysql
FLUSH PRIVILEGES;

#Mostrar Permissoes
SHOW GRANTS FOR 'usuario'@'host';

#Revogar todos os privilegios 


#Dropar os roles
DROP ROLE 'gerente';

#Dropar usuario
drop user 'carlos'@'localhost';
