-- =====================================================
-- BANCO DE DADOS
-- =====================================================

CREATE DATABASE IF NOT EXISTS escola_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE escola_db;


-- =====================================================
-- PRESTADOR DE SERVIÇO
-- =====================================================

CREATE TABLE IF NOT EXISTS prestador_de_servico (
    id_servico INT PRIMARY KEY AUTO_INCREMENT,
    cnpj CHAR(14) UNIQUE,
    servico VARCHAR(100),
    numero VARCHAR(20),
    email VARCHAR(255) UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- ESCOLA
-- =====================================================

CREATE TABLE IF NOT EXISTS escola (
    id_escola INT PRIMARY KEY AUTO_INCREMENT,
    cnpj CHAR(14) NOT NULL UNIQUE,
    prestador_de_servico INT,

    CONSTRAINT fk_escola_prestador
        FOREIGN KEY (prestador_de_servico)
        REFERENCES prestador_de_servico(id_servico)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- CARGO
-- =====================================================

CREATE TABLE IF NOT EXISTS cargo (
    id_cargo INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    acesso_dados_sensiveis BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- ALUNO
-- =====================================================

CREATE TABLE IF NOT EXISTS aluno (
    id_aluno INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL UNIQUE,
    cpf CHAR(11) NOT NULL UNIQUE,
    numero VARCHAR(20),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- PROFESSOR
-- =====================================================

CREATE TABLE IF NOT EXISTS professor (
    id_professor INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL UNIQUE,
    cpf CHAR(11) NOT NULL UNIQUE,
    numero VARCHAR(20),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- FUNCIONARIO
-- =====================================================

CREATE TABLE IF NOT EXISTS funcionario (
    id_funcionario INT PRIMARY KEY AUTO_INCREMENT,
    cpf CHAR(11) NOT NULL UNIQUE,
    numero VARCHAR(20),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    id_cargo INT NOT NULL,

    CONSTRAINT fk_funcionario_cargo
        FOREIGN KEY (id_cargo)
        REFERENCES cargo(id_cargo)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- RESPONSAVEL
-- =====================================================

CREATE TABLE IF NOT EXISTS responsavel (
    id_responsavel INT PRIMARY KEY AUTO_INCREMENT,
    cpf CHAR(11) NOT NULL UNIQUE,
    numero VARCHAR(20),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- CONTA
-- Sistema de autenticação.
--
-- A senha deve ser armazenada como HASH,
-- nunca como senha em texto puro.
-- =====================================================

CREATE TABLE IF NOT EXISTS conta (
    id_conta INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    id_funcionario INT UNIQUE,
    id_professor INT UNIQUE,
    id_aluno INT UNIQUE,
    id_responsavel INT UNIQUE,

    CONSTRAINT fk_conta_funcionario
        FOREIGN KEY (id_funcionario)
        REFERENCES funcionario(id_funcionario),

    CONSTRAINT fk_conta_professor
        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor),

    CONSTRAINT fk_conta_aluno
        FOREIGN KEY (id_aluno)
        REFERENCES aluno(id_aluno),

    CONSTRAINT fk_conta_responsavel
        FOREIGN KEY (id_responsavel)
        REFERENCES responsavel(id_responsavel)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- TURMA
-- =====================================================

CREATE TABLE IF NOT EXISTS turma (
    id_turma ENUM(
        '1a', '1b',
        '2a', '2b',
        '3a', '3b',
        '4a', '4b',
        '5a', '5b',
        '6a', '6b'
    ) PRIMARY KEY
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- ANO LETIVO
-- =====================================================

CREATE TABLE IF NOT EXISTS ano_letivo (
    id_ano INT PRIMARY KEY AUTO_INCREMENT,
    ano YEAR NOT NULL UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- ALUNO_TURMA
-- Permite registrar a turma do aluno em cada ano.
-- =====================================================

CREATE TABLE IF NOT EXISTS aluno_turma (
    matricula INT,
    id_turma ENUM(
        '1a', '1b',
        '2a', '2b',
        '3a', '3b',
        '4a', '4b',
        '5a', '5b',
        '6a', '6b'
    ),
    id_ano INT,

    PRIMARY KEY (matricula, id_turma, id_ano),

    CONSTRAINT fk_aluno_turma_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT fk_aluno_turma_turma
        FOREIGN KEY (id_turma)
        REFERENCES turma(id_turma),

    CONSTRAINT fk_aluno_turma_ano
        FOREIGN KEY (id_ano)
        REFERENCES ano_letivo(id_ano)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- PROFESSOR_TURMA
-- =====================================================

CREATE TABLE IF NOT EXISTS professor_turma (
    id_professor INT,
    id_turma ENUM(
        '1a', '1b',
        '2a', '2b',
        '3a', '3b',
        '4a', '4b',
        '5a', '5b',
        '6a', '6b'
    ),
    id_ano INT,

    PRIMARY KEY (id_professor, id_turma, id_ano),

    CONSTRAINT fk_professor_turma_professor
        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor),

    CONSTRAINT fk_professor_turma_turma
        FOREIGN KEY (id_turma)
        REFERENCES turma(id_turma),

    CONSTRAINT fk_professor_turma_ano
        FOREIGN KEY (id_ano)
        REFERENCES ano_letivo(id_ano)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- MATERIA
-- =====================================================

CREATE TABLE IF NOT EXISTS materia (
    id_materia INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- HISTORICO ESCOLAR
--
-- Cada registro representa uma nota de uma matéria
-- para determinado aluno em determinado ano.
-- =====================================================

CREATE TABLE IF NOT EXISTS historico_escolar (
    id_historico INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL,
    id_materia INT NOT NULL,
    id_ano INT NOT NULL,
    nota DECIMAL(5,2) NOT NULL,

    CONSTRAINT fk_historico_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT fk_historico_materia
        FOREIGN KEY (id_materia)
        REFERENCES materia(id_materia),

    CONSTRAINT fk_historico_ano
        FOREIGN KEY (id_ano)
        REFERENCES ano_letivo(id_ano),

    CONSTRAINT chk_historico_nota
        CHECK (nota >= 0 AND nota <= 10)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- TAREFA
-- =====================================================

CREATE TABLE IF NOT EXISTS tarefa (
    id_tarefa INT PRIMARY KEY AUTO_INCREMENT,
    id_professor INT NOT NULL,
    id_materia INT NOT NULL,
    descricao TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_tarefa_professor
        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor),

    CONSTRAINT fk_tarefa_materia
        FOREIGN KEY (id_materia)
        REFERENCES materia(id_materia)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- NOTA DA TAREFA
-- Uma tarefa pode possuir notas diferentes para vários alunos.
-- =====================================================

CREATE TABLE IF NOT EXISTS tarefa_aluno (
    id_tarefa INT,
    matricula INT,
    nota DECIMAL(5,2) NOT NULL,

    PRIMARY KEY (id_tarefa, matricula),

    CONSTRAINT fk_tarefa_aluno_tarefa
        FOREIGN KEY (id_tarefa)
        REFERENCES tarefa(id_tarefa),

    CONSTRAINT fk_tarefa_aluno_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT chk_tarefa_nota
        CHECK (nota >= 0 AND nota <= 10)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- PROVA
-- =====================================================

CREATE TABLE IF NOT EXISTS prova (
    id_prova INT PRIMARY KEY AUTO_INCREMENT,
    id_professor INT NOT NULL,
    id_materia INT NOT NULL,
    descricao TEXT,
    data_prova DATETIME,

    CONSTRAINT fk_prova_professor
        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor),

    CONSTRAINT fk_prova_materia
        FOREIGN KEY (id_materia)
        REFERENCES materia(id_materia)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- NOTA DA PROVA
-- =====================================================

CREATE TABLE IF NOT EXISTS prova_aluno (
    id_prova INT,
    matricula INT,
    nota DECIMAL(5,2) NOT NULL,

    PRIMARY KEY (id_prova, matricula),

    CONSTRAINT fk_prova_aluno_prova
        FOREIGN KEY (id_prova)
        REFERENCES prova(id_prova),

    CONSTRAINT fk_prova_aluno_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT chk_prova_nota
        CHECK (nota >= 0 AND nota <= 10)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;