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
            # IMPORTANTE: Ahora seleccionamos el 'rol' para guardarlo en la sesión
            cursor.execute("SELECT id, peluqueria, rol FROM usuarios WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session["usuario_id"] = user[0]
                session["usuario_nombre"] = user[1]
                session["rol"] = user[2]  # Aquí guardamos si es 'admin' o 'estilista'
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
        cursor.execute("INSERT INTO clientes (usuario_id, nombre, terminal) VALUES (%s, %s, %s)", (session["usuario_id"], n, t))
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
        cl, s_nombre, f = request.form.get("cliente"), request.form.get("servicio"), request.form.get("fecha")
        cursor.execute("SELECT precio FROM servicios WHERE nombre=%s AND usuario_id=%s", (s_nombre, session["usuario_id"]))
        res = cursor.fetchone()
        precio_v = res[0] if res else 0
        cursor.execute("INSERT INTO citas (usuario_id, cliente, servicio, precio, fecha) VALUES (%s, %s, %s, %s, %s)", 
                       (session["usuario_id"], cl, s_nombre, precio_v, f))
        conn.commit()
        
    cursor.execute("SELECT id, cliente, servicio, precio, fecha FROM citas WHERE usuario_id=%s", (session["usuario_id"],))
    lista_raw = cursor.fetchall()
    lista_final = []
    for c in lista_raw:
        fecha_completa = c[4]
        if fecha_completa and "T" in fecha_completa:
            f_solo, h_solo = fecha_completa.split("T")
        else:
            f_solo, h_solo = fecha_completa, ""
        lista_final.append((c[0], c[1], c[2], c[3], f_solo, h_solo))
    conn.close()
    return render_template("citas.html", citas=lista_final)

@app.route("/editar_cita/<int:id>", methods=["GET", "POST"])
def editar_cita(id):
    if "usuario_id" not in session: return redirect(url_for("login"))
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        cl = request.form.get("cliente")
        s = request.form.get("servicio")
        f_s = request.form.get("fecha_solo")
        h_s = request.form.get("hora_solo")
        
        # Unimos fecha y hora para la BD
        fecha_unida = f"{f_s}T{h_s}"
        
        cursor.execute("SELECT precio FROM servicios WHERE nombre=%s AND usuario_id=%s", (s, session["usuario_id"]))
        res = cursor.fetchone()
        precio_v = res[0] if res else 0
        
        cursor.execute("UPDATE citas SET cliente=%s, servicio=%s, precio=%s, fecha=%s WHERE id=%s AND usuario_id=%s", 
                       (cl, s, precio_v, fecha_unida, id, session["usuario_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("citas"))
        
    cursor.execute("SELECT id, cliente, servicio, precio, fecha FROM citas WHERE id=%s AND usuario_id=%s", (id, session["usuario_id"]))
    cita = cursor.fetchone()
    
    # Separar para que el formulario de edición muestre los valores actuales
    f_solo, h_solo = "", ""
    if cita and cita[4] and "T" in cita[4]:
        f_solo, h_solo = cita[4].split("T")
    elif cita:
        f_solo = cita[4]

    conn.close()
    return render_template("editar_cita.html", cita=cita, fecha_s=f_solo, hora_s=h_solo)

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

@app.route("/crear_estilista", methods=["GET", "POST"])
def crear_estilista():
    if "usuario_id" not in session or session.get("rol") != "admin":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        nombre_p = request.form.get("peluqueria") # Nombre del salón
        email = request.form.get("email")
        password = request.form.get("password")
        
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            # Insertamos al nuevo usuario con rol 'estilista' y amarrado a tu ID
            cursor.execute("""
                INSERT INTO usuarios (peluqueria, email, password, rol, admin_id) 
                VALUES (%s, %s, %s, 'estilista', %s)
            """, (nombre_p, email, password, session["usuario_id"]))
            conn.commit()
            conn.close()
            return redirect(url_for("inicio"))
            
    return render_template("crear_estilista.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)