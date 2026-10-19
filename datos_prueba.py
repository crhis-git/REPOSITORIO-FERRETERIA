"""Carga opcional e idempotente de datos ficticios para probar el sistema.

Uso desde la carpeta del proyecto:
    python datos_prueba.py

No elimina ni modifica registros existentes: añade únicamente los que falten.
Todos los RUC, contactos, direcciones y documentos de esta colección son ficticios.
"""
from datetime import date, timedelta

from database import DB_PATH, inicializar_base_datos, obtener_conexion


PROVEEDORES_PRUEBA = [
    ("PR001", "Ferretería El Norte S.A.C.", "FICTICIO-PR001", "900111001", "ventas@elnorte.example.com", "Av. Los Talleres 101, Trujillo"),
    ("PR002", "Distribuidora Andina S.R.L.", "FICTICIO-PR002", "900111002", "contacto@andina.example.com", "Jr. Las Herramientas 202, Trujillo"),
    ("PR003", "Suministros Industriales Lázaro S.A.C.", "FICTICIO-PR003", "900111003", "ventas@lazaro.example.com", "Av. Industrial 303, Trujillo"),
    ("PR004", "Metalúrgica del Pacífico S.R.L.", "FICTICIO-PR004", "900111004", "pedidos@metalpacifico.example.com", "Calle Los Metales 404, Trujillo"),
    ("PR005", "Tornillos y Accesorios del Norte E.I.R.L.", "FICTICIO-PR005", "900111005", "atencion@tornillosnorte.example.com", "Av. América 505, Trujillo"),
    ("PR006", "Materiales La Esperanza S.A.C.", "FICTICIO-PR006", "900111006", "ventas@laesperanza.example.com", "Calle Progreso 606, La Esperanza"),
    ("PR007", "Herramientas del Valle S.R.L.", "FICTICIO-PR007", "900111007", "pedidos@herramientasvalle.example.com", "Av. Valle 707, Trujillo"),
    ("PR008", "Comercializadora Santa Rosa S.A.C.", "FICTICIO-PR008", "900111008", "contacto@santarosa.example.com", "Jr. Santa Rosa 808, Trujillo"),
    ("PR009", "Equipos y Seguridad Industrial S.A.C.", "FICTICIO-PR009", "900111009", "seguridad@esi.example.com", "Parque Industrial, lote 9, Trujillo"),
    ("PR010", "Servicios Logísticos Trujillo S.R.L.", "FICTICIO-PR010", "900111010", "operaciones@logisticatrujillo.example.com", "Av. Logística 1010, Trujillo"),
]

# Campos: proveedor, tipo, número, días desde hoy para recepción,
# días desde hoy para fecha límite (None = sin fecha), asunto, área,
# estado, observaciones y referencia digital.
DOCUMENTOS_PRUEBA = [
    ("PR001", "Cotización", "COT-2026-001", -5, 2, "Cotización de materiales eléctricos", "Compras", "Pendiente", "Esperando aprobación del área", "pruebas/cotizacion_001.pdf"),
    ("PR002", "Factura", "F001-2026-0045", -20, -5, "Compra de taladros y brocas", "Administración", "Pendiente", "Revisar comprobante vencido", "pruebas/factura_0045.pdf"),
    ("PR003", "Guía de remisión", "GR-2026-011", -15, -1, "Entrega de perfiles metálicos", "Almacén", "En revisión", "Verificar cantidades recibidas", "pruebas/guia_011.pdf"),
    ("PR004", "Orden de compra", "OC-2026-018", -3, 0, "Reposición de discos de corte", "Compras", "Pendiente", "Vence hoy: coordinar aprobación", "pruebas/orden_018.pdf"),
    ("PR005", "Solicitud", "SOL-2026-007", -1, 1, "Solicitud de guantes de seguridad", "Almacén", "Pendiente", "Entrega solicitada con prioridad", "pruebas/solicitud_007.pdf"),
    ("PR006", "Factura", "F002-2026-0093", -10, 4, "Compra de herramientas manuales", "Administración", "En revisión", "Validación contable en curso", "pruebas/factura_0093.pdf"),
    ("PR007", "Cotización", "COT-2026-002", -8, 10, "Cotización de pinturas industriales", "Compras", "Atendido", "Cotización revisada y respondida", "pruebas/cotizacion_002.pdf"),
    ("PR008", "Reclamo", "REC-2026-002", -12, 3, "Reclamo por producto incompleto", "Administración", "Pendiente", "Falta respuesta del proveedor", "pruebas/reclamo_002.pdf"),
    ("PR009", "Nota de crédito", "NC-2026-004", -7, None, "Regularización de una factura", "Administración", "Pendiente", "Documento sin fecha límite", "pruebas/nota_credito_004.pdf"),
    ("PR010", "Informe", "INF-2026-005", -6, 7, "Informe de entrega mensual", "Almacén", "En revisión", "Comparar con el registro de almacén", "pruebas/informe_005.pdf"),
    ("PR001", "Orden de compra", "OC-2026-019", -18, -3, "Compra de cables y conectores", "Compras", "Archivado", "Expediente cerrado", "pruebas/orden_019.pdf"),
    ("PR002", "Solicitud", "SOL-2026-008", -2, None, "Solicitud de mantenimiento de estantes", "Almacén", "Pendiente", "Pendiente de asignación de fecha", "pruebas/solicitud_008.pdf"),
    ("PR003", "Factura", "F001-2026-0046", -4, 2, "Compra de tubos de PVC", "Administración", "Atendido", "Pago registrado en el sistema de prueba", "pruebas/factura_0046.pdf"),
    ("PR004", "Carta", "CAR-2026-003", -9, -1, "Carta de actualización de precios", "Administración", "En revisión", "Solicitar visto bueno del responsable", "pruebas/carta_003.pdf"),
    ("PR005", "Guía de remisión", "GR-2026-012", -2, 6, "Entrega de mascarillas y lentes", "Almacén", "Pendiente", "Contar unidades al recibir", "pruebas/guia_012.pdf"),
    ("PR006", "Reclamo", "REC-2026-003", -5, 0, "Reclamo por herramientas defectuosas", "Administración", "Pendiente", "Vence hoy: preparar respuesta", "pruebas/reclamo_003.pdf"),
    ("PR007", "Orden de compra", "OC-2026-020", -17, -10, "Compra anterior de llaves mixtas", "Compras", "Atendido", "Solicitud atendida", "pruebas/orden_020.pdf"),
    ("PR008", "Factura", "F003-2026-0012", -1, 14, "Compra de adhesivos y selladores", "Administración", "Pendiente", "Factura recién recibida", "pruebas/factura_0012.pdf"),
    ("PR009", "Cotización", "COT-2026-003", -4, 2, "Cotización de equipos de protección", "Compras", "Archivado", "Proceso de cotización concluido", "pruebas/cotizacion_003.pdf"),
    ("PR010", "Solicitud", "SOL-2026-009", -13, 3, "Solicitud de transporte de mercadería", "Almacén", "En revisión", "Confirmar fecha de despacho", "pruebas/solicitud_009.pdf"),
    ("PR001", "Factura", "F001-2026-0047", -7, -2, "Compra de extensiones eléctricas", "Administración", "Pendiente", "Revisar documento fuera de plazo", "pruebas/factura_0047.pdf"),
    ("PR002", "Guía de remisión", "GR-2026-013", -1, 1, "Entrega parcial de pernos", "Almacén", "Atendido", "Entrega verificada", "pruebas/guia_013.pdf"),
    ("PR003", "Informe", "INF-2026-006", -3, None, "Informe de inspección de mercadería", "Almacén", "En revisión", "Pendiente de adjuntar evidencia", "pruebas/informe_006.pdf"),
    ("PR004", "Nota de crédito", "NC-2026-005", -5, 0, "Nota de crédito por diferencia de precio", "Administración", "Archivado", "Expediente archivado", "pruebas/nota_credito_005.pdf"),
    ("PR005", "Carta", "CAR-2026-004", -4, 20, "Carta de condiciones de garantía", "Compras", "Pendiente", "Leer condiciones antes de la compra", "pruebas/carta_004.pdf"),
]


def fecha_relativa(dias):
    """Devuelve una fecha ISO relativa al día en que se cargan las pruebas."""
    return (date.today() + timedelta(days=dias)).isoformat()


def cargar_datos_prueba(ruta_db=DB_PATH):
    """Añade la colección de demostración sin duplicar ni borrar datos previos.

    Retorna True si insertó al menos un proveedor o documento; si la colección
    ya estaba cargada, retorna False.
    """
    inicializar_base_datos(ruta_db)
    proveedores_agregados = 0
    documentos_agregados = 0

    with obtener_conexion(ruta_db) as con:
        for proveedor in PROVEEDORES_PRUEBA:
            cur = con.execute(
                """INSERT OR IGNORE INTO proveedores
                   (codigo,nombre,ruc,telefono,correo,direccion)
                   VALUES(?,?,?,?,?,?)""",
                proveedor,
            )
            proveedores_agregados += cur.rowcount

        for (codigo, tipo, numero, dias_recepcion, dias_limite, asunto, area,
             estado, observaciones, referencia) in DOCUMENTOS_PRUEBA:
            fecha_recepcion = fecha_relativa(dias_recepcion)
            fecha_limite = fecha_relativa(dias_limite) if dias_limite is not None else ""
            cur = con.execute(
                """INSERT OR IGNORE INTO documentos
                   (codigo_proveedor,tipo_documento,numero_documento,fecha_recepcion,
                    fecha_limite,asunto,area_responsable,referencia_digital,estado,observaciones)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (codigo, tipo, numero, fecha_recepcion, fecha_limite, asunto, area,
                 referencia, estado, observaciones),
            )
            if cur.rowcount == 1:
                documentos_agregados += 1
                registro = cur.lastrowid
                con.execute(
                    "INSERT INTO historial(registro_documento,accion) VALUES(?,?)",
                    (registro, f"Documento ficticio de prueba creado en estado {estado}"),
                )

        total_proveedores = con.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0]
        total_documentos = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]

    return bool(proveedores_agregados or documentos_agregados)


if __name__ == "__main__":
    hubo_cambios = cargar_datos_prueba()
    if hubo_cambios:
        print("Colección de datos ficticios cargada correctamente.")
    else:
        print("Los datos ficticios ya estaban cargados; no se duplicó ningún registro.")
    with obtener_conexion(DB_PATH) as con:
        cantidad_proveedores = con.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0]
        cantidad_documentos = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    print(f"Proveedores en la base de datos: {cantidad_proveedores}")
    print(f"Documentos en la base de datos: {cantidad_documentos}")
    print("Nota: todos los datos de demostración son inventados.")
