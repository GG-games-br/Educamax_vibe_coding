# 04 — Módulo Financeiro Simulado (dinheiro fictício)

## Princípio central — leia antes de implementar qualquer coisa aqui

**Nenhuma transação financeira real deve ocorrer neste sistema.** Boletos, mensalidades e salários são apenas registros no banco de dados e representações visuais em tela — não existe dinheiro de verdade envolvido em nenhum momento. Isso vale para o projeto inteiro, mesmo que pareça "mais completo" adicionar uma integração real.

**Proibido, em qualquer circunstância:**
- Integrar gateways de pagamento reais (Stripe, Mercado Pago, PagSeguro, PayPal, etc.)
- Gerar PIX real (chave, QR code que efetivamente transfere dinheiro)
- Pedir ou armazenar dados reais de cartão de crédito/débito
- Qualquer chamada de API externa que envolva movimentação financeira real

Toda operação financeira do sistema é, na prática, apenas um **UPDATE de status** em uma tabela do próprio banco de dados da aplicação.

## Boletos (tabela `boleto`)

- Gerados pelo sistema para: mensalidade (recorrente, ex. mensal) ou como resultado de uma `requisicao` aprovada (farda, material, prova substitutiva, segunda chamada).
- Tela de boleto pode ter aparência visual de um boleto real (valor, vencimento, "beneficiário" = escola, linha digitável de mentirinha), mas isso é só estética — não gera nenhum boleto bancário de verdade.
- Recomenda-se deixar visualmente claro que é uma simulação (ex.: uma tag/selo "Ambiente de demonstração" ou "Valor fictício" na tela do boleto), para não gerar confusão futura sobre a natureza do documento.
- Ação "Pagar boleto", disponível apenas ao responsável:
  - Atualiza `status = 'pago'` e `data_pagamento = NOW()`.
  - Não deduz saldo de lugar nenhum real; se você quiser simular um "saldo fictício" do responsável (funcionalidade extra opcional, não obrigatória), isso pode ser um campo/tabela adicional só para fins de demonstração, sempre deixando claro que é fictício.

## Salários (tabela `folha_pagamento`)

- Lançamento mensal criado pelo administrativo, com `status = 'pendente'` por padrão.
- Administrativo pode marcar como `pago` (apenas muda o status/data, sem mover dinheiro real).
- Professor/funcionário só enxerga o **próprio** status (read-only) — nunca o de colegas.

## Contratos com prestadores de serviço (tabela `contrato_prestador`)

- `valor` do contrato é apenas informativo/fictício.
- Administrativo pode atualizar valor, vigência e status (`ativo`/`encerrado`) do contrato — sem qualquer transferência real associada.

## Resumo para a IA de código

Sempre que for implementar qualquer tela ou rota relacionada a "pagamento", "boleto" ou "salário": a única coisa que o backend faz é ler/escrever linhas nas tabelas `boleto` / `folha_pagamento` / `contrato_prestador`. Não há necessidade (e não é permitido) chamar nenhuma API financeira externa.
