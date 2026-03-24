from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from datos.database_pro import crear_usuario, validar_usuario, crear_usuario_seguro

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = validar_usuario(email, password)
        if usuario:
            # Orden crítico: limpiar sid anterior; marcar permanente ANTES de asignar
            # claves para que PERMANENT_SESSION_LIFETIME y Flask-Session apliquen bien.
            session.clear()
            session.permanent = True
            session["usuario_id"] = usuario["id"]
            session["usuario_email"] = usuario["email"]
            session["usuario_nombre"] = usuario["peluqueria"]
            session["rol"] = usuario["rol"]
            current_app.logger.info("[SESSION DEBUG] Session creada")
            flash("Bienvenido de nuevo.", "success")
            return redirect(url_for("dashboard.inicio"))

        flash("Credenciales inválidas. Revisa tu correo y contraseña.", "error")

    return render_template("login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        peluqueria = request.form.get("peluqueria", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not all([peluqueria, email, password]):
            flash("Todos los campos son obligatorios.", "error")
            return render_template("registro.html")

        nuevo = crear_usuario_seguro(peluqueria, email, password)
        if not nuevo:
            flash("Ese correo ya está registrado.", "error")
            return render_template("registro.html")

        flash("Cuenta creada con éxito. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("registro.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))

