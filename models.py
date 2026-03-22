"""
Modelos SQLAlchemy (TiDB / MySQL compatible).
Conviven con el acceso legacy en datos/database_pro.py.
"""
from datetime import datetime

from app.extensions import db


class Transaccion(db.Model):
    __tablename__ = "transacciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50))
    descripcion = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InventarioItem(db.Model):
    __tablename__ = "inventario"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(80))
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    unidad = db.Column(db.String(30))
    precio_costo = db.Column(db.Float)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
