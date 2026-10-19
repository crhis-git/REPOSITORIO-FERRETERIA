"""Validaciones y normalización de entradas."""
from datetime import datetime

ESTADOS_DOCUMENTO = ("Pendiente", "En revisión", "Atendido", "Archivado")
AREAS = ("Compras", "Administración", "Almacén")


def validar_texto(valor, campo, maximo=250, obligatorio=True):
    texto = str(valor or "").strip()
    if obligatorio and not texto:
        raise ValueError(f"{campo} es obligatorio.")
    if len(texto) > maximo:
        raise ValueError(f"{campo} no puede superar {maximo} caracteres.")
    return texto


def validar_codigo_proveedor(valor):
    codigo = validar_texto(valor, "El código del proveedor", 30).upper()
    if not all(c.isalnum() or c in "_-" for c in codigo):
        raise ValueError("El código solo puede contener letras, números, guion y guion bajo.")
    return codigo


def validar_fecha(valor, obligatoria=True):
    texto = str(valor or "").strip()
    if not texto and not obligatoria:
        return ""
    if not texto:
        raise ValueError("La fecha es obligatoria.")
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            pass
    raise ValueError("Fecha no válida. Use DD/MM/AAAA o AAAA-MM-DD.")


def leer_fecha(valor):
    return validar_fecha(valor)


def validar_registro(valor):
    try:
        n = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ValueError("El número de registro debe ser un entero.") from None
    if n <= 0:
        raise ValueError("El número de registro debe ser mayor que cero.")
    return n


def validar_estado(valor):
    buscado = str(valor or "").strip().casefold()
    for estado in ESTADOS_DOCUMENTO:
        if estado.casefold() == buscado or estado.casefold().replace("ó", "o") == buscado.replace("ó", "o"):
            return estado
    raise ValueError("Estado no válido. Use: " + ", ".join(ESTADOS_DOCUMENTO))
