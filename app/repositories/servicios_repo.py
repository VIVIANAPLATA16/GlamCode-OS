from typing import List, Tuple

from datos.database_pro import obtener_conexion


def get_servicios_by_usuario(usuario_id: int) -> List[Tuple]:
    conn = obtener_conexion()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, precio FROM servicios WHERE usuario_id=%s",
        (usuario_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_servicio(usuario_id: int, nombre: str, precio: float) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO servicios (usuario_id, nombre, precio) VALUES (%s, %s, %s)",
        (usuario_id, nombre, precio),
    )
    conn.commit()
    conn.close()


def delete_servicio(usuario_id: int, servicio_id: int) -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM servicios WHERE id=%s AND usuario_id=%s",
        (servicio_id, usuario_id),
    )
    conn.commit()
    conn.close()

