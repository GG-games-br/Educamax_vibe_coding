# 03 — Perfis de Usuário e Permissões

O sistema deve responder de forma diferente conforme o perfil logado. Toda checagem de permissão precisa ser feita **no backend** (decorators/middleware por rota), nunca só escondendo elementos no HTML.

## Administrativo

**Pode ver:**
- Notas e histórico escolar de um aluno ou de uma turma inteira
- Provas cadastradas por qualquer professor
- Salários (status fictício) de professores e demais colaboradores
- Requisições dos responsáveis (farda, material, provas substitutivas/segunda chamada)
- Status de boletos: se a escola já "pagou" prestadores e se os responsáveis já "pagaram" a mensalidade dos filhos

**Pode alterar:**
- Notas e histórico escolar de qualquer aluno
- Responder requisições dos responsáveis (aprovar/negar, com resposta)
- Atualizar contratos com prestadores de serviço (`contrato_prestador`) e/ou dados de funcionários

**Pode criar/apagar:**
- Turmas (`turma`), alunos, professores, matérias, prestadores de serviço, contas (inclusive aprovar as pendentes)

## Professor

**Pode ver e alterar:**
- Notas de aluno ou turma — **restrito às turmas/matérias que ele leciona** (usar a tabela `professor_turma` para filtrar; um professor não pode editar nota de uma turma que não é sua)

**Pode ver:**
- Se o **próprio** salário já foi pago (somente o dele, nunca de outro professor/funcionário)

**Pode criar/apagar:**
- Provas e tarefas para uma turma que ele leciona

## Responsável

**Pode ver:**
- Notas e histórico escolar do(s) aluno(s) vinculado(s) a ele — usar a tabela `responsavel_aluno` (ver `01-banco-de-dados.md`) para saber quais alunos ele pode enxergar. Um responsável nunca deve ver dados de um aluno que não é seu vinculado.

**Pode fazer:**
- Solicitar farda, material, prova substitutiva ou segunda chamada (cria registro em `requisicao`)
- Pagar boletos gerados pela mensalidade ou por requisições aprovadas (ação **fictícia** — apenas atualiza `status` do boleto para `pago`, ver `04-financeiro-simulado.md`)

## Aluno — observação importante

Os requisitos originais descrevem apenas Administrativo, Professor e Responsável, mas a tabela `conta` também permite login vinculado a `id_aluno`. Como não há uma definição explícita do que o aluno pode fazer, a recomendação (assumida como padrão razoável, a confirmar com você) é:

- Aluno loga e visualiza, **somente as próprias**, notas e histórico escolar (visão parecida com a do responsável, porém restrita a si mesmo, sem acesso a requisições ou boletos).
- Se você quiser um comportamento diferente (ex.: aluno também poder solicitar farda/material, ou aluno não ter login algum nesta primeira versão), isso deve ser ajustado aqui antes de implementar.

## Resumo em tabela

| Ação | Administrativo | Professor | Responsável | Aluno |
|---|---|---|---|---|
| Ver notas/histórico (todos) | ✅ | Só suas turmas | Só seu(s) aluno(s) | Só as próprias |
| Editar notas/histórico | ✅ | Só suas turmas | ❌ | ❌ |
| Ver provas de professores | ✅ | Só as próprias | ❌ | ❌ |
| Criar prova/tarefa | ❌ | ✅ (suas turmas) | ❌ | ❌ |
| Ver salários | Todos | Só o próprio | ❌ | ❌ |
| Ver/responder requisições | ✅ | ❌ | Criar apenas | ❌ |
| Pagar boletos (fictício) | ❌ | ❌ | ✅ | ❌ |
| Criar/apagar turma, aluno, professor, matéria, prestador, conta | ✅ | ❌ | ❌ | ❌ |
| Aprovar contas de professor/administrativo | ✅ | ❌ | ❌ | ❌ |
