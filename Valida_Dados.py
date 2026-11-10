import json
from urllib.request import Request, urlopen

import pandas as pd
import plotly.express as px


def consultar_ollama(prompt):
    pedido = {
        "model": "qwen3:4b",
        "stream": False,
        "think": False,
        "options": {"num_predict": 256},
        "format": "json",
        "messages": [{"role": "user", "content": prompt}],
    }
    requisicao = Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(pedido).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(requisicao, timeout=180) as resposta:
        return json.loads(json.load(resposta)["message"]["content"])


def gerar_painel(vendas):
    vendas = vendas.rename(columns=lambda nome: str(nome).strip())
    colunas = {nome: str(tipo) for nome, tipo in vendas.dtypes.items()}
    colunas_data = vendas.select_dtypes(include="datetime").columns.tolist()

    if not colunas_data:
        raise ValueError("A planilha precisa ter uma coluna com datas completas.")

    config = consultar_ollama(
        "Escolha um gráfico de faturamento mensal. "
        "Retorne JSON com tipo ('line' ou 'bar'), coluna_data, coluna_valor "
        "e agregacao ('sum'). Use os nomes exatos das colunas. "
        f"Colunas e tipos: {json.dumps(colunas, ensure_ascii=False)}. "
        f"Use em coluna_data somente uma destas colunas: {colunas_data}."
    )

    data = config.get("coluna_data")
    valor = config.get("coluna_valor")
    tipo = config.get("tipo")
    graficos = {"line": px.line, "bar": px.bar}

    if data not in colunas_data or valor not in vendas or data == valor:
        raise ValueError(f"O Ollama escolheu colunas inválidas: {config}")

    if tipo not in graficos or config.get("agregacao") != "sum":
        raise ValueError(f"Configuração de gráfico inválida: {config}")

    mensal = (
        pd.DataFrame({
            "Mês": vendas[data].dt.to_period("M").dt.to_timestamp(),
            "Faturamento": pd.to_numeric(vendas[valor]),
        })
        .groupby("Mês", as_index=False)["Faturamento"]
        .sum()
    )

    if mensal.empty:
        raise ValueError("A coluna de data não contém registros para agrupar.")

    grafico = graficos[tipo](
        mensal, x="Mês", y="Faturamento", title="Faturamento mensal"
    )
    pico = mensal.loc[mensal["Faturamento"].idxmax()]
    ultimos_meses = mensal.tail(3).to_json(orient="records", date_format="iso")

    resultado = consultar_ollama(
        "Escreva duas frases em português sobre o faturamento mensal. "
        "Informe o mês de pico e descreva as mudanças entre os últimos meses "
        "na ordem em que aparecem. Use os valores fornecidos e evite atribuir causas. "
        'Retorne JSON no formato {"analise": "texto"}. '
        f"Pico: {pico['Mês']:%m/%Y}, valor {pico['Faturamento']:.2f}. "
        f"Últimos meses: {ultimos_meses}"
    )

    return grafico, resultado["analise"]