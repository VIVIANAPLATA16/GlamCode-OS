from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    id: int
    peluqueria: str
    email: str
    password: str
    rol: str
    

@dataclass
class Cliente:
    id: int
    usuario_id: int
    nombre: str
    telefono: str


@dataclass
class Servicio:
    id: int
    usuario_id: int
    nombre: str
    precio: float


@dataclass
class Cita:
    id: int
    usuario_id: int
    cliente: str
    servicio: str
    precio: float
    fecha: datetime

