import os
from datetime import timedelta

from flask import Flask, request, session, jsonify
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy


# ==========================================================
# GLOBAL DB
# ==========================================================
db = SQLAlchemy()


# ==========================================================
# APP FACTORY
# ==========================================================
def create_app():
    app = Flask(__name__)

    # ------------------------------------------------------
    # SECRET KEY
    # ------------------------------------------------------
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "development-only-secret",
    )

    # ------------------------------------------------------
    # DATABASE (usa tu DATABASE_URL de Render)
    # ------------------------------------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///app.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ------------------------------------------------------
    # SESSION CONFIG (RENDER SAFE)
    # ------------------------------------------------------
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_NAME"] = "render_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    if os.getenv("RENDER"):
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
    else:
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

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
    # BLUEPRINTS
    # ------------------------------------------------------
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # ======================================================
    # SESSION DEBUG (SAFE)
    # ======================================================
    SESSION_DEBUG = True

    @app.before_request
    def debug_in():
        if request.method == "HEAD" and request.path == "/":
            return

        app.logger.info(
            "[SESSION DEBUG][IN] %s %s cookies=%s",
            request.method,
            request.path,
            dict(request.cookies),
        )

    @app.after_request
    def debug_out(response):
        try:
            cookies = response.headers.getlist("Set-Cookie")

            for cookie in cookies:
                app.logger.info(
                    "[SESSION DEBUG][OUT] %s",
                    cookie[:300],
                )
        except Exception:
            pass

        return response

    @app.route("/session-debug")
    def session_debug():
        return jsonify(
            session_data=dict(session),
            cookies_received=dict(request.cookies),
            is_logged_in=bool(session.get("usuario_id")),
        )

    # ------------------------------------------------------
    return app
