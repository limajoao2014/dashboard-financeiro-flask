import pandas as pd
from flask import Flask, render_template_string, request

from Valida_Dados import gerar_painel

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

PAGINA = """
<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>Painel de faturamento</title>

<h1>Painel de faturamento</h1>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="planilha" accept=".xlsx" required>
    <button type="submit">Gerar painel</button>
</form>

{% if erro %}<p role="alert">{{ erro }}</p>{% endif %}
{% if analise %}
    <h2>Análise do faturamento</h2>
    <p>{{ analise }}</p>
    {{ grafico | safe }}
{% endif %}
</html>
"""


@app.route("/", methods=["GET", "POST"])
def painel():
    if request.method == "GET":
        return render_template_string(PAGINA)

    arquivo = request.files.get("planilha")
    if not arquivo or not arquivo.filename.lower().endswith(".xlsx"):
        return render_template_string(PAGINA, erro="Selecione um arquivo .xlsx."), 400

    vendas = pd.read_excel(arquivo.stream, engine="openpyxl")
    grafico, analise = gerar_painel(vendas)

    return render_template_string(
        PAGINA,
        analise=analise,
        grafico=grafico.to_html(full_html=False, default_height="65vh"),
    )