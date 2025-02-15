import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(layout="wide", page_title="DADOS PREVIC")

# Exibir logo
st.image("Aon_Corporation_logo.svg.png", width=150)

st.title("📊 Dashboard de Demonstrações Atuariais - PREVIC")
st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

# Conectar ao banco de dados
DB_PATH = "database/previc_data.db"
conn = sqlite3.connect(DB_PATH)

# 🔹 Carregar lista de Anos e Planos
df_anos = pd.read_sql("SELECT DISTINCT ANO FROM planos_da ORDER BY ANO DESC", conn)
df_planos = pd.read_sql("SELECT DISTINCT SG_PLANO_DA FROM planos_da", conn)

# 🔹 Criar filtros
col1, col2 = st.columns(2)
selected_ano = col1.selectbox("📆 Selecione o Ano", df_anos["ANO"])
selected_plano = col2.selectbox("📌 Selecione um Plano", df_planos["SG_PLANO_DA"])

# 🔹 Obter NU_CNPB_PLANO_DA e SG_EFPC_DA correspondente ao plano selecionado
query_cnpb_efpc = f"""
    SELECT DISTINCT NU_CNPB_PLANO_DA, SG_EFPC_DA FROM planos_da 
    WHERE SG_PLANO_DA = '{selected_plano}'
"""
df_cnpb_efpc = pd.read_sql(query_cnpb_efpc, conn)

if df_cnpb_efpc.empty:
    st.warning("⚠️ Nenhum dado encontrado para o plano selecionado.")
    conn.close()
    st.stop()

# Pegamos o primeiro CNPB e EFPC correspondente
nu_cnpb = df_cnpb_efpc["NU_CNPB_PLANO_DA"].iloc[0]
sg_efpc = df_cnpb_efpc["SG_EFPC_DA"].iloc[0]

st.subheader(f"📌 Informações para o Plano {selected_plano} ({nu_cnpb})")
st.write(f"🏢 **Entidade (EFPC):** {sg_efpc}")


# 🔹 Função para buscar dados de uma tabela específica
def fetch_data(query):
    return pd.read_sql(query, conn)

# 🔹 Atualizar as consultas SQL para incluir o Ano
query_beneficios = f"SELECT NM_REGIME_FINANCEIRO FROM beneficios WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_grupos_custeio = f"SELECT QTD_PART_ATIVOS, VR_FOLHA_SAL, QTD_GRUPOS FROM grupos_custeio WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_total_reservas = f"SELECT VL_CUSTO_ANO, SM_PROVISAO_MATEMATICA, SM_BENEFICIOS_CONCEDIDOS FROM total_reservas WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_dados_grupo_custeio = f"SELECT QT_PARTICIPANTES_ATIVOS, VL_FOLHA_SALARIO, QT_MESES_CONTRIBUICAO, QT_MESES_APOSENTADORIA, NU_GRUPO_CUSTEIO, NM_GRUPO_CUSTEIO FROM dados_grupos_custeio WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_provisoes = f"SELECT SM_PASSIVO_PROVISAO_CONST FROM provisoes_a_constituir WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_resultado_plano = f"SELECT VL_RESULTADO_EXERCICIO, VL_DEFICIT_TECNICO, VL_SUPERAVIT_TECNICO, VL_RESERVA_CONTINGENCIA, VL_RESERVA_ESPECIAL FROM resultado_plano WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"
query_dados_da = f"SELECT NU_DURATION_MESES FROM dados_da WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}' AND ANO = {selected_ano}"

# 🔹 Buscar os dados
df_beneficios = fetch_data(query_beneficios)
df_grupos_custeio = fetch_data(query_grupos_custeio)
df_total_reservas = fetch_data(query_total_reservas)
df_dados_grupo_custeio = fetch_data(query_dados_grupo_custeio)
df_provisoes = fetch_data(query_provisoes)
df_resultado_plano = fetch_data(query_resultado_plano)
df_dados_da = fetch_data(query_dados_da)

# 🔹 Criando Estilo para os Cards
st.markdown("""
    <style>
        .metric-card {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 10px;
        }
        .metric-card h4 {
            margin-bottom: 5px;
            font-size: 16px;
            color: #333;
        }
        .metric-card h3 {
            margin: 0;
            font-size: 22px;
            font-weight: bold;
            color: #007BFF;
        }
    </style>
""", unsafe_allow_html=True)

# 🔹 Exibir métricas principais
st.header("📊 Resumo do Plano")

col1, col2, col3 = st.columns(3)

if not df_beneficios.empty:
    col1.markdown(f'<div class="metric-card"><h4>Regime Financeiro:</h4><h3>{df_beneficios["NM_REGIME_FINANCEIRO"].iloc[0]}</h3></div>',unsafe_allow_html=True )

if not df_grupos_custeio.empty:
    col2.markdown(f'<div class="metric-card"><h4>👥 Qtd Participantes Ativos</h4><h3>{df_grupos_custeio["QTD_PART_ATIVOS"].iloc[0]:,}</h3></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h4>💰 Folha Salarial</h4><h3>R$ {df_grupos_custeio["VR_FOLHA_SAL"].iloc[0]:,.2f}</h3></div>', unsafe_allow_html=True)

if not df_dados_da.empty:
    col1.markdown(f'<div class="metric-card"><h4>📆 Duration (meses)</h4><h3>{df_dados_da["NU_DURATION_MESES"].iloc[0]}</h3></div>', unsafe_allow_html=True)

if not df_resultado_plano.empty:
    col2.markdown(f'<div class="metric-card"><h4>📈 Resultado do Exercício</h4><h3>R$ {df_resultado_plano["VL_RESULTADO_EXERCICIO"].iloc[0]:,.2f}</h3></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h4>⚠️ Déficit Técnico</h4><h3>R$ {df_resultado_plano["VL_DEFICIT_TECNICO"].iloc[0]:,.2f}</h3></div>', unsafe_allow_html=True)

st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

# 🔹 Buscar evolução anual dos dados do plano selecionado
query_evolucao = f"""
    SELECT ANO, 
           (SELECT QTD_PART_ATIVOS FROM grupos_custeio g WHERE g.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND g.ANO = p.ANO) AS PARTICIPANTES_ATIVOS,
           (SELECT NU_DURATION_MESES FROM dados_da d WHERE d.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND d.ANO = p.ANO) AS DURATION,
           (SELECT SM_PROVISAO_MATEMATICA FROM total_reservas t WHERE t.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND t.ANO = p.ANO) AS PATRIMONIO,
           (SELECT VL_SUPERAVIT_TECNICO FROM resultado_plano r WHERE r.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND r.ANO = p.ANO) AS EQUILIBRIO_TECNICO,
           (SELECT VL_RESULTADO_EXERCICIO FROM resultado_plano r WHERE r.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND r.ANO = p.ANO) AS RESULTADO_EXERCICIO,
           (SELECT SM_BENEFICIOS_CONCEDIDOS FROM total_reservas t WHERE t.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND t.ANO = p.ANO) AS BENEFICIOS_CONCEDIDOS,
           (SELECT VL_RESERVA_CONTINGENCIA FROM resultado_plano r WHERE r.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND r.ANO = p.ANO) AS FUNDO_REVERSAO,
           (SELECT NM_EMPRESA_EXTERNA FROM dados_da d WHERE d.NU_CNPB_PLANO_DA = p.NU_CNPB_PLANO_DA AND d.ANO = p.ANO) AS CONSULTORIA
    FROM planos_da p
    WHERE NU_CNPB_PLANO_DA = '{nu_cnpb}'
    ORDER BY ANO
"""
df_evolucao = pd.read_sql(query_evolucao, conn)

if not df_evolucao.empty:
    st.header("📊 Gráficos de Evolução Anual")

    col1, col2 = st.columns(2)
    fig1 = px.bar(df_evolucao, x="ANO", y="PARTICIPANTES_ATIVOS", title="Participantes Ativos")
    fig1.update_xaxes(type='category')  # Define o eixo X como categórico

    fig2 = px.bar(df_evolucao, x="ANO", y="DURATION", title="Duration (meses)")
    fig2.update_xaxes(type='category')  # Define o eixo X como categórico

    st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    fig3 = px.bar(df_evolucao, x="ANO", y="PATRIMONIO", title="Patrimônio")
    fig3.update_xaxes(type='category')  # Define o eixo X como categórico

    fig4 = px.bar(df_evolucao, x="ANO", y="RESULTADO_EXERCICIO", title="Resultado do Exercício")
    fig4.update_xaxes(type='category')  # Define o eixo X como categórico

    
    col1.plotly_chart(fig3, use_container_width=True)
    col2.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

    col1, col2 = st.columns(2)
    fig5 = px.bar(df_evolucao, x="ANO", y="EQUILIBRIO_TECNICO", title="Equilíbrio Técnico")
    fig5.update_xaxes(type='category')  # Define o eixo X como categórico

    fig6 = px.bar(df_evolucao, x="ANO", y="FUNDO_REVERSAO", title="Fundo de Reversão")
    fig6.update_xaxes(type='category')  # Define o eixo X como categórico

    col1.plotly_chart(fig5, use_container_width=True)
    col2.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

    col1, col2 = st.columns(2)
    fig7 = px.bar(df_evolucao, x="ANO", y="BENEFICIOS_CONCEDIDOS", title="Benefícios Concedidos")
    fig7.update_xaxes(type='category')  # Define o eixo X como categórico
    #fig8 = px.bar(df_evolucao, x="ANO", y="FUNDO_REVERSAO", title="Fundo de Reversão")
    # Gráfico de mudança de consultoria
    if "CONSULTORIA" in df_evolucao.columns and not df_evolucao["CONSULTORIA"].isna().all():
        df_evolucao["ANO"] = df_evolucao["ANO"].astype(int).astype(str)
        fig8 = px.line(df_evolucao, x="ANO", y="CONSULTORIA", title="Mudança de Consultoria", markers=True)
        fig8.update_xaxes(type='category')  # Define o eixo X como categórico
        col2.plotly_chart(fig8, use_container_width=True)
    col1.plotly_chart(fig7, use_container_width=True)

st.markdown("---")  # 🔹 Linha separadora para melhorar a organização visual

# 🔹 Exibir tabelas de detalhes
st.header("📋 Informações Detalhadas")

# Grupos de Custeio
if not df_grupos_custeio.empty:
    st.subheader("🔹 Grupos de Custeio")
    st.dataframe(df_grupos_custeio)

# Reservas
if not df_total_reservas.empty:
    st.subheader("🔹 Total de Reservas")
    st.dataframe(df_total_reservas)

# Dados do Grupo de Custeio
if not df_dados_grupo_custeio.empty:
    st.subheader("🔹 Dados do Grupo de Custeio")
    st.dataframe(df_dados_grupo_custeio)

# Provisões
if not df_provisoes.empty:
    st.subheader("🔹 Provisões a Constituir")
    st.dataframe(df_provisoes)

# Resultado do Plano
if not df_resultado_plano.empty:
    st.subheader("🔹 Resultado do Plano")
    st.dataframe(df_resultado_plano)

conn.close()
