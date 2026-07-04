"""
Servidor MCP (Model Context Protocol) para NexusDB.

Expone los conectores de bases de datos existentes de NexusDB como
herramientas utilizables por cualquier cliente compatible con MCP
(Claude Desktop, Claude Code, Cursor, Windsurf, etc.).

Por seguridad, las consultas ejecutadas a través de este servidor
están restringidas a operaciones de solo lectura (SELECT/SHOW/DESCRIBE/EXPLAIN).
"""

import os
import re
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from connectors.sqlite_connector import SQLiteConnector
from connectors.postgres_connector import PostgresConnector
from connectors.mysql_connector import MySQLConnector

mcp = FastMCP("NexusDB")

_CONECTORES = {
    "sqlite": SQLiteConnector,
    "postgres": PostgresConnector,
    "mysql": MySQLConnector,
}

# Solo se permiten operaciones de lectura para evitar que un agente de IA
# modifique o borre datos por accidente (o por una instrucción maliciosa).
_PATRON_SOLO_LECTURA = re.compile(r"^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b", re.IGNORECASE)

_conexion_activa = None
_motor_activo: Optional[str] = None


@mcp.tool()
def conectar(
    motor: str,
    db_path: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[str] = None,
    dbname: Optional[str] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Conecta NexusDB a una base de datos.

    motor: 'sqlite', 'postgres' o 'mysql'.
    Para sqlite: usar db_path (ruta del archivo .db).
    Para postgres: usar dbname, user, password, host, port.
    Para mysql: usar database, user, password, host, port.
    """
    global _conexion_activa, _motor_activo

    motor = motor.lower().strip()
    if motor not in _CONECTORES:
        return f"Motor '{motor}' no soportado. Usa: {', '.join(_CONECTORES)}."

    conector = _CONECTORES[motor]()
    kwargs = {
        "db_path": db_path,
        "host": host,
        "port": port,
        "dbname": dbname,
        "database": database,
        "user": user,
        "password": password,
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    try:
        conector.connect(**kwargs)
    except Exception as e:
        return f"Error al conectar: {e}"

    _conexion_activa = conector
    _motor_activo = motor
    return f"Conectado correctamente a {conector.get_type()} ({conector.get_info()})."


@mcp.tool()
def listar_tablas() -> str:
    """Lista las tablas de la base de datos actualmente conectada."""
    if _conexion_activa is None:
        return "No hay ninguna conexión activa. Usa la herramienta 'conectar' primero."

    exito, tablas, error = _conexion_activa.get_tables()
    if not exito:
        return f"Error al listar tablas: {error}"
    if not tablas:
        return "La base de datos no tiene tablas."
    return "Tablas encontradas:\n" + "\n".join(f"- {t}" for t in tablas)


@mcp.tool()
def ejecutar_consulta(sql: str) -> str:
    """
    Ejecuta una consulta SQL de solo lectura (SELECT, SHOW, DESCRIBE, EXPLAIN)
    contra la base de datos actualmente conectada. Consultas de escritura
    (INSERT, UPDATE, DELETE, DROP, ALTER, etc.) son rechazadas por seguridad.
    """
    if _conexion_activa is None:
        return "No hay ninguna conexión activa. Usa la herramienta 'conectar' primero."

    if not _PATRON_SOLO_LECTURA.match(sql):
        return (
            "Consulta rechazada: este servidor MCP solo permite operaciones de "
            "lectura (SELECT, SHOW, DESCRIBE, EXPLAIN)."
        )

    exito, resultado, error = _conexion_activa.execute_query(sql)
    if not exito:
        return f"Error al ejecutar la consulta: {error}"

    columnas = resultado.get("columns")
    filas = resultado.get("rows")
    if columnas is None:
        return f"Consulta ejecutada. Filas afectadas: {resultado.get('affected_rows')}"

    encabezado = " | ".join(columnas)
    lineas = [encabezado, "-" * len(encabezado)]
    for fila in filas[:200]:
        lineas.append(" | ".join(str(valor) for valor in fila))
    if len(filas) > 200:
        lineas.append(f"... ({len(filas) - 200} filas adicionales no mostradas)")
    return "\n".join(lineas)


@mcp.tool()
def desconectar() -> str:
    """Cierra la conexión activa a la base de datos."""
    global _conexion_activa, _motor_activo
    if _conexion_activa is None:
        return "No hay ninguna conexión activa."
    _conexion_activa.disconnect()
    motor = _motor_activo
    _conexion_activa = None
    _motor_activo = None
    return f"Conexión a {motor} cerrada."


if __name__ == "__main__":
    mcp.run(transport="stdio")
