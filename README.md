# Assistente de P&R sobre Políticas Internas

Projeto do desafio Bootcamp AI/R Fellowship SEP26: um assistente extrativo que busca respostas em políticas internas usando TF-IDF e similaridade de cosseno.

## Como executar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python assistente.py
```

O script utiliza os arquivos `metadados.csv`, `perguntas_gabarito.csv` e os documentos Markdown da pasta `corpus/`.
