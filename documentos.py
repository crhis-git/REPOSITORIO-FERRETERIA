"""Registro, búsqueda, ordenamiento, seguimiento y reportes de documentos."""
import sqlite3
from datetime import date
from database import DB_PATH, obtener_conexion
from validaciones import (
    validar_codigo_proveedor, validar_fecha, validar_registro, validar_estado, validar_texto
)

SELECT_DOC = """
SELECT d.*, p.nombre AS nombre_proveedor
FROM documentos d JOIN proveedores p ON p.codigo=d.codigo_proveedor
"""


def registrar_documento(codigo_proveedor, tipo_documento, numero_documento,
                        fecha_recepcion, fecha_limite="", asunto="", area_responsable="",
                        referencia_digital="", ruta_db=DB_PATH):
    codigo = validar_codigo_proveedor(codigo_proveedor)
    tipo = validar_texto(tipo_documento, "El tipo de documento", 80)
    numero = validar_texto(numero_documento, "El número de documento", 80)
    fecha = validar_fecha(fecha_recepcion)
    limite = validar_fecha(fecha_limite, obligatoria=False)
    asunto = validar_texto(asunto, "El asunto", 300)
    area = validar_texto(area_responsable, "El área responsable", 120)
    referencia = validar_texto(referencia_digital, "La referencia digital", 300, False)
    if limite and limite < fecha:
        raise ValueError("La fecha límite no puede ser anterior a la fecha de recepción.")
    try:
        with obtener_conexion(ruta_db) as con:
            if not con.execute("SELECT 1 FROM proveedores WHERE codigo=?", (codigo,)).fetchone():
                raise ValueError(f"No existe un proveedor registrado con código {codigo}.")
            cur = con.execute("""
                INSERT INTO documentos
                (codigo_proveedor,tipo_documento,numero_documento,fecha_recepcion,fecha_limite,
                 asunto,area_responsable,referencia_digital)
                VALUES(?,?,?,?,?,?,?,?)
            """, (codigo, tipo, numero, fecha, limite, asunto, area, referencia))
            registro = cur.lastrowid
            con.execute("INSERT INTO historial(registro_documento,accion) VALUES(?,?)",
                        (registro, f"Documento creado en estado Pendiente el {fecha}"))
            return int(registro)
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise ValueError(f"Ya existe un documento de tipo '{tipo}' con número '{numero}'.") from None
        raise ValueError(f"No se pudo registrar el documento: {e}") from None


def consultar_documento(registro, ruta_db=DB_PATH):
    n = validar_registro(registro)
    with obtener_conexion(ruta_db) as con:
        fila = con.execute(SELECT_DOC + " WHERE d.registro=?", (n,)).fetchone()
        if not fila:
            return None
        doc = dict(fila)
        doc["historial"] = [dict(x) for x in con.execute(
            "SELECT accion,fecha_hora FROM historial WHERE registro_documento=? ORDER BY id", (n,))]
        return doc


def listar_documentos(ruta_db=DB_PATH):
    with obtener_conexion(ruta_db) as con:
        filas = con.execute(SELECT_DOC + " ORDER BY d.registro").fetchall()
    return [dict(f) for f in filas]


def buscar_documento_binaria(registro, ruta_db=DB_PATH):
    """Búsqueda binaria por registro; los datos se ordenan por registro antes de buscar."""
    n = validar_registro(registro)
    docs = sorted(listar_documentos(ruta_db), key=lambda d: d["registro"])
    izquierda, derecha = 0, len(docs) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        actual = docs[medio]["registro"]
        if actual == n:
            return consultar_documento(n, ruta_db)
        if actual < n:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return None


def buscar_documentos_lineal(texto, ruta_db=DB_PATH):
    q = str(texto or "").strip().casefold()
    if not q:
        return []
    campos = ("codigo_proveedor", "nombre_proveedor", "fecha_recepcion", "asunto",
              "tipo_documento", "numero_documento", "area_responsable", "estado")
    return [d for d in listar_documentos(ruta_db)
            if any(q in str(d.get(c, "")).casefold() for c in campos)]


def ordenar_burbuja(documentos):
    """Bubble Sort por fecha de recepción; devuelve una lista nueva."""
    arr = list(documentos)
    n = len(arr)
    for i in range(n - 1):
        cambio = False
        for j in range(n - i - 1):
            if arr[j]["fecha_recepcion"] > arr[j + 1]["fecha_recepcion"]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                cambio = True
        if not cambio:
            break
    return arr


def ordenar_insercion(documentos):
    """Insertion Sort por código de proveedor."""
    arr = list(documentos)
    for i in range(1, len(arr)):
        actual = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["codigo_proveedor"].casefold() > actual["codigo_proveedor"].casefold():
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = actual
    return arr


def actualizar_estado(registro, nuevo_estado, observacion="", ruta_db=DB_PATH):
    n = validar_registro(registro)
    estado = validar_estado(nuevo_estado)
    obs = validar_texto(observacion, "La observación", 500, False)
    with obtener_conexion(ruta_db) as con:
        fila = con.execute("SELECT estado FROM documentos WHERE registro=?", (n,)).fetchone()
        if not fila:
            raise ValueError(f"No existe el documento con registro {n}.")
        if fila["estado"] == "Archivado":
            raise ValueError("Un documento archivado no puede modificarse directamente.")
        con.execute("UPDATE documentos SET estado=?, observaciones=? WHERE registro=?",
                    (estado, obs or "Sin observaciones", n))
        con.execute("INSERT INTO historial(registro_documento,accion) VALUES(?,?)",
                    (n, f"Estado cambiado a {estado}. Observación: {obs or 'Sin observaciones'}"))
    return estado


def archivar_documento(registro, ruta_db=DB_PATH):
    n = validar_registro(registro)
    with obtener_conexion(ruta_db) as con:
        fila = con.execute("SELECT estado FROM documentos WHERE registro=?", (n,)).fetchone()
        if not fila:
            raise ValueError(f"No existe el documento con registro {n}.")
        if fila["estado"] == "Archivado":
            return
        con.execute("UPDATE documentos SET estado='Archivado' WHERE registro=?", (n,))
        con.execute("INSERT INTO historial(registro_documento,accion) VALUES(?,?)",
                    (n, "Documento archivado"))


def reporte_area_estado(ruta_db=DB_PATH):
    estados = ("Pendiente", "En revisión", "Atendido", "Archivado")
    matriz = {}
    with obtener_conexion(ruta_db) as con:
        filas = con.execute("SELECT area_responsable,estado,COUNT(*) cantidad FROM documentos GROUP BY area_responsable,estado").fetchall()
    for f in filas:
        matriz.setdefault(f["area_responsable"], {e: 0 for e in estados})
        matriz[f["area_responsable"]][f["estado"]] = f["cantidad"]
    return dict(sorted(matriz.items()))


def obtener_alertas(ruta_db=DB_PATH, hoy=None, dias_aviso=3):
    hoy = hoy or date.today()
    if isinstance(hoy, str):
        hoy = date.fromisoformat(hoy)
    docs = listar_documentos(ruta_db)
    alertas = []
    for d in docs:
        if d["estado"] in ("Atendido", "Archivado"):
            continue
        limite = d["fecha_limite"]
        tipo = None
        if not limite:
            if d["estado"] in ("Pendiente", "En revisión"):
                tipo = "PENDIENTE SIN FECHA LÍMITE"
        else:
            fecha = date.fromisoformat(limite)
            dias = (fecha - hoy).days
            if dias < 0:
                tipo = "VENCIDO"
            elif dias <= dias_aviso:
                tipo = "PRÓXIMO A VENCER" if dias > 0 else "VENCE HOY"
            elif d["estado"] in ("Pendiente", "En revisión"):
                tipo = "PENDIENTE"
        if tipo:
            d["tipo_alerta"] = tipo
            alertas.append(d)
    return alertas
