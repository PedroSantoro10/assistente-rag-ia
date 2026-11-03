# ============================================================
# DESAFIO BOOTCAMP AI/R FELLOWSHIP SEP26
# Assistente de P&R sobre Políticas Internas
# ============================================================

import os
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================
PASTA_CORPUS = "corpus"
ARQ_METADADOS = "metadados.csv"
ARQ_GABARITO = "perguntas_gabarito.csv"
THRESHOLD = 0.30

# ============================================================
# PARTE 0 – SETUP E LEITURA DO CORPUS
# ============================================================
print("=" * 60)
print("PARTE 0 – SETUP E LEITURA DO CORPUS")
print("=" * 60)

df_metadados = pd.read_csv(ARQ_METADADOS)
print(f"\nMetadados carregados: {len(df_metadados)} documentos")
print(df_metadados.head())

def ler_documento(nome_arquivo):
    """Lê o arquivo Markdown correspondente ao nome informado."""
    caminho = os.path.join(PASTA_CORPUS, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

df_metadados["texto"] = df_metadados["arquivo"].apply(ler_documento)

print("\nContagem por status:")
print(df_metadados["status"].value_counts())

df_metadados["num_palavras"] = df_metadados["texto"].apply(lambda t: len(t.split()))
evidencia_p0 = df_metadados[["doc_id", "status", "num_palavras"]]
print("\n--- EVIDÊNCIA PARTE 0 ---")
print(evidencia_p0.to_string(index=False))

# ============================================================
# PARTE 1 – CHUNKING POR SEÇÃO
# ============================================================
print("\n" + "=" * 60)
print("PARTE 1 – CHUNKING POR SEÇÃO")
print("=" * 60)

def extrair_titulo_documento(texto):
    for linha in texto.split("\n"):
        if linha.startswith("# "):
            return linha.replace("# ", "").strip()
    return "Título não encontrado"

def dividir_em_chunks(doc_id, texto, status):
    titulo_doc = extrair_titulo_documento(texto)
    chunks = []
    partes = re.split(r"\n## ", texto)
    for parte in partes[1:]:
        linhas = parte.split("\n", 1)
        nome_secao = linhas[0].strip()
        texto_secao = linhas[1].strip() if len(linhas) > 1 else ""
        if texto_secao:
            chunks.append({
                "doc_id": doc_id,
                "titulo": titulo_doc,
                "secao": nome_secao,
                "status": status,
                "texto": texto_secao
            })
    return chunks

todos_chunks = []
for _, row in df_metadados.iterrows():
    chunks = dividir_em_chunks(row["doc_id"], row["texto"], row["status"])
    todos_chunks.extend(chunks)

df_chunks = pd.DataFrame(todos_chunks)
print(f"\nTotal de chunks gerados: {len(df_chunks)}")
print("\nChunks por documento:")
print(df_chunks.groupby("doc_id").size().to_string())

print("\n--- EXEMPLO DE CHUNK COMPLETO ---")
exemplo = df_chunks.iloc[0]
for campo, valor in exemplo.items():
    print(f"{campo}: {valor[:200]}..." if len(str(valor)) > 200 else f"{campo}: {valor}")

# ============================================================
# PARTE 2 – INDEXAÇÃO COM TF-IDF
# ============================================================
print("\n" + "=" * 60)
print("PARTE 2 – INDEXAÇÃO COM TF-IDF")
print("=" * 60)

vetorizador = TfidfVectorizer(lowercase=True)
matriz_chunks = vetorizador.fit_transform(df_chunks["texto"])

print(f"\nShape da matriz TF-IDF: {matriz_chunks.shape}")
print(f"Tamanho do vocabulário: {len(vetorizador.get_feature_names_out())} termos")

# ============================================================
# PARTE 3 – RECUPERAÇÃO TOP-K
# ============================================================
print("\n" + "=" * 60)
print("PARTE 3 – RECUPERAÇÃO TOP-K")
print("=" * 60)

def buscar(pergunta, k=3):
    mascara_vigente = df_chunks["status"] == "vigente"
    indices_vigentes = df_chunks[mascara_vigente].index
    if len(indices_vigentes) == 0:
        return []
    vetor_pergunta = vetorizador.transform([pergunta])
    similaridades = cosine_similarity(vetor_pergunta, matriz_chunks[indices_vigentes]).flatten()
    ordem = similaridades.argsort()[::-1][:k]
    resultados = []
    for i in ordem:
        idx_real = indices_vigentes[i]
        resultados.append({
            "doc_id": df_chunks.loc[idx_real, "doc_id"],
            "titulo": df_chunks.loc[idx_real, "titulo"],  # <-- LINHA ADICIONADA
            "secao": df_chunks.loc[idx_real, "secao"],
            "status": df_chunks.loc[idx_real, "status"],
            "score": float(similaridades[i]),
            "texto": df_chunks.loc[idx_real, "texto"]
        })
    return resultados

df_gabarito = pd.read_csv(ARQ_GABARITO)
print("\n--- TESTE COM P01, P02 e P10 ---")
for pid in ["P01", "P02", "P10"]:
    pergunta = df_gabarito[df_gabarito["pergunta_id"] == pid]["pergunta"].values[0]
    print(f"\n{pid}: {pergunta}")
    resultados = buscar(pergunta, k=3)
    for r in resultados:
        print(f"  {r['doc_id']} | {r['secao']} | score={r['score']:.2f}")

# ============================================================
# PARTE 4 – RESPOSTA EXTRATIVA
# ============================================================
print("\n" + "=" * 60)
print("PARTE 4 – RESPOSTA EXTRATIVA")
print("=" * 60)

def formatar_saida(pergunta, resposta, fonte, score, status):
    return (
        f"PERGUNTA: {pergunta}\n"
        f"RESPOSTA: {resposta}\n"
        f"FONTE: {fonte}\n"
        f"SCORE: {score:.2f}\n"
        f"STATUS: {status}"
    )

def responder(pergunta):
    resultados = buscar(pergunta, k=3)
    if not resultados:
        return formatar_saida(pergunta, "Não encontrei essa informação nas políticas vigentes. Procure a área de Pessoas e Cultura.", "nenhuma", 0.0, "nao_encontrado")
    melhor = resultados[0]
    score = melhor["score"]
    if score < THRESHOLD:
        return formatar_saida(
            pergunta,
            "Não encontrei essa informação nas políticas vigentes. Procure a área de Pessoas e Cultura.",
            "nenhuma", score, "nao_encontrado"
        )
    fonte = f"{melhor['doc_id']} | {melhor['titulo']} | Seção: {melhor['secao']}"
    return formatar_saida(pergunta, melhor["texto"], fonte, score, "encontrado")

print("\n--- TESTE DE RESPOSTA ---")
for pid in ["P02", "P10"]:
    pergunta = df_gabarito[df_gabarito["pergunta_id"] == pid]["pergunta"].values[0]
    print(f"\n{responder(pergunta)}")
    print("-" * 40)

# ============================================================
# PARTE 5 – AVALIAÇÃO
# ============================================================
print("\n" + "=" * 60)
print("PARTE 5 – AVALIAÇÃO")
print("=" * 60)

def avaliar():
    resultados_avaliacao = []
    hits1 = []
    hits3 = []
    for _, row in df_gabarito.iterrows():
        pid = row["pergunta_id"]
        pergunta = row["pergunta"]
        doc_esperado = row["doc_esperado"]
        responder(pergunta)
        resultados = buscar(pergunta, k=3)
        doc_retornado_1 = resultados[0]["doc_id"] if resultados else "nenhum"
        score_1 = resultados[0]["score"] if resultados else 0.0
        status = "nao_encontrado" if score_1 < THRESHOLD else "encontrado"
        if doc_esperado == "nao_encontrado":
            acerto = "sim" if status == "nao_encontrado" else "não"
        else:
            acerto = "sim" if doc_retornado_1 == doc_esperado else "não"
            hits1.append(1 if doc_retornado_1 == doc_esperado else 0)
            docs_retornados = [r["doc_id"] for r in resultados]
            hits3.append(1 if doc_esperado in docs_retornados else 0)
        resultados_avaliacao.append({
            "pergunta_id": pid,
            "doc_esperado": doc_esperado,
            "doc_retornado_1": doc_retornado_1,
            "score": round(score_1, 2),
            "STATUS": status,
            "acerto": acerto
        })
    df_resultados = pd.DataFrame(resultados_avaliacao)
    hit1 = sum(hits1) / len(hits1) if hits1 else 0
    hit3 = sum(hits3) / len(hits3) if hits3 else 0
    return df_resultados, hit1, hit3

df_resultados, hit1, hit3 = avaliar()
print("\n--- TABELA DE AVALIAÇÃO ---")
print(df_resultados.to_string(index=False))
print(f"\nHit@1: {hit1:.2f}")
print(f"Hit@3: {hit3:.2f}")