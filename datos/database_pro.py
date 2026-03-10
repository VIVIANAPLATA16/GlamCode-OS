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
            port=os.getenv('DB_PORT')
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
        return None

# --- AQUÍ ESTÁN LAS FUNCIONES QUE FALTABAN ---

def crear_usuario(peluqueria, email, password):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (peluqueria, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (peluqueria, email, password))
        conexion.commit()
        cursor.close()
        conexion.close()

def validar_usuario(email, password):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()
        return usuario
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