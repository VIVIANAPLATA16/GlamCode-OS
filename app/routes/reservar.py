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


def _salon_id() -> int | None:
    """
    Prioridad:
    1. ?salon=X en la URL (QR del salón)
    2. session["usuario_id"] si el dueño está logueado
    3. None → el caller debe retornar error 400
    Nunca usa fallback hardcodeado — evita cruzar datos entre salones.
    """
    salon_param = request.args.get("salon", type=int)
    if salon_param:
        return salon_param
    from flask import session

    uid = session.get("usuario_id")
    if uid:
        return int(uid)
    return None


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
    sid = _salon_id()
    if not sid:
        return jsonify({"error": "salon_id requerido"}), 400
    rows = reservar_repo.list_servicios_salon(sid)
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
    sid = _salon_id()
    if not sid:
        return jsonify({"error": "salon_id requerido"}), 400
    rows = reservar_repo.list_empleados_salon(sid)
    data = [{"id": r[0], "nombre": r[1]} for r in rows]
    return jsonify(data)


@reservar_bp.route("/reservar/disponibilidad-json")
def disponibilidad_json():
    empleado_id = request.args.get("empleado_id", type=int)
    fecha = request.args.get("fecha", "")
    if not empleado_id or not fecha or not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
        return jsonify({"error": "empleado_id y fecha YYYY-MM-DD requeridos"}), 400
    sid = _salon_id()
    if not sid:
        return jsonify({"error": "salon_id requerido"}), 400
    busy = set(reservar_repo.citas_ocupadas_slot(sid, empleado_id, fecha))
    slots = [{"hora": s, "libre": s not in busy} for s in _slots_dia()]
    return jsonify({"slots": slots})


def _reservar_post_handler():
    payload = request.get_json(silent=True) or {}
    nombre = (payload.get("nombre_cliente") or "").strip()
    tel = (payload.get("telefono") or "").strip()
    sid = payload.get("servicio_id")
    eid = payload.get("empleado_id")
    fecha = (payload.get("fecha") or "").strip()
    hora = (payload.get("hora") or "").strip()

    # Parsear salon_id robusto: acepta int, string numérico o string vacío
    _raw = payload.get("salon_id")
    salon_id = None
    try:
        _parsed = int(str(_raw).strip()) if _raw not in (None, "", "null") else None
        if _parsed and _parsed > 0:
            salon_id = _parsed
    except (TypeError, ValueError):
        salon_id = None
    # Si no vino salon_id válido en el body, intentar desde sesión
    if not salon_id:
        from flask import session

        salon_id = session.get("usuario_id")
    # Nunca fallback a ID hardcodeado — retornar error explícito
    if not salon_id:
        return jsonify({"ok": False, "error": "Salón no identificado. Usa el link QR de tu salón."}), 400

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
    # Log de notificación en tiempo real
    try:
        print(f"🔔 CITA NUEVA: El salón {salon_id} tiene una nueva cita "
              f"de {nombre} para el {fecha} a las {hora}")
    except Exception:
        pass
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
