"""
Armazenamento em memória para o Modo Demonstração Offline do EducaMax.
Permite navegar por todo o sistema escolar, aprovar contas, emitir boletos,
pagar boletos simulados, gerenciar turmas e notas sem precisar de MySQL ativo.
"""

from datetime import datetime, date

class MockDataStore:
    def __init__(self):
        self.reset()

    def reset(self):
        self.anos_letivos = [
            {"id_ano": 1, "ano": 2026}
        ]

        self.cargos = [
            {"id_cargo": 1, "nome": "Administrador Geral", "acesso_dados_sensiveis": 1},
            {"id_cargo": 2, "nome": "Secretário Acadêmico", "acesso_dados_sensiveis": 1},
            {"id_cargo": 3, "nome": "Coordenador Pedagógico", "acesso_dados_sensiveis": 1},
            {"id_cargo": 4, "nome": "Auxiliar Administrativo", "acesso_dados_sensiveis": 0}
        ]

        self.turmas = [
            {"id_turma": "1a", "total_alunos": 2},
            {"id_turma": "1b", "total_alunos": 1},
            {"id_turma": "2a", "total_alunos": 0},
            {"id_turma": "3a", "total_alunos": 0}
        ]

        self.materias = [
            {"id_materia": 1, "nome": "Matemática"},
            {"id_materia": 2, "nome": "Língua Portuguesa"},
            {"id_materia": 3, "nome": "História"},
            {"id_materia": 4, "nome": "Geografia"},
            {"id_materia": 5, "nome": "Ciências da Natureza"}
        ]

        self.prestadores = [
            {
                "id_servico": 1,
                "cnpj": "12345678000199",
                "servico": "Nutrição & Alimentação Escolar Ltda",
                "numero": "11987654321",
                "email": "contato@nutricaoescola.com.br"
            },
            {
                "id_servico": 2,
                "cnpj": "98765432000111",
                "servico": "Transporte e Vans Escolares Segura",
                "numero": "11999887766",
                "email": "transporte@educamax.com.br"
            }
        ]

        self.alunos = [
            {
                "id_aluno": 1,
                "matricula": 1001,
                "cpf": "11122233344",
                "nome": "Lucas Silva de Oliveira",
                "email": "lucas.silva@escola.com",
                "numero": "11911112222",
                "id_turma": "1a",
                "ano": 2026
            },
            {
                "id_aluno": 2,
                "matricula": 1002,
                "cpf": "22233344455",
                "nome": "Mariana Souza Santos",
                "email": "mariana.souza@escola.com",
                "numero": "11922223333",
                "id_turma": "1a",
                "ano": 2026
            },
            {
                "id_aluno": 3,
                "matricula": 1003,
                "cpf": "33344455566",
                "nome": "Gabriel Santos Mendes",
                "email": "gabriel.santos@escola.com",
                "numero": "11933334444",
                "id_turma": "1b",
                "ano": 2026
            }
        ]

        self.professores = [
            {
                "id_professor": 1,
                "matricula": 2001,
                "cpf": "44455566677",
                "nome": "Prof. Carlos Eduardo (Matemática)",
                "email": "professor@gmail.com",
                "numero": "11944445555",
                "total_turmas": 2
            },
            {
                "id_professor": 2,
                "matricula": 2002,
                "cpf": "55566677788",
                "nome": "Profa. Ana Paula (Português)",
                "email": "ana.paula@escola.com",
                "numero": "11955556666",
                "total_turmas": 1
            }
        ]

        self.responsaveis = [
            {
                "id_responsavel": 1,
                "cpf": "66677788899",
                "nome": "Responsável EducaMax (Pai do Lucas)",
                "email": "responsavel@gmail.com",
                "numero": "11966667777",
                "total_dependentes": 1
            },
            {
                "id_responsavel": 2,
                "cpf": "77788899900",
                "nome": "Juliana Souza (Mãe da Mariana)",
                "email": "juliana.souza@email.com",
                "numero": "11977778888",
                "total_dependentes": 1
            }
        ]

        self.professor_turma = [
            {"id_professor": 1, "id_turma": "1a", "id_ano": 1},
            {"id_professor": 1, "id_turma": "2a", "id_ano": 1},
            {"id_professor": 2, "id_turma": "1b", "id_ano": 1}
        ]

        self.aluno_turma = [
            {"matricula": 1001, "id_turma": "1a", "id_ano": 1},
            {"matricula": 1002, "id_turma": "1a", "id_ano": 1},
            {"matricula": 1003, "id_turma": "1b", "id_ano": 1}
        ]

        self.responsavel_aluno = [
            {"id_responsavel": 1, "matricula": 1001, "parentesco": "Pai"},
            {"id_responsavel": 2, "matricula": 1002, "parentesco": "Mãe"}
        ]

        self.contas_pendentes = [
            {
                "id_conta": 101,
                "email": "prof.ricardo@escola.com",
                "ativo": 0,
                "status_conta": "pendente",
                "tipo_perfil": "Professor",
                "nome": "Prof. Ricardo Mendes",
                "cpf": "88899900011",
                "numero": "11988889999",
                "cargo_nome": None
            },
            {
                "id_conta": 102,
                "email": "secretaria.marcela@escola.com",
                "ativo": 0,
                "status_conta": "pendente",
                "tipo_perfil": "Funcionário / Administrativo",
                "nome": "Marcela Lima da Silva",
                "cpf": "99900011122",
                "numero": "11999990000",
                "cargo_nome": "Secretário Acadêmico"
            }
        ]

        self.boletos = [
            {
                "id_boleto": 1,
                "matricula": 1001,
                "tipo": "mensalidade",
                "valor": 650.00,
                "status": "pendente",
                "data_vencimento": "2026-11-10",
                "data_pagamento": None,
                "id_requisicao": None,
                "nome_aluno": "Lucas Silva de Oliveira",
                "cpf_aluno": "11122233344",
                "email_aluno": "lucas.silva@escola.com"
            },
            {
                "id_boleto": 2,
                "matricula": 1001,
                "tipo": "material",
                "valor": 120.00,
                "status": "pago",
                "data_vencimento": "2026-10-15",
                "data_pagamento": "2026-10-14 10:30:00",
                "id_requisicao": None,
                "nome_aluno": "Lucas Silva de Oliveira",
                "cpf_aluno": "11122233344",
                "email_aluno": "lucas.silva@escola.com"
            },
            {
                "id_boleto": 3,
                "matricula": 1002,
                "tipo": "mensalidade",
                "valor": 650.00,
                "status": "pago",
                "data_vencimento": "2026-10-10",
                "data_pagamento": "2026-10-09 14:15:00",
                "id_requisicao": None,
                "nome_aluno": "Mariana Souza Santos",
                "cpf_aluno": "22233344455",
                "email_aluno": "mariana.souza@escola.com"
            }
        ]

        self.folhas_pagamento = [
            {
                "id_pagamento": 1,
                "id_professor": 1,
                "id_funcionario": None,
                "mes_referencia": 10,
                "ano_referencia": 2026,
                "valor": 4800.00,
                "status": "pago",
                "data_pagamento": "2026-10-05 08:00:00",
                "nome_beneficiario": "Prof. Carlos Eduardo (Matemática)",
                "cpf_beneficiario": "44455566677",
                "tipo_cargo": "Professor",
                "cargo_nome": "Professor Titular"
            },
            {
                "id_pagamento": 2,
                "id_professor": 1,
                "id_funcionario": None,
                "mes_referencia": 11,
                "ano_referencia": 2026,
                "valor": 4800.00,
                "status": "pendente",
                "data_pagamento": None,
                "nome_beneficiario": "Prof. Carlos Eduardo (Matemática)",
                "cpf_beneficiario": "44455566677",
                "tipo_cargo": "Professor",
                "cargo_nome": "Professor Titular"
            },
            {
                "id_pagamento": 3,
                "id_professor": None,
                "id_funcionario": 1,
                "mes_referencia": 10,
                "ano_referencia": 2026,
                "valor": 5500.00,
                "status": "pago",
                "data_pagamento": "2026-10-05 08:00:00",
                "nome_beneficiario": "Administrador Geral",
                "cpf_beneficiario": "00000000001",
                "tipo_cargo": "Funcionário",
                "cargo_nome": "Administrador Geral"
            }
        ]

        self.contratos = [
            {
                "id_contrato": 1,
                "id_servico": 1,
                "descricao": "Fornecimento diário de merenda e lanches saudáveis",
                "valor": 12500.00,
                "data_inicio": "2026-02-01",
                "data_fim": "2026-12-20",
                "status": "ativo",
                "nome_prestador": "Nutrição & Alimentação Escolar Ltda",
                "cnpj": "12345678000199"
            },
            {
                "id_contrato": 2,
                "id_servico": 2,
                "descricao": "Vans e transporte de excursões pedagógicas",
                "valor": 8000.00,
                "data_inicio": "2026-03-01",
                "data_fim": "2026-11-30",
                "status": "ativo",
                "nome_prestador": "Transporte e Vans Escolares Segura",
                "cnpj": "98765432000111"
            }
        ]

        self.requisicoes = [
            {
                "id_requisicao": 1,
                "id_responsavel": 1,
                "matricula": 1001,
                "tipo": "farda",
                "descricao": "Solicito 2 novos uniformes escolares completos (tamanho 12).",
                "status": "pendente",
                "resposta_administrativo": None,
                "id_funcionario_resposta": None,
                "data_solicitacao": "2026-10-25 09:12:00",
                "data_resposta": None,
                "nome_aluno": "Lucas Silva de Oliveira",
                "nome_responsavel": "Responsável EducaMax (Pai do Lucas)",
                "cpf_responsavel": "66677788899",
                "nome_funcionario_resposta": None
            },
            {
                "id_requisicao": 2,
                "id_responsavel": 1,
                "matricula": 1001,
                "tipo": "segunda_chamada",
                "descricao": "Segunda chamada de Matemática (atestado médico apresentado).",
                "status": "aprovada",
                "resposta_administrativo": "Segunda chamada autorizada para a próxima quarta-feira.",
                "id_funcionario_resposta": 1,
                "data_solicitacao": "2026-10-20 14:00:00",
                "data_resposta": "2026-10-21 10:00:00",
                "nome_aluno": "Lucas Silva de Oliveira",
                "nome_responsavel": "Responsável EducaMax (Pai do Lucas)",
                "cpf_responsavel": "66677788899",
                "nome_funcionario_resposta": "Administrador Geral"
            }
        ]

        self.provas = [
            {
                "id_prova": 1,
                "id_professor": 1,
                "id_materia": 1,
                "descricao": "Avaliação Bimestral - Álgebra e Equações",
                "data_prova": "2026-10-15 08:00:00",
                "nome_materia": "Matemática"
            }
        ]

        self.tarefas = [
            {
                "id_tarefa": 1,
                "id_professor": 1,
                "id_materia": 1,
                "descricao": "Lista de Exercícios 03 - Geometria Plana",
                "data_criacao": "2026-10-10 11:00:00",
                "nome_materia": "Matemática"
            }
        ]

        self.provas_aluno = [
            {
                "nota": 8.50,
                "descricao": "Avaliação Bimestral - Álgebra e Equações",
                "data_prova": "2026-10-15 08:00:00",
                "nome_materia": "Matemática",
                "nome_professor": "Prof. Carlos Eduardo (Matemática)",
                "matricula": 1001,
                "id_prova": 1
            }
        ]

        self.tarefas_aluno = [
            {
                "nota": 9.00,
                "descricao": "Lista de Exercícios 03 - Geometria Plana",
                "data_criacao": "2026-10-10 11:00:00",
                "nome_materia": "Matemática",
                "nome_professor": "Prof. Carlos Eduardo (Matemática)",
                "matricula": 1001,
                "id_tarefa": 1
            }
        ]

        self.historicos = [
            {
                "id_historico": 1,
                "matricula": 1001,
                "id_materia": 1,
                "nome_materia": "Matemática",
                "id_ano": 1,
                "ano": 2026,
                "nota": 8.80
            },
            {
                "id_historico": 2,
                "matricula": 1001,
                "id_materia": 2,
                "nome_materia": "Língua Portuguesa",
                "id_ano": 1,
                "ano": 2026,
                "nota": 9.20
            },
            {
                "id_historico": 3,
                "matricula": 1001,
                "id_materia": 3,
                "nome_materia": "História",
                "id_ano": 1,
                "ano": 2026,
                "nota": 7.50
            }
        ]

mock_db = MockDataStore()

