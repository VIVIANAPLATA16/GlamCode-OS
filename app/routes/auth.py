from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from datos.database_pro import crear_usuario, validar_usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = validar_usuario(email, password)
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["usuario_nombre"] = usuario["peluqueria"]
            session["rol"] = usuario["rol"]
            flash("Bienvenido de nuevo.", "success")
            return redirect(url_for("dashboard.inicio"))

        flash("Credenciales inválidas. Revisa tu correo y contraseña.", "error")

    return render_template("login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        peluqueria = request.form.get("peluqueria")
        email = request.form.get("email")
        password = request.form.get("password")

        if peluqueria and email and password:
            crear_usuario(peluqueria, email, password)
            flash("Cuenta creada con éxito. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))

        flash("Todos los campos son obligatorios.", "error")

    return render_template("registro.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))

