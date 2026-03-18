from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from app.decorators import login_required
from app.repositories import clientes_repo

clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        if nombre and telefono:
            clientes_repo.create_cliente(session["usuario_id"], nombre, telefono)
            # SE AGREGA ESTO:
            flash("¡Cliente registrado con éxito!", "success")
            return redirect(url_for("clientes.clientes"))

    lista = clientes_repo.get_clientes_by_usuario(session["usuario_id"])
    return render_template("clientes.html", clientes=lista)


@clientes_bp.route("/editar_cliente/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    if request.method == "POST":
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        clientes_repo.update_cliente(session["usuario_id"], id, nombre, telefono)
        # SE AGREGA ESTO (Opcional):
        flash("¡Datos del cliente actualizados!", "success")
        return redirect(url_for("clientes.clientes"))

    cliente = clientes_repo.get_cliente(session["usuario_id"], id)
    return render_template("editar_cliente.html", cliente=cliente)


@clientes_bp.route("/delete_cliente/<int:id>")
@login_required
def delete_cliente(id):
    clientes_repo.delete_cliente(session["usuario_id"], id)
    # SE AGREGA ESTO:
    flash("Cliente eliminado correctamente", "success")
    return redirect(url_for("clientes.clientes"))