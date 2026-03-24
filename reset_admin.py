import mysql.connector
from werkzeug.security import generate_password_hash
from datos.database_pro import obtener_conexion

def reset_password():
    print("🔄 Conectando a la base de datos de GlamCode OS...")
    conn = obtener_conexion()
    if not conn:
        print("❌ ERROR: No se pudo conectar. Revisa tu conexión a internet o el archivo .env")
        return

    try:
        cursor = conn.cursor(dictionary=True)
        email = "barbershop@gmail.com"
        nueva_clave = "admin123"
        
        # Generamos un hash limpio y largo
        nuevo_hash = generate_password_hash(nueva_clave)
        
        print(f"🔐 Generando nuevo hash seguro para: {email}")
        
        # Actualizamos la base de datos
        query = "UPDATE usuarios SET password = %s WHERE email = %s"
        cursor.execute(query, (nuevo_hash, email))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ ÉXITO: La contraseña de {email} ha sido sincronizada correctamente.")
            print(f"🚀 Ya puedes usar 'admin123' para entrar.")
        else:
            print(f"⚠️ AVISO: No se encontró el usuario {email}. Verifica el correo.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR durante la ejecución: {e}")

if __name__ == "__main__":
    reset_password()