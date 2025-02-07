import streamlit as st
import sqlite3
import pandas as pd

# Configuração da Página
st.set_page_config(layout="wide", page_title="DADOS PREVIC")

st.title("📊 Dashboard de Demonstrações Atuariais - PREVIC")

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

# 🔹 Obter o NU_CNPB_PLANO_DA e SG_EFPC_DA correspondente ao plano e ano selecionados
query_cnpb_efpc = f"""
    SELECT DISTINCT NU_CNPB_PLANO_DA, SG_EFPC_DA FROM planos_da 
    WHERE SG_PLANO_DA = '{selected_plano}' AND ANO = {selected_ano}
"""
df_cnpb_efpc = pd.read_sql(query_cnpb_efpc, conn)

if df_cnpb_efpc.empty:
    st.warning("⚠️ Nenhum dado encontrado para o plano e ano selecionados.")
    conn.close()
    st.stop()

# Pegamos o primeiro CNPB e EFPC correspondente
nu_cnpb = df_cnpb_efpc["NU_CNPB_PLANO_DA"].iloc[0]
sg_efpc = df_cnpb_efpc["SG_EFPC_DA"].iloc[0]

st.subheader(f"📌 Informações para o Plano {selected_plano} ({nu_cnpb}) - Ano: {selected_ano}")
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

# 🔹 Exibir métricas principais
st.header("📊 Resumo do Plano")

col1, col2, col3 = st.columns(3)

if not df_beneficios.empty:
    col1.metric("Regime Financeiro", df_beneficios["NM_REGIME_FINANCEIRO"].iloc[0])

if not df_grupos_custeio.empty:
    col2.metric("Qtd Participantes Ativos", f"{df_grupos_custeio['QTD_PART_ATIVOS'].iloc[0]:,}")
    col3.metric("Folha Salarial", f"R$ {df_grupos_custeio['VR_FOLHA_SAL'].iloc[0]:,.2f}")

if not df_dados_da.empty:
    col1.metric("Duration (meses)", df_dados_da["NU_DURATION_MESES"].iloc[0])

if not df_resultado_plano.empty:
    col2.metric("Resultado do Exercício", f"R$ {df_resultado_plano['VL_RESULTADO_EXERCICIO'].iloc[0]:,.2f}")
    col3.metric("Déficit Técnico", f"R$ {df_resultado_plano['VL_DEFICIT_TECNICO'].iloc[0]:,.2f}")

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

# Fechar conexão com o banco
conn.close()
