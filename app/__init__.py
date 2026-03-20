from flask import Flask
import os

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

    # Registro de blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.clientes import clientes_bp
    from app.routes.citas import citas_bp
    from app.routes.servicios import servicios_bp
    from app.routes.equipo import equipo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(citas_bp)
    app.register_blueprint(servicios_bp)
    app.register_blueprint(equipo_bp)

    return app