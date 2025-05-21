
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc


df_2020 = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Base%20Vendas%20-%202020.xlsx")
df_2021 = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Base%20Vendas%20-%202021.xlsx")
df_2022 = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Base%20Vendas%20-%202022.xlsx")
df_vendas = pd.concat([df_2020, df_2021, df_2022], ignore_index=True)
df_clientes = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Cadastro%20Clientes.xlsx")
df_lojas = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Cadastro%20Lojas.xlsx")
df_produtos = pd.read_excel("https://raw.githubusercontent.com/larissa-ms/vendas-dashboard2/main/Cadastro%20Produtos.xlsx")
df_clientes["Nome Completo"] = df_clientes["Primeiro Nome"] + " " + df_clientes["Sobrenome"]
df_vendas = df_vendas.merge(df_clientes[["ID Cliente", "Nome Completo"]], on="ID Cliente", how="left")
df_vendas = df_vendas.merge(df_lojas[["ID Loja", "Nome da Loja"]], on="ID Loja", how="left")
df_vendas = df_vendas.merge(df_produtos[["SKU", "Produto", "Marca", "Tipo do Produto"]], on="SKU", how="left")
df_vendas["Data da Venda"] = pd.to_datetime(df_vendas["Data da Venda"])
df_vendas["Ano"] = df_vendas["Data da Venda"].dt.year

app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "Dashboard Vendas Otimizado"
server = app.server

def dropdown_component(id, options, placeholder):
    return dcc.Dropdown(
        options=[{'label': i, 'value': i} for i in sorted(options.dropna().unique())],
        id=id, placeholder=placeholder, multi=True, style={"margin-bottom": "10px", "backgroundColor": "#FFF", "color": "#000"}
    )

def card_component(title, dropdowns, graph_id):
    return dbc.Col([
        dbc.Card([
            dbc.CardHeader(html.H5(title, className="text-white")),
            dbc.CardBody([
                *dropdowns,
                dcc.Graph(id=graph_id, config={"displayModeBar": False})
            ])
        ], color="dark", inverse=True, className="mb-4 shadow")
    ], md=6)

app.layout = dbc.Container(fluid=True, children=[

    html.H2("Dashboard de Vendas (2020-2022)", className="text-center my-4"),

    dbc.Row([
        card_component("Vendas por Ano", [], "grafico_ano"),
        card_component("Vendas por Produto", [
            dropdown_component("filtro_produto", df_vendas["Produto"], "Produto"),
            dropdown_component("filtro_marca", df_vendas["Marca"], "Marca"),
            dropdown_component("filtro_tipo", df_vendas["Tipo do Produto"], "Tipo")
        ], "grafico_produto"),
    ]),

    dbc.Row([
        card_component("Vendas por Cliente", [
            dropdown_component("filtro_cliente", df_vendas["Nome Completo"], "Cliente")
        ], "grafico_cliente"),

        card_component("Vendas por Loja", [
            dropdown_component("filtro_loja", df_vendas["Nome da Loja"], "Loja")
        ], "grafico_loja")
    ]),

    dbc.Row([
        card_component("Participação por Marca (Pizza)", [
            dropdown_component("filtro_marca_pizza", df_vendas["Marca"], "Marca")
        ], "grafico_pizza_marca"),

        card_component("Vendas por Tipo de Produto (Área)", [
            dropdown_component("filtro_tipo_area", df_vendas["Tipo do Produto"], "Tipo")
        ], "grafico_area_tipo")
    ])
])

# ===================== CALLBACKS =====================

@app.callback(
    Output("grafico_ano", "figure"),
    Input("grafico_ano", "id")
)
def grafico_ano(_):
    df_group = df_vendas.groupby("Ano")["Qtd Vendida"].sum().reset_index()
    fig = px.bar(df_group, x="Ano", y="Qtd Vendida", text="Qtd Vendida",
                 title="Vendas Totais por Ano", color="Ano")
    fig.update_layout(xaxis_title="Ano", yaxis_title="Quantidade Vendida")
    return fig

@app.callback(
    Output("grafico_produto", "figure"),
    Input("filtro_produto", "value"),
    Input("filtro_marca", "value"),
    Input("filtro_tipo", "value")
)
def grafico_por_produto(produtos, marcas, tipos):
    df = df_vendas.copy()
    if produtos:
        df = df[df["Produto"].isin(produtos)]
    if marcas:
        df = df[df["Marca"].isin(marcas)]
    if tipos:
        df = df[df["Tipo do Produto"].isin(tipos)]
    df_group = df.groupby("Produto")["Qtd Vendida"].sum().nlargest(10).reset_index()
    fig = px.bar(df_group, x="Qtd Vendida", y="Produto", orientation="h",
                 title="Top 10 Produtos Vendidos", color="Qtd Vendida", text="Qtd Vendida")
    fig.update_layout(xaxis_title="Quantidade", yaxis_title="Produto")
    return fig

@app.callback(
    Output("grafico_cliente", "figure"),
    Input("filtro_cliente", "value")
)
def grafico_por_cliente(clientes):
    df = df_vendas.copy()
    if clientes:
        df = df[df["Nome Completo"].isin(clientes)]
    df_group = df.groupby("Nome Completo")["Qtd Vendida"].sum().nlargest(10).reset_index()
    fig = px.bar(df_group, x="Qtd Vendida", y="Nome Completo", orientation="h",
                 title="Top 10 Clientes por Vendas", color="Qtd Vendida", text="Qtd Vendida")
    fig.update_layout(xaxis_title="Quantidade", yaxis_title="Cliente")
    return fig

@app.callback(
    Output("grafico_loja", "figure"),
    Input("filtro_loja", "value")
)
def grafico_por_loja(lojas):
    df = df_vendas.copy()
    if lojas:
        df = df[df["Nome da Loja"].isin(lojas)]
    df_group = df.groupby("Nome da Loja")["Qtd Vendida"].sum().nlargest(10).reset_index()
    fig = px.bar(df_group, x="Nome da Loja", y="Qtd Vendida",
                 title="Top Lojas por Volume de Vendas", color="Qtd Vendida", text="Qtd Vendida")
    fig.update_layout(xaxis_title="Loja", yaxis_title="Quantidade")
    return fig

@app.callback(
    Output("grafico_pizza_marca", "figure"),
    Input("filtro_marca_pizza", "value")
)
def grafico_pizza_marca(marcas):
    df = df_vendas.copy()
    if marcas:
        df = df[df["Marca"].isin(marcas)]
    df_group = df.groupby("Marca")["Qtd Vendida"].sum().reset_index()
    fig = px.pie(df_group, names="Marca", values="Qtd Vendida",
                 title="Distribuição de Vendas por Marca")
    return fig

@app.callback(
    Output("grafico_area_tipo", "figure"),
    Input("filtro_tipo_area", "value")
)
def grafico_area_tipo(tipos):
    df = df_vendas.copy()
    if tipos:
        df = df[df["Tipo do Produto"].isin(tipos)]
    df_group = df.groupby(["Ano", "Tipo do Produto"])["Qtd Vendida"].sum().reset_index()
    fig = px.area(df_group, x="Ano", y="Qtd Vendida", color="Tipo do Produto",
                  title="Vendas por Tipo de Produto ao Longo dos Anos")
    return fig

# ===================== EXECUÇÃO =====================

if __name__ == '__main__':
    app.run(debug=True, port=8050, use_reloader = False)