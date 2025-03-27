import pandas as pd
from settings import conn, cursor


def create_registro(data, categoria, descricao, horas):
    cursor.execute(
        "INSERT INTO registros (data, categoria, descricao, horas) VALUES (?, ?, ?, ?)",
        (data, categoria, descricao, horas),
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


def update_registro(id, data, categoria, descricao, horas):
    cursor.execute(
        "UPDATE registros SET data=?, categoria=?, descricao=?, horas=? WHERE id=?",
        (data, categoria, descricao, horas, id),
    )
    conn.commit()


def delete_registro(id):
    cursor.execute("DELETE FROM registros WHERE id=?", (id,))
    conn.commit()
