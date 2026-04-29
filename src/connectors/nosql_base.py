"""
Clase base para conectores NoSQL
Define la interfaz que deben implementar los conectores NoSQL
"""

from abc import abstractmethod
from typing import Any, Tuple, List
from .base import BaseConnector


class BaseNoSQLConnector(BaseConnector):
    """Clase base abstracta para conectores NoSQL"""

    @abstractmethod
    def list_collections(self) -> Tuple[bool, List[str], str]:
        """Retorna lista de colecciones/keys/tablas en la base de datos NoSQL"""
        pass

    def get_tables(self) -> Tuple[bool, List[str], str]:
        """Delegación a list_collections para compatibilidad con la interfaz base"""
        return self.list_collections()
