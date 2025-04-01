import pandas as pd
from settings import conn, cursor


def create_registro(user_id, data, categoria, descricao, minutos):
    if not isinstance(minutos, int) or minutos <= 0:
        raise ValueError("Minutos devem ser um inteiro positivo")

    cursor.execute(
        "INSERT INTO registros (user_id, data, categoria, descricao, minutos) VALUES (?, ?, ?, ?, ?)",
        (user_id, data, categoria, descricao, minutos),
    )
    conn.commit()
    return cursor.lastrowid


def read_registros(user_id, filtro_categoria="Todas", data_inicio=None, data_fim=None):
    query = "SELECT * FROM registros WHERE user_id = ?"
    params = [user_id]

    if filtro_categoria != "Todas":
        query += " AND categoria = ?"
        params.append(filtro_categoria)
    if data_inicio and data_fim:
        query += " AND data BETWEEN ? AND ?"
        params.extend([data_inicio, data_fim])

    return pd.read_sql(query, conn, params=params)


def update_registro(user_id, id, data, categoria, descricao, minutos):
    cursor.execute(
        """UPDATE registros 
        SET data=?, categoria=?, descricao=?, minutos=? 
        WHERE id=? AND user_id=?""",
        (data, categoria, descricao, minutos, id, user_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def delete_registro(user_id, id):
    cursor.execute(
        "DELETE FROM registros WHERE id=? AND user_id=?",
        (id, user_id),
    )
    conn.commit()
    return cursor.rowcount > 0
