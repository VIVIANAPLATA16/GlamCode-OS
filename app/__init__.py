"""
GlamCode OS — factory Flask.

Auditoría de sesiones (Render + Gunicorn + HTTPS detrás de proxy)
------------------------------------------------------------------
Problemas frecuentes que rompen la cookie de sesión tras el login:

1) **Sin ProxyFix**: Gunicorn ve HTTP internamente; sin ``X-Forwarded-Proto``,
   Flask/Werkzeug puede generar URLs ``http://`` y políticas de cookie incoherentes
   con el sitio real en ``https://`` (explícitamente con ``Secure`` cookies).

2) **SESSION_COOKIE_SECURE=True sin HTTPS “visto” por la app**: el navegador
   solo envía cookies ``Secure`` sobre HTTPS; si la app cree que la petición es HTTP,
   la respuesta puede no alinearse con lo que el cliente espera.

3) **SameSite**: ``Lax`` suele funcionar para redirects mismo-sitio; en algunos
   flujos cross-site o iframes hace falta ``None`` + ``Secure`` (solo HTTPS).

4) **SECRET_KEY inestable o distinta por worker**: con sesión firmada en cliente,
   cualquier cambio de clave invalida la cookie. En producción debe venir solo del
   entorno (Render → Environment) y ser idéntica en todos los workers.

5) **session.permanent**: si no se marca ``session.permanent = True`` antes de
   poblar la sesión, la lifetime permanente no se aplica como se espera.

6) **Flask-Session (filesystem)**: la cookie guarda un ID; los datos van al disco.
   En un solo servicio Render, todos los workers comparten el mismo filesystem: usar
   ``SESSION_FILE_DIR`` bajo ``instance/`` para un directorio estable y escribible.

**Logs en Render**: Environment → tu servicio → **Logs**. Busca el prefijo
``[SESSION DEBUG]`` en *before_request* (cookies entrantes) y *after_request*
(headers ``Set-Cookie`` emitidos).
"""
import logging
import os
from datetime import timedelta

from flask import Flask, jsonify, request, session
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config


def create_app():
    """Aplicación principal de GlamCode OS."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    app.config.from_object(get_config())

    # ── SECRET_KEY: obligatoria en producción (evita clave por defecto compartida) ──
    secret = app.config.get("SECRET_KEY")
    flask_env = os.environ.get("FLASK_ENV", "development").lower()
    if flask_env == "production":
        if not secret or secret == "development-only-secret":
            raise RuntimeError(
                "SECRET_KEY debe definirse en el entorno en producción "
                "(Render → Environment). Sin ella las sesiones no son seguras ni estables."
            )

    is_prod = flask_env == "production"

    # ── Flask-Session: almacenamiento servidor (filesystem) ──
    # SESSION_TYPE: datos en disco; la cookie solo lleva el session id firmado.
    app.config["SESSION_TYPE"] = "filesystem"
    # SESSION_FILE_DIR: ruta compartida por workers en la misma instancia Render.
    session_dir = os.path.join(base_dir, "instance", "flask_session")
    os.makedirs(session_dir, exist_ok=True)
    app.config["SESSION_FILE_DIR"] = session_dir
    # SESSION_PERMANENT: permite aplicar PERMANENT_SESSION_LIFETIME cuando
    # session.permanent es True en la petición.
    app.config["SESSION_PERMANENT"] = True
    # SESSION_USE_SIGNER: firma el identificador de sesión en la cookie.
    app.config["SESSION_USE_SIGNER"] = True
    # SESSION_COOKIE_NAME: nombre explícito para no chocar con apps por defecto "session".
    app.config["SESSION_COOKIE_NAME"] = "render_session"
    # SESSION_COOKIE_HTTPONLY: no accesible desde JS (mitiga XSS robando cookie).
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    # SameSite=None REQUIERE Secure=True (navegadores modernos).
    if is_prod:
        # Producción detrás de HTTPS en Render: cookies solo por TLS, cross-site si hace falta.
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
    else:
        # Desarrollo en http://localhost: sin Secure el navegador acepta la cookie.
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    # Duración máxima de sesión permanente (24 h).
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=86400)

    # ── ProxyFix: confiar en X-Forwarded-* del load balancer de Render ──
    # Sin esto request.scheme puede ser "http" y fallan cookies Secure / URLs.
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )

    # Inicializar extension de sesión servidor-después de fijar toda la config anterior.
    Session(app)

    @app.before_request
def _log_incoming_cookies_for_session_debug():
    """
    Log de cookies recibidas.
    IMPORTANTE:
    Render envía HEAD / como health check constantemente.
    Evitamos loggear esos requests para prevenir timeouts.
    """

    # Ignorar health checks de Render
    if request.method == "HEAD" and request.path == "/":
        return

    if app.debug:
        app.logger.debug(
            "[SESSION DEBUG] request.cookies=%s",
            dict(request.cookies),
        )
    else:
        app.logger.info(
            "[SESSION DEBUG] request.cookies=%s",
            dict(request.cookies),
        )

    @app.after_request
def log_set_cookie_headers(response):
    if not SESSION_DEBUG:
        return response

    try:
        raw_headers = response.headers.getlist("Set-Cookie")

        for cookie in raw_headers:
            line = cookie if isinstance(cookie, str) else str(cookie)

            # evitar logs gigantes
            if len(line) > 500:
                line = line[:500] + "..."

            app.logger.info(
                "[SESSION DEBUG][OUT] Set-Cookie => %s",
                line,
            )

    except Exception as e:
        app.logger.error("[SESSION DEBUG][OUT][ERROR] %s", str(e))

    return response


    @app.get("/session-debug")
def session_debug():
    """
    Endpoint temporal para verificar sesión remotamente.

    IMPORTANTE:
    - Eliminar o proteger antes de producción pública.
    """

    return jsonify(
        session_data=dict(session),
        cookies_received=dict(request.cookies),
        is_logged_in=bool(session.get("usuario_id")),
        environment=os.getenv("RENDER", "local"),
    )

    # SQLAlchemy (modelos en models.py)
    from app.extensions import db

    import models  # noqa: F401 — registra tablas ORM

    db.init_app(app)
    with app.app_context():
        db.create_all()
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if uri and not str(uri).startswith("sqlite"):
            from datos.schema_upgrade import upgrade_schema

            upgrade_schema()
        try:
            from utils.qr_generator import ensure_qr_reserva_file

            ensure_qr_reserva_file(os.path.join(app.static_folder, "img"))
        except OSError as e:
            app.logger.warning("No se pudo generar QR: %s", e)

    # Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.clientes import clientes_bp
    from app.routes.citas import citas_bp
    from app.routes.servicios import servicios_bp
    from app.routes.equipo import equipo_bp
    from app.routes.reservar import reservar_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(citas_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(equipo_bp)
    app.register_blueprint(reservar_bp)

    try:
        from services.scheduler import init_scheduler

        init_scheduler(app)
    except Exception as e:
        app.logger.warning("Scheduler no iniciado: %s", e)

    return app
