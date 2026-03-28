"""
Recordatorios vía Twilio WhatsApp. Credenciales solo por variables de entorno.
"""
import os

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


def send_whatsapp_reminder(
    to_number: str, nombre: str, servicio: str, hora: str
) -> bool:
    """
    Envía recordatorio. to_number: E.164 sin prefijo whatsapp:, ej. +573001234567
    """
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_wa = os.environ.get("TWILIO_WHATSAPP_FROM")
    if not sid or not token or not from_wa or not to_number:
        return False
    body = (
        f"Hola {nombre} 👋 Te recordamos tu cita de *{servicio}* hoy a las *{hora}* "
        f"en GlamCode OS. ¡Te esperamos! ✨"
    )
    client = Client(sid, token)
    to_fmt = to_number if to_number.startswith("+") else f"+{to_number}"
    try:
        client.messages.create(
            from_=from_wa,
            to=f"whatsapp:{to_fmt}",
            body=body,
        )
        return True
    except TwilioRestException:
        return False


def notify_salon_owner(
    usuario_id: int,
    cliente_nombre: str,
    servicio_nombre: str,
    fecha: str,
    hora: str,
) -> bool:
    """
    Notifica al dueño del salón cuando llega una cita nueva.
    Busca el whatsapp_number del salón en DB usando usuario_id.
    Si falla, loguea warning pero NUNCA interrumpe el flujo de reserva.
    """
    try:
        from datos.database_pro import get_salon_by_usuario_id

        salon = get_salon_by_usuario_id(usuario_id) or {}
        to_number = salon.get("whatsapp_number")
        salon_nombre = salon.get("peluqueria", "tu salón")
        if not to_number or not str(to_number).strip():
            return False
        sid = os.environ.get("TWILIO_ACCOUNT_SID")
        token = os.environ.get("TWILIO_AUTH_TOKEN")
        from_wa = os.environ.get("TWILIO_WHATSAPP_FROM")
        if not all([sid, token, from_wa]):
            return False
        to_fmt = str(to_number).strip()
        if not to_fmt.startswith("+"):
            to_fmt = f"+{to_fmt}"
        body = (
            f"✨ Nueva cita en {salon_nombre}\n"
            f"👤 Cliente: {cliente_nombre}\n"
            f"💇 Servicio: {servicio_nombre}\n"
            f"📅 {fecha}  🕐 {hora}"
        )
        Client(sid, token).messages.create(
            from_=from_wa,
            to=f"whatsapp:{to_fmt}",
            body=body,
        )
        return True
    except TwilioRestException as e:
        import logging

        logging.getLogger(__name__).warning("WhatsApp failed for salon %s: %s", usuario_id, e)
        return False
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning("notify_salon_owner error: %s", e)
        return False
