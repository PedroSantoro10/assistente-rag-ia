# Evidências – Desafio Bootcamp SEP26

## Parte 0 – Setup e Leitura do Corpus

Metadados carregados: 12 documentos. Contagem por status: 11 vigentes, 1 revogada.

| doc_id | status | num_palavras |
|--------|--------|--------------|
| POL-001 | vigente | 164 |
| POL-002 | vigente | 136 |
| POL-003 | vigente | 128 |
| POL-004 | revogada | 90 |
| POL-005 | vigente | 119 |
| POL-006 | vigente | 117 |
| POL-007 | vigente | 114 |
| POL-008 | vigente | 119 |
| POL-009 | vigente | 142 |
| POL-010 | vigente | 92 |
| POL-011 | vigente | 102 |
| FAQ-001 | vigente | 145 |

## Parte 1 – Chunking por Seção

Total de chunks gerados: **46**.

Chunks por documento:
- FAQ-001: 6
- POL-001: 3
- POL-002: 4
- POL-003: 4
- POL-004: 3
- POL-005: 3
- POL-006: 4
- POL-007: 4
- POL-008: 4
- POL-009: 4
- POL-010: 3
- POL-011: 4

Exemplo de chunk completo:
- doc_id: POL-001
- titulo: POL-001 Política de Onboarding
- secao: Objetivo
- status: vigente
- texto: Esta política define as etapas dos primeiros 30 dias de um novo colaborador na Horizonte Tech.

## Parte 2 – Indexação com TF-IDF

- Shape da matriz TF-IDF: (46, 350)
- Tamanho do vocabulário: 350 termos
- Pré-processamento: lowercase obrigatório aplicado. Sem remoção de acentos e sem remoção de stopwords para manter simplicidade e evitar perda de informação em português.

## Parte 3 – Recuperação Top-K

**P01: Com quantos dias de antecedência devo solicitar minhas férias?**
- POL-002 | Como solicitar | score=0.41
- POL-002 | Venda de dias | score=0.41
- POL-002 | Direito a férias | score=0.25

**P02: Quantos dias por semana posso trabalhar de forma remota?**
- POL-005 | Regra de trabalho remoto | score=0.53
- FAQ-001 | Posso trabalhar remoto todos os dias? | score=0.20
- POL-008 | Entrevista de saída | score=0.17

**P10: Qual é a política de estacionamento da empresa?**
- POL-003 | Auxílio para trabalho remoto | score=0.27
- POL-008 | Aviso | score=0.21
- POL-001 | Objetivo | score=0.18

Confirmação: POL-004 (revogada) não apareceu em nenhum resultado, comprovando a regra de vigência.

## Parte 4 – Resposta Extrativa

Threshold escolhido: **0.30**

Justificativa: Os scores das 9 perguntas com resposta ficaram entre 0.31 e 0.56; a P10 (sem resposta) teve score máximo de 0.27. O valor 0.30 separa corretamente os dois grupos.

Saída para P02:
PERGUNTA: Quantos dias por semana posso trabalhar de forma remota?
RESPOSTA: O colaborador pode trabalhar de forma remota em até 3 dias por semana. Os dias presenciais obrigatórios são terça-feira e quinta-feira.
FONTE: POL-005 | POL-005 Política de Trabalho Híbrido (versão 2) | Seção: Regra de trabalho remoto
SCORE: 0.53
STATUS: encontrado

Saída para P10:
PERGUNTA: Qual é a política de estacionamento da empresa?
RESPOSTA: Não encontrei essa informação nas políticas vigentes. Procure a área de Pessoas e Cultura.
FONTE: nenhuma
SCORE: 0.27
STATUS: nao_encontrado

## Parte 5 – Avaliação

| pergunta_id | doc_esperado | doc_retornado_1 | score | STATUS | acerto |
|-------------|--------------|-----------------|-------|--------|--------|
| P01 | POL-002 | POL-002 | 0.41 | encontrado | sim |
| P02 | POL-005 | POL-005 | 0.53 | encontrado | sim |
| P03 | POL-003 | POL-003 | 0.56 | encontrado | sim |
| P04 | POL-006 | POL-006 | 0.31 | encontrado | sim |
| P05 | POL-009 | POL-009 | 0.33 | encontrado | sim |
| P06 | POL-007 | POL-007 | 0.50 | encontrado | sim |
| P07 | POL-008 | POL-008 | 0.39 | encontrado | sim |
| P08 | POL-009 | POL-009 | 0.47 | encontrado | sim |
| P09 | POL-010 | POL-010 | 0.32 | encontrado | sim |
| P10 | nao_encontrado | POL-003 | 0.27 | nao_encontrado | sim |

**Hit@1: 1.00**
**Hit@3: 1.00**

P10: STATUS devolvido foi `nao_encontrado` - **acerto**.

Análise de erro: Não houve erros. Todas as 10 perguntas foram respondidas corretamente. A margem mais apertada ficou com P04 (score 0.31) e P09 (score 0.32), próximas do threshold de 0.30. Se o threshold fosse maior (ex: 0.35), essas perguntas passariam a ser incorretamente classificadas como "não encontrado"; se fosse menor (ex: 0.25), a P10 poderia ser erroneamente respondida com POL-003. Em um corpus maior, um threshold fixo poderia deixar de funcionar, então eu testaria stopwords, BM25 e embeddings, além de recalibrar o valor com perguntas reais.