# 00 — Visão Geral do Projeto (EducaMax)

> Este é o primeiro de um conjunto de arquivos `.md` com instruções para a IA que vai gerar o código.
> Leia todos antes de começar a codificar, pois eles se complementam:
>
> - `00-visao-geral.md` (este arquivo)
> - `01-banco-de-dados.md`
> - `02-autenticacao-contas.md`
> - `03-perfis-permissoes.md`
> - `04-financeiro-simulado.md`
> - `05-arquitetura-escalabilidade.md`

## O que é o sistema

Software de **gestão operacional escolar**, acessado via navegador, cobrindo:

- Cadastro acadêmico (alunos, professores, funcionários, turmas, matérias, notas, provas, tarefas)
- Autenticação com contas por perfil
- Módulo financeiro **100% simulado** (boletos e salários fictícios)
- Módulo de requisições de responsáveis (farda, material, provas substitutivas/segunda chamada)

## Perfis de usuário

- **Administrativo**
- **Professor**
- **Responsável**
- **Aluno** (perfil com escopo reduzido — ver observação em `03-perfis-permissoes.md`, pois não foi detalhado nos requisitos originais)

## Stack obrigatória

| Camada | Tecnologia |
|---|---|
| Backend | Python + Flask |
| Frontend | HTML + CSS (templates Jinja2), JavaScript apenas quando necessário |
| Banco de dados | MySQL/MariaDB — schema já definido em `educamax.sql` (utf8mb4 / utf8mb4_unicode_ci / InnoDB) |
| Acesso a dados | PyMySQL, mysql-connector-python, **ou** SQLAlchemy mapeando as tabelas já existentes — escolha livre, desde que respeite fielmente nomes de tabelas, colunas e relacionamentos do schema fornecido |

## Regra inegociável: dinheiro é fictício

**Nenhuma parte do sistema deve mover dinheiro real.** Boletos e salários são apenas registros no banco + representação visual. Nada de gateways de pagamento reais, nada de dados de cartão, nada de PIX real. Detalhes completos em `04-financeiro-simulado.md` — essa regra é a mais importante do projeto e não deve ser flexibilizada em nenhuma hipótese, mesmo que pareça "mais completo" implementar um pagamento de verdade.

## Requisitos não funcionais

- Interface gráfica simples, organizada e fácil de entender (não precisa ser bonita, precisa ser clara)
- Código pensado para escalar e para isolar falhas entre módulos (ver `05-arquitetura-escalabilidade.md`)
- Toda entrada de usuário validada e sanitizada (nunca confiar no front-end)
- Código comentado e organizado (PEP8 no Python)

## Ordem sugerida de implementação

1. Banco de dados (schema base + tabelas novas necessárias)
2. Autenticação (registro + login + aprovação de contas)
3. CRUD acadêmico básico (alunos, professores, turmas, matérias)
4. Notas / histórico / provas / tarefas
5. Requisições dos responsáveis
6. Financeiro simulado (boletos + salários)
7. Ajustes de permissão por perfil em todas as rotas já criadas
