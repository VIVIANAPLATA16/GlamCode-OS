import logging
import os

import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()
_log = logging.getLogger(__name__)


def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 4000)),
            ssl_verify_cert=False,
            ssl_ca=None,
        )
        return conexion
    except mysql.connector.Error as err:
        _log.warning("Error al conectar a la base de datos: %s", err)
        return None

def crear_usuario(peluqueria, email, password):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (peluqueria, email, password, rol) VALUES (%s, %s, %s, 'admin')"
        cursor.execute(query, (peluqueria, email, password))
        conexion.commit()
        cursor.close()
        conexion.close()

def validar_usuario(email, password):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT id, peluqueria, email, rol, password FROM usuarios WHERE email = %s"
        cursor.execute(query, (email.strip(),))
        usuario = cursor.fetchone()

        if usuario:
            # Esta línea es la que hace que el login sea SEGURO
            if check_password_hash(usuario['password'], password.strip()):
                cursor.close()
                conexion.close()
                return usuario
        
        cursor.close()
        conexion.close()
    return None

def count_citas_hoy_usuario(usuario_id, fecha_iso: str) -> int:
    """Cuenta citas del día (fecha almacenada como texto ISO o fecha)."""
    conexion = obtener_conexion()
    if not conexion:
        return 0
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*) FROM citas
            WHERE usuario_id = %s
              AND substr(trim(cast(fecha as char)), 1, 10) = %s
            """,
            (usuario_id, fecha_iso[:10]),
        )
        n = cursor.fetchone()[0]
    except Exception:
        n = 0
    cursor.close()
    conexion.close()
    return int(n or 0)


def obtener_dashboard_data(usuario_id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id = %s", (usuario_id,))
        clientes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM servicios WHERE usuario_id = %s", (usuario_id,))
        servicios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM citas WHERE usuario_id = %s", (usuario_id,))
        citas = cursor.fetchone()[0]
        cursor.close()
        conexion.close()
        return {"clientes": clientes, "servicios": servicios, "citas": citas}
    return {"clientes": 0, "servicios": 0, "citas": 0}

def crear_cita(usuario_id, cliente, servicio, precio, fecha_input):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            # Dividimos la cadena donde esté la 'T'
            # "2026-03-21T14:15" -> ["2026-03-21", "14:15"]
            partes = fecha_input.split('T')
            fecha_solo = partes[0]
            hora_solo = partes[1] if len(partes) > 1 else "00:00"

            query = """
                INSERT INTO citas (usuario_id, cliente, servicio, precio, fecha, hora) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (usuario_id, cliente, servicio, precio, fecha_solo, hora_solo))
            conexion.commit()
            return True
        except Exception as e:
            _log.warning("Error al crear cita: %s", e)
            return False
        finally:
            cursor.close()
            conexion.close()
    return False