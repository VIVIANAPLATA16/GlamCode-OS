from datetime import date, timedelta

import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    send_file,
    session,
)
from sqlalchemy import func

from app.decorators import login_required
from app.extensions import db
from datos.database_pro import count_citas_hoy_usuario, obtener_dashboard_data
from models import InventarioItem, Transaccion

dashboard_bp = Blueprint("dashboard", __name__)

_DIAS_SEM = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


@dashboard_bp.route("/")
def inicio():
    if "usuario_id" not in session:
        return render_template("landing.html")

    usuario_id = session["usuario_id"]
    data = obtener_dashboard_data(usuario_id)

    from datos.database_pro import get_salon_by_usuario_id
    salon = get_salon_by_usuario_id(usuario_id) or {}
    nombre_salon = salon.get("peluqueria") or session.get("usuario_nombre", "Mi Salón")

    return render_template(
        "dashboard.html",
        nombre=nombre_salon,
        salon=salon,
        onboarding_completo=salon.get("onboarding_completo", 1),
        total_clientes=data.get("clientes", 0),
        total_citas=data.get("citas", 0),
        total_servicios=data.get("servicios", 0),
    )


@dashboard_bp.route("/dashboard/qr-download")
@login_required
def qr_download():
    base_dir = current_app.static_folder
    path = os.path.join(base_dir, "img", "qr_reserva.png")
    return send_file(
        path,
        as_attachment=True,
        download_name="GlamCode_QR_Reserva.png",
        mimetype="image/png",
    )


@dashboard_bp.route("/dashboard/metricas-json")
@login_required
def metricas_json():
    uid = session["usuario_id"]
    today = date.today()
    today_s = today.isoformat()
    cap = int(current_app.config.get("CAPACIDAD_DIARIA", 20))

    ingresos_hoy = (
        db.session.query(func.coalesce(func.sum(Transaccion.monto), 0.0))
        .filter(
            Transaccion.usuario_id == uid,
            Transaccion.fecha == today,
            Transaccion.tipo == "ingreso",
        )
        .scalar()
        or 0.0
    )

    citas_hoy = count_citas_hoy_usuario(uid, today_s)
    ocupacion_pct = (
        round(min(100, (citas_hoy / cap) * 100)) if cap > 0 else 0
    )
    ticket_promedio = (
        round(float(ingresos_hoy) / citas_hoy, 2) if citas_hoy > 0 else 0.0
    )

    ingresos_semana = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        m = (
            db.session.query(func.coalesce(func.sum(Transaccion.monto), 0.0))
            .filter(
                Transaccion.usuario_id == uid,
                Transaccion.fecha == d,
                Transaccion.tipo == "ingreso",
            )
            .scalar()
            or 0.0
        )
        label = _DIAS_SEM[d.weekday()]
        ingresos_semana.append({"dia": label, "monto": float(m)})

    return jsonify(
        {
            "ingresos_hoy": float(ingresos_hoy),
            "citas_hoy": citas_hoy,
            "ocupacion_pct": ocupacion_pct,
            "ticket_promedio": float(ticket_promedio),
            "ingresos_semana": ingresos_semana,
        }
    )


@dashboard_bp.route("/dashboard/inventario")
@login_required
def inventario_page():
    uid = session["usuario_id"]
    items = (
        InventarioItem.query.filter_by(usuario_id=uid)
        .order_by(InventarioItem.nombre)
        .all()
    )
    return render_template("inventario.html", items=items)


@dashboard_bp.route("/dashboard/metricas")
@login_required
def metricas_page():
    uid = session["usuario_id"]
    items = (
        InventarioItem.query.filter_by(usuario_id=uid)
        .order_by(InventarioItem.nombre)
        .all()
    )
    trans = (
        Transaccion.query.filter_by(usuario_id=uid)
        .order_by(Transaccion.fecha.desc(), Transaccion.id.desc())
        .limit(50)
        .all()
    )
    return render_template("metricas.html", items=items, transacciones=trans)
