# NexusDB MCP Server

Servidor MCP (Model Context Protocol) que expone los conectores de NexusDB
como herramientas para asistentes de IA compatibles con MCP (Claude Desktop,
Claude Code, Cursor, Windsurf, etc.).

## Herramientas expuestas

- `conectar(motor, ...)` — conecta a SQLite, PostgreSQL o MySQL.
- `listar_tablas()` — lista las tablas de la conexión activa.
- `ejecutar_consulta(sql)` — ejecuta una consulta **de solo lectura**
  (SELECT, SHOW, DESCRIBE, EXPLAIN). Las consultas de escritura son rechazadas.
- `desconectar()` — cierra la conexión activa.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración en Claude Desktop

Agrega esto a tu archivo de configuración de Claude Desktop
(`%APPDATA%\Claude\claude_desktop_config.json` en Windows):

```json
{
  "mcpServers": {
    "nexusdb": {
      "command": "python",
      "args": ["RUTA_ABSOLUTA_AL_PROYECTO/src/mcp_server/server.py"]
    }
  }
}
```

Reemplaza `RUTA_ABSOLUTA_AL_PROYECTO` por la ruta real del proyecto en tu
máquina. Reinicia Claude Desktop después de guardar el archivo.

## Configuración en Claude Code / Cursor / Windsurf

La mayoría de estos clientes soportan agregar servidores MCP vía comando:

```bash
claude mcp add nexusdb -- python RUTA_ABSOLUTA_AL_PROYECTO/src/mcp_server/server.py
```

(Ajusta el comando según la documentación de MCP de tu cliente específico.)
