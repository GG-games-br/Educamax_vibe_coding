# 01 — Banco de Dados

## Schema base (não alterar sem necessidade)

O arquivo `educamax.sql`, já existente no projeto, define o schema principal. **Use exatamente esses nomes de tabela/coluna** — não renomeie nada por preferência estilística. Resumo das entidades já existentes:

- `prestador_de_servico` — empresas terceirizadas
- `escola` — vinculada a um prestador de serviço
- `cargo` — cargos de funcionários (tem flag `acesso_dados_sensiveis`)
- `aluno`, `professor`, `funcionario`, `responsavel` — pessoas
- `conta` — autenticação; referencia (via FK opcional) **um** dos quatro perfis acima
- `turma`, `ano_letivo`, `aluno_turma`, `professor_turma` — matrícula em turmas por ano
- `materia`
- `historico_escolar` — notas por aluno/matéria/ano
- `tarefa`, `tarefa_aluno` — atividades e suas notas
- `prova`, `prova_aluno` — provas e suas notas

## Regras gerais de acesso ao banco

- **Sempre** usar queries parametrizadas (placeholders). Nunca concatenar entrada de usuário em SQL — proteção contra SQL Injection.
- Senha **nunca** em texto puro — usar hash (bcrypt ou `werkzeug.security.generate_password_hash`), conforme já indicado no comentário da tabela `conta`.
- Operações que envolvem mais de uma tabela (ex.: criar `aluno` + criar `conta` no mesmo cadastro) devem ocorrer dentro de uma transação (commit/rollback), para não deixar dado incompleto se algo falhar no meio.
- Respeitar as constraints já existentes (CHECK de notas entre 0 e 10, UNIQUE de cpf/email/matrícula, FKs).

## Lacunas do schema atual — tabelas que precisam ser criadas

Os requisitos funcionais pedem coisas que **ainda não existem** no `educamax.sql`. A IA de código deve criar essas tabelas novas, seguindo o mesmo padrão de charset/collation/engine do arquivo original (`utf8mb4`, `utf8mb4_unicode_ci`, `InnoDB`), e adicionar essas definições em um novo arquivo de migração (ex.: `educamax_extensoes.sql`), sem apagar ou reescrever o arquivo original.

### 1. `responsavel_aluno` (vínculo responsável ↔ aluno)

O schema atual não diz qual aluno pertence a qual responsável. Sem isso, um responsável não consegue ver "os alunos dele". Sugestão:

```sql
CREATE TABLE IF NOT EXISTS responsavel_aluno (
    id_responsavel INT,
    matricula INT,
    parentesco VARCHAR(50),

    PRIMARY KEY (id_responsavel, matricula),

    CONSTRAINT fk_resp_aluno_responsavel
        FOREIGN KEY (id_responsavel) REFERENCES responsavel(id_responsavel),

    CONSTRAINT fk_resp_aluno_aluno
        FOREIGN KEY (matricula) REFERENCES aluno(matricula)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 2. `requisicao` (solicitações do responsável)

```sql
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

    CONSTRAINT fk_requisicao_responsavel FOREIGN KEY (id_responsavel) REFERENCES responsavel(id_responsavel),
    CONSTRAINT fk_requisicao_aluno FOREIGN KEY (matricula) REFERENCES aluno(matricula),
    CONSTRAINT fk_requisicao_funcionario FOREIGN KEY (id_funcionario_resposta) REFERENCES funcionario(id_funcionario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3. `boleto` (mensalidades e cobranças fictícias)

```sql
CREATE TABLE IF NOT EXISTS boleto (
    id_boleto INT PRIMARY KEY AUTO_INCREMENT,
    matricula INT NOT NULL,
    tipo ENUM('mensalidade', 'farda', 'material', 'prova_substitutiva', 'segunda_chamada', 'outro') NOT NULL,
    id_requisicao INT,
    valor DECIMAL(10,2) NOT NULL,
    status ENUM('pendente', 'pago') NOT NULL DEFAULT 'pendente',
    data_vencimento DATE NOT NULL,
    data_pagamento DATETIME,

    CONSTRAINT fk_boleto_aluno FOREIGN KEY (matricula) REFERENCES aluno(matricula),
    CONSTRAINT fk_boleto_requisicao FOREIGN KEY (id_requisicao) REFERENCES requisicao(id_requisicao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

> Lembrete: `valor` aqui é **fictício**, nunca dinheiro real. Ver `04-financeiro-simulado.md`.

### 4. `folha_pagamento` (status de salário — fictício)

```sql
CREATE TABLE IF NOT EXISTS folha_pagamento (
    id_pagamento INT PRIMARY KEY AUTO_INCREMENT,
    id_professor INT,
    id_funcionario INT,
    mes_referencia TINYINT NOT NULL,
    ano_referencia YEAR NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    status ENUM('pendente', 'pago') NOT NULL DEFAULT 'pendente',
    data_pagamento DATETIME,

    CONSTRAINT fk_folha_professor FOREIGN KEY (id_professor) REFERENCES professor(id_professor),
    CONSTRAINT fk_folha_funcionario FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario),

    CONSTRAINT chk_folha_um_vinculo
        CHECK ( (id_professor IS NOT NULL AND id_funcionario IS NULL)
             OR (id_professor IS NULL AND id_funcionario IS NOT NULL) )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 5. `contrato_prestador` (contrato com prestadores de serviço)

```sql
CREATE TABLE IF NOT EXISTS contrato_prestador (
    id_contrato INT PRIMARY KEY AUTO_INCREMENT,
    id_servico INT NOT NULL,
    descricao TEXT,
    valor DECIMAL(10,2),
    data_inicio DATE NOT NULL,
    data_fim DATE,
    status ENUM('ativo', 'encerrado') NOT NULL DEFAULT 'ativo',

    CONSTRAINT fk_contrato_prestador FOREIGN KEY (id_servico) REFERENCES prestador_de_servico(id_servico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Essas cinco tabelas são a base mínima para os requisitos de requisições, boletos, salários e contratos funcionarem. A IA pode ajustar tipos/tamanhos se necessário, mas deve manter os relacionamentos (FKs) descritos acima.

## Observação sobre login

A tabela `conta` já referencia `id_funcionario` / `id_professor` / `id_aluno` / `id_responsavel` por FK. Ou seja: **antes de existir uma conta, precisa existir a pessoa correspondente** (linha em `aluno`, `professor`, `funcionario` ou `responsavel`). O fluxo de cadastro deve criar as duas coisas juntas, na mesma transação — ver `02-autenticacao-contas.md`.
