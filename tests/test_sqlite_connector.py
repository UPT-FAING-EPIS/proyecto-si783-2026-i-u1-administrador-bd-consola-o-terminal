import pytest
import sqlite3
import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from connectors.sqlite_connector import SQLiteConnector

def test_sqlite_connect_missing_db_path():
    connector = SQLiteConnector()
    with pytest.raises(ValueError, match="Se requiere db_path"):
        connector.connect()

def test_sqlite_connect_success():
    connector = SQLiteConnector()
    result = connector.connect(db_path=":memory:")
    assert result is True
    assert connector.is_connected is True
    assert connector.db_path == ":memory:"
    connector.disconnect()

def test_sqlite_disconnect():
    connector = SQLiteConnector()
    connector.connect(db_path=":memory:")
    result = connector.disconnect()
    assert result is True
    assert connector.is_connected is False

def test_sqlite_execute_query_not_connected():
    connector = SQLiteConnector()
    success, result, error = connector.execute_query("SELECT 1")
    assert success is False
    assert error == "No hay conexión activa"

def test_sqlite_execute_query_success():
    connector = SQLiteConnector()
    connector.connect(db_path=":memory:")
    
    # Create table
    connector.execute_query("CREATE TABLE test (id INTEGER, name TEXT)")
    
    # Insert data
    success, result, error = connector.execute_query("INSERT INTO test VALUES (1, 'Alice')")
    assert success is True
    assert result['affected_rows'] == 1
    
    # Select data
    success, result, error = connector.execute_query("SELECT * FROM test")
    assert success is True
    assert result['columns'] == ['id', 'name']
    assert result['rows'] == [(1, 'Alice')]
    
    connector.disconnect()

def test_sqlite_execute_query_error():
    connector = SQLiteConnector()
    connector.connect(db_path=":memory:")
    success, result, error = connector.execute_query("SELECT * FROM nonexistent_table")
    assert success is False
    assert "no such table" in error
    connector.disconnect()

def test_sqlite_get_tables():
    connector = SQLiteConnector()
    connector.connect(db_path=":memory:")
    
    connector.execute_query("CREATE TABLE test1 (id INTEGER)")
    connector.execute_query("CREATE TABLE test2 (id INTEGER)")
    
    success, tables, error = connector.get_tables()
    assert success is True
    assert 'test1' in tables
    assert 'test2' in tables
    
    connector.disconnect()

def test_sqlite_get_type_and_info():
    connector = SQLiteConnector()
    assert connector.get_type() == "SQLite"
    assert connector.get_info() == "Desconocido"
    
    connector.connect(db_path=":memory:")
    assert connector.get_info() == ":memory:"
    connector.disconnect()
