import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from settings import conn, cursor
from crud import create_registro, update_registro, delete_registro, read_registros
from authentication import pagina_auth


# Tabela de usuários
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
)

# Tabela de registros (agora com user_id)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    data DATE,
    categoria TEXT,
    descricao TEXT,
    minutos INTEGER,
    FOREIGN KEY (user_id) REFERENCES usuarios (id)
    )
"""
)  # <-- Parêntese de fechamento adicionado aqui
conn.commit()


if "user_id" not in st.session_state:
    pagina_auth()
    st.stop()

user_id = st.session_state["username"]

st.title(f"Bem-vindo, {st.session_state['username']}!")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.title("📊 FocusTrack")

tab1, tab2 = st.tabs(["Registro & Dashboard", "Editar/Excluir"])

with tab1:
    with st.expander("➕ Novo Registro", expanded=True):
        with st.form("form_create"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", datetime.now())
            with col2:
                minutos = st.number_input(
                    "minutos",
                    min_value=1,
                    max_value=1440,  # 24h*60min
                    value=30,  # Valor padrão
                    step=1,
                )

            categoria = st.selectbox("Categoria", ["ESTUDOS", "PROJETOS", "TREINOS"])
            descricao = st.text_input("Descrição")

            if st.form_submit_button("Salvar"):
                create_registro(user_id, data, categoria, descricao, minutos)
                st.success("Registro criado!")

    with st.sidebar:
        st.subheader("Filtros")

        filtro_categoria = st.selectbox(
            "Categoria", ["Todas", "ESTUDOS", "PROJETOS", "TREINOS"]
        )

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

    df = read_registros(user_id, filtro_categoria, data_inicio, data_fim)

    st.divider()
    st.subheader("Estatísticas")

    df["horas"] = df["minutos"] / 60

    total_minutos = df["minutos"].sum()
    st.metric("Total de Tempo", f"{total_minutos} min ({total_minutos/60:.1f}h)")

    st.bar_chart(df.groupby("categoria")["horas"].sum(), color=["#fd0"])

    with st.expander("Visualizar Tabela"):
        st.dataframe(
            df.assign(horas=lambda x: round(x["minutos"] / 60, 1))[
                ["data", "categoria", "descricao", "minutos", "horas"]
            ].sort_values("data", ascending=False),
            hide_index=True,
            use_container_width=True,
        )

# --- EDITAR REGISTROS  ---
with tab2:
    st.subheader("Editar Registros")

    df_editar = read_registros(user_id, filtro_categoria, data_inicio, data_fim)

    if not df_editar.empty:
        registro_selecionado = st.selectbox(
            "Selecione um registro",
            df_editar["id"],
            format_func=lambda x: f"ID {x} - {df_editar[df_editar['id']==x].iloc[0]['descricao']} ({df_editar[df_editar['id']==x].iloc[0]['minutos']} min)",
        )

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
            minutos = st.number_input(
                "Minutos",
                min_value=1,
                max_value=1440,
                value=int(dados_registro["minutos"]),
                step=1,
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Atualizar"):
                    update_registro(
                        user_id,
                        registro_selecionado,
                        data,
                        categoria,
                        descricao,
                        minutos,
                    )
                    st.success("Registro atualizado!")
            with col2:
                if st.form_submit_button("🗑️ Excluir"):
                    delete_registro(user_id, registro_selecionado)
                    conn.commit()
                    st.success("Registro excluído!")
                    st.rerun()
    else:
        st.warning("Nenhum registro encontrado para edição.")
