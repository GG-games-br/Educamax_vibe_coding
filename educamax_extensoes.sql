-- =====================================================
-- BANCO DE DADOS: ESCOLA_DB - EXTENSÕES E COMPLEMENTOS
-- =====================================================
-- Arquivo complementar ao educamax.sql para atender
-- aos requisitos das fases do projeto:
-- - Vínculo Responsável <-> Aluno
-- - Módulo de Requisições de Responsáveis
-- - Módulo Financeiro Simulado (Boletos e Salários)
-- - Contratos com Prestadores de Serviços
-- - Status de aprovação de contas
--
-- ATENÇÃO (REGRA INEGOCIÁVEL):
-- Todos os valores financeiros registrados aqui
-- são 100% FICTÍCIOS. Nenhuma transação real deve ocorrer.
-- =====================================================

USE escola_db;


-- =====================================================
-- 1. VÍNCULO RESPONSÁVEL <-> ALUNO
-- Permite que um responsável visualize e gerencie
-- exclusivamente seus alunos vinculados.
-- =====================================================

CREATE TABLE IF NOT EXISTS responsavel_aluno (
    id_responsavel INT NOT NULL,
    matricula INT NOT NULL,
    parentesco VARCHAR(50),

    PRIMARY KEY (id_responsavel, matricula),

    CONSTRAINT fk_resp_aluno_responsavel
        FOREIGN KEY (id_responsavel)
        REFERENCES responsavel(id_responsavel),

    CONSTRAINT fk_resp_aluno_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- 2. REQUISIÇÃO (SOLICITAÇÕES DO RESPONSÁVEL)
-- Registro de solicitações de farda, material escolar,
-- prova substitutiva ou segunda chamada.
-- =====================================================

CREATE TABLE IF NOT EXISTS requisicao (
    id_requisicao INT PRIMARY KEY AUTO_INCREMENT,
    id_responsavel INT NOT NULL,
    matricula INT NOT NULL,
    tipo ENUM('farda', 'material', 'prova_substitutiva', 'segunda_chamada') NOT NULL,
    descricao TEXT,
    status ENUM('pendente', 'aprovada', 'negada') NOT NULL DEFAULT 'pendente',
    resposta_administrativo TEXT,
    id_funcionario_resposta INT,
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_resposta DATETIME,

    CONSTRAINT fk_requisicao_responsavel
        FOREIGN KEY (id_responsavel)
        REFERENCES responsavel(id_responsavel),

    CONSTRAINT fk_requisicao_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT fk_requisicao_funcionario
        FOREIGN KEY (id_funcionario_resposta)
        REFERENCES funcionario(id_funcionario)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- 3. BOLETO (MENSALIDADES E COBRANÇAS SIMULADAS)
-- Registros de cobranças fictícias geradas pelo sistema
-- (mensalidades recorrentes ou derivadas de requisições).
-- =====================================================

CREATE TABLE IF NOT EXISTS boleto (
    id_boleto INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL,
    tipo ENUM('mensalidade', 'farda', 'material', 'prova_substitutiva', 'segunda_chamada', 'outro') NOT NULL,
    id_requisicao INT,
    valor DECIMAL(10,2) NOT NULL,
    status ENUM('pendente', 'pago') NOT NULL DEFAULT 'pendente',
    data_vencimento DATE NOT NULL,
    data_pagamento DATETIME,

    CONSTRAINT fk_boleto_aluno
        FOREIGN KEY (matricula)
        REFERENCES aluno(matricula),

    CONSTRAINT fk_boleto_requisicao
        FOREIGN KEY (id_requisicao)
        REFERENCES requisicao(id_requisicao)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- 4. FOLHA DE PAGAMENTO (SALÁRIOS SIMULADOS)
-- Registros de salários de professores e funcionários.
-- Status de pagamento fictício controlado pelo administrativo.
-- =====================================================

CREATE TABLE IF NOT EXISTS folha_pagamento (
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    id_professor INT,
    id_funcionario INT,
    mes_referencia TINYINT NOT NULL,
    ano_referencia YEAR NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    status ENUM('pendente', 'pago') NOT NULL DEFAULT 'pendente',
    data_pagamento DATETIME,

    CONSTRAINT fk_folha_professor
        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor),

    CONSTRAINT fk_folha_funcionario
        FOREIGN KEY (id_funcionario)
        REFERENCES funcionario(id_funcionario),

    CONSTRAINT chk_folha_um_vinculo
        CHECK (
            (id_professor IS NOT NULL AND id_funcionario IS NULL)
            OR (id_professor IS NULL AND id_funcionario IS NOT NULL)
        )
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- 5. CONTRATO DE PRESTADOR DE SERVIÇO
-- Contratos firmados entre a instituição e prestadores.
-- Valores meramente informativos e fictícios.
-- =====================================================

CREATE TABLE IF NOT EXISTS contrato_prestador (
    id_contrato INT PRIMARY KEY AUTO_INCREMENT,
    id_servico INT NOT NULL,
    descricao TEXT,
    valor DECIMAL(10,2),
    data_inicio DATE NOT NULL,
    data_fim DATE,
    status ENUM('ativo', 'encerrado') NOT NULL DEFAULT 'ativo',

    CONSTRAINT fk_contrato_prestador
        FOREIGN KEY (id_servico)
        REFERENCES prestador_de_servico(id_servico)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- =====================================================
-- 6. AJUSTE DE STATUS NA TABELA CONTA (PROCEDURE SEGURA)
-- Adiciona a coluna status_conta ('pendente', 'ativo', 'recusado')
-- na tabela conta para o fluxo de aprovação de contas
-- (professores e funcionários) conforme 02-autenticacao-contas.md.
-- =====================================================

DROP PROCEDURE IF EXISTS adicionar_coluna_status_conta;

DELIMITER //
CREATE PROCEDURE adicionar_coluna_status_conta()
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'conta'
          AND COLUMN_NAME = 'status_conta'
    ) THEN
        ALTER TABLE conta
            ADD COLUMN status_conta ENUM('pendente', 'ativo', 'recusado') NOT NULL DEFAULT 'ativo';
    END IF;
END //
DELIMITER ;

CALL adicionar_coluna_status_conta();

DROP PROCEDURE IF EXISTS adicionar_coluna_status_conta;
