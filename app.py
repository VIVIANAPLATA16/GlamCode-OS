from flask import Flask, render_template, request, redirect, url_for, session
import os
from datos.database_pro import obtener_conexion

app = Flask(__name__)
app.secret_key = "glamcode_secret"

def conectar():
    try:
        return obtener_conexion()
    except Exception as e:
        print(f"Error BD: {e}")
        return None

@app.route("/")
def inicio():
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    conexion = conectar()
    total_clientes, total_citas = 0, 0
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
        total_clientes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
        total_citas = cursor.fetchone()[0]
        conexion.close()
    return render_template("dashboard.html", nombre=session.get("usuario_nombre", "Admin"), total_clientes=total_clientes, total_citas=total_citas)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email, password = request.form.get("email"), request.form.get("password")
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, peluqueria FROM usuarios WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session["usuario_id"], session["usuario_nombre"] = user[0], user[1]
                return redirect(url_for("inicio"))
        return "Error en login", 401
    return render_template("login.html")

@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        p, e, passw = request.form.get("peluqueria"), request.form.get("email"), request.form.get("password")
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (peluqueria, email, password) VALUES (%s, %s, %s)", (p, e, passw))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        n, t = request.form.get("nombre"), request.form.get("telefono")
        cursor.execute("INSERT INTO clientes (usuario_id, nombre, telefono) VALUES (%s, %s, %s)", (session["usuario_id"], n, t))
        conn.commit()
    cursor.execute("SELECT id, nombre, telefono FROM clientes WHERE usuario_id=%s", (session["usuario_id"],))
    lista = cursor.fetchall()
    conn.close()
    return render_template("clientes.html", clientes=lista)

@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        n, t = request.form.get("nombre"), request.form.get("telefono")
        cursor.execute("UPDATE clientes SET nombre=%s, telefono=%s WHERE id=%s AND usuario_id=%s", (n, t, id, session["usuario_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("clientes"))
    cursor.execute("SELECT id, nombre, telefono FROM clientes WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    c = cursor.fetchone()
    conn.close()
    return render_template("editar_cliente.html", cliente=c)

@app.route("/delete_cliente/<int:id>")
def delete_cliente(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("clientes"))

@app.route("/citas", methods=["GET","POST"])
def citas():
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        cl, s, f = request.form.get("cliente"), request.form.get("servicio"), request.form.get("fecha")
        cursor.execute("INSERT INTO citas (usuario_id, cliente, servicio, fecha) VALUES (%s, %s, %s, %s)", (session["usuario_id"], cl, s, f))
        conn.commit()
    cursor.execute("SELECT id, cliente, servicio, fecha FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
    lista = cursor.fetchall()
    conn.close()
    return render_template("citas.html", citas=lista)

@app.route("/editar_cita/<int:id>", methods=["GET", "POST"])
def editar_cita(id):
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        cl, s, f = request.form.get("cliente"), request.form.get("servicio"), request.form.get("fecha")
        cursor.execute("UPDATE citas SET cliente=%s, servicio=%s, fecha=%s WHERE id=%s AND usuario_id=%s", (cl, s, f, id, session["usuario_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("citas"))
    cursor.execute("SELECT id, cliente, servicio, fecha FROM citas WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    cita = cursor.fetchone()
    conn.close()
    return render_template("editar_cita.html", cita=cita)

@app.route("/delete_cita/<int:id>")
def delete_cita(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("citas"))

@app.route("/servicios", methods=["GET", "POST"])
def servicios():
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    
    if request.method == "POST":
        n = request.form.get("nombre")
        p = request.form.get("precio")
        cursor.execute("INSERT INTO servicios (usuario_id, nombre, precio) VALUES (%s, %s, %s)", (session["usuario_id"], n, p))
        conn.commit()
    
    cursor.execute("SELECT id, nombre, precio FROM servicios WHERE usuario_id=%s", (session["usuario_id"],))
    lista = cursor.fetchall()
    conn.close()
    return render_template("servicios.html", servicios=lista)

@app.route("/delete_servicio/<int:id>")
def delete_servicio(id):
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicios WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("servicios"))

if __name__ == "__main__":
    # Render usa la variable PORT, si no existe usa 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)