# Reflexão

## 1. Por que citar a FONTE?

O assistente precisa citar a FONTE porque as políticas internas podem ser atualizadas ou revogadas. Sem rastreabilidade, um colaborador poderia seguir uma regra antiga, como a POL-004, gerando erros operacionais, riscos trabalhistas e problemas de compliance. A citação permite conferir a vigência e a autoridade da informação, aumentando a confiança no sistema.

## 2. Decisão mais difícil

A decisão mais difícil foi o threshold. Um valor alto faria o assistente dizer "não encontrei" para perguntas respondíveis, como P04, com score 0.31. Um valor baixo permitiria respostas irrelevantes para perguntas sem resposta, como P10, com score 0.27. Esse score ficou relativamente alto porque perguntas iniciadas por "quantos" ou "qual" podem puxar chunks inadequados devido à frequência dessas palavras. Como as perguntas respondíveis ficaram entre 0.31 e 0.56, escolhi 0.30.

Essa limitação me levou a questionar se um limite fixo funcionaria com centenas de documentos. Em produção, empresas combinam busca lexical, como BM25, com embeddings, busca híbrida e reranking. Também usam stopwords, query rewriting e conjuntos de avaliação com perguntas reais para recalibrar o sistema conforme o corpus muda.

## 3. Se tivesse um LLM

O LLM poderia transformar os chunks recuperados em uma resposta mais natural. O risco seria alucinar ou misturar políticas. Para reduzi-lo, eu usaria o score como pré-filtro e instruiria o modelo a responder somente com base nos chunks, citar a FONTE e dizer "não encontrei" quando eles não sustentassem uma resposta.
