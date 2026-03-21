from flask import Blueprint, render_template, session

from datos.database_pro import obtener_dashboard_data

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def inicio():
    if "usuario_id" not in session:
        return render_template("landing.html")
    usuario_id = session["usuario_id"]
    data = obtener_dashboard_data(usuario_id)

    return render_template(
        "dashboard.html",
        nombre=session.get("usuario_nombre", "Admin"),
        total_clientes=data.get("clientes", 0),
        total_citas=data.get("citas", 0),
        total_servicios=data.get("servicios", 0),
    )

