import os
from urllib.parse import quote_plus


def build_sqlalchemy_uri() -> str:
    """TiDB/MySQL via mysqlconnector, o SQLite local si no hay credenciales."""
    explicit = os.environ.get("DATABASE_URL")
    if explicit:
        return explicit
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    host = os.environ.get("DB_HOST")
    name = os.environ.get("DB_NAME")
    if user and host and name and password is not None:
        port = os.environ.get("DB_PORT", "4000")
        return (
            f"mysql+mysqlconnector://{user}:{quote_plus(password)}"
            f"@{host}:{port}/{name}"
        )
    base = os.path.abspath(os.path.dirname(__file__))
    inst = os.path.join(base, "instance")
    os.makedirs(inst, exist_ok=True)
    return f"sqlite:///{os.path.join(inst, 'glamcode_local.db')}"


class Config:
    # En producción definir SECRET_KEY en el entorno (Render).
    SECRET_KEY = os.environ.get("SECRET_KEY") or "development-only-secret"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = build_sqlalchemy_uri()
    BASE_URL = os.environ.get("BASE_URL", "https://glamcode-os.onrender.com")
    CAPACIDAD_DIARIA = int(os.environ.get("CAPACIDAD_DIARIA", "20"))
    PUBLIC_BOOKING_USUARIO_ID = int(os.environ.get("PUBLIC_BOOKING_USUARIO_ID", "1"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)

