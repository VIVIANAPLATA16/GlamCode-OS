import mysql.connector
import os
from dotenv import load_dotenv

# Esto permite que el código lea las variables (llaves) que pusimos en Render
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
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Esta parte es para que puedas probar si la conexión a la nube funciona
if __name__ == "__main__":
    con = obtener_conexion()
    if con and con.is_connected():
        print("¡CONEXIÓN EXITOSA A TIDB CLOUD! Tu base de datos ya está en la nube.")
        con.close()
    else:
        print("No se pudo conectar. Revisa las variables en Render.")