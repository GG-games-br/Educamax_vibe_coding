# 05 — Arquitetura e Escalabilidade

## "Microsserviços" vs. monolito modular — leitura recomendada antes de decidir

Microsserviços de verdade (serviços independentes, cada um com seu próprio processo/deploy/possivelmente seu próprio banco, comunicando-se por HTTP ou fila de mensagens) resolvem o problema de isolamento de falhas, mas trazem bastante complexidade operacional (descoberta de serviços, chamadas de rede, consistência entre bancos, etc.) — normalmente mais do que um projeto deste porte precisa no início.

Uma alternativa pragmática, que entrega o mesmo objetivo prático descrito no requisito ("quando uma parte não funcionar, as outras continuam operando"), é um **monolito modular**: uma única aplicação Flask organizada em **Blueprints**, um por domínio (auth, admin, professor, responsável, financeiro, requisições, notas, provas/tarefas), onde:

- Cada blueprint tem suas próprias rotas e sua própria camada de acesso a dados.
- Cada blueprint trata suas próprias exceções (try/except nas bordas), para que uma falha em "financeiro" nunca derrube "login" ou "notas".
- As fronteiras entre módulos já ficam bem definidas, então **depois**, se realmente for necessário, dá para extrair qualquer blueprint para um microsserviço de verdade sem reescrever tudo.

Recomendação: comece com o monolito modular. Se, mais adiante, algum módulo específico precisar escalar de forma independente (ex.: muito tráfego só no módulo financeiro), aí sim vale a pena separá-lo como um serviço próprio.

## Estrutura de pastas sugerida

```
project/
  app/
    __init__.py            # application factory (create_app)
    extensions.py           # instância do db, login_manager, etc.
    blueprints/
      auth/
      admin/
      professor/
      responsavel/
      financeiro/
      requisicoes/
      notas/
      provas_tarefas/
    templates/
      base.html
      auth/...
      admin/...
      ...
    static/
      css/
      js/
    models/                  # mapeamento das tabelas (se usar SQLAlchemy)
    services/                # regras de negócio (camada entre rota e banco)
  config.py                  # lê variáveis de ambiente
  requirements.txt
  run.py
```

## Camadas dentro de cada módulo

`rota (view)` → `service (regra de negócio)` → `repository/DAO (acesso ao banco)`

Isso evita queries SQL soltas espalhadas dentro das views, facilitando manutenção e testes.

## Boas práticas de escalabilidade

- Configuração (credenciais de banco, secret key) sempre via variáveis de ambiente (`.env`), nunca hardcoded no código.
- Logging por módulo, para localizar rapidamente onde uma falha ocorreu.
- Paginação em qualquer listagem potencialmente grande (lista de alunos, lista de notas, etc.) desde o início — evita reescrever isso depois.
- Testes automatizados (ex.: `pytest`) ao menos para as regras mais críticas: login, permissões por perfil, e o módulo financeiro fictício.
- Rota simples de health-check (`/health`) para monitorar se a aplicação está de pé.

## Interface gráfica

- HTML + CSS via templates Jinja2, reaproveitando um `base.html` comum (menu lateral/topo variando conforme o perfil logado).
- Pode usar um framework CSS leve (ex.: Bootstrap) para acelerar, desde que a interface fique clara e organizada — não é necessário design sofisticado, apenas fácil de entender e navegar por qualquer um dos quatro perfis.
