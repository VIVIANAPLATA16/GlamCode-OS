from flask import Flask, render_template, request, redirect, url_for, session
import os
from datos.database_pro import obtener_conexion

app = Flask(__name__)
app.secret_key = "glamcode_secret"

# =============================
# FUNCION DE CONEXIÓN (NUBE)
# =============================
def conectar():
    try:
        return obtener_conexion()
    except Exception as e:
        print(f"DEBUG: Error de conexión a la base de datos: {e}")
        return None

# =============================
# DASHBOARD
# =============================
@app.route("/")
def inicio():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    total_clientes = 0
    total_citas = 0
    
    if conexion:
        try:
            cursor = conexion.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
                total_clientes = cursor.fetchone()[0]
            except:
                total_clientes = 0

            try:
                cursor.execute("SELECT COUNT(*) FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
                total_citas = cursor.fetchone()[0]
            except:
                total_citas = 0
            
            return render_template(
                "dashboard.html", 
                nombre=session.get("usuario_nombre", "Glam Beauty"), 
                total_clientes=total_clientes, 
                total_citas=total_citas
            )
        except Exception as e:
            return f"Error en Dashboard: {e}", 500
        finally:
            conexion.close()
    return redirect(url_for("login"))

# =============================
# LOGIN / REGISTRO / LOGOUT
# =============================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = conectar()
        if conn:
            try:
                cursor = conn.cursor()
                query = "SELECT id, peluqueria FROM usuarios WHERE email=%s AND password=%s"
                cursor.execute(query, (email, password))
                user = cursor.fetchone()
                if user:
                    session["usuario_id"] = user[0]
                    session["usuario_nombre"] = user[1]
                    return redirect(url_for("inicio"))
                return "Usuario o contraseña incorrectos", 401
            finally:
                conn.close()
    return render_template("login.html")

@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        peluqueria = request.form.get("peluqueria")
        email = request.form.get("email")
        password = request.form.get("password")
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                query = "INSERT INTO usuarios (peluqueria, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (peluqueria, email, password))
                conexion.commit()
                return redirect(url_for("login"))
            finally:
                conexion.close()
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =============================
# CLIENTES
# =============================
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500
    
    try:
        cursor = conexion.cursor()
        if request.method == "POST":
            nombre = request.form.get("nombre")
            telefono = request.form.get("telefono")
            if nombre and telefono:
                cursor.execute(
                    "INSERT INTO clientes (usuario_id, nombre, telefono) VALUES (%s, %s, %s)",
                    (session["usuario_id"], nombre, telefono)
                )
                conexion.commit()

        cursor.execute("SELECT id, nombre, telefono FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
        lista_clientes = cursor.fetchall()
        return render_template("clientes.html", clientes=lista_clientes)
    except Exception as e:
        return f"Error: {e}", 500
    finally:
        conexion.close()

@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre")
        nuevo_telefono = request.form.get("telefono")
        cursor.execute(
            "UPDATE clientes SET nombre=%s, telefono=%s WHERE id=%s AND usuario_id=%s",
            (nuevo_nombre, nuevo_telefono, id, session["usuario_id"])
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("clientes"))

    cursor.execute("SELECT id, nombre, telefono FROM clientes WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    cliente = cursor.fetchone()
    conexion.close()
    if not cliente: return redirect(url_for("clientes"))
    return render_template("editar_cliente.html", cliente=cliente)

@app.route("/delete_cliente/<int:id>")
def delete_cliente(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM clientes WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
        conexion.commit()
        conexion.close()
    return redirect(url_for("clientes"))

# =============================
# SERVICIOS
# =============================
@app.route("/servicios", methods=["GET","POST"])
def servicios():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500

    try:
        cursor = conexion.cursor()
        if request.method == "POST":
            nombre = request.form.get("nombre")
            precio = request.form.get("precio")
            if nombre and precio:
                cursor.execute(
                    "INSERT INTO servicios (usuario_id, nombre, precio) VALUES (%s, %s, %s)",
                    (session["usuario_id"], nombre, precio)
                )
                conexion.commit()

        cursor.execute("SELECT id, nombre, precio FROM servicios WHERE usuario_id=%s", (session["usuario_id"],))
        lista_servicios = cursor.fetchall()
        return render_template("servicios.html", servicios=lista_servicios)
    finally:
        conexion.close()

# =============================
# CITAS
# =============================
@app.route("/citas", methods=["GET","POST"])
def citas():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    if not conexion: return "Error de conexión", 500

    try:
        cursor = conexion.cursor()
        if request.method == "POST":
            cliente = request.form.get("cliente")
            servicio = request.form.get("servicio")
            fecha = request.form.get("fecha")
            if cliente and servicio and fecha:
                cursor.execute(
                    "INSERT INTO citas (usuario_id, cliente, servicio, fecha) VALUES (%s, %s, %s, %s)",
                    (session["usuario_id"], cliente, servicio, fecha)
                )
                conexion.commit()

        cursor.execute("SELECT id, cliente, servicio, fecha FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
        lista_citas = cursor.fetchall()
        return render_template("citas.html", citas=lista_citas)
    finally:
        conexion.close()

@app.route("/editar_cita/<int:id>", methods=["GET", "POST"])
def editar_cita(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":
        nuevo_cliente = request.form.get("cliente")
        nuevo_servicio = request.form.get("servicio")
        nueva_fecha = request.form.get("fecha")
        
        cursor.execute(
            "UPDATE citas SET cliente=%s, servicio=%s, fecha=%s WHERE id=%s AND usuario_id=%s",
            (nuevo_cliente, nuevo_servicio, nueva_fecha, id, session["usuario_id"])
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("citas"))

    cursor.execute("SELECT id, cliente, servicio, fecha FROM citas WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    cita = cursor.fetchone()
    conexion.close()
    
    if not cita:
        return redirect(url_for("citas"))
        
    return render_template("editar_cita.html", cita=cita)

@app.route("/delete_cita/<int:id>")
def delete_cita(id):
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    conexion = conectar()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM citas WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
        conexion.commit()
        conexion.close()
    return redirect(url_for("citas"))

# =============================
# ARRANQUE
# =============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
