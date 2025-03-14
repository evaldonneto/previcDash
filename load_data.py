import pandas as pd
import sqlite3
import os
import unicodedata
import re

# Caminho do banco de dados SQLite
DB_PATH = "database/previc_data.db"

# Lista de arquivos CSV e tabelas correspondentes
FILES_TABLES = {
    "2023-GRUPOS_CUSTEIO.csv": "grupos_custeio",
    "2023-DADOS_GRUPOS_CUSTEIO.csv": "dados_grupos_custeio",
    "2023-RESULTADO_PLANO.csv": "resultado_plano",
    "2023-PLANOS_DA.csv": "planos_da",
    "2023-TOTAL_RESERVAS.csv": "total_reservas",
    "2023-PROVISOES_A_CONSTITUIR.csv": "provisoes_a_constituir",
    "2023-FONTES_RECURSOS.csv": "fontes_recursos",
    "2023-DADOS_DA.csv": "dados_da",
    "2023-BENEFICIOS.csv": "beneficios",
    "2023-PARECER_PLANO.csv": "parecer_plano",
}

def extract_year_from_filename(filename):
    """Extrai o ano do nome do arquivo (exemplo: '2018' de '2018-GRUPOS_CUSTEIO-20211004.csv')."""
    return int(filename.split("-")[0])

def clean_column_names(columns):
    """Remove acentos e caracteres especiais dos nomes das colunas, mas mantém underscores e espaços."""
    cleaned_columns = []
    for col in columns:
        col = str(col).strip()
        col = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode("ASCII")  # Remove acentos
        col = re.sub(r"[^a-zA-Z0-9_ ]", "", col)  # Substitui apenas caracteres especiais
        cleaned_columns.append(col.strip().upper())  # Converte tudo para maiúsculas
    return cleaned_columns

def load_data():
    """Lê arquivos CSV e adiciona os dados ao banco de dados SQLite sem duplicar registros."""

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for file, table_name in FILES_TABLES.items():
        file_path = f"data/{file}"

        if os.path.exists(file_path):
            print(f"🔹 Carregando {file} para a tabela {table_name}...")

            try:
                df = pd.read_csv(file_path, encoding="utf-8-sig", sep=";")
            except:
                df = pd.read_csv(file_path, encoding="ISO-8859-1", sep=";")

            df.columns = clean_column_names(df.columns)
            df["ANO"] = extract_year_from_filename(file)

            # 🔹 Verificar se registros desse ANO e NU_CNPB_PLANO_DA já existem
            if "NU_CNPB_PLANO_DA" in df.columns:
                existing_query = f"""
                    SELECT NU_CNPB_PLANO_DA FROM {table_name} WHERE ANO = ?
                """
                existing_cnpbs = pd.read_sql(existing_query, conn, params=[df["ANO"].iloc[0]])["NU_CNPB_PLANO_DA"].tolist()
                df = df[~df["NU_CNPB_PLANO_DA"].astype(str).isin(existing_cnpbs)]

                if df.empty:
                    print(f"⚠️ Todos os registros do ano {df['ANO'].iloc[0]} já estão na tabela {table_name}. Pulando inserção.")
                    continue

            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"✅ {table_name} atualizado com {len(df)} novos registros do ano {df['ANO'].iloc[0]}.")

        else:
            print(f"⚠️ Arquivo {file} não encontrado. Pulando...")

    conn.close()
    print("🎯 Importação concluída!")

if __name__ == "__main__":
    load_data()
