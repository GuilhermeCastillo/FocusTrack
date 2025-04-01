import sqlite3
from settings import conn, cursor


# Funções de autenticação
def criar_usuario(username, password):
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, password),  # Na prática, armazene hash da senha!
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def verificar_login(username, password):
    cursor.execute("SELECT id, password FROM usuarios WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    if resultado and resultado[1] == password:  # Compare com hash na prática!
        return resultado[0]  # Retorna o user_id
    return None
