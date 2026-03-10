from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "glamcode_secret"
DB = "database.db"

# =============================
# CONEXIÓN
# =============================

def conectar():
    return sqlite3.connect("database.db")


# =============================
# CREAR TABLAS
# =============================

def crear_tablas():

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        peluqueria TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nombre TEXT,
        telefono TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        nombre TEXT,
        precio TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        cliente TEXT,
        servicio TEXT,
        fecha TEXT
    )
    """)

    conexion.commit()
    conexion.close()

crear_tablas()

# =============================
# LOGIN
# =============================

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = conectar()
        c = conn.cursor()

        c.execute("SELECT id, peluqueria FROM usuarios WHERE email=? AND password=?", (email, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["usuario_id"] = user[0]
            session["usuario_nombre"] = user[1] 
            return redirect(url_for("inicio")) 

    return render_template("login.html")


# =============================
# REGISTRO
# =============================

@app.route("/registro", methods=["GET","POST"])
def registro():

    if request.method == "POST":

        peluqueria = request.form["peluqueria"]
        email = request.form["email"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios(peluqueria,email,password) VALUES(?,?,?)",
            (peluqueria,email,password)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("registro.html")


# =============================
# LOGOUT
# =============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =============================
# DASHBOARD
# =============================

@app.route("/")
def inicio():
    # 1. Verificación de seguridad
    if "usuario_id" not in session:
        return redirect(url_for("login"))
    
    # 2. Conexión a la base de datos
    conexion = conectar()
    cursor = conexion.cursor()

    # 3. Contar total de clientes del usuario actual
    cursor.execute(
        "SELECT COUNT(*) FROM clientes WHERE usuario_id=?",
        (session["usuario_id"],)
    )
    total_clientes = cursor.fetchone()[0]

    # 4. Contar total de citas del usuario actual
    cursor.execute(
        "SELECT COUNT(*) FROM citas WHERE usuario_id=?",
        (session["usuario_id"],)
    )
    total_citas = cursor.fetchone()[0]

    conexion.close()

    # 5. Renderizar el nuevo dashboard con la información real
    return render_template(
        "dashboard.html", 
        nombre=session.get("usuario_nombre", "Glam Beauty"), 
        total_clientes=total_clientes, 
        total_citas=total_citas
    )

# =============================
# CLIENTES
# =============================

@app.route("/clientes", methods=["GET","POST"])
def clientes():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        cursor.execute(
            "INSERT INTO clientes(usuario_id,nombre,telefono) VALUES(?,?,?)",
            (session["usuario_id"],nombre,telefono)
        )

        conexion.commit()

    cursor.execute(
        "SELECT * FROM clientes WHERE usuario_id=?",
        (session["usuario_id"],)
    )

    lista_clientes = cursor.fetchall()

    conexion.close()

    return render_template("clientes.html",clientes=lista_clientes)


# =============================
# SERVICIOS
# =============================

@app.route("/servicios", methods=["GET","POST"])
def servicios():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]

        cursor.execute(
            "INSERT INTO servicios(usuario_id,nombre,precio) VALUES(?,?,?)",
            (session["usuario_id"],nombre,precio)
        )

        conexion.commit()

    cursor.execute(
        "SELECT * FROM servicios WHERE usuario_id=?",
        (session["usuario_id"],)
    )

    lista_servicios = cursor.fetchall()

    conexion.close()

    return render_template("servicios.html",servicios=lista_servicios)


# =============================
# CITAS
# =============================

@app.route("/citas", methods=["GET","POST"])
def citas():

    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":

        cliente = request.form["cliente"]
        servicio = request.form["servicio"]
        fecha = request.form["fecha"]

        cursor.execute(
            "INSERT INTO citas(usuario_id,cliente,servicio,fecha) VALUES(?,?,?,?)",
            (session["usuario_id"],cliente,servicio,fecha)
        )

        conexion.commit()

    cursor.execute(
        "SELECT * FROM citas WHERE usuario_id=?",
        (session["usuario_id"],)
    )

    lista_citas = cursor.fetchall()

    conexion.close()

    return render_template("citas.html",citas=lista_citas)


if __name__ == "__main__":
    app.run(debug=True)