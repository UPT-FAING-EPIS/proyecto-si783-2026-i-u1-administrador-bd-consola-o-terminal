"""
Conector para MongoDB
"""

import json
from typing import Any, Tuple, List
from .nosql_base import BaseNoSQLConnector

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class MongoDBConnector(BaseNoSQLConnector):
    """Conector para bases de datos MongoDB"""

    def __init__(self):
        super().__init__()
        self.client = None
        self.db = None
        self.db_name = None
        self.host = None
        self.port = None

    def connect(self, **kwargs) -> bool:
        """
        Conecta a una base de datos MongoDB

        Parámetros:
            db_name: nombre de la base de datos
            host: dirección del servidor (default: localhost)
            port: puerto (default: 27017)
        """
        if not PYMONGO_AVAILABLE:
            raise ImportError("pymongo no está instalado. Ejecuta: pip install pymongo")

        self.db_name = kwargs.get('db_name', 'test')
        self.host = kwargs.get('host', 'localhost')
        self.port = int(kwargs.get('port', 27017))

        try:
            self.client = MongoClient(
                host=self.host,
                port=self.port,
                serverSelectionTimeoutMS=5000
            )
            # Forzar la conexión para detectar errores temprano
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            return True
        except Exception as e:
            raise Exception(f"Error conectando a MongoDB: {e}")

    def disconnect(self) -> bool:
        """Cierra la conexión"""
        try:
            if self.client:
                self.client.close()
            self.is_connected = False
            return True
        except Exception as e:
            raise Exception(f"Error desconectando de MongoDB: {e}")

    def execute_query(self, command: str) -> Tuple[bool, Any, str]:
        """
        Ejecuta un comando NoSQL de MongoDB.
        Formatos soportados:
          find <coleccion> <json_filtro>
          insert <coleccion> <json_doc>
          update <coleccion> <filtro_json> <set_json>
          delete <coleccion> <json_filtro>
        """
        if not self.is_connected:
            return False, None, "No hay conexión activa a MongoDB"

        parts = command.strip().split(None, 1)
        if not parts:
            return False, None, "Comando vacío"

        op = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        try:
            if op == "find":
                return self._find(rest)
            elif op == "insert":
                return self._insert(rest)
            elif op == "update":
                return self._update(rest)
            elif op == "delete":
                return self._delete(rest)
            else:
                return False, None, f"Operación MongoDB no soportada: {op}. Usa find, insert, update o delete."
        except Exception as e:
            return False, None, str(e)

    def _find(self, rest: str) -> Tuple[bool, Any, str]:
        """Ejecuta find en una colección"""
        tokens = rest.strip().split(None, 1)
        collection_name = tokens[0] if tokens else ""
        filter_json = tokens[1] if len(tokens) > 1 else "{}"

        try:
            query_filter = json.loads(filter_json)
        except json.JSONDecodeError as e:
            return False, None, f"JSON inválido en filtro: {e}"

        collection = self.db[collection_name]
        docs = list(collection.find(query_filter))

        if not docs:
            return True, {'columns': [], 'rows': []}, ""

        # Obtener todas las claves únicas como columnas preservando el orden de inserción
        seen = {}
        for doc in docs:
            for k in doc.keys():
                seen[k] = None
        all_keys = list(seen)

        rows = [[str(doc.get(k, "")) for k in all_keys] for doc in docs]
        return True, {'columns': all_keys, 'rows': rows}, ""

    def _insert(self, rest: str) -> Tuple[bool, Any, str]:
        """Inserta un documento en una colección"""
        tokens = rest.strip().split(None, 1)
        if len(tokens) < 2:
            return False, None, "Uso: insert <coleccion> <json_doc>"
        collection_name = tokens[0]
        doc_json = tokens[1]

        try:
            doc = json.loads(doc_json)
        except json.JSONDecodeError as e:
            return False, None, f"JSON inválido: {e}"

        collection = self.db[collection_name]
        result = collection.insert_one(doc)
        return True, {'affected_rows': 1}, ""

    def _update(self, rest: str) -> Tuple[bool, Any, str]:
        """Actualiza documentos en una colección"""
        tokens = rest.strip().split(None, 2)
        if len(tokens) < 3:
            return False, None, "Uso: update <coleccion> <filtro_json> <set_json>"
        collection_name = tokens[0]
        filter_json = tokens[1]
        set_json = tokens[2]

        try:
            query_filter = json.loads(filter_json)
            set_values = json.loads(set_json)
        except json.JSONDecodeError as e:
            return False, None, f"JSON inválido: {e}"

        collection = self.db[collection_name]
        result = collection.update_many(query_filter, {"$set": set_values})
        return True, {'affected_rows': result.modified_count}, ""

    def _delete(self, rest: str) -> Tuple[bool, Any, str]:
        """Elimina documentos de una colección"""
        tokens = rest.strip().split(None, 1)
        if len(tokens) < 2:
            return False, None, "Uso: delete <coleccion> <json_filtro>"
        collection_name = tokens[0]
        filter_json = tokens[1]

        try:
            query_filter = json.loads(filter_json)
        except json.JSONDecodeError as e:
            return False, None, f"JSON inválido en filtro: {e}"

        collection = self.db[collection_name]
        result = collection.delete_many(query_filter)
        return True, {'affected_rows': result.deleted_count}, ""

    def list_collections(self) -> Tuple[bool, List[str], str]:
        """Retorna lista de colecciones en la base de datos"""
        if not self.is_connected:
            return False, [], "No hay conexión activa"
        try:
            collections = self.db.list_collection_names()
            return True, collections, ""
        except Exception as e:
            return False, [], str(e)

    def get_type(self) -> str:
        """Retorna el tipo de base de datos"""
        return "MongoDB"

    def get_info(self) -> str:
        """Retorna información de la conexión"""
        return f"{self.db_name}@{self.host}:{self.port}"
