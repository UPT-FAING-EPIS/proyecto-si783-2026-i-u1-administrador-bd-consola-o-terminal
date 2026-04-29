"""
Módulo REPL - Read-Eval-Print Loop
Bucle principal que lee comandos y los ejecuta
"""

import sys
import os
import csv

# Agregar la carpeta actual al path para poder importar .
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.sqlite_connector import SQLiteConnector
from connectors.postgres_connector import PostgresConnector
from connectors.mysql_connector import MySQLConnector
from connectors.mongodb_connector import MongoDBConnector
from connectors.redis_connector import RedisConnector
from connectors.cassandra_connector import CassandraConnector
from formatters.table_formatter import TableFormatter

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint


class REPL:
    """Bucle principal de la aplicación"""

    def __init__(self, mode='rel'):
        self.running = True
        self.mode = mode
        self.console = Console()
        self.connector = None
        self.formatter = TableFormatter()
        self.last_results = None  # Almacena el resultado del último SELECT.

    def _get_prompt(self):
        """Genera el prompt dinámicamente según el estado de la conexión"""
        base = "dbcli-rel" if self.mode == "rel" else "dbcli-nosql"
        if self.connector and self.connector.is_connected:
            db_type = self.connector.get_type().lower()
            db_info = self.connector.get_info()
            # Extraer solo el nombre del archivo si es path completo
            db_name = os.path.basename(db_info)
            return f"[{base} | {db_type}: {db_name}] > "
        return f"{base} > "

    def run(self):
        """Ejecuta el bucle principal"""
        while self.running:
            try:
                current_prompt = self._get_prompt()
                command = input(current_prompt).strip()
                if not command:
                    continue
                
                # Try-except global para capturar errores de ejecución sin cerrar la app
                try:
                    self.execute(command)
                except Exception as e:
                    rprint(f"\n[bold red]ERROR de ejecución:[/bold red] [white]{e}[/white]")
                    rprint("[yellow]La aplicación sigue activa. Intenta de nuevo.[/yellow]\n")
                    
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                rprint("\n[yellow]Usa 'exit' para salir correctamente.[/yellow]")
                continue

    def execute(self, command: str):
        """Ejecuta un comando según su tipo"""
        cmd = command.lower().strip()

        if cmd == "exit":
            self._exit()
        elif cmd == "help":
            self._help()
        elif cmd.startswith("connect"):
            self._connect(command)
        elif cmd == "status":
            self._status()
        elif cmd == "disconnect":
            self._disconnect()
        elif cmd.startswith("export"):
            self._export(command)
        else:
            if not self.connector or not self.connector.is_connected:
                rprint("[bold red]ERROR:[/bold red] No hay conexión activa. [yellow]Usa 'connect' primero.[/yellow]")
                return

            if self.mode == "rel":
                if cmd.startswith("select"):
                    self._select(command)
                elif cmd.startswith("insert"):
                    self._insert(command)
                elif cmd.startswith("update"):
                    self._update(command)
                elif cmd.startswith("delete"):
                    self._delete(command)
                elif cmd.startswith("create table"):
                    self._create_table(command)
                elif cmd.startswith("drop table"):
                    self._drop_table(command)
                elif cmd == "show tables":
                    self._show_tables()
                else:
                    rprint(f"[bold red]ERROR: Comando no reconocido:[/bold red] [white]{command}[/white]")
                    rprint("   Usa [bold cyan]'help'[/bold cyan] para ver los comandos disponibles")
            else:
                if cmd in ["show collections", "show keys", "show tables"]:
                    self._show_tables()
                else:
                    self._execute_nosql_query(command)

    # ==================== COMANDOS BÁSICOS ====================

    def _exit(self):
        """Salir de la aplicación"""
        if self.connector and self.connector.is_connected:
            self._disconnect()
        rprint("\n[bold green]Hasta luego[/bold green]")
        self.running = False

    def _help(self):
        """Mostrar ayuda"""
        help_text = Text()
        if self.mode == "rel":
            help_text.append("\nCONEXIÓN RELACIONAL:\n", style="bold cyan")
            help_text.append("  connect sqlite <ruta>                       - Ej: connect sqlite test.db\n")
            help_text.append("  connect postgres <db> <user> <pass> [host]  - Ej: connect postgres mi_db postgres 123\n")
            help_text.append("  connect mysql <db> <user> <pass> [host]     - Ej: connect mysql mi_db root 123\n")
            
            help_text.append("\nCONSULTAS (CRUD):\n", style="bold green")
            help_text.append("  select * from <tabla> [where ...]           - Ej: select * from usuarios\n")
            help_text.append("  insert into <tabla> (...) values (...)      - Ej: insert into usuarios (nombre) values ('Ana')\n")
            help_text.append("  update <tabla> set col=val where ...        - Ej: update usuarios set edad=30 where id=1\n")
            help_text.append("  delete from <tabla> where ...               - Ej: delete from usuarios where id=1\n")
            
            help_text.append("\nESTRUCTURA:\n", style="bold magenta")
            help_text.append("  create table <nombre> (...)                 - Crear nueva tabla\n")
            help_text.append("  drop table <nombre>                         - Eliminar tabla\n")
            help_text.append("  show tables                                 - Listar tablas existentes\n")
        else:
            help_text.append("\nCONEXIÓN NOSQL:\n", style="bold cyan")
            help_text.append("  connect mongodb <db> [host] [puerto]        - Ej: connect mongodb testdb localhost 27017\n")
            help_text.append("  connect redis [db_index] [host] [puerto]    - Ej: connect redis 0 localhost 6379\n")
            help_text.append("  connect cassandra <keyspace> [host]         - Ej: connect cassandra testks localhost\n")
            
            help_text.append("\nCOMANDOS NOSQL:\n", style="bold green")
            help_text.append("  MongoDB:\n")
            help_text.append("    find <coleccion> <json_filtro>            - Ej: find usuarios {\"edad\": 30}\n")
            help_text.append("    insert <coleccion> <json_doc>             - Ej: insert usuarios {\"nombre\": \"Ana\", \"edad\": 30}\n")
            help_text.append("    update <coleccion> <filtro> <set>         - Ej: update usuarios {\"nombre\": \"Ana\"} {\"edad\": 31}\n")
            help_text.append("    delete <coleccion> <json_filtro>          - Ej: delete usuarios {\"nombre\": \"Ana\"}\n")
            help_text.append("  Redis:\n")
            help_text.append("    set <clave> <valor>                       - Ej: set saludo hola\n")
            help_text.append("    get <clave>                               - Ej: get saludo\n")
            help_text.append("    del <clave>                               - Ej: del saludo\n")
            help_text.append("    keys <patron>                             - Ej: keys *\n")
            help_text.append("  Cassandra:\n")
            help_text.append("    Soporte para comandos CQL como select, insert, update...\n")
            
            help_text.append("\nESTRUCTURA:\n", style="bold magenta")
            help_text.append("  show collections / show keys / show tables  - Listar estructuras existentes\n")

        help_text.append("\nCOMUNES:\n", style="bold yellow")
        help_text.append("  status                                      - Ver estado de conexión\n")
        help_text.append("  disconnect                                  - Cerrar sesión activa\n")
        help_text.append("  export <archivo.csv>                        - Exportar últimos resultados a CSV\n")
        help_text.append("  help                                        - Muestra esta ayuda\n")
        help_text.append("  exit                                        - Salir de la aplicación\n")

        self.console.print(Panel(help_text, title="[bold white]COMANDOS DISPONIBLES[/bold white]", border_style="blue"))

    def _connect(self, command: str):
        """Conectar a una base de datos"""
        parts = command.split()
        if len(parts) < 2:
            print("❌ Uso: connect <tipo> <parámetros>")
            print("   Tipos: sqlite, postgres, mysql")
            return

        db_type = parts[1].lower()

        if db_type == "sqlite":
            if len(parts) < 3:
                print("❌ Uso: connect sqlite <ruta>")
                return
            db_path = parts[2]
            rprint(f"[bold blue]Conectando a SQLite:[/bold blue] [white]{db_path}...[/white]")
            try:
                self.connector = SQLiteConnector()
                self.connector.connect(db_path=db_path)
                rprint(f"[bold green]OK: Conectado a SQLite correctamente.[/bold green]")
            except Exception as e:
                rprint(f"[bold red]ERROR de conexión:[/bold red] {e}")
                self.connector = None

        elif db_type == "postgres":
            if len(parts) < 5:
                print("❌ Uso: connect postgres <db> <usuario> <contraseña> [host] [puerto]")
                return
            db_name = parts[2]
            user = parts[3]
            password = parts[4]
            host = parts[5] if len(parts) > 5 else "localhost"
            port = parts[6] if len(parts) > 6 else "5432"
            print(f"🔌 Conectando a PostgreSQL: {db_name}...")
            try:
                self.connector = PostgresConnector()
                self.connector.connect(
                    dbname=db_name,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                print(f"✅ Conectado a PostgreSQL: {db_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.connector = None

        elif db_type == "mysql":
            if len(parts) < 5:
                print("❌ Uso: connect mysql <db> <usuario> <contraseña> [host] [puerto]")
                return
            db_name = parts[2]
            user = parts[3]
            password = parts[4]
            host = parts[5] if len(parts) > 5 else "localhost"
            port = parts[6] if len(parts) > 6 else "3306"
            print(f"🔌 Conectando a MySQL: {db_name}...")
            try:
                self.connector = MySQLConnector()
                self.connector.connect(
                    database=db_name,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                print(f"✅ Conectado a MySQL: {db_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.connector = None

        elif db_type == "mongodb":
            if self.mode != "nosql":
                print("❌ MongoDB solo está disponible en modo NoSQL")
                return
            if len(parts) < 3:
                print("❌ Uso: connect mongodb <db> [host] [puerto]")
                return
            db_name = parts[2]
            host = parts[3] if len(parts) > 3 else "localhost"
            port = parts[4] if len(parts) > 4 else "27017"
            print(f"🔌 Conectando a MongoDB: {db_name}...")
            try:
                self.connector = MongoDBConnector()
                self.connector.connect(db_name=db_name, host=host, port=port)
                print(f"✅ Conectado a MongoDB: {db_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.connector = None

        elif db_type == "redis":
            if self.mode != "nosql":
                print("❌ Redis solo está disponible en modo NoSQL")
                return
            db_index = parts[2] if len(parts) > 2 else "0"
            host = parts[3] if len(parts) > 3 else "localhost"
            port = parts[4] if len(parts) > 4 else "6379"
            print(f"🔌 Conectando a Redis DB {db_index}...")
            try:
                self.connector = RedisConnector()
                self.connector.connect(db_index=db_index, host=host, port=port)
                print(f"✅ Conectado a Redis DB {db_index}")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.connector = None

        elif db_type == "cassandra":
            if self.mode != "nosql":
                print("❌ Cassandra solo está disponible en modo NoSQL")
                return
            if len(parts) < 3:
                print("❌ Uso: connect cassandra <keyspace> [host]")
                return
            keyspace = parts[2]
            host = parts[3] if len(parts) > 3 else "localhost"
            print(f"🔌 Conectando a Cassandra keyspace: {keyspace}...")
            try:
                self.connector = CassandraConnector()
                self.connector.connect(keyspace=keyspace, host=host)
                print(f"✅ Conectado a Cassandra keyspace: {keyspace}")
            except Exception as e:
                print(f"❌ Error: {e}")
                self.connector = None

        else:
            print(f"❌ Tipo de base de datos no soportado: {db_type}")
            if self.mode == "rel":
                print("   Tipos soportados: sqlite, postgres, mysql")
            else:
                print("   Tipos soportados: mongodb, redis, cassandra")

    def _status(self):
        """Mostrar estado de la conexión"""
        status_text = Text()
        if self.connector and self.connector.is_connected:
            status_text.append("OK: ESTADO: CONECTADO\n", style="bold green")
            status_text.append(f"TIPO: {self.connector.get_type()}\n", style="white")
            status_text.append(f"INFO: {self.connector.get_info()}", style="cyan")
        else:
            status_text.append("ERROR: ESTADO: NO CONECTADO", style="bold red")

        self.console.print(Panel(status_text, title="[bold white]INFORMACIÓN DE CONEXIÓN[/bold white]", expand=False))

    def _disconnect(self):
        """Desconectar de la base de datos"""
        if self.connector and self.connector.is_connected:
            rprint("[bold blue]Desconectando...[/bold blue]")
            try:
                self.connector.disconnect()
                self.connector = None
                rprint("[bold green]OK: Desconectado con éxito.[/bold green]")
            except Exception as e:
                rprint(f"[bold red]ERROR al desconectar:[/bold red] {e}")
        else:
            rprint("[bold yellow]INFO: No hay conexión activa para cerrar.[/bold yellow]")

    # ==================== OPERACIONES ====================

    def _select(self, command: str):
        """Ejecutar SELECT"""
        success, data, error = self.connector.execute_query(command)
        if success:
            if data and 'columns' in data and data['columns']:
                self.last_results = data  # Guardar para exportación
                self.formatter.print_table(data['columns'], data['rows'])
                rprint(f"\n[bold cyan]INFO: Total:[/bold cyan] [white]{len(data['rows'])} fila(s)[/white]")
            elif data and 'affected_rows' in data:
                rprint(f"[bold green]OK: Éxito:[/bold green] [white]{data['affected_rows']} fila(s) afectada(s)[/white]")
            else:
                rprint("[bold yellow]INFO: Consulta ejecutada sin resultados.[/bold yellow]")
        else:
            rprint(f"[bold red]ERROR SQL:[/bold red] [white]{error}[/white]")

    def _export(self, command: str):
        """Exporta los últimos resultados a un archivo CSV"""
        parts = command.split()
        if len(parts) < 2:
            rprint("[bold red]ERROR:[/bold red] Debes especificar un nombre de archivo. [yellow]Ej: export resultados.csv[/yellow]")
            return

        if not self.last_results:
            rprint("[bold yellow]INFO: No hay resultados para exportar.[/bold yellow] [white]Primero realiza un SELECT.[/white]")
            return

        filename = parts[1]
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.last_results['columns'])
                writer.writerows(self.last_results['rows'])
            rprint(f"[bold green]OK: Datos exportados correctamente a:[/bold green] [white]{filename}[/white]")
        except Exception as e:
            rprint(f"[bold red]ERROR al exportar:[/bold red] {e}")

    def _insert(self, command: str):
        """Ejecutar INSERT"""
        success, data, error = self.connector.execute_query(command)
        if success:
            print("✅ Registro insertado correctamente")
        else:
            print(f"❌ Error: {error}")

    def _update(self, command: str):
        """Ejecutar UPDATE"""
        success, data, error = self.connector.execute_query(command)
        if success:
            print("✅ Registro(s) actualizado(s) correctamente")
        else:
            print(f"❌ Error: {error}")

    def _delete(self, command: str):
        """Ejecutar DELETE"""
        success, data, error = self.connector.execute_query(command)
        if success:
            print("✅ Registro(s) eliminado(s) correctamente")
        else:
            print(f"❌ Error: {error}")

    def _create_table(self, command: str):
        """Ejecutar CREATE TABLE"""
        success, data, error = self.connector.execute_query(command)
        if success:
            print("✅ Tabla creada correctamente")
        else:
            print(f"❌ Error: {error}")

    def _drop_table(self, command: str):
        """Ejecutar DROP TABLE"""
        success, data, error = self.connector.execute_query(command)
        if success:
            print("✅ Tabla eliminada correctamente")
        else:
            print(f"❌ Error: {error}")

    def _show_tables(self):
        """Listar todas las tablas"""
        success, data, error = self.connector.get_tables()
        if success:
            if data:
                table_list = Text()
                for table in data:
                    table_list.append(f"  * {table}\n", style="cyan")
                
                self.console.print(Panel(
                    table_list, 
                    title="[bold white]TABLAS ENCONTRADAS[/bold white]", 
                    subtitle=f"[yellow]Total: {len(data)}[/yellow]",
                    expand=False
                ))
            else:
                rprint("[bold yellow]INFO: No hay tablas en la base de datos.[/bold yellow]")
        else:
            rprint(f"[bold red]ERROR:[/bold red] [white]{error}[/white]")

    
    def _execute_nosql_query(self, command: str):
        """Ejecuta una consulta NoSQL y muestra los resultados"""
        success, data, error = self.connector.execute_query(command)
        if success:
            if data and 'columns' in data and data['columns']:
                self.last_results = data
                self.formatter.print_table(data['columns'], data['rows'])
                rprint(f"\n[bold cyan]INFO: Total:[/bold cyan] [white]{len(data['rows'])} fila(s)/documento(s)[/white]")
            elif data and 'affected_rows' in data:
                rprint(f"[bold green]OK: Éxito:[/bold green] [white]{data['affected_rows']} fila(s)/documento(s) afectada(s)[/white]")
            elif isinstance(data, list):
                # Formateo simple para listas planas (ej: KEYS en Redis)
                self.formatter.print_table(["Resultados"], [[str(item)] for item in data])
                rprint(f"\n[bold cyan]INFO: Total:[/bold cyan] [white]{len(data)} resultado(s)[/white]")
            elif isinstance(data, dict):
                # Formateo para diccionarios simples
                self.formatter.print_table(["Clave", "Valor"], [[str(k), str(v)] for k, v in data.items()])
            elif data is not None:
                rprint(f"[bold green]Resultado:[/bold green] [white]{data}[/white]")
            else:
                rprint("[bold green]OK: Comando ejecutado correctamente sin devolver datos.[/bold green]")
        else:
            rprint(f"[bold red]ERROR NOSQL:[/bold red] [white]{error}[/white]")
