import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

conn = sqlite3.connect("focustrack.db")
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE,
    categoria TEXT,
    descricao TEXT,
    horas FLOAT
)
"""
)
conn.commit()

st.sidebar.title("Filtros")
categoria = st.sidebar.selectbox(
    "Categoria", ["Todas", "ESTUDOS", "PROJETOS", "TREINOS"]
)

periodo = st.sidebar.selectbox("Período", ["Hoje", "Semana", "Mês", "Personalizado"])


if periodo == "Personalizado":
    data_inicio = st.sidebar.date_input("Data inicial")
    data_fim = st.sidebar.date_input("Data final")
elif periodo == "Hoje":
    data_inicio = data_fim = datetime.now().date()
elif periodo == "Semana":
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=7)
else:  # Mês
    data_fim = datetime.now().date()
    data_inicio = data_fim.replace(day=1)

st.title("📊 Meu Gestor de Produtividade")

with st.form("registro"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", datetime.now())
    with col2:
        horas = st.number_input("Horas", 0.5, 24.0, 1.0, step=0.5)

    categoria_registro = st.selectbox("Categoria", ["ESTUDOS", "PROJETOS", "TREINOS"])
    descricao = st.text_input("Descrição")

    if st.form_submit_button("Registrar"):
        cursor.execute(
            "INSERT INTO registros (data, categoria, descricao, horas) VALUES (?, ?, ?, ?)",
            (data, categoria_registro, descricao, horas),
        )
        conn.commit()
        st.success("✅ Atividade registrada!")

# --- Dashboard ---
st.divider()
st.header("Estatísticas")

query = f"SELECT * FROM registros WHERE data BETWEEN '{data_inicio}' AND '{data_fim}'"
if categoria != "Todas":
    query += f" AND categoria = '{categoria}'"

df = pd.read_sql(query, conn)

# Métricas
total_horas = df["horas"].sum()
st.metric("Total de Horas", f"{total_horas}h")

# Gráficos
tab1, tab2 = st.tabs(["Por Categoria", "Evolução Diária"])
with tab1:
    st.bar_chart(df.groupby("categoria")["horas"].sum())
with tab2:
    st.line_chart(df.groupby("data")["horas"].sum())

st.divider()
st.dataframe(df.sort_values("data", ascending=False))
