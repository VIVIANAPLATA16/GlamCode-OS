from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ==============================
# CONEXIÓN BASE DE DATOS
# ==============================

def conectar():
    return sqlite3.connect("database.db")


# ==============================
# INICIO
# ==============================

@app.route("/")
def inicio():
    return render_template("clientes.html")

# ==============================
# CLIENTES
# ==============================

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        cursor.execute(
            "INSERT INTO clientes (nombre, telefono) VALUES (?, ?)",
            (nombre, telefono),
        )
        conexion.commit()
        return redirect(url_for("clientes"))

    cursor.execute("SELECT * FROM clientes")
    lista_clientes = cursor.fetchall()
    conexion.close()

    return render_template("clientes.html", clientes=lista_clientes)


@app.route("/delete_cliente/<int:id>")
def delete_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM clientes WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("clientes"))


@app.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
def editar_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]

        cursor.execute(
            "UPDATE clientes SET nombre = ?, telefono = ? WHERE id = ?",
            (nombre, telefono, id),
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("clientes"))

    cursor.execute("SELECT * FROM clientes WHERE id = ?", (id,))
    cliente = cursor.fetchone()
    conexion.close()

    return render_template("editar_cliente.html", cliente=cliente)


if __name__ == "__main__":
    app.run(debug=True)
