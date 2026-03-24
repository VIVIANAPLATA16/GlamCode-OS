import logging
import os

import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

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

def validar_usuario(email: str, password: str) -> dict | None:
    conexion = obtener_conexion()
    if not conexion:
        return None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, peluqueria, email, rol, password FROM usuarios WHERE email = %s",
            (email.strip(),),
        )
        usuario = cursor.fetchone()
        
        if not usuario or not usuario["password"]:
            cursor.close()
            conexion.close()
            return None

        pwd_stored = usuario["password"]
        
        # Verificamos que el hash tenga el formato correcto (debe tener al menos un ':')
        if ":" in pwd_stored:
            autenticado = check_password_hash(pwd_stored, password.strip())
        else:
            # Si no es un hash válido, comparamos texto plano y migramos
            autenticado = (pwd_stored == password.strip())
            if autenticado:
                _migrar_password_a_hash(usuario["id"], password.strip(), cursor, conexion)

        cursor.close()
        conexion.close()
        return usuario if autenticado else None
    except Exception as e:
        print(f"Error en validación: {e}")
        return None


def _migrar_password_a_hash(usuario_id: int, password_plano: str,
                             cursor, conexion) -> None:
    try:
        nuevo_hash = generate_password_hash(password_plano)
        cursor.execute(
            "UPDATE usuarios SET password = %s WHERE id = %s",
            (nuevo_hash, usuario_id),
        )
        conexion.commit()
    except Exception:
        pass

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


def crear_usuario_seguro(peluqueria: str, email: str, password: str) -> dict | None:
    conexion = obtener_conexion()
    if not conexion:
        return None
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email.strip(),))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return None
    hashed = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO usuarios (peluqueria, email, password, rol) VALUES (%s, %s, %s, 'owner')",
        (peluqueria.strip(), email.strip(), hashed),
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conexion.close()
    return {"id": nuevo_id, "peluqueria": peluqueria, "rol": "owner"}


def get_salon_by_usuario_id(usuario_id: int) -> dict | None:
    """
    Retorna todos los datos del salón/tenant autenticado.
    Usado en dashboard, QR download y onboarding.
    """
    conexion = obtener_conexion()
    if not conexion:
        return None
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, peluqueria, email, rol, ciudad, horario,
                   servicios_principales, whatsapp_number, qr_code_url,
                   onboarding_completo, admin_id
            FROM usuarios WHERE id = %s
            """,
            (usuario_id,),
        )
        row = cursor.fetchone()
    except Exception as e:
        _log.warning("get_salon_by_usuario_id error: %s", e)
        row = None
    cursor.close()
    conexion.close()
    return row


def update_salon_config(usuario_id: int, **kwargs) -> bool:
    """
    Actualiza campos del salón. Solo acepta columnas de la whitelist.
    Uso: update_salon_config(1, ciudad="Bogotá", horario="Lun-Sáb 9-7")
    Retorna True si actualizó, False si no había campos válidos o falló conexión.
    """
    ALLOWED = {
        "ciudad", "horario", "servicios_principales",
        "whatsapp_number", "onboarding_completo", "peluqueria",
    }
    fields = {k: v for k, v in kwargs.items() if k in ALLOWED}
    if not fields:
        return False
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [usuario_id]
    conexion = obtener_conexion()
    if not conexion:
        return False
    cursor = conexion.cursor()
    try:
        cursor.execute(
            f"UPDATE usuarios SET {set_clause} WHERE id = %s", values
        )
        conexion.commit()
        return True
    except Exception as e:
        _log.warning("update_salon_config error: %s", e)
        return False
    finally:
        cursor.close()
        conexion.close()


def verificar_columnas_fase2() -> dict:
    """
    Utilidad de diagnóstico. Verifica que las columnas de Fase 2 existen en TiDB.
    Llamar desde flask shell: from datos.database_pro import verificar_columnas_fase2; print(verificar_columnas_fase2())
    """
    ESPERADAS = {
        "ciudad", "horario", "servicios_principales", "whatsapp_number",
        "qr_code_url", "onboarding_completo", "stylist_slug", "admin_id",
    }
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "Sin conexión a TiDB"}
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT COLUMN_NAME, COLUMN_TYPE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'usuarios'
        ORDER BY ORDINAL_POSITION
        """,
    )
    existentes = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    conexion.close()
    faltantes = ESPERADAS - set(existentes.keys())
    return {
        "columnas_existentes": list(existentes.keys()),
        "columnas_fase2_faltantes": list(faltantes),
        "fase2_completa": len(faltantes) == 0,
    }