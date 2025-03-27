import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from settings import conn, cursor
from crud import create_registro, update_registro, delete_registro, read_registros


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

st.title("📊 Gestor de Produtividade")

tab1, tab2 = st.tabs(["Registro & Dashboard", "Editar/Excluir"])

with tab1:
    with st.expander("➕ Novo Registro", expanded=True):
        with st.form("form_create"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", datetime.now())
            with col2:
                horas = st.number_input("Horas", 0.5, 24.0, 1.0, step=0.5)

            categoria = st.selectbox("Categoria", ["ESTUDOS", "PROJETOS", "TREINOS"])
            descricao = st.text_input("Descrição")

            if st.form_submit_button("Salvar"):
                create_registro(data, categoria, descricao, horas)
                st.success("Registro criado!")

    st.divider()
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        filtro_categoria = st.selectbox(
            "Categoria", ["Todas", "ESTUDOS", "PROJETOS", "TREINOS"]
        )
    with col2:
        periodo = st.selectbox(
            "Período", ["Todo o período", "Últimos 7 dias", "Este mês"]
        )

    data_inicio, data_fim = None, None
    if periodo == "Últimos 7 dias":
        data_fim = datetime.now().date()
        data_inicio = data_fim - timedelta(days=7)
    elif periodo == "Este mês":
        data_fim = datetime.now().date()
        data_inicio = data_fim.replace(day=1)

    df = read_registros(filtro_categoria, data_inicio, data_fim)

    st.metric("Total de Horas", f"{df['horas'].sum():.1f}h")
    st.bar_chart(df.groupby("categoria")["horas"].sum())

    st.dataframe(
        df.sort_values("data", ascending=False),
        hide_index=True,
        use_container_width=True,
    )

with tab2:
    st.subheader("Editar ou Excluir Registros")

    df_editar = read_registros()

    registro_selecionado = st.selectbox(
        "Selecione um registro para editar",
        df_editar["id"],
        format_func=lambda x: f"ID {x} - {df_editar[df_editar['id']==x].iloc[0]['descricao']}",
    )

    if registro_selecionado:
        dados_registro = df_editar[df_editar["id"] == registro_selecionado].iloc[0]

        with st.form("form_edit"):
            data = st.date_input("Data", pd.to_datetime(dados_registro["data"]))
            categoria = st.selectbox(
                "Categoria",
                ["ESTUDOS", "PROJETOS", "TREINOS"],
                index=["ESTUDOS", "PROJETOS", "TREINOS"].index(
                    dados_registro["categoria"]
                ),
            )
            descricao = st.text_input("Descrição", dados_registro["descricao"])
            horas = st.number_input(
                "Horas", 0.5, 24.0, float(dados_registro["horas"]), step=0.5
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Atualizar"):
                    update_registro(
                        registro_selecionado, data, categoria, descricao, horas
                    )
                    st.success("Registro atualizado!")
            with col2:
                if st.form_submit_button("🗑️ Excluir"):
                    delete_registro(registro_selecionado)
                    st.success("Registro excluído!")
                    st.rerun()
