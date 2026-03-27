"""
Generador de códigos QR para reservas públicas (dorado sobre negro carbón).
"""
import os
from pathlib import Path

import qrcode


def generate_qr(url: str, output_path: str, fill_color: str, back_color: str) -> None:
    """Genera un PNG de QR con los colores indicados."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img.save(str(out))


def default_reserva_url() -> str:
    base = os.environ.get("BASE_URL", "https://glamcode-os.onrender.com").rstrip("/")
    return f"{base}/reservar"


def ensure_qr_reserva_file(static_img_dir: str) -> str:
    """
    Garantiza que exista static/img/qr_reserva.png apuntando a /reservar.
    Se llama al arrancar la app (cada deploy regenera el PNG).
    """
    path = os.path.join(static_img_dir, "qr_reserva.png")
    generate_qr(
        default_reserva_url(),
        path,
        fill_color="#c5a059",
        back_color="#0a0a0a",
    )
    return path


if __name__ == "__main__":
    _root = Path(__file__).resolve().parents[1]
    _static_img = _root / "static" / "img"
    generate_qr(
        default_reserva_url(),
        str(_static_img / "qr_reserva.png"),
        fill_color="#c5a059",
        back_color="#0a0a0a",
    )
    print("QR generado en", _static_img / "qr_reserva.png")


def generate_qr_for_salon(salon_id: int, base_url: str, static_folder: str) -> str:
    """
    Genera QR único por salón apuntando a /reservar?salon={id}.
    Usa los mismos colores dorado/negro de la identidad GlamCode.
    NO toca qr_reserva.png (QR genérico existente).
    Retorna URL relativa tipo '/static/img/qr_salon_3.png'.
    """
    booking_url = f"{base_url.rstrip('/')}/reservar?salon={salon_id}"
    filename = f"qr_salon_{salon_id}.png"
    output_path = os.path.join(static_folder, "img", filename)
    generate_qr(
        booking_url,
        output_path,
        fill_color="#c5a059",
        back_color="#0a0a0a",
    )
    return f"/static/img/{filename}"
