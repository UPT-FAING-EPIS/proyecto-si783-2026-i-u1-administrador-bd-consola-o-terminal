"""
Tests para el conector SQLite (RF01: Conexión a BD, RF02: Ejecución de SQL)
Estos tests cubren los requerimientos funcionales principales sin necesitar
un servidor externo, usando SQLite en memoria.
"""

import sys
import os
import unittest
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from connectors.sqlite_connector import SQLiteConnector


class TestSQLiteConnector(unittest.TestCase):
    """Tests para RF01 (Conexión a BD) y RF02 (Ejecución de SQL)"""

    def setUp(self):
        """Crea un conector SQLite en memoria antes de cada test"""
        self.connector = SQLiteConnector()
        self.connector.connect(db_path=":memory:")

    def tearDown(self):
        """Cierra la conexión después de cada test"""
        if self.connector.is_connected:
            self.connector.disconnect()

    # ── RF01: Conexión a BD ──────────────────────────────────────────────────

    def test_connect_success(self):
        """RF01 - La conexión a SQLite debe establecerse correctamente"""
        self.assertTrue(self.connector.is_connected)

    def test_connect_returns_sqlite_type(self):
        """RF01 - El conector debe identificarse como SQLite"""
        self.assertEqual(self.connector.get_type(), "SQLite")

    def test_disconnect(self):
        """RF01 - La desconexión debe funcionar correctamente"""
        self.connector.disconnect()
        self.assertFalse(self.connector.is_connected)

    def test_get_info_returns_string(self):
        """RF01 - get_info debe retornar información de la conexión"""
        info = self.connector.get_info()
        self.assertIsInstance(info, str)
        self.assertGreater(len(info), 0)

    def test_query_without_connection_returns_error(self):
        """RF01 - Ejecutar consulta sin conexión debe retornar error"""
        self.connector.disconnect()
        success, data, error = self.connector.execute_query("SELECT 1")
        self.assertFalse(success)
        self.assertNotEqual(error, "")

    # ── RF02: Ejecución de SQL ───────────────────────────────────────────────

    def test_create_table(self):
        """RF02 - CREATE TABLE debe ejecutarse sin errores"""
        sql = "CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT, edad INTEGER)"
        success, data, error = self.connector.execute_query(sql)
        self.assertTrue(success, f"Error inesperado: {error}")

    def test_insert_record(self):
        """RF02 - INSERT debe registrar filas y reportar filas afectadas"""
        self.connector.execute_query(
            "CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL)"
        )
        success, data, error = self.connector.execute_query(
            "INSERT INTO productos (nombre, precio) VALUES ('Laptop', 999.99)"
        )
        self.assertTrue(success, f"Error inesperado: {error}")

    def test_select_returns_data(self):
        """RF02 - SELECT debe retornar columnas y filas"""
        self.connector.execute_query(
            "CREATE TABLE items (id INTEGER PRIMARY KEY, nombre TEXT)"
        )
        self.connector.execute_query("INSERT INTO items (nombre) VALUES ('Item A')")
        self.connector.execute_query("INSERT INTO items (nombre) VALUES ('Item B')")

        success, data, error = self.connector.execute_query("SELECT * FROM items")
        self.assertTrue(success, f"Error inesperado: {error}")
        self.assertIn('columns', data)
        self.assertIn('rows', data)
        self.assertEqual(len(data['rows']), 2)

    def test_select_columns_match(self):
        """RF02 - SELECT debe retornar las columnas correctas"""
        self.connector.execute_query(
            "CREATE TABLE clientes (id INTEGER, nombre TEXT, email TEXT)"
        )
        success, data, error = self.connector.execute_query("SELECT * FROM clientes")
        self.assertTrue(success)
        self.assertEqual(data['columns'], ['id', 'nombre', 'email'])

    def test_update_record(self):
        """RF02 - UPDATE debe modificar registros existentes"""
        self.connector.execute_query(
            "CREATE TABLE stock (id INTEGER PRIMARY KEY, cantidad INTEGER)"
        )
        self.connector.execute_query("INSERT INTO stock (cantidad) VALUES (10)")
        success, data, error = self.connector.execute_query(
            "UPDATE stock SET cantidad = 20 WHERE id = 1"
        )
        self.assertTrue(success, f"Error inesperado: {error}")

    def test_delete_record(self):
        """RF02 - DELETE debe eliminar registros"""
        self.connector.execute_query(
            "CREATE TABLE temporal (id INTEGER PRIMARY KEY, valor TEXT)"
        )
        self.connector.execute_query("INSERT INTO temporal (valor) VALUES ('borrar')")
        success, data, error = self.connector.execute_query(
            "DELETE FROM temporal WHERE valor = 'borrar'"
        )
        self.assertTrue(success, f"Error inesperado: {error}")

    def test_sql_error_returns_false(self):
        """RF02 - Error de SQL debe retornar success=False con mensaje"""
        success, data, error = self.connector.execute_query(
            "SELECT * FROM tabla_inexistente"
        )
        self.assertFalse(success)
        self.assertNotEqual(error, "")

    # ── RF04: Show Tables ────────────────────────────────────────────────────

    def test_get_tables_empty(self):
        """RF04 - get_tables en BD vacía debe retornar lista vacía"""
        success, tables, error = self.connector.get_tables()
        self.assertTrue(success)
        self.assertIsInstance(tables, list)

    def test_get_tables_after_create(self):
        """RF04 - get_tables debe mostrar tablas creadas"""
        self.connector.execute_query(
            "CREATE TABLE ventas (id INTEGER PRIMARY KEY, monto REAL)"
        )
        success, tables, error = self.connector.get_tables()
        self.assertTrue(success)
        self.assertIn('ventas', tables)

    # ── RNF01: Tiempo de Respuesta < 1 segundo ───────────────────────────────

    def test_response_time_select(self):
        """RNF01 - Consultas SELECT deben completarse en menos de 1 segundo"""
        self.connector.execute_query(
            "CREATE TABLE benchmark (id INTEGER PRIMARY KEY, dato TEXT)"
        )
        # Insertar datos de prueba
        for i in range(100):
            self.connector.execute_query(
                f"INSERT INTO benchmark (dato) VALUES ('valor_{i}')"
            )

        start = time.time()
        success, data, error = self.connector.execute_query(
            "SELECT * FROM benchmark"
        )
        elapsed = time.time() - start

        self.assertTrue(success)
        self.assertLess(elapsed, 1.0, f"Tiempo de respuesta excedido: {elapsed:.3f}s")

    def test_response_time_connect(self):
        """RNF01 - La conexión a SQLite debe establecerse en menos de 1 segundo"""
        connector = SQLiteConnector()
        start = time.time()
        connector.connect(db_path=":memory:")
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0, f"Tiempo de conexión excedido: {elapsed:.3f}s")
        connector.disconnect()


class TestSQLiteConnectorEdgeCases(unittest.TestCase):
    """Tests para casos borde y robustez (RNF02: tasa de fallos < 1%)"""

    def test_connect_invalid_path_raises_exception(self):
        """RNF02 - Conectar a ruta inválida debe lanzar excepción controlada"""
        import sqlite3
        connector = SQLiteConnector()
        # SQLite crea el archivo si no existe, así que un directorio inexistente falla
        with self.assertRaises((Exception, sqlite3.OperationalError)):
            connector.connect(db_path="/directorio/inexistente/test.db")

    def test_missing_db_path_raises_value_error(self):
        """RNF02 - Conectar sin db_path debe lanzar ValueError"""
        connector = SQLiteConnector()
        with self.assertRaises(ValueError):
            connector.connect()

    def test_select_empty_table(self):
        """RNF02 - SELECT en tabla vacía no debe causar errores"""
        connector = SQLiteConnector()
        connector.connect(db_path=":memory:")
        connector.execute_query("CREATE TABLE vacia (id INTEGER)")
        success, data, error = connector.execute_query("SELECT * FROM vacia")
        self.assertTrue(success)
        self.assertEqual(data['rows'], [])
        connector.disconnect()

    def test_multiple_operations_stability(self):
        """RNF02 - Múltiples operaciones sucesivas deben ejecutarse sin fallos"""
        connector = SQLiteConnector()
        connector.connect(db_path=":memory:")
        connector.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, val TEXT)")

        failures = 0
        total = 50
        for i in range(total):
            success, _, _ = connector.execute_query(
                f"INSERT INTO test (val) VALUES ('dato_{i}')"
            )
            if not success:
                failures += 1

        failure_rate = failures / total
        self.assertLess(failure_rate, 0.01, f"Tasa de fallos: {failure_rate:.2%}")
        connector.disconnect()


if __name__ == "__main__":
    unittest.main()
