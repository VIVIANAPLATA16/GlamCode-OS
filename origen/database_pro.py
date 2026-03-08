import sqlite3

def probar_base_de_datos():
    # 1. Conectar (Crea el archivo si no existe)
    conexion = sqlite3.connect('peluqueria_avanzada.db')
    cursor = conexion.cursor()

    # 2. Crear la tabla de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            servicio TEXT,
            precio REAL
        )
    ''')

    # 3. Insertar datos "Inventados" para la prueba
    cursor.execute("INSERT INTO clientes (nombre, servicio, precio) VALUES ('Viviana Plata', 'Diseño de Imagen', 50.0)")
    cursor.execute("INSERT INTO clientes (nombre, servicio, precio) VALUES ('Cliente VIP', 'Corte y Barba', 35.0)")

    # 4. Recuperar los datos para verlos
    cursor.execute("SELECT * FROM clientes")
    usuarios = cursor.fetchall()

    print("--- DATOS EN LA BASE DE DATOS ---")
    for usuario in usuarios:
        print(f"ID: {usuario[0]} | Nombre: {usuario[1]} | Servicio: {usuario[2]} | Precio: ${usuario[3]}")

    conexion.commit()
    conexion.close()

# Ejecutar la prueba
if __name__ == "__main__":
    probar_base_de_datos()
