"""
Tests para TableFormatter (RF03: Visualización en tablas)
y el sistema de ayuda REPL (RF04: Sistema de ayuda)
"""

import sys
import os
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from formatters.table_formatter import TableFormatter
from cli.repl import REPL


class TestTableFormatter(unittest.TestCase):
    """Tests para RF03 - Visualización de resultados en tablas"""

    def setUp(self):
        self.formatter = TableFormatter()

    def test_print_table_with_data(self):
        """RF03 - print_table no debe lanzar excepciones con datos válidos"""
        columns = ['id', 'nombre', 'edad']
        rows = [
            [1, 'Alice', 30],
            [2, 'Bob', 25],
        ]
        # No debe lanzar excepción
        try:
            self.formatter.print_table(columns, rows)
        except Exception as e:
            self.fail(f"print_table lanzó excepción inesperada: {e}")

    def test_print_table_empty_columns(self):
        """RF03 - print_table con columnas vacías no debe lanzar excepción"""
        try:
            self.formatter.print_table([], [])
        except Exception as e:
            self.fail(f"print_table lanzó excepción con columnas vacías: {e}")

    def test_print_table_single_column(self):
        """RF03 - print_table debe funcionar con una sola columna"""
        try:
            self.formatter.print_table(['nombre'], [['Alice'], ['Bob']])
        except Exception as e:
            self.fail(f"print_table lanzó excepción con una columna: {e}")

    def test_print_table_string_conversion(self):
        """RF03 - print_table debe manejar distintos tipos de datos"""
        columns = ['id', 'activo', 'precio']
        rows = [[1, True, 9.99], [2, False, None]]
        try:
            self.formatter.print_table(columns, rows)
        except Exception as e:
            self.fail(f"print_table falló con tipos mixtos: {e}")

    def test_formatter_has_console(self):
        """RF03 - TableFormatter debe tener una consola Rich configurada"""
        self.assertIsNotNone(self.formatter.console)


class TestREPLHelpSystem(unittest.TestCase):
    """Tests para RF04 - Sistema de ayuda"""

    def test_help_command_relacional(self):
        """RF04 - El comando 'help' en modo relacional no debe lanzar excepción"""
        repl = REPL(mode='rel')
        try:
            repl._help()
        except Exception as e:
            self.fail(f"_help() lanzó excepción en modo relacional: {e}")

    def test_help_command_nosql(self):
        """RF04 - El comando 'help' en modo NoSQL no debe lanzar excepción"""
        repl = REPL(mode='nosql')
        try:
            repl._help()
        except Exception as e:
            self.fail(f"_help() lanzó excepción en modo nosql: {e}")

    def test_execute_help_dispatches_correctly(self):
        """RF04 - execute('help') debe llamar a _help"""
        repl = REPL(mode='rel')
        with patch.object(repl, '_help') as mock_help:
            repl.execute('help')
            mock_help.assert_called_once()

    def test_execute_exit_stops_loop(self):
        """RF04 - execute('exit') debe detener el bucle"""
        repl = REPL(mode='rel')
        repl.execute('exit')
        self.assertFalse(repl.running)

    def test_execute_status_no_connection(self):
        """RF04 - execute('status') sin conexión no debe lanzar excepción"""
        repl = REPL(mode='rel')
        try:
            repl.execute('status')
        except Exception as e:
            self.fail(f"execute('status') lanzó excepción sin conexión: {e}")

    def test_execute_unknown_command_shows_error(self):
        """RF04 - Comando desconocido sin conexión debe mostrar error apropiado"""
        repl = REPL(mode='rel')
        # No debe lanzar excepción, solo mostrar error
        try:
            repl.execute('comando_invalido')
        except Exception as e:
            self.fail(f"Comando inválido lanzó excepción: {e}")

    def test_repl_default_mode_is_rel(self):
        """RF04 - El modo por defecto del REPL debe ser 'rel'"""
        repl = REPL()
        self.assertEqual(repl.mode, 'rel')

    def test_repl_nosql_mode(self):
        """RF04 - El REPL debe aceptar el modo 'nosql'"""
        repl = REPL(mode='nosql')
        self.assertEqual(repl.mode, 'nosql')

    def test_connect_sqlite_integration(self):
        """RF01+RF04 - connect sqlite debe establecer conexión correctamente"""
        repl = REPL(mode='rel')
        repl.execute('connect sqlite :memory:')
        self.assertIsNotNone(repl.connector)
        self.assertTrue(repl.connector.is_connected)

    def test_disconnect_command(self):
        """RF01+RF04 - disconnect debe cerrar la conexión activa"""
        repl = REPL(mode='rel')
        repl.execute('connect sqlite :memory:')
        repl.execute('disconnect')
        # Después de disconnect el connector debe ser None
        self.assertIsNone(repl.connector)

    def test_prompt_without_connection(self):
        """RF04 - El prompt sin conexión debe retornar el formato base"""
        repl = REPL(mode='rel')
        prompt = repl._get_prompt()
        self.assertIn('dbcli-rel', prompt)

    def test_prompt_with_connection(self):
        """RF04 - El prompt con conexión debe incluir el tipo de BD"""
        repl = REPL(mode='rel')
        repl.execute('connect sqlite :memory:')
        prompt = repl._get_prompt()
        self.assertIn('sqlite', prompt.lower())

    def test_export_without_results_warns(self):
        """RF04 - export sin resultados previos no debe lanzar excepción"""
        repl = REPL(mode='rel')
        try:
            repl.execute('export resultados.csv')
        except Exception as e:
            self.fail(f"export sin resultados lanzó excepción: {e}")


class TestREPLSQLOperations(unittest.TestCase):
    """Tests de integración para operaciones SQL a través del REPL"""

    def setUp(self):
        self.repl = REPL(mode='rel')
        self.repl.execute('connect sqlite :memory:')
        self.repl.execute(
            'create table empleados (id INTEGER PRIMARY KEY, nombre TEXT, salario REAL)'
        )

    def tearDown(self):
        if self.repl.connector and self.repl.connector.is_connected:
            self.repl.execute('disconnect')

    def test_select_through_repl(self):
        """RF02 - SELECT ejecutado a través del REPL no debe lanzar excepción"""
        try:
            self.repl.execute('select * from empleados')
        except Exception as e:
            self.fail(f"SELECT lanzó excepción: {e}")

    def test_insert_through_repl(self):
        """RF02 - INSERT ejecutado a través del REPL no debe lanzar excepción"""
        try:
            self.repl.execute(
                "insert into empleados (nombre, salario) values ('Carlos', 3000)"
            )
        except Exception as e:
            self.fail(f"INSERT lanzó excepción: {e}")

    def test_show_tables_through_repl(self):
        """RF02 - 'show tables' a través del REPL no debe lanzar excepción"""
        try:
            self.repl.execute('show tables')
        except Exception as e:
            self.fail(f"show tables lanzó excepción: {e}")


if __name__ == "__main__":
    unittest.main()
