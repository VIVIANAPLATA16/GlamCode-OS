from flask import Blueprint, redirect, render_template, request, session, url_for

from app.decorators import login_required
from app.repositories import citas_repo, servicios_repo

citas_bp = Blueprint("citas", __name__)


@citas_bp.route("/citas", methods=["GET", "POST"])
@login_required
def citas():
    if request.method == "POST":
        cliente = request.form.get("cliente")
        servicio_nombre = request.form.get("servicio")
        fecha = request.form.get("fecha")

        # reutilizamos capa de servicios para obtener precios
        servicios = servicios_repo.get_servicios_by_usuario(session["usuario_id"])
        precio_v = 0
        for s in servicios:
            if s[1] == servicio_nombre:
                precio_v = s[2]
                break

        citas_repo.create_cita(
            session["usuario_id"], cliente, servicio_nombre, precio_v, fecha
        )

    lista_raw = citas_repo.get_citas_by_usuario(session["usuario_id"])
    lista_final = []
    for cita in lista_raw:
        fecha_completa = cita[4]
        if fecha_completa and "T" in fecha_completa:
            fecha_solo, hora_solo = fecha_completa.split("T")
        else:
            fecha_solo, hora_solo = fecha_completa, ""
        lista_final.append((cita[0], cita[1], cita[2], cita[3], fecha_solo, hora_solo))

    return render_template("citas.html", citas=lista_final)


@citas_bp.route("/editar_cita/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cita(id):
    if request.method == "POST":
        cliente = request.form.get("cliente")
        servicio = request.form.get("servicio")
        fecha_solo = request.form.get("fecha_solo")
        hora_solo = request.form.get("hora_solo")

        fecha_unida = f"{fecha_solo}T{hora_solo}"

        servicios = servicios_repo.get_servicios_by_usuario(session["usuario_id"])
        precio_v = 0
        for s in servicios:
            if s[1] == servicio:
                precio_v = s[2]
                break

        citas_repo.update_cita(
            session["usuario_id"], id, cliente, servicio, precio_v, fecha_unida
        )
        return redirect(url_for("citas.citas"))

    cita = citas_repo.get_cita(session["usuario_id"], id)

    fecha_solo, hora_solo = "", ""
    if cita and cita[4] and "T" in cita[4]:
        fecha_solo, hora_solo = cita[4].split("T")
    elif cita:
        fecha_solo = cita[4]

    return render_template(
        "editar_cita.html", cita=cita, fecha_s=fecha_solo, hora_s=hora_solo
    )


@citas_bp.route("/delete_cita/<int:id>")
@login_required
def delete_cita(id):
    citas_repo.delete_cita(session["usuario_id"], id)
    return redirect(url_for("citas.citas"))

