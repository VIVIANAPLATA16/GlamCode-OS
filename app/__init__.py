import logging
import os

from flask import Flask

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
    
    # --- AGREGAR ESTO PARA RENDER ---
    app.config.update(
        SESSION_COOKIE_SECURE=True,   # Obliga a usar HTTPS (necesario en Render)
        SESSION_COOKIE_SAMESITE='Lax', # Permite que la sesión persista entre rutas
        SESSION_COOKIE_HTTPONLY=True  # Protege la cookie de ataques JS
    )
    # --------------------------------

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
