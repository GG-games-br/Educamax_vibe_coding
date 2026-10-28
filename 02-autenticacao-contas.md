# 02 — Autenticação e Gestão de Contas

## Registro — dois fluxos diferentes

### A) Aluno e Responsável → cadastro direto (sem aprovação)

- Formulário pede os campos obrigatórios da tabela correspondente (`aluno` ou `responsavel`), **exceto o Id** (auto incremento): nome, cpf, número, email, e no caso de aluno também a matrícula.
- Junto, pede email + senha para a `conta`.
- Ao enviar: criar, na mesma transação, (1) a linha em `aluno`/`responsavel` e (2) a linha em `conta` já vinculada por FK, com `ativo = TRUE`.
- Validar duplicidade de `cpf`, `email` e (se aluno) `matricula` **antes** de tentar inserir, mostrando erro claro em vez de deixar o banco estourar a constraint UNIQUE.

### B) Professor e Administrativo (`funcionario`) → depende de aprovação

- Formulário pede os campos obrigatórios de `professor` ou `funcionario` (incluindo `id_cargo`, no caso de funcionário), exceto o Id.
- **Não ativa a conta imediatamente.** Sugestão de implementação simples: adicionar uma coluna de status na conta, por exemplo `status_conta ENUM('pendente','ativo','recusado') DEFAULT 'pendente'`, em vez do booleano `ativo` sozinho (ou usar `ativo = FALSE` até a aprovação, se preferir manter o schema mais próximo do original).
- A pessoa (`professor`/`funcionario`) e a `conta` já podem ser criadas no banco no momento do cadastro, mas a conta fica marcada como pendente e **não permite login** até aprovação.
- Um usuário administrativo (funcionário com permissão adequada — ex.: cargo específico, ou `cargo.acesso_dados_sensiveis = TRUE`, a critério da implementação) deve ter uma tela listando "solicitações de conta pendentes", com ações de **aprovar** ou **recusar**.
- Ao aprovar: `status_conta = 'ativo'` (ou `ativo = TRUE`). Ao recusar: `status_conta = 'recusado'` (mantém histórico) ou remove o registro, a critério da implementação — mas nunca deixar recusado logar.

## Login

- Login exige apenas **dois campos**: (**email OU nome**) + **senha**.
- Lógica sugerida no backend:
  1. Tentar encontrar `conta` pelo campo `email`.
  2. Se o valor digitado não bater com nenhum email, buscar pelo `nome` na tabela do perfil correspondente (`aluno`, `professor`, `funcionario`, `responsavel`) e fazer o JOIN até a `conta` vinculada.
  3. Comparar a senha informada com o hash salvo.
  4. Se a conta estiver `pendente` ou `recusada`/inativa, bloquear o login com mensagem explicativa ("sua conta ainda aguarda aprovação do administrativo" / "conta desativada").

## Sessão e autorização

- Usar `Flask-Login` (ou mecanismo equivalente de sessão) guardando: `id_conta` e **qual perfil** está logado (qual das 4 FKs da conta está preenchida — isso define o "tipo de usuário" usado em `03-perfis-permissoes.md`).
- Toda rota protegida deve checar o perfil no backend (nunca confiar apenas em esconder botões no HTML).

## Segurança recomendada

- CSRF protection nos formulários (ex.: `Flask-WTF`).
- Limitar tentativas de login (rate limiting), para evitar força bruta — opcional, mas recomendado.
- Nunca logar/expor senha ou hash em mensagens de erro, logs ou respostas da API.
