import os
from datetime import timedelta

from flask import Flask, request, session, jsonify
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix

from .extensions import db


# ==========================================================
# APP FACTORY
# ==========================================================
def create_app():
    app = Flask(__name__)

    # ------------------------------------------------------
    # BASIC CONFIG
    # ------------------------------------------------------
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "development-only-secret",
    )

    # ------------------------------------------------------
    # SESSION CONFIG (RENDER SAFE)
    # ------------------------------------------------------
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_NAME"] = "render_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    # HTTPS detrás del proxy de Render
    if os.getenv("RENDER"):
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
    else:
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # carpeta donde Flask-Session guarda sesiones
    session_dir = os.path.join(app.instance_path, "flask_session")
    os.makedirs(session_dir, exist_ok=True)

    app.config["SESSION_FILE_DIR"] = session_dir

    Session(app)

    # ------------------------------------------------------
    # PROXY FIX (CRÍTICO EN RENDER)
    # ------------------------------------------------------
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )

    # ------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ------------------------------------------------------
    # REGISTER BLUEPRINTS
    # ------------------------------------------------------
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # ==========================================================
    # SESSION DEBUG TOOLKIT (SEGURO PARA RENDER)
    # ==========================================================

    SESSION_DEBUG = os.getenv("SESSION_DEBUG", "true").lower() == "true"

    @app.before_request
    def session_debug_before_request():
        if not SESSION_DEBUG:
            return

        # Render hace health checks HEAD /
        if request.method == "HEAD" and request.path == "/":
            return

        app.logger.info(
            "[SESSION DEBUG][IN] %s %s cookies=%s",
            request.method,
            request.path,
            dict(request.cookies),
        )

    @app.after_request
    def session_debug_after_request(response):
        if not SESSION_DEBUG:
            return response

        try:
            cookies = response.headers.getlist("Set-Cookie")

            for cookie in cookies:
                line = cookie if isinstance(cookie, str) else str(cookie)

                if len(line) > 500:
                    line = line[:500] + "..."

                app.logger.info(
                    "[SESSION DEBUG][OUT] Set-Cookie=%s",
                    line,
                )

        except Exception as e:
            app.logger.error(
                "[SESSION DEBUG][ERROR]=%s",
                str(e),
            )

        return response

    @app.route("/session-debug")
    def session_debug():
        return jsonify(
            session_data=dict(session),
            cookies_received=dict(request.cookies),
            is_logged_in=bool(session.get("usuario_id")),
            environment=os.getenv("RENDER", "local"),
        )

    # ------------------------------------------------------
    return app
