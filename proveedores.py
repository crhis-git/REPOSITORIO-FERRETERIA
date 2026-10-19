"""Operaciones de registro y consulta de proveedores."""
import sqlite3
from database import DB_PATH, obtener_conexion
from validaciones import validar_codigo_proveedor, validar_texto


def registrar_proveedor(codigo, nombre, ruc="", telefono="", correo="", direccion="", ruta_db=DB_PATH):
    codigo = validar_codigo_proveedor(codigo)
    nombre = validar_texto(nombre, "El nombre o razón social", 150)
    ruc = validar_texto(ruc, "RUC", 20, False)
    telefono = validar_texto(telefono, "Teléfono", 30, False)
    correo = validar_texto(correo, "Correo", 120, False)
    direccion = validar_texto(direccion, "Dirección", 200, False)
    try:
        with obtener_conexion(ruta_db) as con:
            con.execute(
                "INSERT INTO proveedores(codigo,nombre,ruc,telefono,correo,direccion) VALUES(?,?,?,?,?,?)",
                (codigo, nombre, ruc, telefono, correo, direccion))
    except sqlite3.IntegrityError:
        raise ValueError(f"Ya existe un proveedor con el código {codigo}.") from None


def obtener_proveedor(codigo, ruta_db=DB_PATH):
    codigo = validar_codigo_proveedor(codigo)
    with obtener_conexion(ruta_db) as con:
        fila = con.execute("SELECT * FROM proveedores WHERE codigo=?", (codigo,)).fetchone()
    return dict(fila) if fila else None


def listar_proveedores(ruta_db=DB_PATH):
    with obtener_conexion(ruta_db) as con:
        filas = con.execute("SELECT * FROM proveedores ORDER BY codigo").fetchall()
    return [dict(f) for f in filas]
