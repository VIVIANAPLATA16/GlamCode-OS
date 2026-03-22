#!/usr/bin/env python3
"""
Inserta datos de prueba en TiDB / MySQL para GlamCode OS.

Requisitos: variables DB_* en .env (como en datos/database_pro.py).

Uso:
  python seed_data.py

El salón destino es PUBLIC_BOOKING_USUARIO_ID (o SEED_SALON_USUARIO_ID), por defecto 1.
Debe existir ese usuario (admin del negocio). Los datos se marcan con (SEED) / SEED_GLAMCODE
para poder borrarlos al volver a ejecutar el script.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# Import tras load_dotenv para que DB_* esté disponible
from datos.database_pro import obtener_conexion  # noqa: E402

SALON_ID = int(
    os.environ.get(
        "PUBLIC_BOOKING_USUARIO_ID",
        os.environ.get("SEED_SALON_USUARIO_ID", "1"),
    )
)

ESTILISTAS_SEED = [
    ("Ana García (SEED)", "estilista1@seed.glamcode.local"),
    ("Luis Morales (SEED)", "estilista2@seed.glamcode.local"),
]

SERVICIOS_SEED = [
    ("Corte premium (SEED)", 45000.0, 45),
    ("Coloración completa (SEED)", 120000.0, 120),
    ("Keratina express (SEED)", 85000.0, 90),
]

INVENTARIO_SEED = [
    ("Tinte rubio ceniza (SEED)", "Coloración", 32, 10, "unidad", 28000.0),
    ("Champú keratina (SEED)", "Cuidado", 18, 6, "botella", 45000.0),
    ("Cera modeladora (SEED)", "Estilismo", 12, 4, "tarro", 22000.0),
]

# 5 montos de ingresos, uno por día laboral de la semana actual (lun–vie)
MONTOS_SEMANA = [185000.0, 142000.0, 210000.0, 97500.0, 168000.0]


def _cleanup(cur) -> None:
    cur.execute(
        "DELETE FROM usuarios WHERE email IN (%s, %s)",
        (ESTILISTAS_SEED[0][1], ESTILISTAS_SEED[1][1]),
    )
    cur.execute(
        "DELETE FROM servicios WHERE usuario_id = %s AND nombre LIKE %s",
        (SALON_ID, "% (SEED)"),
    )
    cur.execute(
        "DELETE FROM transacciones WHERE usuario_id = %s AND descripcion LIKE %s",
        (SALON_ID, "SEED_GLAMCODE_TXN%"),
    )
    cur.execute(
        "DELETE FROM inventario WHERE usuario_id = %s AND nombre LIKE %s",
        (SALON_ID, "% (SEED)"),
    )


def _insert_empleados_y_servicios(cur) -> None:
    pw = generate_password_hash("seed1234")
    for nombre, email in ESTILISTAS_SEED:
        display = nombre.replace(" (SEED)", "").strip()
        try:
            cur.execute(
                """
                INSERT INTO usuarios (peluqueria, email, password, rol, admin_id)
                VALUES (%s, %s, %s, 'estilista', %s)
                """,
                (display, email, pw, SALON_ID),
            )
        except Exception:
            cur.execute(
                """
                INSERT INTO usuarios (peluqueria, email, password, rol)
                VALUES (%s, %s, %s, 'estilista')
                """,
                (display, email, pw),
            )

    for nombre, precio, duracion in SERVICIOS_SEED:
        try:
            cur.execute(
                """
                INSERT INTO servicios (usuario_id, nombre, precio, duracion_minutos)
                VALUES (%s, %s, %s, %s)
                """,
                (SALON_ID, nombre, precio, duracion),
            )
        except Exception:
            cur.execute(
                """
                INSERT INTO servicios (usuario_id, nombre, precio)
                VALUES (%s, %s, %s)
                """,
                (SALON_ID, nombre, precio),
            )


def _insert_transacciones(cur) -> None:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    for i, monto in enumerate(MONTOS_SEMANA):
        d = monday + timedelta(days=i)
        cur.execute(
            """
            INSERT INTO transacciones (usuario_id, fecha, monto, tipo, descripcion)
            VALUES (%s, %s, %s, 'ingreso', %s)
            """,
            (
                SALON_ID,
                d,
                monto,
                f"SEED_GLAMCODE_TXN_{i + 1}",
            ),
        )


def _insert_inventario(cur) -> None:
    for nombre, cat, stock, minimo, unidad, costo in INVENTARIO_SEED:
        cur.execute(
            """
            INSERT INTO inventario
            (usuario_id, nombre, categoria, stock_actual, stock_minimo, unidad, precio_costo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (SALON_ID, nombre, cat, stock, minimo, unidad, costo),
        )


def main() -> int:
    conn = obtener_conexion()
    if not conn:
        print(
            "Error: sin conexión a la base de datos. "
            "Define DB_HOST, DB_USER, DB_PASSWORD, DB_NAME y DB_PORT en .env"
        )
        return 1

    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE id = %s", (SALON_ID,))
    if not cur.fetchone():
        print(
            f"Error: no existe usuario con id={SALON_ID} (dueño del salón). "
            "Crea una cuenta o ajusta PUBLIC_BOOKING_USUARIO_ID / SEED_SALON_USUARIO_ID."
        )
        cur.close()
        conn.close()
        return 1

    try:
        _cleanup(cur)
        _insert_empleados_y_servicios(cur)
        _insert_transacciones(cur)
        _insert_inventario(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar datos: {e}")
        cur.close()
        conn.close()
        return 1

    cur.close()
    conn.close()
    print(
        f"OK — Seed aplicado para usuario_id={SALON_ID}:\n"
        "  • 2 empleados (estilista1@seed.glamcode.local / estilista2@seed.glamcode.local, pass: seed1234)\n"
        "  • 3 servicios (SEED)\n"
        "  • 5 transacciones ingreso (lun–vie de esta semana)\n"
        "  • 3 ítems de inventario (SEED)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
