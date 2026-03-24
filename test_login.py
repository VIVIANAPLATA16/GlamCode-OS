import mysql.connector
from werkzeug.security import check_password_hash

def validar_usuario():
    try:
        # Configuración con tus datos de TiDB
        config = {
            'user': '3aYzvGv4rQtRA2y.root',
            'password': 'Lkw9wDj5Po1V8B8K',
            'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
            'port': 4000,
            'database': 'test',
            'ssl_verify_cert': True,
            'ssl_ca': '/etc/ssl/certs/ca-certificates.crt'
        }
        
        email_input = "barbershop@gmail.com"
        password_input = "admin123"

        print(f"--- Iniciando prueba para {email_input} ---")

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        query = "SELECT password FROM usuarios WHERE email = %s"
        cursor.execute(query, (email_input,))
        usuario = cursor.fetchone()

        if usuario:
            if check_password_hash(usuario['password'], password_input):
                print("✅ LOGIN CORRECTO")
            else:
                print("❌ CONTRASEÑA INCORRECTA")
        else:
            print("🚫 USUARIO NO ENCONTRADO")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    validar_usuario()