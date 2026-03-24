import os
from datetime import timedelta

from flask import Flask, jsonify, request, session
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import db
from config import get_config


def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )

    app.config.from_object(get_config())

    secret = app.config.get("SECRET_KEY")
    flask_env = os.environ.get("FLASK_ENV", "development").lower()
    on_render = bool(os.environ.get("RENDER"))
    if (flask_env == "production" or on_render) and (
        not secret or secret == "development-only-secret"
    ):
        raise RuntimeError(
            "SECRET_KEY debe estar definido en el entorno en producción (Render → Environment)."
        )

    use_secure_cookies = flask_env == "production" or on_render

    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=86400)
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_NAME"] = "render_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    if use_secure_cookies:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
    else:
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    session_dir = os.path.join(base_dir, "instance", "flask_session")
    os.makedirs(session_dir, exist_ok=True)
    app.config["SESSION_FILE_DIR"] = session_dir

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )

    Session(app)

    @app.before_request
    def _log_session_cookies_in():
        if request.method == "HEAD" and request.path == "/":
            return
        app.logger.info(
            "[SESSION DEBUG][IN] %s %s cookies=%s",
            request.method,
            request.path,
            dict(request.cookies),
        )

    @app.after_request
    def _log_session_set_cookie(response):
        try:
            for cookie in response.headers.getlist("Set-Cookie"):
                app.logger.info("[SESSION DEBUG][OUT] %s", cookie[:300])
        except Exception:
            pass
        return response

    @app.get("/session-debug")
    def session_debug():
        return jsonify(
            session_data=dict(session),
            cookies_received=dict(request.cookies),
            is_logged_in=bool(session.get("usuario_id")),
        )

    db.init_app(app)
    import models  # noqa: F401

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

    from app.routes.auth import auth_bp
    from app.routes.citas import citas_bp
    from app.routes.clientes import clientes_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.equipo import equipo_bp
    from app.routes.reservar import reservar_bp
    from app.routes.servicios import servicios_bp

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
