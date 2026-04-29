"""
Conector para Apache Cassandra
"""

from typing import Any, Tuple, List
from .nosql_base import BaseNoSQLConnector

try:
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from cassandra import InvalidRequest, Unauthorized
    CASSANDRA_AVAILABLE = True
except ImportError:
    CASSANDRA_AVAILABLE = False


class CassandraConnector(BaseNoSQLConnector):
    """Conector para bases de datos Apache Cassandra"""

    def __init__(self):
        super().__init__()
        self.cluster = None
        self.session = None
        self.keyspace = None
        self.host = None

    def connect(self, **kwargs) -> bool:
        """
        Conecta a una base de datos Cassandra

        Parámetros:
            keyspace: nombre del keyspace
            host: dirección del servidor (default: localhost)
            port: puerto (default: 9042)
            username: nombre de usuario (opcional)
            password: contraseña (opcional)
        """
        if not CASSANDRA_AVAILABLE:
            raise ImportError(
                "cassandra-driver no está instalado. Ejecuta: pip install cassandra-driver"
            )

        self.keyspace = kwargs.get('keyspace')
        self.host = kwargs.get('host', 'localhost')
        port = int(kwargs.get('port', 9042))
        username = kwargs.get('username')
        password = kwargs.get('password')

        try:
            auth_provider = None
            if username and password:
                auth_provider = PlainTextAuthProvider(
                    username=username, password=password
                )

            self.cluster = Cluster(
                contact_points=[self.host],
                port=port,
                auth_provider=auth_provider,
                connect_timeout=5
            )
            self.session = self.cluster.connect()

            if self.keyspace:
                self.session.set_keyspace(self.keyspace)

            self.is_connected = True
            return True
        except Exception as e:
            raise Exception(f"Error conectando a Cassandra: {e}")

    def disconnect(self) -> bool:
        """Cierra la conexión"""
        try:
            if self.session:
                self.session.shutdown()
            if self.cluster:
                self.cluster.shutdown()
            self.is_connected = False
            return True
        except Exception as e:
            raise Exception(f"Error desconectando de Cassandra: {e}")

    def execute_query(self, cql: str) -> Tuple[bool, Any, str]:
        """
        Ejecuta una sentencia CQL en Cassandra

        Retorna:
            (éxito, resultados, mensaje_error)
        """
        if not self.is_connected:
            return False, None, "No hay conexión activa a Cassandra"

        try:
            result = self.session.execute(cql)

            # Si hay filas devueltas (SELECT)
            if result and result.column_names:
                columns = list(result.column_names)
                rows = [list(row) for row in result]
                return True, {'columns': columns, 'rows': rows}, ""
            else:
                return True, {'affected_rows': -1}, ""

        except Exception as e:
            return False, None, str(e)

    def list_collections(self) -> Tuple[bool, List[str], str]:
        """Retorna la lista de tablas del keyspace actual"""
        if not self.is_connected:
            return False, [], "No hay conexión activa"
        try:
            if not self.keyspace:
                return False, [], "No se especificó keyspace"

            cql = (
                "SELECT table_name FROM system_schema.tables "
                "WHERE keyspace_name = %s"
            )
            result = self.session.execute(cql, [self.keyspace])
            tables = [row.table_name for row in result]
            return True, tables, ""
        except Exception as e:
            return False, [], str(e)

    def get_type(self) -> str:
        """Retorna el tipo de base de datos"""
        return "Cassandra"

    def get_info(self) -> str:
        """Retorna información de la conexión"""
        return f"{self.keyspace}@{self.host}"
