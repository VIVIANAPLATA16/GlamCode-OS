import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 4000)),
            # Configuración obligatoria para TiDB Cloud en producción
            ssl_verify_cert=False,
            ssl_ca=None
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
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

        query = """
        SELECT id, peluqueria, email, rol, password
        FROM usuarios
        WHERE email = %s
        """

        cursor.execute(query, (email.strip(),))
        usuario = cursor.fetchone()

        if usuario:
            if password.strip() == usuario["password"]:
                cursor.close()
                conexion.close()
                return usuario

        cursor.close()
        conexion.close()

    return None

def obtener_dashboard_data(usuario_id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        # Contar clientes
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id = %s", (usuario_id,))
        clientes = cursor.fetchone()[0]
        # Contar servicios
        cursor.execute("SELECT COUNT(*) FROM servicios WHERE usuario_id = %s", (usuario_id,))
        servicios = cursor.fetchone()[0]
        # Contar citas
        cursor.execute("SELECT COUNT(*) FROM citas WHERE usuario_id = %s", (usuario_id,))
        citas = cursor.fetchone()[0]
        
        cursor.close()
        conexion.close()
        return {"clientes": clientes, "servicios": servicios, "citas": citas}
    return {"clientes": 0, "servicios": 0, "citas": 0}