import tempfile
import unittest
from pathlib import Path
from database import inicializar_base_datos
from proveedores import registrar_proveedor
from datos_prueba import cargar_datos_prueba
from database import obtener_conexion
from documentos import (
    registrar_documento, consultar_documento, actualizar_estado, archivar_documento,
    buscar_documento_binaria, buscar_documentos_lineal, ordenar_burbuja,
    ordenar_insercion, reporte_area_estado, obtener_alertas,
)


class TestMesaDePartes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "test.db"
        inicializar_base_datos(self.db)
        registrar_proveedor("PR001", "Proveedor de prueba", ruta_db=self.db)
        self.reg = registrar_documento(
            "PR001", "Factura", "F-001", "10/10/2026", "22/10/2026",
            "Compra de herramientas", "Compras", "factura.pdf", self.db
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_registrar_consultar_y_historial(self):
        doc = consultar_documento(self.reg, self.db)
        self.assertEqual(doc["estado"], "Pendiente")
        self.assertEqual(doc["asunto"], "Compra de herramientas")
        self.assertTrue(doc["historial"])

    def test_busquedas(self):
        self.assertIsNotNone(buscar_documento_binaria(self.reg, self.db))
        self.assertEqual(len(buscar_documentos_lineal("herramientas", self.db)), 1)

    def test_actualizar_archivar_y_bloquear_cambios(self):
        actualizar_estado(self.reg, "Atendido", "Revisado", self.db)
        archivar_documento(self.reg, self.db)
        self.assertEqual(consultar_documento(self.reg, self.db)["estado"], "Archivado")
        with self.assertRaises(ValueError):
            actualizar_estado(self.reg, "Pendiente", "", self.db)

    def test_ordenamientos_y_reporte(self):
        docs = [consultar_documento(self.reg, self.db)]
        self.assertEqual(ordenar_burbuja(docs)[0]["registro"], self.reg)
        self.assertEqual(ordenar_insercion(docs)[0]["registro"], self.reg)
        self.assertEqual(reporte_area_estado(self.db)["Compras"]["Pendiente"], 1)

    def test_alerta_proximo_vencimiento(self):
        alertas = obtener_alertas(self.db, hoy="2026-10-20")
        self.assertEqual(len(alertas), 1)
        self.assertEqual(alertas[0]["tipo_alerta"], "PRÓXIMO A VENCER")


    def test_carga_datos_ficticios_completa_e_idempotente(self):
        db_demo = Path(self.temp.name) / "demo.db"
        self.assertTrue(cargar_datos_prueba(db_demo))
        with obtener_conexion(db_demo) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0], 10)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0], 25)
            self.assertGreaterEqual(con.execute("SELECT COUNT(*) FROM historial").fetchone()[0], 25)
        self.assertFalse(cargar_datos_prueba(db_demo))
        with obtener_conexion(db_demo) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0], 10)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0], 25)


if __name__ == "__main__":
    unittest.main()
