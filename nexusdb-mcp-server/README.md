# nexusdb-mcp-server

Servidor MCP (Model Context Protocol) que expone conectores de bases de
datos (SQLite, PostgreSQL, MySQL) del proyecto NexusDB como herramientas
para asistentes de IA compatibles con MCP (Claude Desktop, Claude Code,
Cursor, Windsurf, etc.).

Por seguridad, solo permite consultas de lectura (`SELECT`, `SHOW`,
`DESCRIBE`, `EXPLAIN`). Cualquier operación de escritura es rechazada.

## Instalación

```bash
pip install nexusdb-mcp-server
```

## Herramientas expuestas

- `conectar(motor, ...)` — conecta a `sqlite`, `postgres` o `mysql`.
- `listar_tablas()` — lista las tablas de la conexión activa.
- `ejecutar_consulta(sql)` — ejecuta una consulta de solo lectura.
- `desconectar()` — cierra la conexión activa.

## Configuración en Claude Desktop

Edita tu archivo de configuración (`%APPDATA%\Claude\claude_desktop_config.json`
en Windows) y agrega:

```json
{
  "mcpServers": {
    "nexusdb": {
      "command": "nexusdb-mcp-server"
    }
  }
}
```

Reinicia Claude Desktop. No necesitas indicar ninguna ruta: el comando
`nexusdb-mcp-server` queda disponible globalmente después de instalar el
paquete con pip.

## Configuración en otros clientes MCP (Cursor, Cline, Windsurf, etc.)

Usa el mismo comando `nexusdb-mcp-server` en la configuración de servidores
MCP de tu cliente. Consulta la documentación de tu cliente para la ubicación
exacta del archivo de configuración.
