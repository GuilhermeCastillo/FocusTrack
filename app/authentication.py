import streamlit as st
from users import criar_usuario, verificar_login


# Página de Login/Registro
def pagina_auth():
    st.title("🔐 Autenticação")

    tab1, tab2 = st.tabs(["Login", "Registro"])

    with tab1:
        with st.form("login"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")

            if st.form_submit_button("Entrar"):
                user_id = verificar_login(username, password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Credenciais inválidas!")

    with tab2:
        with st.form("registro"):
            new_user = st.text_input("Novo usuário")
            new_pass = st.text_input("Nova senha", type="password")

            if st.form_submit_button("Criar conta"):
                if criar_usuario(new_user, new_pass):
                    st.success("Conta criada! Faça login.")
                else:
                    st.error("Usuário já existe!")
