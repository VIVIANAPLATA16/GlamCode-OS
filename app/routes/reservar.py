"""Flujo público de reserva (wizard mobile-first)."""
from __future__ import annotations

import re

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)

from app.repositories import reservar_repo

reservar_bp = Blueprint("reservar", __name__, url_prefix="")


def _salon_id() -> int:
    """
    Prioridad:
    1. ?salon=X en la URL (QR del salón)
    2. JSON body salon_id (POST del wizard)
    3. Config PUBLIC_BOOKING_USUARIO_ID (fallback)
    """
    # GET param (QR link: /reservar?salon=3)
    salon_param = request.args.get("salon", type=int)
    if salon_param:
        return salon_param
    # Fallback a config
    return int(current_app.config.get("PUBLIC_BOOKING_USUARIO_ID", 1))


def _slots_dia() -> list[str]:
    out = []
    for h in range(9, 18):
        for m in (0, 30):
            if h == 17 and m > 0:
                break
            out.append(f"{h:02d}:{m:02d}")
    return out


@reservar_bp.route("/reservar", methods=["GET", "POST"])
def reservar():
    if request.method == "POST":
        return _reservar_post_handler()
    return render_template("reservar.html")


@reservar_bp.route("/reservar/servicios-json")
def servicios_json():
    rows = reservar_repo.list_servicios_salon(_salon_id())
    data = [
        {
            "id": r[0],
            "nombre": r[1],
            "duracion_minutos": int(r[2] or 60),
            "precio": float(r[3]),
        }
        for r in rows
    ]
    return jsonify(data)


@reservar_bp.route("/reservar/empleados-json")
def empleados_json():
    servicio_id = request.args.get("servicio_id", type=int)
    if not servicio_id:
        return jsonify({"error": "servicio_id requerido"}), 400
    rows = reservar_repo.list_empleados_salon(_salon_id())
    data = [{"id": r[0], "nombre": r[1]} for r in rows]
    return jsonify(data)


@reservar_bp.route("/reservar/disponibilidad-json")
def disponibilidad_json():
    empleado_id = request.args.get("empleado_id", type=int)
    fecha = request.args.get("fecha", "")
    if not empleado_id or not fecha or not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return jsonify({"error": "empleado_id y fecha YYYY-MM-DD requeridos"}), 400
    busy = set(
        reservar_repo.citas_ocupadas_slot(_salon_id(), empleado_id, fecha)
    )
    slots = []
    for s in _slots_dia():
        slots.append({"hora": s, "libre": s not in busy})
    return jsonify({"slots": slots})


def _reservar_post_handler():
    payload = request.get_json(silent=True) or {}
    nombre = (payload.get("nombre_cliente") or "").strip()
    tel = (payload.get("telefono") or "").strip()
    sid = payload.get("servicio_id")
    eid = payload.get("empleado_id")
    fecha = (payload.get("fecha") or "").strip()
    hora = (payload.get("hora") or "").strip()

    # salon_id: desde el body JSON (enviado por el wizard) o fallback a _salon_id()
    salon_id_body = payload.get("salon_id", type=int) if hasattr(payload.get("salon_id"), "__int__") else None
    try:
        salon_id_body = int(payload.get("salon_id")) if payload.get("salon_id") else None
    except (TypeError, ValueError):
        salon_id_body = None
    salon_id = salon_id_body or _salon_id()

    if not all([nombre, tel, sid, eid, fecha, hora]):
        return jsonify({"ok": False, "error": "Faltan campos obligatorios"}), 400
    ok, err, cid = reservar_repo.create_reserva(
        salon_id,
        nombre,
        tel,
        int(sid),
        int(eid),
        fecha,
        hora,
    )
    if not ok:
        return jsonify({"ok": False, "error": err or "No se pudo crear la cita"})
    return jsonify({"ok": True, "cita_id": cid})


@reservar_bp.route("/reservar/confirmacion/<int:cita_id>")
def reservar_confirmacion(cita_id: int):
    cita = reservar_repo.get_cita_publica(cita_id)
    if not cita:
        return render_template("reservar_error.html", mensaje="Cita no encontrada."), 404
    fecha_v = cita.get("fecha") or ""
    hora_v = cita.get("hora") or ""
    if "T" in str(fecha_v):
        fd, fh = str(fecha_v).split("T", 1)
        fecha_txt = fd
        hora_txt = (fh[:5] if len(fh) >= 5 else hora_v) or hora_v
    else:
        fecha_txt = str(fecha_v)[:10]
        hora_txt = str(hora_v)[:5] if hora_v else ""
    return render_template(
        "reservar_confirmacion.html",
        cita=cita,
        fecha_txt=fecha_txt,
        hora_txt=hora_txt,
    )
