"""
Asistente inteligente: convierte texto en español a SQL.
"""

import re


def sugerir_sql(texto: str):
    """
    Convierte una frase en español a SQL.
    Retorna un string con la consulta SQL, o None si no se reconoce el patrón.
    """
    orig = texto.strip()           # texto original (preserva mayúsculas en valores)
    t    = orig.lower()            # versión en minúsculas para coincidencia de patrones

    # ── [muéstrame] cuántos X de/con VALOR ────────────────────────────────────
    # "cuántos pedidos de laptop" / "muéstrame cuántos pedidos con laptop"
    m = re.match(
        r'(?:mu[eé]stra(?:me)?\s+)?cu[aá]ntos?\s+(\w+)\s+(?:de|con|hay\s+de)\s+(\w+)', t
    )
    if m:
        tabla, valor = m.group(1), m.group(2)
        return (
            f"SELECT COUNT(*) FROM {tabla} WHERE "
            f"nombre LIKE '%{valor}%' OR producto LIKE '%{valor}%' "
            f"OR descripcion LIKE '%{valor}%'"
        )

    # ── [muéstrame] cuántos X [hay] ───────────────────────────────────────────
    # "cuántos pedidos hay" / "muéstrame cuántos usuarios"
    m = re.match(r'(?:mu[eé]stra(?:me)?\s+)?cu[aá]ntos?\s+(\w+)(?:\s+hay)?$', t)
    if m:
        return f"SELECT COUNT(*) FROM {m.group(1)}"

    # ── cuantos X hay (original) ───────────────────────────────────────────────
    m = re.match(r'cu[aá]ntos?\s+(\w+)\s+hay', t)
    if m:
        return f"SELECT COUNT(*) FROM {m.group(1)}"

    # ── [muéstrame] el/la X más ORDEN ─────────────────────────────────────────
    # "el pedido más caro" / "muéstrame el pedido más alto"
    _ORDENES = r'(caro|alto|grande|reciente|nuevo|barato|peque[ñn]o|antiguo)'
    m = re.match(
        r'(?:mu[eé]stra(?:me)?\s+)?(?:el|la)\s+(\w+)\s+m[aá]s\s+' + _ORDENES,
        t
    )
    if m:
        tabla_sing, orden = m.group(1), m.group(2)
        tabla = tabla_sing if tabla_sing.endswith('s') else tabla_sing + 's'
        campo = _inferir_campo(orden)
        desc = orden in ('caro', 'alto', 'grande', 'reciente', 'nuevo')
        return f"SELECT * FROM {tabla} ORDER BY {campo} {'DESC' if desc else 'ASC'} LIMIT 1"

    # ── [muéstrame] los/las N X más ORDEN ─────────────────────────────────────
    # "los 3 pedidos más caros" / "muéstrame los 5 productos más baratos"
    m = re.match(
        r'(?:mu[eé]stra(?:me)?\s+)?(?:los|las|lo|la)\s+(\d+)\s+(\w+)\s+m[aá]s\s+'
        r'(caros?|altos?|grandes?|recientes?|nuevos?|baratos?|peque[ñn]os?|antiguos?)',
        t
    )
    if m:
        n, tabla, orden = m.group(1), m.group(2), m.group(3)
        campo = _inferir_campo(orden)
        desc = any(orden.startswith(p) for p in ('car', 'alt', 'gran', 'recien', 'nuev'))
        return f"SELECT * FROM {tabla} ORDER BY {campo} {'DESC' if desc else 'ASC'} LIMIT {n}"

    # "los pedidos más caros" / "muéstrame los productos más baratos" (sin número → top 5)
    m = re.match(
        r'(?:mu[eé]stra(?:me)?\s+)?(?:los|las)\s+(\w+)\s+m[aá]s\s+'
        r'(caros?|altos?|grandes?|recientes?|nuevos?|baratos?|peque[ñn]os?|antiguos?)',
        t
    )
    if m:
        tabla, orden = m.group(1), m.group(2)
        campo = _inferir_campo(orden)
        desc = any(orden.startswith(p) for p in ('car', 'alt', 'gran', 'recien', 'nuev'))
        return f"SELECT * FROM {tabla} ORDER BY {campo} {'DESC' if desc else 'ASC'} LIMIT 5"

    # ── muestra los N X mas ORDEN (patrón legacy sin acento) ──────────────────
    m = re.match(
        r'muestra\s+(?:los|la|lo|las)\s+(\d+)\s+(\w+)\s+m[aá]s\s+'
        r'(caros?|baratos?|recientes?|antiguos?|grandes?|peque[ñn]os?)',
        t
    )
    if m:
        n, tabla, orden = m.group(1), m.group(2), m.group(3)
        campo = _inferir_campo(orden)
        desc = any(orden.startswith(p) for p in ('car', 'gran', 'recien'))
        return f"SELECT * FROM {tabla} ORDER BY {campo} {'DESC' if desc else 'ASC'} LIMIT {n}"

    # ── elimina X donde Y es Z ─────────────────────────────────────────────────
    m = re.match(r'elimina\s+(\w+)\s+donde\s+(\w+)\s+es\s+(\S+)', t)
    if m:
        # Obtener los valores originales (posición en el texto original)
        mo = re.match(r'elimina\s+(\w+)\s+donde\s+(\w+)\s+es\s+(\S+)', orig, re.IGNORECASE)
        tabla, col, val = mo.group(1), mo.group(2), mo.group(3)
        return f"DELETE FROM {tabla} WHERE {col} = {_fmt(val)}"

    # ── actualiza X set Y a Z donde W es V ────────────────────────────────────
    m = re.match(
        r'actualiza\s+(\w+)\s+set\s+(\w+)\s+a\s+(\S+)\s+donde\s+(\w+)\s+es\s+(\S+)', t
    )
    if m:
        mo = re.match(
            r'actualiza\s+(\w+)\s+set\s+(\w+)\s+a\s+(\S+)\s+donde\s+(\w+)\s+es\s+(\S+)',
            orig, re.IGNORECASE
        )
        tabla, col_s, val_s, col_w, val_w = mo.groups()
        return f"UPDATE {tabla} SET {col_s} = {_fmt(val_s)} WHERE {col_w} = {_fmt(val_w)}"

    # ── inserta X col1 val1 col2 val2 … ───────────────────────────────────────
    m = re.match(r'inserta\s+(\w+)\s+(.+)', t)
    if m:
        mo = re.match(r'inserta\s+(\w+)\s+(.+)', orig, re.IGNORECASE)
        tabla = mo.group(1)
        tokens = mo.group(2).split()
        cols, vals = [], []
        i = 0
        while i + 1 < len(tokens):
            cols.append(tokens[i])
            vals.append(_fmt(tokens[i + 1]))
            i += 2
        if cols:
            return f"INSERT INTO {tabla} ({', '.join(cols)}) VALUES ({', '.join(vals)})"

    # ── muestra X donde Y es Z ─────────────────────────────────────────────────
    m = re.match(r'muestra\s+(\w+)\s+donde\s+(\w+)\s+es\s+(\S+)', t)
    if m:
        mo = re.match(r'muestra\s+(\w+)\s+donde\s+(\w+)\s+es\s+(\S+)', orig, re.IGNORECASE)
        tabla, col, val = mo.groups()
        return f"SELECT * FROM {tabla} WHERE {col} = {_fmt(val)}"

    # ── muestra X con Y mayor a Z ──────────────────────────────────────────────
    m = re.match(r'muestra\s+(\w+)\s+con\s+(\w+)\s+mayor\s+[aá]\s+(\S+)', t)
    if m:
        mo = re.match(r'muestra\s+(\w+)\s+con\s+(\w+)\s+mayor\s+[aá]\s+(\S+)', orig, re.IGNORECASE)
        tabla, col, val = mo.groups()
        return f"SELECT * FROM {tabla} WHERE {col} > {val}"

    # ── muestra X con Y menor a Z ──────────────────────────────────────────────
    m = re.match(r'muestra\s+(\w+)\s+con\s+(\w+)\s+menor\s+[aá]\s+(\S+)', t)
    if m:
        mo = re.match(r'muestra\s+(\w+)\s+con\s+(\w+)\s+menor\s+[aá]\s+(\S+)', orig, re.IGNORECASE)
        tabla, col, val = mo.groups()
        return f"SELECT * FROM {tabla} WHERE {col} < {val}"

    # ── muéstrame las tablas / lista las tablas ───────────────────────────────
    m = re.match(
        r'(?:mu[eé]stra(?:me)?\s+|listar?\s+|dame\s+)(?:todas?\s+)?(?:las?\s+)?tablas?$', t
    )
    if m:
        return "show tables"

    # ── muestra X / muéstrame [todos los] X ───────────────────────────────────
    m = re.match(r'mu[eé]stra(?:me)?\s+(?:todos?\s+)?(?:los?\s+|las?\s+)?(\w+)', t)
    if m:
        return f"SELECT * FROM {m.group(1)}"

    # ── dame [todos los] X / tráeme X ─────────────────────────────────────────
    m = re.match(r'(?:dame|tr[aá]eme)\s+(?:todos?\s+)?(?:los?\s+|las?\s+)?(\w+)', t)
    if m:
        return f"SELECT * FROM {m.group(1)}"

    # ── lista [los] X / listar X ───────────────────────────────────────────────
    m = re.match(r'listar?\s+(?:los?\s+|las?\s+)?(\w+)', t)
    if m:
        return f"SELECT * FROM {m.group(1)}"

    return None


# ── helpers ────────────────────────────────────────────────────────────────────

def _fmt(val: str) -> str:
    """Formatea un valor: numérico sin comillas, texto con comillas simples."""
    try:
        float(val)
        return val
    except ValueError:
        return f"'{val}'"


def _inferir_campo(orden: str) -> str:
    mapa = {
        'caro': 'precio',   'caros': 'precio',
        'barato': 'precio', 'baratos': 'precio',
        'alto': 'total',    'altos': 'total',
        'reciente': 'fecha','recientes': 'fecha',
        'nuevo': 'fecha',   'nuevos': 'fecha',
        'antiguo': 'fecha', 'antiguos': 'fecha',
        'grande': 'cantidad','grandes': 'cantidad',
        'pequeño': 'cantidad','pequeños': 'cantidad',
        'rapido': 'velocidad','rápido': 'velocidad',
    }
    return mapa.get(orden, 'id')
