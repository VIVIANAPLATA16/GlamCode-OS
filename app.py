from flask import Flask, render_template, request, redirect, url_for, session
import os
from datos.database_pro import obtener_conexion

app = Flask(__name__)
app.secret_key = "glamcode_secret"

# =============================
# FUNCION DE CONEXIÓN (NUBE)
# =============-================
def conectar():
    return obtener_conexion()

# =============================
# DASHBOARD (RUTA PRINCIPAL)
# =============================
@app.route("/")
def inicio():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        # Contar clientes
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
        total_clientes = cursor.fetchone()[0]

        # Contar citas
        cursor.execute("SELECT COUNT(*) FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
        total_citas = cursor.fetchone()[0]
        
        conexion.close()

        return render_template(
            "dashboard.html", 
            nombre=session.get("usuario_nombre", "Glam Beauty"), 
            total_clientes=total_clientes, 
            total_citas=total_citas
        )
    return "Error de conexión con la base de datos", 500

# =============================
# LOGIN
# =============================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return "Por favor, ingresa correo y contraseña", 400

        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # Buscamos el ID y el nombre de la peluquería para la sesión
            cursor.execute("SELECT id, peluqueria FROM usuarios WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session["usuario_id"] = user[0]
                session["usuario_nombre"] = user[1] 
                return redirect(url_for("inicio")) 
            else:
                return "Usuario o contraseña incorrectos. <a href='/login'>Volver a intentar</a>", 401
        else:
            return "Error de conexión a la base de datos", 500

    return render_template("login.html")

# =============================
# REGISTRO
# =============================
@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        peluqueria = request.form.get("peluqueria")
        email = request.form.get("email")
        password = request.form.get("password")

        if not peluqueria or not email or not password:
            return "Todos los campos son obligatorios", 400

        conexion = conectar()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "INSERT INTO usuarios(peluqueria, email, password) VALUES(%s, %s, %s)",
                    (peluqueria, email, password)
                )
                conexion.commit()
                return redirect(url_for("login"))
            except Exception as e:
                return f"Error al registrar: {e}", 500
            finally:
                conexion.close()
        else:
            return "Error de conexión", 500

    return render_template("registro.html")

# =============================
# LOGOUT
# =============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =============================
# CLIENTES
# =============================
@app.route("/clientes", methods=["GET","POST"])
def clientes():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500
    
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        if nombre and telefono:
            cursor.execute(
                "INSERT INTO clientes(usuario_id, nombre, telefono) VALUES(%s, %s, %s)",
                (session["usuario_id"], nombre, telefono)
            )
            conexion.commit()

    cursor.execute("SELECT id, nombre, telefono FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
    lista_clientes = cursor.fetchall()
    conexion.close()

    return render_template("clientes.html", clientes=lista_clientes)

# =============================
# SERVICIOS
# =============================
@app.route("/servicios", methods=["GET","POST"])
def servicios():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500

    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        if nombre and precio:
            cursor.execute(
                "INSERT INTO servicios(usuario_id, nombre, precio) VALUES(%s, %s, %s)",
                (session["usuario_id"], nombre, precio)
            )
            conexion.commit()

    cursor.execute("SELECT id, nombre, precio FROM servicios WHERE usuario_id=%s", (session["usuario_id"],))
    lista_servicios = cursor.fetchall()
    conexion.close()

    return render_template("servicios.html", servicios=lista_servicios)

# =============================
# CITAS
# =============================
@app.route("/citas", methods=["GET","POST"])
def citas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500

    cursor = conexion.cursor()

    if request.method == "POST":
        cliente = request.form.get("cliente")
        servicio = request.form.get("servicio")
        fecha = request.form.get("fecha")
        if cliente and servicio and fecha:
            cursor.execute(
                "INSERT INTO citas(usuario_id, cliente, servicio, fecha) VALUES(%s, %s, %s, %s)",
                (session["usuario_id"], cliente, servicio, fecha)
            )
            conexion.commit()

    cursor.execute("SELECT id, cliente, servicio, fecha FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
    lista_citas = cursor.fetchall()
    conexion.close()

    return render_template("citas.html", citas=lista_citas)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)