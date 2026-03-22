"""
Migraciones ligeras vía DDL (TiDB/MySQL). Ignora errores si la columna ya existe.
"""
import mysql.connector

from datos.database_pro import obtener_conexion


def _try(cursor, sql: str) -> None:
    try:
        cursor.execute(sql)
    except mysql.connector.Error:
        pass


def upgrade_schema() -> None:
    conn = obtener_conexion()
    if not conn:
        return
    cur = conn.cursor()
    # Tablas ORM (por si create_all no corre en el mismo engine)
    _try(
        cur,
        """
        CREATE TABLE IF NOT EXISTS transacciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            fecha DATE NOT NULL,
            monto DOUBLE NOT NULL,
            tipo VARCHAR(50),
            descripcion VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_trans_usuario (usuario_id),
            INDEX idx_trans_fecha (fecha)
        )
        """,
    )
    _try(
        cur,
        """
        CREATE TABLE IF NOT EXISTS inventario (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            nombre VARCHAR(120) NOT NULL,
            categoria VARCHAR(80),
            stock_actual INT DEFAULT 0,
            stock_minimo INT DEFAULT 5,
            unidad VARCHAR(30),
            precio_costo DOUBLE,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_inv_usuario (usuario_id)
        )
        """,
    )
    # Extensiones citas (reservas + recordatorios)
    for stmt in (
        "ALTER TABLE citas ADD COLUMN telefono VARCHAR(40) NULL",
        "ALTER TABLE citas ADD COLUMN empleado_id INT NULL",
        "ALTER TABLE citas ADD COLUMN servicio_id INT NULL",
        "ALTER TABLE citas ADD COLUMN estado VARCHAR(50) DEFAULT 'confirmada'",
        "ALTER TABLE citas ADD COLUMN recordatorio_enviado TINYINT(1) DEFAULT 0",
        "ALTER TABLE citas ADD COLUMN reminder_time DATETIME NULL",
        "ALTER TABLE citas ADD COLUMN hora VARCHAR(10) NULL",
    ):
        _try(cur, stmt)
    _try(
        cur,
        "ALTER TABLE servicios ADD COLUMN duracion_minutos INT DEFAULT 60",
    )
    conn.commit()
    cur.close()
    conn.close()
