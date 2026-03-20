from typing import List, Tuple

from datos.database_pro import obtener_conexion


def get_clientes_by_usuario(usuario_id: int) -> List[Tuple]:
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, telefono FROM clientes WHERE usuario_id=%s",
        (usuario_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_cliente(usuario_id: int, nombre: str, telefono: str) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (usuario_id, nombre, telefono) VALUES (%s, %s, %s)",
        (usuario_id, nombre, telefono),
    )
    conn.commit()
    conn.close()


def get_cliente(usuario_id: int, cliente_id: int):
    conn = obtener_conexion()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, telefono FROM clientes WHERE id=%s AND usuario_id=%s",
        (cliente_id, usuario_id),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_cliente(usuario_id: int, cliente_id: int, nombre: str, telefono: str) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre=%s, telefono=%s WHERE id=%s AND usuario_id=%s",
        (nombre, telefono, cliente_id, usuario_id),
    )
    conn.commit()
    conn.close()


def delete_cliente(usuario_id: int, cliente_id: int) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM clientes WHERE id=%s AND usuario_id=%s",
        (cliente_id, usuario_id),
    )
    conn.commit()
    conn.close()

