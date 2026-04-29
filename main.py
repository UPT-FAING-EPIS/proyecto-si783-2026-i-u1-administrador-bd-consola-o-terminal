#!/usr/bin/env python3
"""
DB Admin CLI - Administrador de Bases de Datos por Consola
Punto de entrada principal de la aplicación.

Uso:
    python main.py           # Modo relacional (por defecto)
    python main.py --nosql   # Modo NoSQL
"""

import sys
import os
import argparse

# Agregar src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from cli.repl import REPL
from rich import print as rprint
from rich.panel import Panel


def main():
    parser = argparse.ArgumentParser(
        description="DB Admin CLI - Administrador de Bases de Datos por Consola"
    )
    parser.add_argument(
        "--nosql",
        action="store_true",
        help="Iniciar en modo NoSQL (MongoDB, Redis, Cassandra)"
    )
    args = parser.parse_args()

    mode = "nosql" if args.nosql else "rel"

    rprint(Panel(
        "[bold white]DB Admin CLI[/bold white]\n"
        "[cyan]Administrador de Bases de Datos por Consola/Terminal[/cyan]\n"
        f"[yellow]Modo: {'NoSQL' if mode == 'nosql' else 'Relacional'}[/yellow]\n"
        "[dim]Escribe 'help' para ver los comandos disponibles[/dim]",
        title="[bold blue]Bienvenido[/bold blue]",
        border_style="blue"
    ))

    repl = REPL(mode=mode)
    repl.run()


if __name__ == "__main__":
    main()
