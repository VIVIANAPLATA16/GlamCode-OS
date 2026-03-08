import sqlite3

def conectar():
    conexion = sqlite3.connect("peluqueria.db")
    return conexion

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()
    # Esta línea crea la tabla automáticamente si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

# Esto hace que las tablas se creen apenas se importe el archivo
crear_tablas()
