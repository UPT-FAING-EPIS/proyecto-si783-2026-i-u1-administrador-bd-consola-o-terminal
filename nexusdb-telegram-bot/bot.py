"""
Bot de Telegram para NexusDB (modo solo lectura, multi-motor).

Soporta los mismos motores que el CLI de NexusDB: relacionales
(SQLite, PostgreSQL, MySQL) y NoSQL (MongoDB, Redis, Cassandra).
Los nombres de comandos siguen los mismos que el menú "help" del CLI.

Reglas de seguridad:
- /conectar solo funciona en chats privados (no en grupos).
- El mensaje con credenciales se borra automáticamente tras procesarse.
- Solo se permiten operaciones de lectura en cada motor:
    - SQL (sqlite/postgres/mysql) y CQL (cassandra): SELECT/SHOW/DESCRIBE/EXPLAIN
    - MongoDB: find
    - Redis: GET/MGET/KEYS/EXISTS/TTL/TYPE/STRLEN/HGET/HGETALL/HKEYS/HVALS/
      LRANGE/LLEN/SMEMBERS/SCARD/ZRANGE/ZSCORE/SCAN
- /preguntar genera SQL con IA (o patrones de respaldo) a partir del
  esquema real de tu conexión relacional, pero nunca lo ejecuta solo.
"""

import os
import re
import sys
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# El bot es autocontenido: usa su propia copia de los conectores en vendor/,
# para poder desplegarse solo (ej. en un VPS) sin depender del repo del CLI.
_RUTA_VENDOR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if _RUTA_VENDOR not in sys.path:
    sys.path.insert(0, _RUTA_VENDOR)

from connectors.sqlite_connector import SQLiteConnector
from connectors.postgres_connector import PostgresConnector
from connectors.mysql_connector import MySQLConnector
from connectors.mongodb_connector import MongoDBConnector
from connectors.redis_connector import RedisConnector
from connectors.cassandra_connector import CassandraConnector
from features.cerebro_sql import generar_sql, disponible as ia_disponible, proveedor as ia_proveedor

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("nexusdb-telegram-bot")

_LIMITE_FILAS = 30

_CONECTORES = {
    "sqlite": SQLiteConnector,
    "postgres": PostgresConnector,
    "mysql": MySQLConnector,
    "mongodb": MongoDBConnector,
    "redis": RedisConnector,
    "cassandra": CassandraConnector,
}

_MOTORES_SQL = {"sqlite", "postgres", "mysql", "cassandra"}  # cassandra usa CQL, muy similar a SQL
_PATRON_SQL_LECTURA = re.compile(r"^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b", re.IGNORECASE)

_COMANDOS_REDIS_LECTURA = {
    "GET", "MGET", "KEYS", "EXISTS", "TTL", "TYPE", "STRLEN",
    "HGET", "HGETALL", "HKEYS", "HVALS", "LRANGE", "LLEN",
    "SMEMBERS", "SCARD", "ZRANGE", "ZSCORE", "SCAN",
}

# Patrones de comandos peligrosos, igual que src/features/comparador.py
# pero adaptados para responder por chat en vez de pedir confirmación por consola.
_PATRONES_PELIGROSOS = [
    ("drop", "DROP eliminaría la tabla/colección permanentemente"),
    ("truncate", "TRUNCATE borraría TODOS los datos"),
    ("alter", "ALTER modificaría la estructura"),
]

# Conexión activa + motor por chat_id. Solo en memoria: se pierde si el bot
# se reinicia, y nunca se escribe a disco ni a los logs.
_conexiones: dict[int, object] = {}
_motores: dict[int, str] = {}


def _validar_lectura(motor: str, comando: str) -> tuple[bool, str]:
    """Verifica si 'comando' es una operación de solo lectura para 'motor'.
    Retorna (es_valido, mensaje_si_no_lo_es)."""
    if motor in _MOTORES_SQL:
        if _PATRON_SQL_LECTURA.match(comando):
            return True, ""
        return False, "Solo se permiten SELECT, SHOW, DESCRIBE o EXPLAIN."

    if motor == "mongodb":
        primera_palabra = comando.strip().split(maxsplit=1)[0].lower() if comando.strip() else ""
        if primera_palabra == "find":
            return True, ""
        return False, "Solo se permite 'find' (lectura) en MongoDB."

    if motor == "redis":
        primera_palabra = comando.strip().split(maxsplit=1)[0].upper() if comando.strip() else ""
        if primera_palabra in _COMANDOS_REDIS_LECTURA:
            return True, ""
        return False, f"Solo se permiten comandos de lectura en Redis: {', '.join(sorted(_COMANDOS_REDIS_LECTURA))}."

    return False, f"Motor '{motor}' no reconocido."


def _sin_conexion(update_message):
    return update_message.reply_text(
        "⚠️ No tienes ninguna conexión activa.\nUsa /conectar para empezar (ver /start)."
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    estado_ia = "activa ✅" if ia_disponible() else "no configurada (usa patrones de respaldo)"
    await update.message.reply_text(
        "🗄️ <b>NexusDB Bot</b> — modo solo lectura\n\n"
        "Soporta los mismos motores que el CLI de NexusDB. Nunca escribe, "
        "borra ni modifica datos: todas las operaciones son de solo lectura.\n\n"
        "<b>CONEXIÓN RELACIONAL</b>\n"
        "<code>connect sqlite &lt;ruta&gt;</code>\n"
        "<code>connect postgres &lt;db&gt; &lt;user&gt; &lt;pass&gt; [host]</code>\n"
        "<code>connect mysql &lt;db&gt; &lt;user&gt; &lt;pass&gt; [host]</code>\n\n"
        "<b>CONEXIÓN NOSQL</b>\n"
        "<code>connect mongodb &lt;db&gt; [host] [puerto]</code>\n"
        "<code>connect redis [db_index] [host] [puerto]</code>\n"
        "<code>connect cassandra &lt;keyspace&gt; [host]</code>\n\n"
        "<b>CÓMO CONECTAR EN ESTE BOT</b> (usa clave=valor)\n"
        "<code>/conectar sqlite db_path=C:\\ruta\\a\\mi.db</code>\n"
        "<code>/conectar postgres dbname=mi_db user=postgres password=123 host=localhost</code>\n"
        "<code>/conectar mysql database=mi_db user=root password=123 host=localhost</code>\n"
        "<code>/conectar mongodb db_name=testdb host=localhost port=27017</code>\n"
        "<code>/conectar redis db_index=0 host=localhost port=6379</code>\n"
        "<code>/conectar cassandra keyspace=testks host=localhost</code>\n\n"
        "<b>CONSULTAS (solo lectura)</b>\n"
        "SQL/CQL: <code>select * from usuarios</code>\n"
        "MongoDB: <code>find usuarios {\"edad\": 30}</code>\n"
        "Redis: <code>GET saludo</code>, <code>KEYS *</code>\n"
        "→ ejecútalas con <code>/consulta &lt;comando&gt;</code>\n\n"
        "<b>ESTRUCTURA</b>\n"
        "/tablas — <code>show tables</code> / <code>show collections</code> / <code>show keys</code>\n\n"
        "<b>OTROS</b>\n"
        "/status — equivalente a <code>status</code> del CLI\n"
        "/info — igual que /status\n"
        f"/preguntar &lt;pregunta en español&gt; — genera SQL desde lenguaje natural (IA: {estado_ia})\n"
        "/revisar &lt;comando&gt; — analiza si sería peligroso, sin ejecutarlo\n"
        "/disconnect — cierra tu conexión\n\n"
        "🔒 /conectar solo funciona en chat privado, nunca en grupos.",
        parse_mode=ParseMode.HTML,
    )


async def cmd_conectar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    if update.effective_chat.type != ChatType.PRIVATE:
        await update.message.reply_text(
            "🔒 Por seguridad, /conectar solo funciona en un chat privado con el bot "
            "(nunca en un grupo), para no exponer tus credenciales a otras personas."
        )
        return

    args = context.args
    # Borramos el mensaje original de inmediato: puede contener una contraseña.
    try:
        await update.message.delete()
    except Exception:
        pass

    if not args:
        await context.bot.send_message(
            chat_id,
            "Uso: /conectar <motor> clave=valor clave2=valor2 ...\n"
            f"Motores disponibles: {', '.join(_CONECTORES)}\n\n"
            "Consulta /start para ver ejemplos completos.",
        )
        return

    motor = args[0].lower()
    if motor not in _CONECTORES:
        await context.bot.send_message(
            chat_id, f"❌ Motor '{motor}' no soportado. Usa: {', '.join(_CONECTORES)}."
        )
        return

    kwargs = {}
    for par in args[1:]:
        if "=" not in par:
            continue
        clave, valor = par.split("=", 1)
        kwargs[clave] = valor

    conector = _CONECTORES[motor]()
    try:
        conector.connect(**kwargs)
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Error al conectar: {e}")
        return

    conexion_previa = _conexiones.get(chat_id)
    if conexion_previa is not None:
        try:
            conexion_previa.disconnect()
        except Exception:
            pass

    _conexiones[chat_id] = conector
    _motores[chat_id] = motor
    await context.bot.send_message(
        chat_id,
        f"✅ Conectado a {conector.get_type()} ({conector.get_info()}).\n"
        "🗑️ El mensaje con tus credenciales fue eliminado del chat.",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conector = _conexiones.get(update.effective_chat.id)
    if conector is None:
        await update.message.reply_text("🔌 Sin conexión activa.")
        return
    await update.message.reply_text(
        f"🔌 Conexión activa: {conector.get_type()}\n"
        f"📍 {conector.get_info()}"
    )


async def cmd_tablas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conector = _conexiones.get(update.effective_chat.id)
    if conector is None:
        await _sin_conexion(update.message)
        return

    exito, tablas, error = conector.get_tables()
    if not exito:
        await update.message.reply_text(f"❌ Error: {error}")
        return
    if not tablas:
        await update.message.reply_text("No se encontraron tablas/colecciones/keys.")
        return
    await update.message.reply_text("📋 Tablas/colecciones:\n" + "\n".join(f"- {t}" for t in tablas))


def _formatear_resultado(resultado) -> str:
    if isinstance(resultado, dict):
        columnas = resultado.get("columns")
        filas = resultado.get("rows")
        if columnas is not None:
            encabezado = " | ".join(columnas)
            lineas = [encabezado, "-" * len(encabezado)]
            for fila in filas[:_LIMITE_FILAS]:
                lineas.append(" | ".join(str(v) for v in fila))
            if len(filas) > _LIMITE_FILAS:
                lineas.append(f"... ({len(filas) - _LIMITE_FILAS} filas adicionales no mostradas)")
            return "\n".join(lineas)
        return f"Resultado: {resultado}"
    # Redis puede devolver strings, listas, números, etc. directamente.
    if isinstance(resultado, list):
        if not resultado:
            return "(vacío)"
        return "\n".join(str(v) for v in resultado[:_LIMITE_FILAS])
    return str(resultado)


async def cmd_consulta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    conector = _conexiones.get(chat_id)
    motor = _motores.get(chat_id)
    if conector is None or motor is None:
        await _sin_conexion(update.message)
        return

    comando = " ".join(context.args)
    if not comando:
        await update.message.reply_text("Uso: /consulta <comando>\nVer /start para ejemplos por motor.")
        return

    es_valido, motivo = _validar_lectura(motor, comando)
    if not es_valido:
        await update.message.reply_text(f"🚫 Comando rechazado: {motivo}")
        return

    exito, resultado, error = conector.execute_query(comando)
    if not exito:
        await update.message.reply_text(f"❌ Error: {error}")
        return

    texto = _formatear_resultado(resultado)
    await update.message.reply_text(f"<pre>{texto}</pre>", parse_mode=ParseMode.HTML)


async def cmd_preguntar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    conector = _conexiones.get(chat_id)
    motor = _motores.get(chat_id)
    if conector is None:
        await _sin_conexion(update.message)
        return
    if motor not in _MOTORES_SQL:
        await update.message.reply_text(
            "🤔 /preguntar solo genera SQL para motores relacionales (sqlite, postgres, mysql). "
            f"Tu conexión actual es {motor}."
        )
        return

    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("Uso: /preguntar cuántos usuarios hay")
        return

    sql, fuente = generar_sql(texto, connector=conector)
    if not sql:
        await update.message.reply_text(
            "🤔 No pude traducir esa pregunta a SQL. Prueba reformularla o usa /consulta directamente."
        )
        return

    origen = "🧠 IA" if fuente == "ia" else "🔤 patrones de respaldo (sin IA configurada)"
    await update.message.reply_text(
        f"SQL generado ({origen}):\n<pre>{sql}</pre>\n\n"
        "Esto NO se ejecutó automáticamente. Si es una consulta de lectura y "
        f"quieres correrla, usa:\n<code>/consulta {sql}</code>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_revisar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    motor = _motores.get(chat_id, "sqlite")
    comando = " ".join(context.args)
    if not comando:
        await update.message.reply_text("Uso: /revisar DELETE FROM usuarios")
        return

    cmd = comando.lower().strip()
    alertas = [desc for patron, desc in _PATRONES_PELIGROSOS if cmd.startswith(patron)]
    if cmd.startswith("delete") and "where" not in cmd:
        alertas.append("DELETE sin WHERE eliminaría TODOS los registros")
    if cmd.startswith("update") and "where" not in cmd:
        alertas.append("UPDATE sin WHERE actualizaría TODOS los registros")

    if not alertas:
        await update.message.reply_text(
            "✅ No se detectaron patrones peligrosos conocidos.\n"
            "(Este análisis es orientativo, no reemplaza tu criterio.)"
        )
        return

    texto = "⚠️ <b>Advertencias detectadas:</b>\n" + "\n".join(f"- {a}" for a in alertas)
    es_valido, _ = _validar_lectura(motor, comando)
    if not es_valido:
        texto += "\n\n🚫 Además, este bot no ejecutaría este comando de todas formas (no es de solo lectura)."
    await update.message.reply_text(texto, parse_mode=ParseMode.HTML)


async def cmd_disconnect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    conector = _conexiones.pop(chat_id, None)
    _motores.pop(chat_id, None)
    if conector is None:
        await update.message.reply_text("No tenías ninguna conexión activa.")
        return
    conector.disconnect()
    await update.message.reply_text("🔌 Conexión cerrada.")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en el archivo .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("conectar", cmd_conectar))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("info", cmd_status))
    app.add_handler(CommandHandler("tablas", cmd_tablas))
    app.add_handler(CommandHandler("consulta", cmd_consulta))
    app.add_handler(CommandHandler("preguntar", cmd_preguntar))
    app.add_handler(CommandHandler("revisar", cmd_revisar))
    app.add_handler(CommandHandler("disconnect", cmd_disconnect))
    app.add_handler(CommandHandler("desconectar", cmd_disconnect))

    logger.info("Bot NexusDB iniciado. IA: %s (%s)", ia_disponible(), ia_proveedor() or "ninguno")
    app.run_polling()


if __name__ == "__main__":
    main()
