"""
APScheduler: recordatorios 2h antes de la cita (ventana ±2 min cada 5 min).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from datos.database_pro import obtener_conexion
from services.whatsapp_service import send_whatsapp_reminder

_scheduler: BackgroundScheduler | None = None
_scheduler_started = False


def _parse_cita_dt(fecha_val, hora_val: str | None) -> datetime | None:
    if not fecha_val:
        return None
    s = str(fecha_val).strip()
    try:
        if "T" in s:
            d, t = s.split("T", 1)
            hh, mm = (t[:5] + ":00").split(":")[:2]
            return datetime.strptime(f"{d} {hh}:{mm}", "%Y-%m-%d %H:%M")
        if hora_val:
            hh, mm = (str(hora_val)[:5] + ":00").split(":")[:2]
            return datetime.strptime(f"{s[:10]} {hh}:{mm}", "%Y-%m-%d %H:%M")
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except ValueError:
        return None


def _job_recordatorios():
    conn = obtener_conexion()
    if not conn:
        return
    now = datetime.now()
    win_start = now + timedelta(hours=2, minutes=-2)
    win_end = now + timedelta(hours=2, minutes=2)
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT id, telefono, cliente, servicio, fecha, hora, recordatorio_enviado, estado
        FROM citas
        WHERE estado = 'pendiente'
          AND (recordatorio_enviado IS NULL OR recordatorio_enviado = 0)
        """
    )
    rows = cur.fetchall()
    for row in rows:
        if not row.get("telefono"):
            continue
        dt = _parse_cita_dt(row.get("fecha"), row.get("hora"))
        if not dt:
            continue
        if not (win_start <= dt <= win_end):
            continue
        hora_str = dt.strftime("%H:%M")
        ok = send_whatsapp_reminder(
            str(row["telefono"]).strip(),
            row.get("cliente") or "cliente",
            row.get("servicio") or "servicio",
            hora_str,
        )
        if ok:
            cur2 = conn.cursor()
            cur2.execute(
                "UPDATE citas SET recordatorio_enviado = 1 WHERE id = %s",
                (row["id"],),
            )
            conn.commit()
            cur2.close()
    cur.close()
    conn.close()


def init_scheduler(app) -> None:
    global _scheduler, _scheduler_started
    if _scheduler_started:
        return
    if os.environ.get("ENABLE_SCHEDULER", "").lower() not in ("1", "true", "yes"):
        return
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _job_recordatorios,
        "interval",
        minutes=5,
        id="recordatorios_whatsapp",
        replace_existing=True,
    )
    _scheduler.start()
    _scheduler_started = True
    app.logger.info("APScheduler iniciado (recordatorios cada 5 min).")
