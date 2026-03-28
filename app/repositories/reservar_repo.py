"""Reservas públicas (TiDB/MySQL) para el flujo /reservar."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple

from datos.database_pro import obtener_conexion


def _conn():
    return obtener_conexion()


def list_servicios_salon(usuario_id: int) -> List[Tuple[Any, ...]]:
    c = _conn()
    if not c:
        return []
    cur = c.cursor()
    try:
        cur.execute(
            """
            SELECT id, nombre, COALESCE(duracion_minutos, 60), precio
            FROM servicios WHERE usuario_id = %s ORDER BY nombre
            """,
            (usuario_id,),
        )
        rows = cur.fetchall()
    except Exception:
        cur.execute(
            "SELECT id, nombre, 60, precio FROM servicios WHERE usuario_id = %s ORDER BY nombre",
            (usuario_id,),
        )
        rows = cur.fetchall()
    cur.close()
    c.close()
    return rows


def list_empleados_salon(admin_usuario_id: int) -> List[Tuple[Any, ...]]:
    c = _conn()
    if not c:
        return []
    cur = c.cursor()
    cur.execute(
        """
        SELECT id, peluqueria FROM usuarios
        WHERE admin_id = %s AND rol = 'estilista'
        ORDER BY peluqueria
        """,
        (admin_usuario_id,),
    )
    rows = cur.fetchall()
    if not rows:
        cur.execute(
            "SELECT id, peluqueria FROM usuarios WHERE id = %s",
            (admin_usuario_id,),
        )
        rows = cur.fetchall()
    cur.close()
    c.close()
    return rows


def _normalize_fecha_hora(fecha_val, hora_val: Optional[str]) -> Tuple[str, str]:
    s = str(fecha_val or "").strip()
    if "T" in s:
        d, t = s.split("T", 1)
        return d[:10], (t[:5] if len(t) >= 5 else "09:00")
    return s[:10], (str(hora_val or "09:00"))[:5]


def citas_ocupadas_slot(
    usuario_id: int, empleado_id: int, fecha_dia: str
) -> List[str]:
    """Horas 'HH:MM' ya ocupadas para ese empleado y día."""
    c = _conn()
    if not c:
        return []
    cur = c.cursor()
    cur.execute(
        """
        SELECT fecha, hora FROM citas
        WHERE usuario_id = %s AND empleado_id = %s
        """,
        (usuario_id, empleado_id),
    )
    rows = cur.fetchall()
    cur.close()
    c.close()
    busy = []
    for fecha_v, hora_v in rows:
        d, h = _normalize_fecha_hora(fecha_v, hora_v)
        if d == fecha_dia[:10]:
            busy.append(h)
    return busy


def create_reserva(
    usuario_salon_id: int,
    nombre_cliente: str,
    telefono: str,
    servicio_id: int,
    empleado_id: int,
    fecha: str,
    hora: str,
) -> Tuple[bool, str, Optional[int]]:
    c = _conn()
    if not c:
        return False, "Sin conexión a base de datos", None
    cur = c.cursor()
    cur.execute(
        "SELECT nombre, precio FROM servicios WHERE id = %s AND usuario_id = %s",
        (servicio_id, usuario_salon_id),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        c.close()
        return False, "Servicio no válido", None
    nombre_serv, precio = row[0], float(row[1])
    fecha_iso = f"{fecha[:10]}T{hora[:5]}"
    try:
        dt_cita = datetime.strptime(f"{fecha[:10]} {hora[:5]}", "%Y-%m-%d %H:%M")
    except ValueError:
        cur.close()
        c.close()
        return False, "Fecha u hora inválida", None
    reminder_time = dt_cita - timedelta(hours=2)
    try:
        cur.execute(
            """
            INSERT INTO citas (
                usuario_id, cliente, servicio, precio, fecha, hora,
                telefono, empleado_id, servicio_id, estado,
                recordatorio_enviado, reminder_time
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, 'pendiente',
                0, %s
            )
            """,
            (
                usuario_salon_id,
                nombre_cliente,
                nombre_serv,
                precio,
                fecha_iso,
                hora[:5],
                telefono,
                empleado_id,
                servicio_id,
                reminder_time,
            ),
        )
        c.commit()
        cid = cur.lastrowid

        # ── Fase 6: WhatsApp + notificación para polling ──────────────
        try:
            from services.whatsapp_service import notify_salon_owner

            notify_salon_owner(
                usuario_salon_id,
                nombre_cliente,
                nombre_serv,
                fecha[:10],
                hora[:5],
            )
        except Exception:
            pass  # WhatsApp nunca rompe el flujo

        try:
            _guardar_notificacion(
                c, cur, usuario_salon_id, nombre_cliente, nombre_serv, hora[:5]
            )
        except Exception:
            pass  # notificación nunca rompe el flujo

        cur.close()
        c.close()
        return True, "", cid
    except Exception as e:
        c.rollback()
        cur.close()
        c.close()
        return False, str(e)[:200], None


def get_cita_publica(cita_id: int) -> Optional[dict]:
    c = _conn()
    if not c:
        return None
    cur = c.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT c.id, c.cliente, c.servicio, c.fecha, c.hora, c.telefono, c.estado, c.precio,
                   u.peluqueria AS profesional
            FROM citas c
            LEFT JOIN usuarios u ON c.empleado_id = u.id
            WHERE c.id = %s
            """,
            (cita_id,),
        )
    except Exception:
        cur.execute(
            """
            SELECT id, cliente, servicio, fecha, hora, telefono, estado, precio
            FROM citas WHERE id = %s
            """,
            (cita_id,),
        )
    row = cur.fetchone()
    cur.close()
    c.close()
    return row


def _guardar_notificacion(c, cur, salon_id: int, cliente: str, servicio: str, hora: str) -> None:
    """
    Guarda notificación en tabla notificaciones para que el polling del dashboard la lea.
    Tabla creada automáticamente si no existe.
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            salon_id INT NOT NULL,
            cliente VARCHAR(200),
            servicio VARCHAR(200),
            hora VARCHAR(10),
            leida TINYINT(1) DEFAULT 0,
            creada_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        INSERT INTO notificaciones (salon_id, cliente, servicio, hora)
        VALUES (%s, %s, %s, %s)
        """,
        (salon_id, cliente, servicio, hora),
    )
    c.commit()


def get_notificaciones_nuevas(salon_id: int) -> list:
    """Retorna notificaciones no leídas del salón. Usado por el endpoint de polling."""
    from datos.database_pro import obtener_conexion

    conn = obtener_conexion()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT id, cliente, servicio, hora, creada_en
            FROM notificaciones
            WHERE salon_id = %s AND leida = 0
            ORDER BY creada_en DESC
            LIMIT 10
            """,
            (salon_id,),
        )
        return cur.fetchall() or []
    except Exception:
        return []
    finally:
        cur.close()
        conn.close()


def marcar_notificaciones_leidas(salon_id: int) -> None:
    """Marca todas las notificaciones del salón como leídas."""
    from datos.database_pro import obtener_conexion

    conn = obtener_conexion()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE notificaciones SET leida = 1 WHERE salon_id = %s AND leida = 0",
            (salon_id,),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        cur.close()
        conn.close()
