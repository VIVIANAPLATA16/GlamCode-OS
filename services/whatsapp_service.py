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
