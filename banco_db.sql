CREATE DATABASE IF NOT EXISTS banco_db;
USE banco_db;

CREATE TABLE usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    CPF VARCHAR(14) UNIQUE NOT NULL,
    data_nascimento DATE NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    tipo_usuario ENUM('Funcionario', 'Cliente') NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    otp_ativo VARCHAR(6),
    otp_expiracao DATETIME
);

CREATE TABLE funcionario (
    id_funcionario INT PRIMARY KEY AUTO_INCREMENT,
    codigo_funcionario VARCHAR(20) UNIQUE NOT NULL,
    cargo ENUM('Estagiario', 'Atendente', 'Gerente') NOT NULL,
    id_usuario INT NOT NULL,
    id_supervisor INT, -- Supervisor pode ser nulo (para o gerente geral, por exemplo)
    CONSTRAINT fk_funcionario_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_funcionario_supervisor FOREIGN KEY (id_supervisor) REFERENCES funcionario(id_funcionario)
);

-- CORREÇÃO: Nome da FK do usuário
CREATE TABLE cliente (
    id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    score_credito DECIMAL(5, 2) DEFAULT 0,
    CONSTRAINT fk_cliente_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- CORREÇÃO: Adicionada a chave primária e o índice no CEP
CREATE TABLE endereco (
    id_endereco INT PRIMARY KEY AUTO_INCREMENT,
    cep VARCHAR(9) NOT NULL, -- Ajustado para tamanho padrão de CEP
    local VARCHAR(100) NOT NULL,
    numero_casa INT NOT NULL,
    bairro VARCHAR(50) NOT NULL,
    estado CHAR(2) NOT NULL,
    complemento VARCHAR(50),
    INDEX idx_cep (cep) -- Adicionado índice para otimizar buscas por CEP
);

-- CORREÇÃO: Nome da FK do endereço
CREATE TABLE agencia (
    id_agencia INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    codigo_agencia VARCHAR(10) UNIQUE NOT NULL,
    id_endereco INT NOT NULL,
    CONSTRAINT fk_agencia_endereco FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco)
);

-- CORREÇÃO: Nomes das FKs e adicionado índice no número da conta
CREATE TABLE conta (
    id_conta INT PRIMARY KEY AUTO_INCREMENT,
    numero_conta VARCHAR(20) UNIQUE NOT NULL,
    saldo DECIMAL(15, 2) NOT NULL DEFAULT 0,
    tipo_conta ENUM('Poupanca', 'Corrente', 'Investimento') NOT NULL,
    data_abertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Ativa', 'Encerrada', 'Bloqueada') NOT NULL DEFAULT 'Ativa',
    id_agencia INT NOT NULL,
    id_cliente INT NOT NULL,
    CONSTRAINT fk_conta_agencia FOREIGN KEY (id_agencia) REFERENCES agencia(id_agencia),
    CONSTRAINT fk_conta_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    INDEX idx_numero_conta (numero_conta) -- Adicionado índice
);

-- CORREÇÃO: Nome da FK da conta
CREATE TABLE conta_poupanca (
    id_conta_poupanca INT PRIMARY KEY AUTO_INCREMENT,
    id_conta INT NOT NULL,
    taxa_rendimento DECIMAL(5, 2) NOT NULL,
    ultimo_rendimento DATETIME,
    CONSTRAINT fk_poupanca_conta FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

-- CORREÇÃO: Nome da FK da conta
CREATE TABLE conta_corrente (
    id_conta_corrente INT PRIMARY KEY AUTO_INCREMENT,
    id_conta INT NOT NULL,
    limite_cheque_especial DECIMAL(10, 2) NOT NULL DEFAULT 0, -- Nome mais descritivo
    taxa_manutencao DECIMAL(5, 2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_corrente_conta FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

-- CORREÇÃO: Nome da FK da conta
CREATE TABLE conta_investimento (
    id_conta_investimento INT PRIMARY KEY AUTO_INCREMENT,
    id_conta INT NOT NULL,
    perfil_risco ENUM('Baixo', 'Medio', 'Alto') NOT NULL, -- 'Alta' para 'Alto'
    valor_minimo_deposito DECIMAL(15, 2) NOT NULL, -- Nome mais descritivo
    taxa_rendimento_base DECIMAL(5, 2) NOT NULL,
    CONSTRAINT fk_investimento_conta FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

-- CORREÇÃO: Lógica e nomes das FKs, adicionado índice na data
CREATE TABLE transacao (
    id_transacao INT PRIMARY KEY AUTO_INCREMENT,
    tipo_transacao ENUM('Deposito', 'Saque', 'Transferencia', 'Pagamento', 'Rendimento') NOT NULL,
    valor DECIMAL(15, 2) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descricao VARCHAR(100),
    id_conta_origem INT, -- Origem pode ser nula (ex: depósito em caixa)
    id_conta_destino INT, -- Destino pode ser nulo (ex: saque)
    CONSTRAINT fk_transacao_conta_origem FOREIGN KEY (id_conta_origem) REFERENCES conta(id_conta),
    CONSTRAINT fk_transacao_conta_destino FOREIGN KEY (id_conta_destino) REFERENCES conta(id_conta),
    INDEX idx_data_hora (data_hora)
);

-- CORREÇÃO: Adicionada a chave primária e nome da FK
CREATE TABLE auditoria (
    id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    acao VARCHAR(50) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detalhes TEXT,
    CONSTRAINT fk_auditoria_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

-- CORREÇÃO: Nome da FK
CREATE TABLE relatorio (
    id_relatorio INT PRIMARY KEY AUTO_INCREMENT,
    id_funcionario INT NOT NULL,
    tipo_relatorio VARCHAR(50) NOT NULL,
    data_geracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conteudo TEXT NOT NULL,
    CONSTRAINT fk_relatorio_funcionario FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario)
);