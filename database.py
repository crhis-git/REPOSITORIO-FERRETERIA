"""Conexión e inicialización de la base de datos SQLite."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

RUTA_PROYECTO = Path(__file__).resolve().parent
CARPETA_DATOS = RUTA_PROYECTO / "data"
DB_PATH = CARPETA_DATOS / "mesa_partes.db"


@contextmanager
def obtener_conexion(ruta_db=DB_PATH):
    ruta = Path(ruta_db)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(str(ruta))
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar_base_datos(ruta_db=DB_PATH):
    esquema = """
    CREATE TABLE IF NOT EXISTS proveedores (
        codigo TEXT PRIMARY KEY COLLATE NOCASE,
        nombre TEXT NOT NULL CHECK(length(trim(nombre)) > 0),
        ruc TEXT DEFAULT '',
        telefono TEXT DEFAULT '',
        correo TEXT DEFAULT '',
        direccion TEXT DEFAULT '',
        creado_en TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );
    CREATE TABLE IF NOT EXISTS documentos (
        registro INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_proveedor TEXT NOT NULL,
        tipo_documento TEXT NOT NULL,
        numero_documento TEXT NOT NULL,
        fecha_recepcion TEXT NOT NULL,
        fecha_limite TEXT DEFAULT '',
        asunto TEXT NOT NULL,
        area_responsable TEXT NOT NULL,
        referencia_digital TEXT DEFAULT '',
        estado TEXT NOT NULL DEFAULT 'Pendiente'
          CHECK(estado IN ('Pendiente','En revisión','Atendido','Archivado')),
        observaciones TEXT NOT NULL DEFAULT 'Sin observaciones',
        creado_en TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(codigo_proveedor) REFERENCES proveedores(codigo)
          ON UPDATE CASCADE ON DELETE RESTRICT,
        UNIQUE(tipo_documento, numero_documento)
    );
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registro_documento INTEGER NOT NULL,
        accion TEXT NOT NULL,
        fecha_hora TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(registro_documento) REFERENCES documentos(registro) ON DELETE CASCADE
    );
    """
    with obtener_conexion(ruta_db) as con:
        con.executescript(esquema)
