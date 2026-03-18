from flask import Blueprint, redirect, render_template, request, session, url_for

from app.decorators import login_required
from app.repositories import servicios_repo

servicios_bp = Blueprint("servicios", __name__)


@servicios_bp.route("/servicios", methods=["GET", "POST"])
@login_required
def servicios():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        if nombre and precio:
            servicios_repo.create_servicio(session["usuario_id"], nombre, precio)

    lista = servicios_repo.get_servicios_by_usuario(session["usuario_id"])
    return render_template("servicios.html", servicios=lista)


@servicios_bp.route("/delete_servicio/<int:id>")
@login_required
def delete_servicio(id):
    servicios_repo.delete_servicio(session["usuario_id"], id)
    return redirect(url_for("servicios.servicios"))

