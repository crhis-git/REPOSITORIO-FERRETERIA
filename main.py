"""Punto de entrada del Sistema de Mesa de Partes - Ferretería Lázaro."""
from datetime import date
from database import DB_PATH, inicializar_base_datos
from proveedores import registrar_proveedor, listar_proveedores
from documentos import (
    registrar_documento, consultar_documento, buscar_documentos_lineal,
    buscar_documento_binaria, listar_documentos, actualizar_estado,
    archivar_documento, ordenar_burbuja, ordenar_insercion,
    reporte_area_estado, obtener_alertas,
)
from validaciones import leer_fecha, ESTADOS_DOCUMENTO, AREAS


def pedir(texto):
    return input(texto).strip()


def mostrar_documento(d):
    print("\n" + "-" * 60)
    print(f"Registro: {d['registro']} | Proveedor: {d['codigo_proveedor']} - {d.get('nombre_proveedor', '')}")
    print(f"Tipo/Número: {d['tipo_documento']} / {d['numero_documento']}")
    print(f"Recepción: {d['fecha_recepcion']} | Límite: {d['fecha_limite'] or 'No indicada'}")
    print(f"Asunto: {d['asunto']}")
    print(f"Área: {d['area_responsable']} | Estado: {d['estado']}")
    print(f"Referencia digital: {d['referencia_digital'] or 'No indicada'}")
    print(f"Observaciones: {d['observaciones']}")
    print("Historial:")
    for h in d.get("historial", []):
        print(f"  - {h['fecha_hora']}: {h['accion']}")
    print("-" * 60)


def opcion_proveedor():
    print("\n--- REGISTRAR PROVEEDOR ---")
    codigo = pedir("Código (ej. PR001): ")
    nombre = pedir("Nombre o razón social: ")
    ruc = pedir("RUC (opcional): ")
    telefono = pedir("Teléfono (opcional): ")
    correo = pedir("Correo (opcional): ")
    direccion = pedir("Dirección (opcional): ")
    registrar_proveedor(codigo, nombre, ruc, telefono, correo, direccion)
    print("Proveedor registrado correctamente.")


def opcion_documento():
    proveedores = listar_proveedores()
    if not proveedores:
        print("Primero debe registrar un proveedor.")
        return
    print("\n--- PROVEEDORES REGISTRADOS ---")
    for p in proveedores:
        print(f"{p['codigo']} - {p['nombre']}")
    codigo = pedir("Código del proveedor: ")
    tipo = pedir("Tipo de documento (Cotización/Factura/Orden/Otro): ")
    numero = pedir("Número del documento: ")
    fecha = leer_fecha(pedir("Fecha de recepción (DD/MM/AAAA o AAAA-MM-DD): "))
    limite_txt = pedir("Fecha límite (Enter si no aplica): ")
    limite = leer_fecha(limite_txt) if limite_txt else ""
    asunto = pedir("Asunto: ")
    print("Áreas sugeridas:", ", ".join(AREAS))
    area = pedir("Área responsable: ")
    referencia = pedir("Referencia digital/ruta del archivo (opcional): ")
    registro = registrar_documento(codigo, tipo, numero, fecha, limite, asunto, area, referencia)
    print(f"Documento registrado. Número de registro: {registro}. Estado inicial: Pendiente.")


def opcion_consultar():
    print("1. Búsqueda binaria por número de registro")
    print("2. Búsqueda lineal por proveedor, fecha o asunto")
    op = pedir("Seleccione: ")
    if op == "1":
        registro = pedir("Número de registro: ")
        d = buscar_documento_binaria(registro)
        if d:
            mostrar_documento(d)
        else:
            print("Documento no encontrado.")
    elif op == "2":
        texto = pedir("Texto a buscar: ")
        resultados = buscar_documentos_lineal(texto)
        if not resultados:
            print("No se encontraron documentos.")
        for d in resultados:
            mostrar_documento(d)
    else:
        print("Opción no válida.")


def opcion_listar_ordenados():
    print("1. Ordenar por fecha de recepción (Burbuja)")
    print("2. Ordenar por código de proveedor (Inserción)")
    op = pedir("Seleccione: ")
    if op == "1":
        docs = ordenar_burbuja(listar_documentos())
    elif op == "2":
        docs = ordenar_insercion(listar_documentos())
    else:
        print("Opción no válida.")
        return
    if not docs:
        print("No hay documentos registrados.")
    for d in docs:
        print(f"Reg. {d['registro']} | {d['fecha_recepcion']} | {d['codigo_proveedor']} | "
              f"{d['asunto']} | {d['estado']}")


def opcion_estado():
    registro = pedir("Número de registro: ")
    d = consultar_documento(registro)
    if not d:
        print("Documento no encontrado.")
        return
    if d["estado"] == "Archivado":
        print("Un documento archivado no puede modificarse directamente.")
        return
    for i, estado in enumerate(ESTADOS_DOCUMENTO[:3], 1):
        print(f"{i}. {estado}")
    op = pedir("Nuevo estado: ")
    if op not in ("1", "2", "3"):
        print("Estado no válido.")
        return
    observacion = pedir("Observación de seguimiento (opcional): ")
    actualizar_estado(registro, ESTADOS_DOCUMENTO[int(op)-1], observacion)
    print("Estado, observaciones e historial actualizados.")


def opcion_archivar():
    registro = pedir("Número de registro: ")
    d = consultar_documento(registro)
    if not d:
        print("Documento no encontrado.")
        return
    if d["estado"] != "Atendido":
        confirmar = pedir("El documento no está Atendido. ¿Desea archivarlo de todos modos? (s/n): ").lower()
        if confirmar != "s":
            print("Operación cancelada.")
            return
    archivar_documento(registro)
    print("Documento archivado correctamente.")


def opcion_reporte():
    matriz = reporte_area_estado()
    estados = ["Pendiente", "En revisión", "Atendido", "Archivado"]
    print("\n--- MATRIZ ÁREA x ESTADO ---")
    print(f"{'Área':<22}" + "".join(f"{e:<16}" for e in estados) + f"{'Total':<8}")
    for area, valores in matriz.items():
        print(f"{area:<22}" + "".join(f"{valores[e]:<16}" for e in estados) + f"{sum(valores.values()):<8}")
    print("\n--- ALERTAS DE DOCUMENTOS ---")
    alertas = obtener_alertas()
    if not alertas:
        print("No hay documentos pendientes, próximos a vencer o vencidos.")
    for d in alertas:
        print(f"[{d['tipo_alerta']}] Reg. {d['registro']} | {d['asunto']} | "
              f"Límite: {d['fecha_limite'] or 'sin fecha'} | Área: {d['area_responsable']}")


def menu():
    inicializar_base_datos()
    print(f"Base de datos: {DB_PATH}")
    acciones = {
        "1": opcion_proveedor, "2": opcion_documento, "3": opcion_consultar,
        "4": opcion_listar_ordenados, "5": opcion_estado, "6": opcion_archivar,
        "7": opcion_reporte,
    }
    while True:
        print("\n" + "=" * 54)
        print(" SISTEMA DE MESA DE PARTES - FERRETERÍA LÁZARO")
        print("=" * 54)
        print("1. Registrar proveedor")
        print("2. Registrar documento")
        print("3. Consultar documento (lineal/binaria)")
        print("4. Listar documentos ordenados (burbuja/inserción)")
        print("5. Actualizar estado y observaciones")
        print("6. Archivar documento")
        print("7. Reporte matriz Área x Estado y alertas")
        print("8. Listar todos los documentos")
        print("9. Salir")
        op = pedir("Seleccione una opción: ")
        try:
            if op in acciones:
                acciones[op]()
            elif op == "8":
                docs = listar_documentos()
                if not docs:
                    print("No hay documentos registrados.")
                for d in docs:
                    mostrar_documento(d)
            elif op == "9":
                print("Programa finalizado. Los datos se conservaron en SQLite.")
                break
            else:
                print("Opción no válida.")
        except (ValueError, RuntimeError, OSError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma finalizado.")
