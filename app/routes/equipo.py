from flask import Blueprint, redirect, render_template, request, session, url_for

from app.decorators import login_required
from datos.database_pro import obtener_conexion

equipo_bp = Blueprint("equipo", __name__)


def _conectar():
    return obtener_conexion()


@equipo_bp.route("/crear_estilista", methods=["GET", "POST"])
@login_required
def crear_estilista():
    conn = _conectar()
    if not conn:
        return "Error: No se pudo conectar a la base de datos", 500

    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("peluqueria")
        email = request.form.get("email")
        password = request.form.get("password")

        if nombre and email and password:
            cursor.execute(
                """
                INSERT INTO usuarios (peluqueria, email, password, rol, admin_id) 
                VALUES (%s, %s, %s, 'estilista', %s)
                """,
                (nombre, email, password, session["usuario_id"]),
            )
            conn.commit()
        conn.close()
        return redirect(url_for("equipo.crear_estilista"))

    cursor.execute(
        "SELECT id, peluqueria, email FROM usuarios WHERE admin_id=%s",
        (session["usuario_id"],),
    )
    equipo = cursor.fetchall()
    conn.close()

    return render_template("crear_estilista.html", colaboradores=equipo)


@equipo_bp.route("/eliminar_estilista/<int:id>")
@login_required
def eliminar_estilista(id):
    conn = _conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM usuarios WHERE id = %s AND admin_id = %s",
            (id, session["usuario_id"]),
        )
        conn.commit()
        conn.close()

    return redirect(url_for("equipo.crear_estilista"))

