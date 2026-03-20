from typing import List, Tuple

from datos.database_pro import obtener_conexion


def get_citas_by_usuario(usuario_id: int) -> List[Tuple]:
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, cliente, servicio, precio, fecha FROM citas WHERE usuario_id=%s",
        (usuario_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_cita(
    usuario_id: int, cliente: str, servicio: str, precio: float, fecha: str
) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO citas (usuario_id, cliente, servicio, precio, fecha) VALUES (%s, %s, %s, %s, %s)",
        (usuario_id, cliente, servicio, precio, fecha),
    )
    conn.commit()
    conn.close()


def get_cita(usuario_id: int, cita_id: int):
    conn = obtener_conexion()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, cliente, servicio, precio, fecha FROM citas WHERE id=%s AND usuario_id=%s",
            (cita_id, usuario_id),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_cita(
    usuario_id: int,
    cita_id: int,
    cliente: str,
    servicio: str,
    precio: float,
    fecha: str,
) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE citas SET cliente=%s, servicio=%s, precio=%s, fecha=%s WHERE id=%s AND usuario_id=%s",
        (cliente, servicio, precio, fecha, cita_id, usuario_id),
    )
    conn.commit()
    conn.close()


def delete_cita(usuario_id: int, cita_id: int) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM citas WHERE id=%s AND usuario_id=%s",
        (cita_id, usuario_id),
    )
    conn.commit()
    conn.close()

