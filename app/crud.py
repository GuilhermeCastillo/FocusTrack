import pandas as pd
from settings import conn, cursor


def create_registro(data, categoria, descricao, minutos):
    cursor.execute(
        "INSERT INTO registros (data, categoria, descricao, minutos) VALUES (?, ?, ?, ?)",
        (data, categoria, descricao, minutos),
    )
    conn.commit()


def read_registros(filtro_categoria="Todas", data_inicio=None, data_fim=None):
    query = "SELECT * FROM registros"
    conditions = []

    if filtro_categoria != "Todas":
        conditions.append(f"categoria = '{filtro_categoria}'")
    if data_inicio and data_fim:
        conditions.append(f"data BETWEEN '{data_inicio}' AND '{data_fim}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return pd.read_sql(query, conn)


def update_registro(id, data, categoria, descricao, minutos):
    cursor.execute(
        "UPDATE registros SET data=?, categoria=?, descricao=?, minutos=? WHERE id=?",
        (data, categoria, descricao, minutos, id),
    )
    conn.commit()


def delete_registro(id):
    cursor.execute("DELETE FROM registros WHERE id=?", (id,))
    conn.commit()
